# Avtomatik avtoturargoh — kodning to'liq tushuntirishi

Bu hujjat `avtomatik/` papkasidagi har bir faylni, har bir funksiyani va muhim qatorlarni oddiy tilda tushuntiradi.

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
main.py ──► nazorat.py ──► camera.py        (kadr olish)
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
HAR_NECHTA_KADR = 15
MIN_ISHONCH = 0.5
TAKROR_SONIYA = 60
```
- **HAR_NECHTA_KADR** — raqamni o'qish og'ir ish (sekin). Kamera sekundiga ~30 kadr beradi, hammasini o'qish shart emas. Har 15-kadrda bir marta o'qiymiz.
- **MIN_ISHONCH** — OCR har natijaga 0 dan 1 gacha «ishonch» beradi. 0.5 dan pasti ishonchsiz, e'tiborsiz qoldiriladi.
- **TAKROR_SONIYA** — mashina kamera oldida turganda yuzlab kadr keladi. Bir mashinani 60 soniya ichida qayta ishlamaymiz.

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
```
`re` — «regular expression» (andoza bilan matn tekshirish) moduli.

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

- 1-andoza: `01A123AA` (2 raqam + harf + 3 raqam + 2 harf)
- 2-andoza: `01123ABC` (5 raqam + 3 harf)

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
- `easyocr` modeli yuklanishi sekin (bir necha soniya) va ko'p xotira oladi. Shuning uchun **birinchi marta kerak bo'lganda** yuklaymiz, keyin eslab qolamiz (`_oqiydigan` ichida).
- `global _oqiydigan` — funksiya ichida tashqaridagi o'zgaruvchini o'zgartirish uchun.
- `import easyocr` funksiya ichida: kutubxona o'rnatilmagan bo'lsa ham, dasturning boshqa qismlari (menyu, Excel) ishlayveradi.
- Nom boshidagi `_` — «bu ichki narsa, tashqaridan tegmang» degan kelishuv.

### 3.5. Asosiy funksiya

```python
def raqamni_aniqlash(kadr):
    try:
        oqiydigan = _oqiydiganni_olish()
    except ImportError:
        print("easyocr o'rnatilmagan. Terminalda: pip install easyocr")
        return None, 0.0
```
`try/except` — xato bo'lishi mumkin bo'lgan joy. `easyocr` o'rnatilmagan bo'lsa `ImportError` chiqadi; dastur qulamasdan, tushunarli xabar beradi va `(None, 0.0)` («raqam yo'q, ishonch 0») qaytaradi.

```python
    natijalar = oqiydigan.readtext(
        kadr, allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ")
```
Rasmdan matnlarni o'qiydi. `allowlist` — faqat shu belgilarni qidir (boshqa belgilar xatoni ko'paytiradi). Natija — ro'yxat, har element `(joylashuv, matn, ishonch)`. Masalan:
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
Raqam ba'zan bo'laklarga bo'lib o'qiladi (`"01"` va `"A123AA"`). Shuning uchun **ikki xil** nomzod yig'amiz:
1. Hamma bo'lakni birlashtirib: `"01A123AA"`, ishonchi — o'rtachasi.
2. Har bo'lakni alohida.

`for _, m, i in natijalar` — har elementni uchga ochamiz (tuple unpacking). `_` — «bu qiymat kerak emas».

```python
    nomzodlar = [(r, i) for r, i in nomzodlar if togri_formatmi(r)]
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
    return kamera
```
`cv2.VideoCapture(0)` — 0-kamerani ochadi. `isOpened()` — ochilganini tekshiradi. Muvaffaqiyatsiz bo'lsa `None` qaytaradi — chaqiruvchi shuni tekshiradi.

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
import billing, camera, database, gate, recognition
from config import (KAMERALAR, HAR_NECHTA_KADR, MIN_ISHONCH, TAKROR_SONIYA, RUXSAT)
```
Fayllarni to'liq (`billing.daqiqani_hisoblash(...)` ko'rinishida) va sozlamalarni alohida olamiz.

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

**Nima uchun kerak?** Mashina kamera oldida bir necha soniya turadi, 15-kadrda bir marta o'qisak ham, bir necha marta o'qiladi. Bu himoya bo'lmasa, bitta mashinaga bir nechta «kirdi» yozilib ketardi.

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
Bazada yo'q — rad etamiz. `oxirgi_vaqt` ga ham yozamiz: bo'lmasa, yo'q mashina har 15-kadrda qayta-qayta rad etilib, ekranni to'ldirib yuboradi.

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
xabarlar = {}
sanoq = 0
try:
    while True:
        sanoq += 1
        for yonalish, indeks, kamera in ochiq:
```
`sanoq` — nechanchi aylanish. Ichki `for` — har kamera uchun navbat bilan.

```python
            kadr = camera.kadr_olish(kamera)
            if kadr is None:
                continue
```
Kadr kelmasa, shu kamerani o'tkazib yuboramiz (`continue` — keyingi aylanishga).

```python
            oyna = f"{yonalish} (kamera {indeks})"
            if sanoq % HAR_NECHTA_KADR == 0:
```
`%` — qoldiq. `sanoq % 15 == 0` — faqat 15, 30, 45… aylanishlarda `True`. Ya'ni har 15-kadrda bir marta o'qiymiz.

