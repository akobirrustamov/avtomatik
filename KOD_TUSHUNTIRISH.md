# Avtomatik avtoturargoh — kodning to'liq tushuntirishi

Bu hujjat loyihadagi har bir faylni, har bir funksiyani va muhim qatorlarni oddiy tilda tushuntiradi.

Loyiha **1-24 ATT guruhi** talabalari bilan birga, dars paytida yozilgan.

## Mundarija
0. Katta rasm: kod qanday ishlaydi
1. `config.py` — sozlamalar
2. `billing.py` — pul hisoblash
3. `recognition.py` — raqamni o'qish
4. `camera.py` — kamera
5. `database.py` — Excel bazasi
6. `gate.py` — shlagbaum
7. `nazorat.py` — asosiy mantiq (eng muhimi)
8. `main.py` — menyu
9. Dastur boshdan oxirigacha: bitta mashinaning yo'li
10. Ehtiyot bo'lish kerak bo'lgan joylar
11. Tekshirib ko'rish uchun savollar

---

## 0. Katta rasm

```
main.py ──► nazorat.py ──► camera.py        (kadr olish, harakatni sezish)
                       ├─► recognition.py   (kadrdan raqam o'qish)
                       ├─► database.py      (Excel: kim ruxsatli, kim ichkarida)
                       ├─► billing.py       (daqiqa va so'm)
                       └─► gate.py          (shlagbaum)
config.py  ◄── hamma fayl shu yerdan sozlama o'qiydi
```

**Asosiy g'oya:** har fayl bitta ishni biladi. `nazorat.py` — «boshliq»: u qolgan fayllarning funksiyalarini to'g'ri tartibda chaqiradi. Xizmat fayllari bir-birini bilmaydi. Shuning uchun, masalan, OCR vositasini almashtirsangiz, faqat `recognition.py` o'zgaradi.

**Faylni ishga tushirish:** `python main.py`. Boshqa fayllar o'zi ishlamaydi, ular `import` orqali chaqiriladi.

---

## 1. `config.py` — sozlamalar

Bu faylda faqat o'zgaruvchilar bor, funksiya yo'q. Sabab: narxni yoki kamera raqamini o'zgartirmoqchi bo'lsangiz, butun kodni qidirib yurmaysiz, faqat shu faylni ochasiz.

```python
EXCEL_FILE = "avtomobillar.xlsx"
RASMLAR_PAPKASI = "rasmlar"
```
Excel fayl nomi va rasmlar saqlanadigan papka nomi. Matnlar (`str`).

```python
TARIF_DAQIQAGA = 100
```
Bir daqiqa narxi, so'mda (`int`). **Narxni o'zgartirish uchun faqat shu raqamni o'zgartiring.**

```python
KAMERALAR = [("avto", 0)]
```
Ro'yxat (`list`), ichida tuple (`tuple`) bor. Har tuple: `(yo'nalish, kamera_raqami)`.
- `0` — kompyuterning birinchi kamerasi, `1` — ikkinchisi.
- `"avto"` — yo'nalishni dastur o'zi aniqlaydi (ichkarida bo'lsa chiqish, bo'lmasa kirish).
- Ikkita kamera bo'lsa: `[("kirish", 0), ("chiqish", 1)]`.

```python
KADR_ENI, KADR_BOYI = 1280, 720
```
Kameradan so'raladigan kadr o'lchami (piksel). Kadr qancha katta bo'lsa, raqam shuncha aniq ko'rinadi, lekin o'qish sekinlashadi.

```python
HARAKAT_CHEGARASI = 0.01
HARAKATDAN_KEYIN_SONIYA = 3
ANIQLASH_ENI = 960
MIN_ISHONCH = 0.5
TAKROR_SONIYA = 60
```
- **HARAKAT_CHEGARASI** — raqam doim emas, faqat kadrda **harakat** bo'lganda (mashina kelganda) o'qiladi. Kadrning 1% i (`0.01`) o'zgarsa — harakat bor deb hisoblaymiz.
- **HARAKATDAN_KEYIN_SONIYA** — harakat to'xtagandan keyin yana 3 soniya o'qishda davom etamiz. Mashina to'xtab turgan paytda raqam eng aniq ko'rinadi.
- **ANIQLASH_ENI** — matn joyini qidirishda kadr 960 piksel enga kichraytiriladi (tezroq ishlaydi). Raqamning o'zi keyin asl kadrdan o'qiladi.
- **MIN_ISHONCH** — OCR har natijaga 0 dan 1 gacha «ishonch» beradi. 0.5 dan pasti ishonchsiz, e'tiborsiz qoldiriladi.
- **TAKROR_SONIYA** — mashina kamera oldida turganda u bir necha marta o'qiladi. Bir mashinani 60 soniya ichida qayta ishlamaymiz.

```python
VARAQ_AVTO = "Avtomobillar"
VARAQ_SESSIYA = "Sessiyalar"
SARLAVHA_AVTO = ["ID", "Davlat raqami", "Egasi", "Model", "Holati"]
SARLAVHA_SESSIYA = ["ID", "Davlat raqami", "Kirish vaqti", "Chiqish vaqti",
                    "Daqiqa", "Summa (so'm)", "Kirish rasmi", "Chiqish rasmi"]
```
Excelning ikki varag'i nomi va ularning ustun sarlavhalari. **Sessiya** — mashinaning bitta kirishidan chiqishigacha bo'lgan davr.

```python
VAQT_FORMATI = "%Y-%m-%d %H:%M:%S"
RUXSAT = "Ruxsat berilgan"
TAQIQ = "Taqiqlangan"
```
- Vaqt formati: `2026-11-04 10:00:00`. `%Y` — yil, `%m` — oy, `%d` — kun, `%H:%M:%S` — soat:daqiqa:soniya.
- `RUXSAT` va `TAQIQ` — matnni har joyda qayta yozmaslik uchun. Bir joyda xato yozilsa (`"Ruxsat berligan"`), dastur ishlamay qoladi. O'zgaruvchi bo'lsa, xatoni Python o'zi ko'rsatadi.

---

## 2. `billing.py` — pul hisoblash

Bu fayl **faqat hisob-kitob** qiladi: Excelni ham, kamerani ham bilmaydi. Shuning uchun uni alohida sinash juda oson.

```python
import math
from config import TARIF_DAQIQAGA
```
- `import math` — Python'ning matematika modulini olamiz (`math.ceil` kerak).
- `from config import TARIF_DAQIQAGA` — `config.py` faylidan faqat bitta o'zgaruvchini olamiz.

```python
def daqiqani_hisoblash(kirish, chiqish):
    soniya = (chiqish - kirish).total_seconds()
    return max(1, math.ceil(soniya / 60))
```
Qadam-baqadam:
1. `chiqish - kirish` — ikkita `datetime` ni ayirsak, `timedelta` (vaqt farqi) chiqadi.
2. `.total_seconds()` — shu farqni soniyaga aylantiradi. 65 soniya bo'lsa → `65.0`.
3. `soniya / 60` — daqiqaga: `65 / 60 = 1.083…`
4. `math.ceil(...)` — **yuqoriga yaxlitlaydi**: `1.083 → 2`. Shu sabab «har boshlangan daqiqa to'liq hisoblanadi».
5. `max(1, ...)` — natija kamida 1 bo'lsin. 10 soniya turgan mashina ham 1 daqiqa to'laydi (`ceil(0.17) = 1` bo'lsa ham, `0` soniya bo'lsa `ceil(0) = 0` bo'lardi, `max` buni to'sadi).

| Turgan vaqt | soniya/60 | ceil | max(1, …) |
|---|---|---|---|
| 30 s | 0.5 | 1 | 1 |
| 60 s | 1.0 | 1 | 1 |
| 65 s | 1.08 | 2 | 2 |
| 600 s | 10.0 | 10 | 10 |

```python
def summani_hisoblash(daqiqa):
    return daqiqa * TARIF_DAQIQAGA
