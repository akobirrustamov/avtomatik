"""Rasmdan davlat raqamini o'qish (OCR)."""
import re

from config import ANIQLASH_ENI

# O'zbekiston raqamlari: 01A123AA (jismoniy) va 01123ABC (yuridik)
SHABLONLAR = [re.compile(r"^\d{2}[A-Z]\d{3}[A-Z]{2}$"),
              re.compile(r"^\d{2}\d{3}[A-Z][a-z]{3}$")]

_oqiydigan = None


def raqamni_tozalash(matn):
    """Bo'sh joy va belgilarni olib tashlaydi, katta harfga o'tkazadi."""
    return re.sub(r"[^A-Z0-9]", "", matn.upper())


def togri_formatmi(raqam):
    return any(sh.match(raqam) for sh in SHABLONLAR)


def _oqiydiganni_olish():
    global _oqiydigan
    if _oqiydigan is None:
        import easyocr  # og'ir kutubxona, faqat kerak bo'lganda yuklanadi
        _oqiydigan = easyocr.Reader(["en"], gpu=False)
    return _oqiydigan


# Raqam ichidagi guruhlar: (nechta belgi, raqammi yoki harfmi)
RAQAMLAR = "0123456789"
HARFLAR = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
GURUHLAR = [[(2, RAQAMLAR), (1, HARFLAR), (3, RAQAMLAR), (2, HARFLAR)],   # 01 A 123 AA
            [(2, RAQAMLAR), (3, RAQAMLAR), (3, HARFLAR)]]                 # 01 123 ABC
KESIM_BALANDLIGI = 220        # kesilgan raqam shu balandlikka kattalashtiriladi (piksel)
# Kesishda raqam atrofidan qoldiriladigan joy (ulushda). Har biri alohida o'qiladi,
# keyin natijalar "ovoz beradi" — bitta o'qish adashsa ham umumiy natija to'g'ri chiqadi.
CHEKKALAR = (0.05, 0.1, 0.15)


def tayyorlash():
    """OCR modelini oldindan yuklaydi (birinchi yuklash bir necha soniya oladi)."""
    try:
        _oqiydiganni_olish()
        return True
    except ImportError:
        print("easyocr o'rnatilmagan. Terminalda: pip install easyocr")
        return False


def _qatorlarga_birlashtirish(qutilar):
    """Bir qatorda yonma-yon turgan matn qutilarini bitta qutiga qo'shadi.

    OCR raqamni ba'zan "01" va "A123AA" deb ikkiga bo'lib topadi."""
    qutilar = sorted(qutilar)
    natija = []
    for x0, y0, x1, y1 in qutilar:
        if natija:
            a0, b0, a1, b1 = natija[-1]
            balandlik = min(y1 - y0, b1 - b0)
            ustma_ust = min(y1, b1) - max(y0, b0)
            if ustma_ust > 0.5 * balandlik and x0 - a1 < 1.5 * balandlik:
                natija[-1] = (min(a0, x0), min(b0, y0), max(a1, x1), max(b1, y1))
                continue
        natija.append((x0, y0, x1, y1))
    return natija