```python
                raqam, ishonch = recognition.raqamni_aniqlash(kadr)
                if raqam and ishonch >= MIN_ISHONCH:
                    xabar = qayta_ishlash(raqam, yonalish, kadr)
                    if xabar:
                        print(xabar)
                        xabarlar[oyna] = xabar
```
Raqam o'qildi **va** ishonchli bo'lsa — qaror qilamiz. Xabar bo'lsa — ekranga chiqaramiz va oynada ko'rsatish uchun eslab qolamiz.

```python
            if camera.oynada_korsatish(oyna, kadr, xabarlar.get(oyna, oyna)) == "q":
                return
```
Oynada kadrni va oxirgi xabarni ko'rsatamiz. `Q` bosilsa — chiqamiz. `xabarlar.get(oyna, oyna)` — xabar bo'lmasa, oyna nomini yozadi.

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

**10:00:00 — kirish**
1. `main.py` → menyuda `1` → `nazorat.avtomatik_nazorat()`.
2. Kamera ochiladi. Sikl boshlanadi, har aylanishda `kadr_olish`.
3. 15-aylanishda `raqamni_aniqlash(kadr)` → `("01A123AA", 0.87)`.
4. 0.87 ≥ 0.5 → `qayta_ishlash("01A123AA", "avto", kadr)`.
5. Takror emas. Bazada bor, «Ruxsat berilgan».
6. `ochiq_sessiya` → `None` (ichkarida emas) → yo'nalish **kirish** bo'ladi.
7. Rasm `rasmlar/kirish_01A123AA_20261104_100000.jpg` ga saqlanadi.
8. Sessiyalarga qator: `[1, "01A123AA", "2026-11-04 10:00:00", "", "", "", "rasmlar/kirish_…", ""]`.
9. 🟢 Shlagbaum ochiladi. Ekran: `KIRDI: 01A123AA (Cobalt, Ali)`.

**10:00:05 — mashina hali kadrda**
Raqam yana o'qiladi → `takror_mi` → 5 s < 60 s → `None` qaytadi, hech narsa bo'lmaydi.

**10:05:10 — qaytib keldi (chiqish)**
1. Raqam o'qiladi, `takror_mi` → 310 s > 60 s → davom etadi.
2. `ochiq_sessiya` → lug'at topiladi (chiqish bo'sh) → yo'nalish **chiqish**.
3. `daqiqani_hisoblash`: 310 s → 5.17 → `ceil` → **6 daqiqa**.
4. `summani_hisoblash(6)` → **600 so'm**.
5. Excelda shu qatorga: chiqish vaqti, 6, 600, chiqish rasmi.
6. 🟢 Shlagbaum ochiladi. Ekran: `CHIQDI: 01A123AA | 6 daqiqa | 600 so'm`.

---

## 10. Ehtiyot bo'lish kerak bo'lgan joylar

Hammasini ochiq aytish muhim: kod sinovdan o'tgan qismlar bor, o'tmagan qismlar ham.

**Sinalgan:** kirish/chiqish mantiqi, daqiqa va summa, takror himoyasi, taqiqlangan va bazada yo'q mashinalar, Excelga yozish (soxta vaqt bilan).

**Sinalmagan:** haqiqiy kamera (`camera.py`) va OCR (`recognition.raqamni_aniqlash`). Bu kompyuterda `opencv-python` va `easyocr` o'rnatilmagan edi. Ularning aniqligi real kamerada, yorug'likda, burchakda tekshirilishi kerak.

**Ma'lum cheklovlar:**
1. **Bitta kamera + `"avto"`:** mashina kirgandan keyin 60 soniya o'tib ham kamera oldida tursa, chiqayotgan deb hisoblanadi. Ikki kamera ishonchliroq.
2. **`oxirgi_vaqt` xotirada:** dastur qayta ishga tushsa, tozalanadi. Excelda yozuvlar saqlanadi, shuning uchun ma'lumot yo'qolmaydi, lekin 60 soniyalik himoya qayta boshlanadi.
3. **Excel ochiq bo'lsa:** Excel dasturida `avtomobillar.xlsx` ochiq turganda dastur yoza olmay xato berishi mumkin. Dastur ishlayotganda faylni yoping.
4. **ID `max_row` dan:** Excelda qatorni qo'lda o'chirsangiz, ID'lar takrorlanishi mumkin. Ishonchliroq usul — oxirgi ID ga 1 qo'shish.
5. **To'lov faqat yoziladi:** pul olish tizimi yo'q. Summa Excelga yoziladi, xolos.
6. **Chiqishda kirish yozuvi yo'q:** shlagbaum ochilmaydi. Haqiqiy hayotda bunday mashinani nima qilish biznes qoidasi — hal qilish kerak.

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

**Javoblar:** 1) narx sozlama, hisoblash mantiqi emas. 2) 121 s → 2.02 → 3 daqiqa → 300 so'm. 3) 0 soniyada `ceil(0) = 0` bo'lib qolmasligi uchun. 4) bitta mashinaga yuzlab «kirdi» yoziladi. 5) Sessiyalarda uning chiqish vaqti bo'sh qatori bor-yo'qligiga qarab. 6) kutubxona o'rnatilmagan bo'lsa ham dastur qolgan qismlari ishlashi va model faqat kerak bo'lganda yuklanishi uchun. 7) xato yoki chiqishda ham kamerani bo'shatish uchun. 8) bitta: `config.py`. 9) faqat `gate.py`. 10) `config.py` dagi `KAMERALAR` ni `[("kirish", 0), ("chiqish", 1)]` qilish.