```
Daqiqani narxga ko'paytiradi: `2 * 100 = 200`.

---

## 3. `recognition.py` — raqamni o'qish

```python
import re

from config import ANIQLASH_ENI
```
`re` — «regular expression» (andoza bilan matn tekshirish) moduli. `ANIQLASH_ENI` — sozlamalardan olinadi.

Bu fayl ikki qismdan iborat: **matn bilan ishlash** (3.1–3.3, kamerasiz sinab ko'rsa bo'ladi) va **rasmdan o'qish** (3.4–3.7).

### 3.1. Raqam andozalari

```python
SHABLONLAR = [re.compile(r"^\d{2}[A-Z]\d{3}[A-Z]{2}$"),
              re.compile(r"^\d{2}\d{3}[A-Z]{3}$")]
```
O'zbekiston raqamining ikki xil ko'rinishi bor. Andozani o'qish:

| Belgi | Ma'nosi |
|---|---|
| `^` | matn boshi |
| `\d{2}` | aynan 2 ta raqam |
| `[A-Z]` | 1 ta katta lotin harfi |
| `\d{3}` | 3 ta raqam |
| `[A-Z]{2}` | 2 ta harf |
| `$` | matn oxiri |

- 1-andoza: `01A123AA` (2 raqam + harf + 3 raqam + 2 harf) — jismoniy shaxs raqami.
- 2-andoza: `01123ABC` (5 raqam + 3 harf) — yuridik shaxs raqami.

Nima uchun kerak? OCR ba'zan axlat o'qiydi («XYZ», «12»). Andozaga to'g'ri kelmasa, uni raqam deb qabul qilmaymiz.

### 3.2. Tozalash

```python
def raqamni_tozalash(matn):
    return re.sub(r"[^A-Z0-9]", "", matn.upper())
```
- `matn.upper()` — hamma harfni kattaga: `"01a 123-aa"` → `"01A 123-AA"`.
- `re.sub(r"[^A-Z0-9]", "", ...)` — «A–Z va 0–9 dan **boshqa** hamma belgini bo'shga almashtir». `^` qavs ichida «emas» degani. Natija: `"01A123AA"`.

### 3.3. Format tekshiruvi

```python
def togri_formatmi(raqam):
    return any(sh.match(raqam) for sh in SHABLONLAR)
```
`any(...)` — ichidagilardan kamida bittasi `True` bo'lsa, `True` qaytaradi. Ya'ni raqam ikkala andozadan biriga mos bo'lsa — to'g'ri.

### 3.4. OCR'ni yuklash

```python
_oqiydigan = None

def _oqiydiganni_olish():
    global _oqiydigan
    if _oqiydigan is None:
        import easyocr
        _oqiydigan = easyocr.Reader(["en"], gpu=False)
    return _oqiydigan
```
- `easyocr` modeli yuklanishi sekin (bir necha soniya) va ko'p xotira oladi. Shuning uchun **bir marta** yuklaymiz, keyin eslab qolamiz (`_oqiydigan` ichida).
- `global _oqiydigan` — funksiya ichida tashqaridagi o'zgaruvchini o'zgartirish uchun.
- `import easyocr` funksiya ichida: kutubxona o'rnatilmagan bo'lsa ham, dasturning boshqa qismlari (menyu, Excel) ishlayveradi.
- Nom boshidagi `_` — «bu ichki narsa, tashqaridan tegmang» degan kelishuv.

```python
def tayyorlash():
    try:
        _oqiydiganni_olish()
        return True
    except ImportError:
        print("easyocr o'rnatilmagan. Terminalda: pip install easyocr")
        return False