def _belgilarni_topish(kulrang):
    """Kesilgan raqamdagi belgilarni topadi.

    (belgilar, oq_qora) qaytaradi: belgilar — chapdan o'ngga (x, y, eni, bo'yi) qutilar,
    oq_qora — oq fonda qora belgili tozalangan rasm."""
    import cv2
    _, qora_oq = cv2.threshold(kulrang, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    _, _, malumot, _ = cv2.connectedComponentsWithStats(qora_oq)
    bal = kulrang.shape[0]
    belgilar = [tuple(int(v) for v in m[:4]) for m in malumot[1:]
                if 0.25 * bal < m[3] < 0.95 * bal and 0.15 * m[3] < m[2] < 1.2 * m[3]]
    if not belgilar:
        return [], 255 - qora_oq
    eng_baland = max(b[3] for b in belgilar)
    # Viloyat kodi ("01") kichikroq yoziladi, shuning uchun 0.6 gacha ruxsat beramiz.
    return sorted(b for b in belgilar if b[3] >= 0.6 * eng_baland), 255 - qora_oq


def _formatni_tanlash(belgilar):
    """Belgilar orasidagi bo'shliqqa qarab raqam turini tanlaydi.

    "01 A 123 AA" da katta bo'shliq 3- va 6-belgidan keyin, "01 123 ABC" da 5-belgidan
    keyin keladi. Aniq bo'lmasa ikkala tur ham sinab ko'riladi."""
    b = [belgilar[i + 1][0] - (belgilar[i][0] + belgilar[i][2]) for i in range(7)]
    if min(b[2], b[5]) > max(b[3], b[4], b[6]):
        return GURUHLAR[:1]
    if b[4] > max(b[2], b[3], b[5], b[6]):
        return GURUHLAR[1:]
    return GURUHLAR


def _guruhni_oqish(oqiydigan, rasmlar, belgilar, ruxsat):
    """Bir nechta belgini faqat raqam yoki faqat harf deb o'qiydi. (matn, ishonch).

    Kulrang va oq-qora rasmning ikkalasidan o'qib, uzunligi to'g'ri chiqqanlaridan
    ishonchlirog'ini oladi."""
    import cv2
    x0 = max(0, min(b[0] for b in belgilar) - 6)
    y0 = max(0, min(b[1] for b in belgilar) - 6)
    x1 = max(b[0] + b[2] for b in belgilar) + 6
    y1 = max(b[1] + b[3] for b in belgilar) + 6
    eng_yaxshi = ("", 0.0)
    for rasm in rasmlar:
        bolak = cv2.copyMakeBorder(rasm[y0:y1, x0:x1], 12, 12, 24, 24,
                                   cv2.BORDER_CONSTANT, value=255)
        natija = oqiydigan.recognize(bolak, allowlist=ruxsat)
        if len(natija) != 1 or len(natija[0][1]) != len(belgilar):
            continue
        if float(natija[0][2]) > eng_yaxshi[1]:
            eng_yaxshi = (natija[0][1], float(natija[0][2]))
    return eng_yaxshi


def _kesib_oqish(oqiydigan, kadr, quti):
    """Raqam turgan joyni kesib, kattalashtirib, guruhma-guruh o'qiydi.

    Har xil chekka bilan bir necha marta o'qiydi va eng ko'p "ovoz" olgan raqamni
    [(raqam, ishonch)] ko'rinishida qaytaradi (topilmasa bo'sh ro'yxat)."""
    import cv2
    x0, y0, x1, y1 = quti
    topilgan = []
    for chekka in CHEKKALAR:
        cx, cy = int((x1 - x0) * chekka), int((y1 - y0) * chekka)
        kesim = kadr[max(0, y0 - cy):y1 + cy, max(0, x0 - cx):x1 + cx]
        if kesim.size == 0:
            continue
        olchov = KESIM_BALANDLIGI / kesim.shape[0]
        kesim = cv2.resize(kesim, None, fx=olchov, fy=olchov, interpolation=cv2.INTER_CUBIC)
        kulrang = cv2.cvtColor(kesim, cv2.COLOR_BGR2GRAY) if kesim.ndim == 3 else kesim
        belgilar, oq_qora = _belgilarni_topish(kulrang)
        if len(belgilar) != 8:
            continue
        for guruhlar in _formatni_tanlash(belgilar):
            raqam, ishonchlar, boshi = "", [], 0
            for soni, ruxsat in guruhlar:
                matn, ishonch = _guruhni_oqish(
                    oqiydigan, (kulrang, oq_qora), belgilar[boshi:boshi + soni], ruxsat)
                if len(matn) != soni:
                    break
                raqam += matn
                ishonchlar.append(ishonch)
                boshi += soni
            else:
                topilgan.append((raqam, min(ishonchlar)))
    if not topilgan:
        return []
    ovozlar = {}
    for raqam, ishonch in topilgan:
        ovozlar.setdefault(raqam, []).append(ishonch)
    golib = max(ovozlar, key=lambda r: sum(ovozlar[r]))
    return [(golib, sum(ovozlar[golib]) / len(ovozlar[golib]))]


def raqamni_aniqlash(kadr):
    """(raqam, ishonch) qaytaradi. Aniqlanmasa (None, 0.0).

    Boshqa OCR vositasiga o'tish uchun faqat shu funksiya ichini almashtirish kifoya."""
    try:
        oqiydigan = _oqiydiganni_olish()
    except ImportError:
        print("easyocr o'rnatilmagan. Terminalda: pip install easyocr")
        return None, 0.0

    # Matn joyini kichraytirilgan kadrdan qidiramiz (ancha tez), raqamning o'zini esa
    # keyin asl, to'liq o'lchamli kadrdan kesib o'qiymiz.
    import cv2
    olchov = min(1.0, ANIQLASH_ENI / kadr.shape[1])
    kichik = cv2.resize(kadr, None, fx=olchov, fy=olchov) if olchov < 1 else kadr
    natijalar = oqiydigan.readtext(kichik, allowlist=HARFLAR + RAQAMLAR + " ")
    # Raqam ba'zan bo'laklarga bo'linib o'qiladi ("01", "A123AA"), shuning uchun
    # avval hammasini birlashtirib, keyin alohida-alohida sinab ko'ramiz.
    nomzodlar = []
    if natijalar:
        birlashgan = raqamni_tozalash("".join(m for _, m, _ in natijalar))
        ortacha = sum(i for _, _, i in natijalar) / len(natijalar)
        nomzodlar.append((birlashgan, ortacha))
        nomzodlar += [(raqamni_tozalash(m), i) for _, m, i in natijalar]

    # Butun kadrdan o'qish kichik raqamlarda adashadi (4 ni G deb o'qiydi).
    # Shuning uchun topilgan matn joyini kesib olib, aniqroq qayta o'qiymiz.
    qutilar = [(int(min(n[0] for n in q) / olchov), int(min(n[1] for n in q) / olchov),
                int(max(n[0] for n in q) / olchov), int(max(n[1] for n in q) / olchov))
               for q, _, _ in natijalar]
    for x0, y0, x1, y1 in set(qutilar + _qatorlarga_birlashtirish(qutilar)):
        # Raqam belgisi yotiq to'rtburchak; boshqa shakldagi matnlarga vaqt sarflamaymiz.
        if y1 - y0 >= 12 and 2 <= (x1 - x0) / (y1 - y0) <= 8:
            nomzodlar += _kesib_oqish(oqiydigan, kadr, (x0, y0, x1, y1))

    nomzodlar = [(r, float(i)) for r, i in nomzodlar if togri_formatmi(r)]
    if not nomzodlar:
        return None, 0.0
    return max(nomzodlar, key=lambda x: x[1])