```
Modelni **oldindan** yuklaydi. `nazorat.py` uni kamera sikli boshlanishidan oldin chaqiradi. Aks holda model birinchi kadr o'qilayotganda yuklanib, dastur bir necha soniya «qotib» qolardi. `True` — tayyor, `False` — kutubxona yo'q.

### 3.5. Nima uchun raqamni kesib o'qiymiz

Darsda sinab ko'rganimizda `70 A 444 AA` raqamli rasmni OCR `ZAGGGAA` deb o'qidi: `4` ni `G`, `70` ni `Z` deb. Ikki sabab bor edi:

1. Raqam kadrda juda kichik edi (bo'yi ~28 piksel).
2. OCR har bir belgi harf ham, raqam ham bo'lishi mumkin deb o'ylaydi, shuning uchun o'xshash belgilarni adashtiradi (`4`/`G`, `0`/`O`, `1`/`I`).

Yechim — raqamni **ikki bosqichda** o'qish:

```
1. kadrni kichraytir → matn turgan joylarni top
2. har bir joyni asl kadrdan kesib ol va kattalashtir
3. kesimni alohida belgilarga ajrat (8 ta bo'lishi kerak)
4. belgilar orasidagi bo'shliqqa qarab raqam turini tanla
5. har guruhni faqat raqam yoki faqat harf deb o'qi:  70 | A | 444 | AA
6. buni uch xil chekka bilan takrorla → natijalar «ovoz beradi»
```

5-qadam asosiy g'oya: «bu joyda faqat raqam bo'ladi» deb aytsak, OCR `4` ni `G` deb o'qiy olmaydi.

Sozlamalar (fayl ichida):

```python
RAQAMLAR = "0123456789"
HARFLAR = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
GURUHLAR = [[(2, RAQAMLAR), (1, HARFLAR), (3, RAQAMLAR), (2, HARFLAR)],   # 01 A 123 AA
            [(2, RAQAMLAR), (3, RAQAMLAR), (3, HARFLAR)]]                 # 01 123 ABC
KESIM_BALANDLIGI = 220
CHEKKALAR = (0.05, 0.1, 0.15)
```
- `GURUHLAR` — har raqam turi uchun guruhlar ro'yxati. Har guruh tuple: `(nechta belgi, qaysi belgilarga ruxsat)`. Ikkala turda ham jami **8 ta belgi**.
- `KESIM_BALANDLIGI` — kesilgan raqam shu balandlikka (piksel) kattalashtiriladi.
- `CHEKKALAR` — kesishda raqam atrofidan qoldiriladigan joy: 5%, 10%, 15%.

### 3.6. Yordamchi funksiyalar

Hammasining nomi `_` bilan boshlanadi — ular faqat shu fayl ichida ishlatiladi.

**`_qatorlarga_birlashtirish(qutilar)`** — OCR raqamni ba'zan ikki bo'lak qilib topadi (`"01"` va `"A123AA"`). Bu funksiya bir qatorda yonma-yon turgan qutilarni bitta katta qutiga qo'shadi. Quti — `(x0, y0, x1, y1)`: chap-yuqori va o'ng-past burchak.

```python
if ustma_ust > 0.5 * balandlik and x0 - a1 < 1.5 * balandlik:
```
Ikki quti qo'shiladi, agar ular bir balandlikda tursa (`ustma_ust` katta) **va** oralari yaqin bo'lsa.

**`_belgilarni_topish(kulrang)`** — kesilgan raqamdan har bir belgining joyini topadi.

```python
_, qora_oq = cv2.threshold(kulrang, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
_, _, malumot, _ = cv2.connectedComponentsWithStats(qora_oq)
```
- `threshold` — kulrang rasmni faqat **oq va qora** ga aylantiradi. `OTSU` — chegarani o'zi tanlaydi. `BINARY_INV` — teskari: belgilar oq, fon qora bo'ladi.
- `connectedComponentsWithStats` — bir-biriga tegib turgan oq piksellarni bitta «bo'lak» deb sanaydi. Har belgi — alohida bo'lak. `malumot` da har bo'lakning `x, y, eni, bo'yi` turadi.

```python
if 0.25 * bal < m[3] < 0.95 * bal and 0.15 * m[3] < m[2] < 1.2 * m[3]
```
Faqat belgiga o'xshash bo'laklarni qoldiramiz: bo'yi kesim balandligining 25–95% i, eni esa bo'yiga mos. Shunda raqam ramkasi, bayroqcha va mayda dog'lar tashlab yuboriladi.

**`_formatni_tanlash(belgilar)`** — raqam qaysi turda ekanini **bo'shliqlardan** aniqlaydi.

```python
b = [belgilar[i + 1][0] - (belgilar[i][0] + belgilar[i][2]) for i in range(7)]
```
`b` — 8 ta belgi orasidagi 7 ta bo'shliq (keyingi belgining boshi − oldingisining oxiri).
- `01 A 123 AA` da katta bo'shliq 3- va 6-belgidan keyin.
- `01 123 ABC` da katta bo'shliq 5-belgidan keyin.
- Aniq bo'lmasa — ikkala tur ham sinab ko'riladi.

**`_guruhni_oqish(oqiydigan, rasmlar, belgilar, ruxsat)`** — bitta guruhni (masalan `444`) o'qiydi.

```python
natija = oqiydigan.recognize(bolak, allowlist=ruxsat)
if len(natija) != 1 or len(natija[0][1]) != len(belgilar):
    continue
```
- `allowlist=ruxsat` — faqat raqamlar **yoki** faqat harflar. Eng muhim qator shu.
- O'qilgan matn uzunligi belgilar soniga teng bo'lmasa (3 ta belgi o'rniga 2 ta harf chiqsa) — natija tashlanadi.
- Kulrang va oq-qora rasmning ikkalasidan o'qib, ishonchi yuqorisini oladi.

**`_kesib_oqish(oqiydigan, kadr, quti)`** — yuqoridagilarni birlashtiradi.

```python
for chekka in CHEKKALAR:
    ... kes, kattalashtir, belgilarni top ...
    if len(belgilar) != 8:
        continue
```
Har chekka uchun: kesadi → kattalashtiradi → belgilarni topadi. Belgilar soni 8 ta bo'lmasa, bu raqam emas — o'tkazib yuboramiz.

```python
            for soni, ruxsat in guruhlar:
                matn, ishonch = _guruhni_oqish(...)
                if len(matn) != soni:
                    break
                raqam += matn
                ...
            else:
                topilgan.append((raqam, min(ishonchlar)))
```
Guruhlarni ketma-ket o'qib, raqamni yig'adi. Bu yerda **`for ... else`** bor: `else` qismi sikl `break` siz, oxirigacha yetgandagina bajariladi. Ya'ni hamma guruh o'qilgan bo'lsagina raqam ro'yxatga qo'shiladi. Ishonch — guruhlar ichida **eng pasti** (`min`): bitta guruh shubhali bo'lsa, butun raqam shubhali.

```python
ovozlar = {}
for raqam, ishonch in topilgan:
    ovozlar.setdefault(raqam, []).append(ishonch)
golib = max(ovozlar, key=lambda r: sum(ovozlar[r]))
```
**Ovoz berish.** Uch xil chekka bilan uchta natija chiqadi, masalan: `70A444AA`, `70A444AA`, `70A644AA`. Lug'atda har raqamning ishonchlari yig'iladi va yig'indisi eng katta bo'lgani g'olib bo'ladi. Bitta o'qish adashsa ham, umumiy natija to'g'ri chiqadi. `setdefault(raqam, [])` — kalit bo'lmasa bo'sh ro'yxat yaratadi.

### 3.7. Asosiy funksiya

```python
def raqamni_aniqlash(kadr):
    try:
        oqiydigan = _oqiydiganni_olish()
    except ImportError:
        print("easyocr o'rnatilmagan. Terminalda: pip install easyocr")
        return None, 0.0
```
`try/except` — xato bo'lishi mumkin bo'lgan joy. `easyocr` o'rnatilmagan bo'lsa `ImportError` chiqadi; dastur qulamasdan, tushunarli xabar beradi va `(None, 0.0)` («raqam yo'q, ishonch 0») qaytaradi.

`kadr` — bu **rasmning o'zi** (`cv2.imread` yoki kameradan olingan massiv). Fayl yo'li (`"rasm.jpg"`) yoki bo'sh matn berib bo'lmaydi.

```python
    olchov = min(1.0, ANIQLASH_ENI / kadr.shape[1])
    kichik = cv2.resize(kadr, None, fx=olchov, fy=olchov) if olchov < 1 else kadr
    natijalar = oqiydigan.readtext(kichik, allowlist=HARFLAR + RAQAMLAR + " ")
```
- `kadr.shape[1]` — kadr eni. Kadr 960 dan keng bo'lsa, kichraytiramiz (`olchov < 1`); tor bo'lsa, tegmaymiz.
- `readtext` rasmdan matnlarni topadi. Natija — ro'yxat, har element `(joylashuv, matn, ishonch)`:
```
[ ([...], "01", 0.9), ([...], "A123AA", 0.8) ]
```

```python
    nomzodlar = []
    if natijalar:
        birlashgan = raqamni_tozalash("".join(m for _, m, _ in natijalar))
        ortacha = sum(i for _, _, i in natijalar) / len(natijalar)
        nomzodlar.append((birlashgan, ortacha))
        nomzodlar += [(raqamni_tozalash(m), i) for _, m, i in natijalar]
```
**Birinchi urinish** — butun kadrdan o'qilgan matnning o'zi. Ikki xil nomzod yig'amiz: hamma bo'lak birlashtirilgani va har bo'lak alohida. `for _, m, i in natijalar` — har elementni uchga ochamiz (tuple unpacking). `_` — «bu qiymat kerak emas».

```python
    qutilar = [(int(min(n[0] for n in q) / olchov), int(min(n[1] for n in q) / olchov),
                int(max(n[0] for n in q) / olchov), int(max(n[1] for n in q) / olchov))
               for q, _, _ in natijalar]
```
Har topilgan matnning joyini `(x0, y0, x1, y1)` qutiga aylantiramiz. `/ olchov` — koordinatalarni kichraytirilgan kadrdan **asl kadrga** qaytaradi (kichraytirishda 0.75 ga ko'paytirilgan bo'lsa, endi 0.75 ga bo'lamiz).

```python
    for x0, y0, x1, y1 in set(qutilar + _qatorlarga_birlashtirish(qutilar)):
        if y1 - y0 >= 12 and 2 <= (x1 - x0) / (y1 - y0) <= 8:
            nomzodlar += _kesib_oqish(oqiydigan, kadr, (x0, y0, x1, y1))
```
**Ikkinchi urinish** — har qutini kesib, aniqroq o'qish (3.5–3.6).
- `set(...)` — bir xil qutilar ikki marta o'qilmasin.
- `if` — raqam belgisi yotiq to'rtburchak: eni bo'yidan 2–8 marta katta, bo'yi kamida 12 piksel. Boshqa shakldagi matnlarga vaqt sarflamaymiz.

```python
    nomzodlar = [(r, float(i)) for r, i in nomzodlar if togri_formatmi(r)]
    if not nomzodlar:
        return None, 0.0
    return max(nomzodlar, key=lambda x: x[1])
```
- Faqat to'g'ri formatdagilarni qoldiramiz (list comprehension).
- Hech narsa qolmasa — `(None, 0.0)`.
- Qolganlaridan **ishonchi eng yuqorisini** tanlaymiz. `key=lambda x: x[1]` — «solishtirishda har juftning 2-elementiga (ishonchga) qara».

---

## 4. `camera.py` — kamera

```python
try:
    import cv2
except ImportError:
    cv2 = None
```
Fayl boshida `opencv` ni olishga urinamiz. Yo'q bo'lsa, `cv2 = None` qilib qo'yamiz; dastur tushunarli xabar beradi, qulamaydi.

```python
def kutubxona_bormi():
    if cv2 is None:
        print("opencv o'rnatilmagan. Terminalda: pip install opencv-python")
        return False
    return True
```
Kutubxona borligini tekshirib, yo'q bo'lsa nima qilishni aytadi.

```python
def kamerani_ochish(indeks):
    if not kutubxona_bormi():
        return None
    kamera = cv2.VideoCapture(indeks)
    if not kamera.isOpened():
        print(f"{indeks}-kamerani ochib bo'lmadi!")
        return None
    kamera.set(cv2.CAP_PROP_FRAME_WIDTH, KADR_ENI)
    kamera.set(cv2.CAP_PROP_FRAME_HEIGHT, KADR_BOYI)
    kamera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return kamera
```
- `cv2.VideoCapture(0)` — 0-kamerani ochadi. `isOpened()` — ochilganini tekshiradi. Muvaffaqiyatsiz bo'lsa `None` qaytaradi — chaqiruvchi shuni tekshiradi.
- `kamera.set(...)` — kameradan 1280×720 o'lchamli kadr so'raymiz. Kamera bu o'lchamni bermasa, o'zi bera oladigan eng yaqinini beradi.
- `CAP_PROP_BUFFERSIZE, 1` — eski kadrlar navbatda to'planib qolmasin, doim eng yangi kadr kelsin.

> macOS'da kamera birinchi marta ochilganda tizim ruxsat so'raydi. Ruxsat berilmasa, `OpenCV: not authorized to capture video` xatosi chiqadi: **System Settings → Privacy & Security → Camera** dan terminalga ruxsat bering.

```python
def harakat_bormi(oldingi, kadr):
    kichik = cv2.cvtColor(cv2.resize(kadr, (160, 90)), cv2.COLOR_BGR2GRAY)
    kichik = cv2.GaussianBlur(kichik, (5, 5), 0)
    if oldingi is None:
        return True, kichik
    ozgargan = (cv2.absdiff(oldingi, kichik) > 25).mean()
    return ozgargan > HARAKAT_CHEGARASI, kichik
```
Mashina kelganini qanday bilamiz? Ikki ketma-ket kadrni **solishtirib**: hech narsa qimirlamasa, ular deyarli bir xil bo'ladi.
1. Kadrni 160×90 ga kichraytirib, kulrang qilamiz — solishtirish tez bo'ladi.
2. `GaussianBlur` — biroz xiralashtiradi. Kameraning mayda «shovqini» harakat deb hisoblanmasligi uchun.
3. Birinchi kadrda solishtiradigan narsa yo'q (`oldingi is None`) — `True` qaytaramiz.
4. `cv2.absdiff` — ikki rasmning har pikseli orasidagi farq. `> 25` — sezilarli o'zgargan piksellar (`True`/`False`). `.mean()` — ularning **ulushi** (0 dan 1 gacha).
5. Ulush `HARAKAT_CHEGARASI` dan katta bo'lsa — harakat bor.

Funksiya **ikki narsa** qaytaradi: `(harakat, kichik_kadr)`. `kichik_kadr` ni keyingi safar `oldingi` sifatida beramiz.

```python
def kadr_olish(kamera):
    holat, kadr = kamera.read()
    return kadr if holat else None
```
`kamera.read()` ikki narsa qaytaradi: `holat` (`True` — o'qildi) va `kadr` (rasm). Muvaffaqiyatsiz bo'lsa `None` qaytaramiz.

```python
def kamerani_yopish(kameralar):
    for kamera in kameralar:
        kamera.release()
    cv2.destroyAllWindows()
```
Kameralarni bo'shatadi (boshqa dastur ishlata olishi uchun) va oynalarni yopadi.

```python
def rasmni_oqish(fayl_yoli):
    return cv2.imread(fayl_yoli) if kutubxona_bormi() else None
```
Fayldan rasm o'qiydi (kamerasiz sinash uchun). `A if shart else B` — bir qatorli `if`.

```python
def rasm_saqlash(kadr, raqam, yonalish, vaqt):
    os.makedirs(RASMLAR_PAPKASI, exist_ok=True)
    nom = f"{yonalish}_{raqam}_{vaqt.strftime('%Y%m%d_%H%M%S')}.jpg"
    yol = os.path.join(RASMLAR_PAPKASI, nom)
    if cv2 is not None and kadr is not None:
        cv2.imwrite(yol, kadr)
    return yol
```
- `os.makedirs(..., exist_ok=True)` — papka yo'q bo'lsa yaratadi, bor bo'lsa xato bermaydi.
- Fayl nomi: `kirish_01A123AA_20261104_100000.jpg` — yo'nalish, raqam, vaqt. Shunda har rasm noyob va tushunarli.
- `os.path.join` — yo'lni to'g'ri qo'shadi (Mac va Windows'da belgilar boshqa: `/` va `\`).
- `cv2.imwrite` — rasmni faylga yozadi.
- Yo'lni **qaytaramiz**, chunki uni Excelga yozamiz.

```python
def oynada_korsatish(oyna_nomi, kadr, matn):
    cv2.putText(kadr, matn, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imshow(oyna_nomi, kadr)
    return chr(cv2.waitKey(1) & 0xFF)
```
- `putText` — kadr ustiga yashil matn yozadi (`(0, 255, 0)` = yashil, BGR tartibida).
- `imshow` — oynada ko'rsatadi.
- `waitKey(1)` — 1 ms davomida tugma bosilishini kutadi. U **majburiy**: busiz oyna yangilanmaydi.
- `& 0xFF` — tugma kodining oxirgi baytini oladi, `chr()` — uni harfga aylantiradi (`"q"`).

---

## 5. `database.py` — Excel bazasi

Excel faylda **ikki varaq** bor:
- **Avtomobillar** — kimga ruxsat bor (doimiy ro'yxat).
- **Sessiyalar** — har kirish-chiqish uchun yangi qator (tarix).

Umumiy andoza (har funksiyada bir xil): **ochish → ishlash → (kerak bo'lsa saqlash) → yopish**.

### Yordamchilar

```python
def vaqt_matni(vaqt):
    return vaqt.strftime(VAQT_FORMATI)

def vaqtni_oqish(matn):
    return datetime.strptime(matn, VAQT_FORMATI)
```
Excelga vaqtni **matn** qilib yozamiz (`strftime`: vaqt → matn), o'qiyotganda yana vaqtga qaytaramiz (`strptime`: matn → vaqt). Vaqtga qaytarish kerak, chunki ayirish (`chiqish - kirish`) faqat `datetime` bilan ishlaydi.

### `bazani_yaratish()`

```python
if os.path.exists(EXCEL_FILE):
    kitob = openpyxl.load_workbook(EXCEL_FILE)
else:
    kitob = openpyxl.Workbook()
    kitob.active.title = VARAQ_AVTO
    kitob[VARAQ_AVTO].append(SARLAVHA_AVTO)
    kitob[VARAQ_AVTO].append([1, "01A123AA", "Ali", "Cobalt", RUXSAT])
    ...
```
- Fayl bor bo'lsa — ochamiz. Yo'q bo'lsa — yangi yaratib, birinchi varaqqa nom beramiz, sarlavha va 3 ta namunaviy mashina yozamiz.
- `.append([...])` — jadvalning oxiriga yangi qator qo'shadi.

```python
if VARAQ_SESSIYA not in kitob.sheetnames:
    kitob.create_sheet(VARAQ_SESSIYA).append(SARLAVHA_SESSIYA)
kitob.save(EXCEL_FILE)
kitob.close()
```
«Sessiyalar» varag'i yo'q bo'lsa qo'shadi (eski fayl bilan ham ishlashi uchun). Keyin saqlaydi va yopadi.

### `avtomobil_qidirish(raqam)`

```python
for qator in varaq.iter_rows(min_row=2, values_only=True):
    if qator[1] == raqam:
        natija = {"id": qator[0], "raqam": qator[1], ...}
        break
```
- `iter_rows(min_row=2, ...)` — 2-qatordan boshlab (1-qator — sarlavha).
- `values_only=True` — katakning o'zini emas, faqat qiymatini beradi. Har qator **tuple**: `(1, "01A123AA", "Ali", "Cobalt", "Ruxsat berilgan")`.
- `qator[1]` — 2-element (raqam ustuni). **Indeks 0 dan boshlanadi**, shuning uchun 2-ustun = `[1]`.
- Topilsa tuple'ni **lug'at** (`dict`) ga aylantiramiz: `avtomobil["egasi"]` ko'proq tushunarli, `qator[2]` dan ko'ra.
- `break` — topdik, qidirishni to'xtatamiz.
- Topilmasa `natija` `None` bo'lib qoladi.

### `avtomobil_qoshish(raqam, egasi, model, holati=RUXSAT)`

```python
if avtomobil_qidirish(raqam) is not None:
    return False
...
varaq.append([varaq.max_row, raqam, egasi, model, holati])
```
- Avval bor-yo'qligini tekshiradi. Bor bo'lsa `False` qaytaradi.
- Yangi ID: `varaq.max_row`. Sarlavha 1-qatorda, shuning uchun 3 ta mashina bo'lsa `max_row = 4`, yangi ID = 4. (Qator o'chirilsa ID'lar buzilishi mumkin — pastdagi 10-bo'limga qarang.)
- `holati=RUXSAT` — **standart qiymat**: ko'rsatilmasa, avtomatik «Ruxsat berilgan».
- Funksiya `input()` ishlatmaydi: so'rash `main.py` ning ishi, bu yerda faqat saqlash.

### `barcha_avtomobillar()`
Hamma qatorni o'qib, lug'atlar **ro'yxati** qaytaradi. Ekranga chiqarish — `main.py` ning ishi.

### `ochiq_sessiya(raqam)`

```python
for q in kitob[VARAQ_SESSIYA].iter_rows(min_row=2, values_only=True):
    if q[1] == raqam and not q[3]:
        topildi = {"id": q[0], "raqam": q[1], "kirish": vaqtni_oqish(q[2])}
```
**Eng muhim funksiyalardan biri.** «Ochiq sessiya» — kirgan, lekin hali chiqmagan mashina.
- `q[1] == raqam` — shu mashinaning qatori.
- `not q[3]` — `q[3]` (Chiqish vaqti) **bo'sh** (`None` yoki `""`). `not` bo'shni `True` qiladi.
- Natijada: ichkarida bo'lsa — lug'at, bo'lmasa — `None`.
- Excel katakning bo'shligi shu yerda «mashina ichkarida» degan ma'noni beradi.

### `kirish_yozish(raqam, vaqt, rasm_yoli)`
Sessiyalar varag'iga yangi qator: `[id, raqam, kirish_vaqti, "", "", "", rasm_yoli, ""]`. Bo'sh `""` — chiqishda to'ldiriladigan kataklar.

### `chiqish_yozish(sessiya_id, vaqt, daqiqa, summa, rasm_yoli)`

```python
for qator in kitob[VARAQ_SESSIYA].iter_rows(min_row=2):
    if qator[0].value == sessiya_id:
        qator[3].value = vaqt_matni(vaqt)
        ...
        break
```
Bu yerda `values_only` **yo'q**: biz katakning o'zini olamiz, chunki unga **yozish** kerak. Shuning uchun `qator[0].value` deb yozamiz. ID bo'yicha qatorni topib, 4 ta bo'sh katakni to'ldiramiz.

---

## 6. `gate.py` — shlagbaum

```python
def shlagbaum_ochish(yonalish, raqam):
    print(f"   🟢 SHLAGBAUM OCHILDI ({yonalish}): {raqam}")

def shlagbaum_yopiq_qoldirish(raqam, sabab):
    print(f"   🔴 Shlagbaum yopiq: {raqam} — {sabab}")
```
Hozircha faqat ekranga yozadi. Haqiqiy shlagbaum (Arduino, Raspberry Pi) ulanganda **faqat shu faylning ichi o'zgaradi**, `nazorat.py` ga tegmaymiz. Bu «fayllarga bo'lishning» eng yaxshi namunasi.

---

## 7. `nazorat.py` — asosiy mantiq

Bu — dasturning miyasi. Ikki qismdan iborat: **qaror qiluvchi funksiya** (`qayta_ishlash`) va **kamera sikli** (`avtomatik_nazorat`).

### Importlar

```python
import threading
from datetime import datetime

import billing, camera, database, gate, recognition
from config import (KAMERALAR, MIN_ISHONCH, TAKROR_SONIYA, RUXSAT,
                    HARAKATDAN_KEYIN_SONIYA)
```
Fayllarni to'liq (`billing.daqiqani_hisoblash(...)` ko'rinishida) va sozlamalarni alohida olamiz. `threading` — bir vaqtda ikki ishni bajarish uchun (pastda, `Aniqlovchi` da).

### Takrorni to'xtatish

```python
oxirgi_vaqt = {}

def takror_mi(raqam, hozir):
    oldingi = oxirgi_vaqt.get(raqam)
    return oldingi is not None and (hozir - oldingi).total_seconds() < TAKROR_SONIYA
```
- `oxirgi_vaqt` — **lug'at**: `{"01A123AA": 10:00:00, ...}` — «bu mashinani oxirgi marta qachon ishladik».
- `.get(raqam)` — kalit bo'lmasa xato bermaydi, `None` qaytaradi.
- Funksiya `True` qaytaradi, agar mashina oldin ishlangan **va** shundan beri 60 soniyadan kam o'tgan bo'lsa.

**Nima uchun kerak?** Mashina kamera oldida bir necha soniya turadi va shu vaqt ichida raqami bir necha marta o'qiladi. Bu himoya bo'lmasa, bitta mashina avval «kirdi», bir soniyadan keyin «chiqdi» deb yozilib ketardi.

### `qayta_ishlash(raqam, yonalish, kadr, hozir=None)`

```python
hozir = hozir or datetime.now()
```
`hozir` berilmasa, joriy vaqtni oladi. Nima uchun `hozir` parametr? **Sinash uchun**: soxta vaqt berib, «1 daqiqa 5 soniya turdi» holatini kutmasdan tekshirish mumkin.

#### 1-to'siq: takror

```python
if takror_mi(raqam, hozir):
    return None
```
Yaqinda ishlangan bo'lsa, hech narsa qilmaymiz. `None` — «yangi xabar yo'q».

#### 2-to'siq: bazada bormi

```python
avtomobil = database.avtomobil_qidirish(raqam)
if avtomobil is None:
    oxirgi_vaqt[raqam] = hozir
    gate.shlagbaum_yopiq_qoldirish(raqam, "bazada yo'q")
    return f"{raqam}: bazada yo'q"
```
Bazada yo'q — rad etamiz. `oxirgi_vaqt` ga ham yozamiz: bo'lmasa, yo'q mashina qayta-qayta rad etilib, ekranni to'ldirib yuboradi.

Bu to'siq **majburiy**: u bo'lmasa `avtomobil` `None` bo'lib qoladi va keyingi qatordagi `avtomobil["holati"]` xato beradi (`TypeError: 'NoneType' object is not subscriptable`), nazorat to'xtaydi.

#### 3-to'siq: ruxsati bormi

```python
if avtomobil["holati"] != RUXSAT:
    ... shlagbaum yopiq: "taqiqlangan"
```

#### Yo'nalishni aniqlash

```python
sessiya = database.ochiq_sessiya(raqam)
if yonalish == "avto":
    yonalish = "chiqish" if sessiya else "kirish"
```
Bitta kamera bo'lsa: mashina ichkarida (ochiq sessiya bor) → **chiqish**, aks holda → **kirish**. `if sessiya` — lug'at bo'sh emas (`None` emas) bo'lsa `True`.

#### Kirish tarmog'i

```python
if yonalish == "kirish":
    if sessiya:
        ... "allaqachon ichkarida"
    yol = camera.rasm_saqlash(kadr, raqam, "kirish", hozir)
    database.kirish_yozish(raqam, hozir, yol)
    oxirgi_vaqt[raqam] = hozir
    gate.shlagbaum_ochish("kirish", raqam)
    return f"KIRDI: ..."
```
Tartib: rasmni saqlash → Excelga yozish → eslab qolish → shlagbaumni ochish → xabar qaytarish. Agar mashina allaqachon ichkarida bo'lsa (ikki kamerali rejimda xato bo'lishi mumkin), ochilmaydi.

#### Chiqish tarmog'i

```python
if not sessiya:
    ... "kirish yozuvi yo'q"
daqiqa = billing.daqiqani_hisoblash(sessiya["kirish"], hozir)
summa = billing.summani_hisoblash(daqiqa)
yol = camera.rasm_saqlash(kadr, raqam, "chiqish", hozir)
database.chiqish_yozish(sessiya["id"], hozir, daqiqa, summa, yol)
...
gate.shlagbaum_ochish("chiqish", raqam)
return f"CHIQDI: {raqam} | {daqiqa} daqiqa | {summa} so'm"
```
Kirish yozuvi yo'q bo'lsa, **shlagbaum ochilmaydi** (qancha to'lashni bilmaymiz). Bo'lsa: daqiqa → summa → rasm → Excelga yozish → shlagbaum.

**Diqqat:** bu funksiya `input()` va kamera bilan ishlamaydi. Faqat raqam, yo'nalish va kadrni oladi. Shuning uchun uni kamerasiz sinash oson.

### `Aniqlovchi` — raqamni fonda o'qish

**Muammo.** Bitta raqamni o'qish 0.5–1 soniya oladi. Avvalgi kodda o'qish kamera sikli ichida turardi: o'qish tugaguncha yangi kadr ko'rsatilmasdi va oyna **qotib qolardi**.

**Yechim.** O'qishni alohida **oqim**ga (`thread`) beramiz. Oqim — dastur ichidagi ikkinchi «ishchi»: asosiy ishchi kamerani ko'rsatib turadi, ikkinchisi shu paytda raqamni o'qiydi.

```python
class Aniqlovchi:
    def __init__(self):
        self.band = False
        self.natija = None
```
`class` — o'z ma'lumoti va funksiyalari bor «buyum». Har kamera uchun bittadan `Aniqlovchi` yaratiladi.
- `self.band` — hozir kadr o'qilyaptimi.
- `self.natija` — tayyor, lekin hali olinmagan natija: `(raqam, ishonch, kadr)`.

```python
    def yuborish(self, kadr):
        if self.band:
            return
        self.band = True
        threading.Thread(target=self._oqish, args=(kadr.copy(),), daemon=True).start()
```
- Band bo'lsa — kadr **tashlab yuboriladi**. Navbat yig'ilmaydi: bizga eski emas, eng yangi kadr kerak.
- `threading.Thread(target=..., args=...)` — yangi oqim yaratadi, `.start()` — ishga tushiradi. Shundan keyin `yuborish` darhol qaytadi, o'qish esa fonda davom etadi.
- `kadr.copy()` — nusxa. Asosiy oqim shu kadr ustiga yashil matn yozadi; nusxa bo'lmasa, o'sha matn ham «o'qilib» ketardi.
- `daemon=True` — dastur yopilganda bu oqim ham o'zi to'xtaydi.

```python
    def _oqish(self, kadr):
        try:
            raqam, ishonch = recognition.raqamni_aniqlash(kadr)
            self.natija = (raqam, ishonch, kadr)
        except Exception as xato:
            print(f"Raqamni o'qishda xato: {xato}")
        finally:
            self.band = False
```
Fonda ishlaydigan qism. `finally` — xato bo'lsa ham `band` ni `False` qiladi; aks holda bitta xatodan keyin boshqa hech narsa o'qilmay qolardi.

```python
    def natijani_olish(self):
        natija, self.natija = self.natija, None
        return natija
```
Natijani **bir marta** beradi va joyini bo'shatadi: bitta natija ikki marta qayta ishlanmasin.

**Diqqat:** fon oqimi faqat **o'qiydi**. Excelga yozish va shlagbaum (`qayta_ishlash`) asosiy oqimda qoladi. Ikki oqim bir vaqtda bitta Excel faylga yozsa, fayl buzilishi mumkin.

### `avtomatik_nazorat()`

```python
database.bazani_yaratish()
ochiq = []
for yonalish, indeks in KAMERALAR:
    kamera = camera.kamerani_ochish(indeks)
    if kamera is not None:
        ochiq.append((yonalish, indeks, kamera))
if not ochiq:
    return
```
- Baza tayyorligini ta'minlaymiz.
- `for yonalish, indeks in KAMERALAR` — har tuple'ni ikkiga ajratamiz.
- Ochilgan kameralarni `ochiq` ro'yxatiga yig'amiz. Birorta ham kamera ochilmasa — to'xtaymiz; bittasi ochilmasa, qolganlari bilan ishlayveramiz.

```python
try:
    print("Raqam o'qish modeli yuklanmoqda...")
    if not recognition.tayyorlash():
        return
```
Modelni sikldan **oldin** yuklaymiz (3.4). `easyocr` o'rnatilmagan bo'lsa — to'xtaymiz.

```python
    holat = {indeks: {"aniqlovchi": Aniqlovchi(), "oldingi": None,
                      "faol_gacha": None, "xabar": None}
             for _, indeks, _ in ochiq}
```
Har kamera uchun alohida «xotira» (lug'at ichida lug'at):
- `aniqlovchi` — shu kameraning fon o'quvchisi;
- `oldingi` — harakatni solishtirish uchun oldingi kichik kadr;
- `faol_gacha` — qaysi vaqtgacha raqam o'qishda davom etamiz;
- `xabar` — oynada ko'rsatiladigan oxirgi xabar.

```python
    while True:
        for yonalish, indeks, kamera in ochiq:
            kadr = camera.kadr_olish(kamera)
            if kadr is None:
                continue
            h = holat[indeks]
            hozir = datetime.now()
```
Cheksiz sikl, ichida har kamera uchun navbat. Kadr kelmasa, shu kamerani o'tkazib yuboramiz (`continue`).

**1-qadam: tayyor natija bormi?**

```python
            natija = h["aniqlovchi"].natijani_olish()
            if natija:
                raqam, ishonch, oqilgan_kadr = natija
                if raqam and ishonch >= MIN_ISHONCH:
                    xabar = qayta_ishlash(raqam, yonalish, oqilgan_kadr, hozir)
                    if xabar:
                        print(xabar)
                        h["xabar"] = xabar
```
Fon oqimi biror kadrni o'qib bo'lgan bo'lsa, natijasini olamiz. Raqam topilgan **va** ishonchli bo'lsa — qaror qilamiz. Rasmga `oqilgan_kadr` (raqam o'qilgan kadrning o'zi) saqlanadi, hozirgi kadr emas.

**2-qadam: harakat bormi?**

```python
            harakat, h["oldingi"] = camera.harakat_bormi(h["oldingi"], kadr)
            if harakat:
                h["faol_gacha"] = hozir.timestamp() + HARAKATDAN_KEYIN_SONIYA
            faol = h["faol_gacha"] is not None and hozir.timestamp() <= h["faol_gacha"]
            if faol:
                h["aniqlovchi"].yuborish(kadr)
```
- Harakat sezilsa, «faol» vaqtni hozirdan 3 soniya keyinga suramiz. `.timestamp()` — vaqtni soniyalardagi oddiy songa aylantiradi (qo'shish oson).
- `faol` — hali o'sha vaqt o'tmagan bo'lsa `True`.
- Faol paytda kadrni o'qishga yuboramiz. Kamera oldi bo'sh va tinch bo'lsa, **hech narsa o'qilmaydi** — protsessor bekorga ishlamaydi.

**3-qadam: ko'rsatish**

```python
            oyna = f"{yonalish} (kamera {indeks})"
            matn = h["xabar"] or ("Raqam o'qilmoqda..." if faol else "Mashina kutilmoqda")
            if camera.oynada_korsatish(oyna, kadr, matn) == "q":
                return
```
Oynada oxirgi xabar turadi. Hali xabar bo'lmasa: faol paytda «Raqam o'qilmoqda...», tinch paytda «Mashina kutilmoqda». `Q` bosilsa — chiqamiz.

```python
finally:
    camera.kamerani_yopish([k for _, _, k in ochiq])
    print("Nazorat to'xtatildi.")
```
`finally` — nima bo'lsa ham (`return`, xato, Ctrl+C) **doim** bajariladi. Kamera har holda bo'shatiladi. Aks holda kamera band qolib, keyingi safar ochilmay qoladi.

---

## 8. `main.py` — menyu

```python
def menyu():
    database.bazani_yaratish()
    while True:
        print(f"""...Tarif: {billing.summani_hisoblash(1)} so'm / daqiqa...""")
        tanlov = input("Tanlov: ").strip()
        if tanlov == "1": nazorat.avtomatik_nazorat()
        elif tanlov == "2": avtomobil_qoshish_menyu()
        ...
        elif tanlov == "0": break
        else: print("Noto'g'ri tanlov!")
```
- `while True` — menyu `0` tanlanguncha qayta-qayta chiqadi. `break` — sikldan chiqish.
- `.strip()` — tasodifan yozilgan bo'sh joyni olib tashlaydi.
- Tarif `config.py` dan olinadi: narx o'zgarsa, menyu ham o'zi yangilanadi.

**Yordamchi funksiyalar:**
- `avtomobil_qoshish_menyu()` — foydalanuvchidan raqam, egasi, modelni **so'raydi** (`input`), raqamni tozalaydi va to'g'riligini tekshiradi, keyin `database.avtomobil_qoshish` ni chaqiradi. `input` shu yerda, `database.py` da emas: bazaga tegishli fayl foydalanuvchi bilan gaplashmasligi kerak.
- `sessiyalarni_korsatish()` — `_, raqam, kirish, chiqish, daqiqa, summa, _, _ = s` — 8 elementli qatorni ochadi; kerak bo'lmaganlari `_`. `chiqish` bo'sh bo'lsa «ichkarida» deb yozadi.
- `rasmdan_sinash()` — **kamerasiz sinash**: rasm fayl yo'lini so'raydi, raqamni o'qib ishonchini ko'rsatadi. OCR sifatini tekshirishga qulay.

```python
if __name__ == "__main__":
    menyu()
```
Fayl to'g'ridan-to'g'ri ishga tushirilganda (`python main.py`) menyu ochiladi. Boshqa fayldan `import main` qilinsa — ochilmaydi.

---

## 9. Dastur boshdan oxirigacha: bitta mashinaning yo'li

Mashina `01A123AA`, bitta kamera (`"avto"` rejimi). Tarif 100 so'm.

**Boshlanishi**
1. `main.py` → menyuda `1` → `nazorat.avtomatik_nazorat()`.
2. Kamera ochiladi, OCR modeli yuklanadi. Sikl boshlanadi, har aylanishda `kadr_olish`.
3. Kamera oldi bo'sh: `harakat_bormi` → `False`. Oynada «Mashina kutilmoqda», hech narsa o'qilmaydi.

**10:00:00 — kirish**
1. Mashina kadrga kiradi → `harakat_bormi` → `True` → 3 soniyaga «faol». Oynada «Raqam o'qilmoqda...».
2. `Aniqlovchi.yuborish(kadr)` — kadr fon oqimiga beriladi. Video to'xtamaydi.
3. Fonda `raqamni_aniqlash(kadr)` → `("01A123AA", 0.87)`.
4. Keyingi aylanishda `natijani_olish()` shu natijani beradi. 0.87 ≥ 0.5 → `qayta_ishlash("01A123AA", "avto", kadr)`.
5. Takror emas. Bazada bor, «Ruxsat berilgan».
6. `ochiq_sessiya` → `None` (ichkarida emas) → yo'nalish **kirish** bo'ladi.
7. Rasm `rasmlar/kirish_01A123AA_20261104_100000.jpg` ga saqlanadi.
8. Sessiyalarga qator: `[1, "01A123AA", "2026-11-04 10:00:00", "", "", "", "rasmlar/kirish_…", ""]`.
9. 🟢 Shlagbaum ochiladi. Ekran: `KIRDI: 01A123AA (Cobalt, Ali)`.

**10:00:02 — mashina hali kadrda**
Raqam yana o'qiladi → `takror_mi` → 2 s < 60 s → `None` qaytadi, hech narsa bo'lmaydi. Mashina to'xtab tursa, 3 soniyadan keyin o'qish ham to'xtaydi.

**10:05:10 — qaytib keldi (chiqish)**
1. Yana harakat → raqam o'qiladi, `takror_mi` → 310 s > 60 s → davom etadi.
2. `ochiq_sessiya` → lug'at topiladi (chiqish bo'sh) → yo'nalish **chiqish**.
3. `daqiqani_hisoblash`: 310 s → 5.17 → `ceil` → **6 daqiqa**.
4. `summani_hisoblash(6)` → **600 so'm**.
5. Excelda shu qatorga: chiqish vaqti, 6, 600, chiqish rasmi.
6. 🟢 Shlagbaum ochiladi. Ekran: `CHIQDI: 01A123AA | 6 daqiqa | 600 so'm`.

---

## 10. Ehtiyot bo'lish kerak bo'lgan joylar

Hammasini ochiq aytish muhim: kodning sinovdan o'tgan qismlari bor, o'tmagan qismlari ham.

**Sinalgan:**
- Kirish/chiqish mantiqi, daqiqa va summa, takror himoyasi, taqiqlangan va bazada yo'q mashinalar, Excelga yozish (soxta vaqt bilan).
- Ikkala raqam andozasi (`01A123AA`, `01123ABC`) — matn sifatida.
- Raqamni o'qish — bitta rasmda (`70 A 444 AA`): asl o'lchamda va 1.5–3 marta kattalashtirilgan nusxalarida to'g'ri o'qildi.
- Jonli kamera — darsda telefon ekranidagi shu rasm ko'rsatildi: kirish va bir daqiqadan keyin chiqish yozildi, ikkala rasm saqlandi.

**Sinalmagan:** haqiqiy mashina, ko'cha yorug'ligi, tun, qiya burchak, iflos yoki ikki qatorli raqam, yuridik shaxs raqamini (`01 123 ABC`) **rasmdan** o'qish, ikki kamerali rejim.

**Ma'lum cheklovlar:**
1. **Kichik raqam:** raqam kadrda juda kichik bo'lsa (bo'yi ~22 pikseldan kam), xato o'qiladi yoki umuman topilmaydi. Sinovda shunday rasm `70A644AA` deb o'qildi (ishonch 0.49 — chegaradan zo'rg'a past). Kamera mashinaga yaqin turishi kerak.
2. **Harakat — har qanday harakat:** odam o'tsa yoki yorug'lik o'zgarsa ham raqam o'qish boshlanadi. Bu xato natija bermaydi (raqam topilmaydi), lekin protsessorni band qiladi.
3. **Bitta kamera + `"avto"`:** mashina kirgandan keyin 60 soniya o'tib ham kamera oldida qimirlab tursa, chiqayotgan deb hisoblanadi. Ikki kamera ishonchliroq.
4. **`oxirgi_vaqt` xotirada:** dastur qayta ishga tushsa, tozalanadi. Excelda yozuvlar saqlanadi, shuning uchun ma'lumot yo'qolmaydi, lekin 60 soniyalik himoya qayta boshlanadi.
5. **Excel ochiq bo'lsa:** Excel dasturida `avtomobillar.xlsx` ochiq turganda dastur yoza olmay xato berishi mumkin. Dastur ishlayotganda faylni yoping.
6. **ID `max_row` dan:** Excelda qatorni qo'lda o'chirsangiz, ID'lar takrorlanishi mumkin. Ishonchliroq usul — oxirgi ID ga 1 qo'shish.
7. **To'lov faqat yoziladi:** pul olish tizimi yo'q. Summa Excelga yoziladi, xolos.
8. **Chiqishda kirish yozuvi yo'q:** shlagbaum ochilmaydi. Haqiqiy hayotda bunday mashinani nima qilish biznes qoidasi — hal qilish kerak.
9. **Protsessorda ishlaydi:** `easyocr` `gpu=False` bilan yuklanadi, bitta kadr 0.5–1 soniya oladi.

---

## 11. Tekshirib ko'rish uchun savollar (talabalar uchun)

1. Nima uchun narx `billing.py` ichiga emas, `config.py` ga yozilgan?
2. 2 daqiqa 1 soniya turgan mashina qancha to'laydi? Nima uchun?
3. `max(1, math.ceil(...))` dagi `max` nima uchun kerak?
4. `takror_mi` bo'lmasa, nima bo'ladi?
5. `ochiq_sessiya` mashina ichkarida ekanini qanday biladi?
6. Nima uchun `import easyocr` funksiya ichida yozilgan?
7. `finally` bloki nima uchun kerak?
8. Narxni 150 so'mga o'zgartirish uchun nechta faylni o'zgartirish kerak?
9. Haqiqiy shlagbaum ulansa, qaysi fayl o'zgaradi?
10. Ikki kamerali rejimga o'tish uchun nimani o'zgartirish kerak?
11. Nima uchun raqam o'qish alohida oqimda (`Aniqlovchi`) bajariladi?
12. Dastur mashina kelganini qanday biladi?
13. `444` ni o'qiyotganda OCR'ga nima uchun faqat raqamlarga ruxsat beramiz?
14. Uch o'qishdan ikkitasi `70A444AA`, bittasi `70A644AA` chiqdi. Qaysi biri tanlanadi va nima uchun?
15. Andozada `[A-Z]{3}` o'rniga `[a-z]{3}` yozilsa, `togri_formatmi("01123ABC")` nima qaytaradi? Nima uchun?
16. `qayta_ishlash` dagi «bazada yo'q» tekshiruvi olib tashlansa, bazada yo'q mashina kelganda nima bo'ladi?

**Javoblar:** 1) narx sozlama, hisoblash mantiqi emas. 2) 121 s → 2.02 → 3 daqiqa → 300 so'm. 3) 0 soniyada `ceil(0) = 0` bo'lib qolmasligi uchun. 4) mashina kamera oldida turganda avval «kirdi», keyin darhol «chiqdi» yoziladi. 5) Sessiyalarda uning chiqish vaqti bo'sh qatori bor-yo'qligiga qarab. 6) kutubxona o'rnatilmagan bo'lsa ham dasturning qolgan qismlari ishlashi uchun. 7) xato yoki chiqishda ham kamerani bo'shatish uchun. 8) bitta: `config.py`. 9) faqat `gate.py`. 10) `config.py` dagi `KAMERALAR` ni `[("kirish", 0), ("chiqish", 1)]` qilish. 11) o'qish 0.5–1 soniya oladi; sikl ichida tursa, kamera oynasi qotib qoladi. 12) ikki ketma-ket kadrni solishtirib: piksellarning 1% dan ko'pi o'zgarsa — harakat bor (`camera.harakat_bormi`). 13) shunda `4` ni `G`, `0` ni `O` deb adashtira olmaydi. 14) `70A444AA` — ishonchlari yig'indisi kattaroq (ovoz berish). 15) `False`: `[a-z]{3}` kichik harf kutadi, `raqamni_tozalash` esa hammasini katta harfga o'tkazadi — hech qachon mos kelmaydi. 16) `avtomobil` `None` bo'ladi, `avtomobil["holati"]` `TypeError` beradi va nazorat to'xtaydi.
