# Avtomatik avtoturargoh: noldan yozish tartibi

Qoida: **pastdan yuqoriga yoziladi.** Boshqa fayllarga tayanmaydigan fayl birinchi yoziladi, hammasini ulaydigan `main.py` oxirgi yoziladi. Har qadamda fayl alohida sinab ko'riladi, keyin keyingisiga o'tiladi.

```
config → billing → database → gate → camera → recognition → nazorat → main
 (1)       (2)        (3)       (4)     (5)        (6)          (7)      (8)
```

Loyiha **1-24 ATT guruhi** talabalari bilan birga, dars paytida yozilgan. Quyida har fayl nima uchun va nima bilan boshlanishi yozilgan. Har qatorning to'liq tushuntirishi — `KOD_TUSHUNTIRISH.md` da.

---

## 0-qadam. Papka va reja (kod yo'q)

Daftarga 3 ta gap yoziladi:
1. Kamera mashina raqamini o'qiydi.
2. Mashina ichkarida bo'lmasa, **kirish** yoziladi. Ichkarida bo'lsa, **chiqish** yoziladi va pul hisoblanadi.
3. 1 daqiqa = 100 so'm.

Papka ochiladi: `avtoturargoh/`, ichida bo'sh `main.py`.

---

## 1. `config.py` — sozlamalar (faqat o'zgaruvchilar)

Funksiya yo'q. Dasturda tez-tez o'zgaradigan qiymatlar shu yerda turadi.

```python
TARIF_DAQIQAGA = 100
EXCEL_FILE = "avtomobillar.xlsx"
RASMLAR_PAPKASI = "rasmlar"
KAMERALAR = [("avto", 0)]
KADR_ENI, KADR_BOYI = 1280, 720
HARAKAT_CHEGARASI = 0.01
HARAKATDAN_KEYIN_SONIYA = 3
ANIQLASH_ENI = 960
MIN_ISHONCH = 0.5
TAKROR_SONIYA = 60
VAQT_FORMATI = "%Y-%m-%d %H:%M:%S"
RUXSAT = "Ruxsat berilgan"
TAQIQ = "Taqiqlangan"
```

Harakat va o'lchamga oid 4 ta sozlama (`KADR_ENI` … `ANIQLASH_ENI`) boshida kerak emas — ular 9-qadamda qo'shiladi.

**Sinov:** `python -c "import config; print(config.TARIF_DAQIQAGA)"` → `100`.

---

## 2. `billing.py` — pul hisoblash (eng oson funksiyalar)

| Funksiya | Oddiy tilda nima qiladi |
|---|---|
| `daqiqani_hisoblash(kirish, chiqish)` | Necha daqiqa turdi? Boshlangan har daqiqa hisoblanadi, kamida 1. |
| `summani_hisoblash(daqiqa)` | Daqiqani tarifga ko'paytiradi. |

```python
import math
from config import TARIF_DAQIQAGA

def daqiqani_hisoblash(kirish, chiqish):
    soniya = (chiqish - kirish).total_seconds()
    return max(1, math.ceil(soniya / 60))

def summani_hisoblash(daqiqa):
    return daqiqa * TARIF_DAQIQAGA
```

**Sinov:** 5 daqiqa 10 soniya → 6 daqiqa → 600 so'm. 10 soniya → 1 daqiqa → 100 so'm.

---

## 3. `database.py` — ma'lumotlar ombori

Avval **xotirada (list/dict)** yozing, ishlaganini ko'rgach Excelga o'tkazing. Funksiya nomlari o'zgarmaydi, shuning uchun boshqa fayllar buzilmaydi.

Yozish tartibi:

1. `bazani_yaratish()` — fayl yo'q bo'lsa 3 ta namunaviy mashina bilan yaratadi.
2. `avtomobil_qidirish(raqam)` — topsa dict, topmasa `None`.
3. `avtomobil_qoshish(raqam, egasi, model, holati=RUXSAT)` — qo'shdi bo'lsa `True`, bor bo'lsa `False`.
4. `barcha_avtomobillar()` — ro'yxat qaytaradi.
5. `ochiq_sessiya(raqam)` — chiqish vaqti bo'sh bo'lgan yozuv. Bor bo'lsa mashina ichkarida.
6. `kirish_yozish(raqam, vaqt, rasm_yoli)` — yangi sessiya ochadi.
7. `chiqish_yozish(sessiya_id, vaqt, daqiqa, summa, rasm_yoli)` — sessiyani yopadi.
8. `barcha_sessiyalar()` — tarix.

**Sinov:** kirish yozing → `ochiq_sessiya` topsin → chiqish yozing → `ochiq_sessiya` `None` qaytarsin.

Muhim g'oya: mashina ichkarida yoki yo'qligini **faqat** `ochiq_sessiya` aytadi.

---

## 4. `gate.py` — shlagbaum (hozircha `print`)

```python
def shlagbaum_ochish(yonalish, raqam):
    print(f"   🟢 SHLAGBAUM OCHILDI ({yonalish}): {raqam}")

def shlagbaum_yopiq_qoldirish(raqam, sabab):
    print(f"   🔴 Shlagbaum yopiq: {raqam} — {sabab}")
```

Keyin haqiqiy qurilma ulansa, faqat shu fayl o'zgaradi.

---

## 5. `camera.py` — kamera bilan ishlash

`cv2` ni fayl boshida emas, `try/except` ichida import qiling. Shunda kutubxona yo'q bo'lsa ham dastur yiqilmaydi.

Funksiyalar: `kutubxona_bormi`, `kamerani_ochish(indeks)`, `kadr_olish(kamera)`, `kamerani_yopish(kameralar)`, `rasmni_oqish(yol)`, `rasm_saqlash(kadr, raqam, yonalish, vaqt)`, `oynada_korsatish(oyna, kadr, matn)`.

**Sinov:** kamera ochilib, oynada tasvir chiqsin, `q` bosilganda yopilsin.

macOS'da birinchi safar kamera ruxsati so'raladi: **System Settings → Privacy & Security → Camera** dan terminalga ruxsat bering. Noutbukning o'z kamerasi odatda `0` raqamli.

---

## 6. `recognition.py` — raqamni o'qish

Uch qism, tartib bilan:

1. **Matn tozalash (OCRsiz sinab ko'riladi):**
   - `raqamni_tozalash(matn)` — bo'sh joy va belgilarni olib tashlaydi, katta harfga o'tkazadi.
   - `togri_formatmi(raqam)` — `01A123AA` yoki `01123ABC` shakliga mos keladimi.
2. **Oddiy OCR:**
   - `raqamni_aniqlash(kadr)` → `(raqam yoki None, ishonch)`. Avval eng sodda ko'rinishi: butun kadrni `readtext` bilan o'qib, formatga mos kelganini qaytarish.
   - `kadr` — rasmning o'zi (`cv2.imread(...)` natijasi), fayl yo'li emas.
3. **Aniqlikni oshirish (9-qadamda).**

**Sinov:** avval faqat 1-qism (`"01 a 123 aa"` → `01A123AA`). Keyin rasmdan: menyudagi "rasmdan raqamni sinash" yoki bitta buyruq bilan:

```
python -c "import cv2, recognition; print(recognition.raqamni_aniqlash(cv2.imread('rasmlar/raqam.jpg')))"
```

Fayl oxiriga sinov uchun `raqamni_aniqlash("")` kabi chaqiruv yozib qoldirmang: fayl har `import` qilinganda u ham ishga tushadi va `main.py` ni buzadi.

---

## 7. `nazorat.py` — asosiy mantiq (eng muhim fayl)

`qayta_ishlash(raqam, yonalish, kadr, hozir=None)` ichidagi tekshiruvlar **shu tartibda**:

1. Takror emasmi? (`takror_mi`, shu mashina oxirgi 60 soniyada ko'rilganmi)
2. Bazada bormi? Yo'q bo'lsa → yopiq.
3. Holati `Ruxsat berilgan`mi? Yo'q bo'lsa → yopiq.
4. `ochiq_sessiya(raqam)` bormi?
5. Yo'nalish: ochiq sessiya yo'q → **kirish**, bor → **chiqish**.
6. Kirish: `kirish_yozish` + `shlagbaum_ochish`.
7. Chiqish: daqiqa → summa → `chiqish_yozish` + `shlagbaum_ochish`.

Avval `hozir` parametri bilan **soxta vaqt** berib sinang. Kamera kerak emas.

Keyin `avtomatik_nazorat()` — avval eng sodda ko'rinishi:
```
kameralarni och
while True:
    kadr ol
    raqamni aniqla
    raqam topilsa → qayta_ishlash
    oynada ko'rsat
    q bosilsa → break
finally: kameralarni yop
```

Shu holatda ishlaydi, lekin oyna **qotadi** (har kadrni o'qish 0.5–1 soniya). Buni 9-qadam tuzatadi.

---

## 8. `main.py` — menyu

Menyu faqat tugma vazifasini bajaradi, mantiq yo'q:

```
1 avtomatik nazorat     → nazorat.avtomatik_nazorat()
2 avtomobil qo'shish    → database.avtomobil_qoshish(...)
3 barcha avtomobillar   → database.barcha_avtomobillar()
4 kirish-chiqish tarixi → database.barcha_sessiyalar()
5 rasmdan sinash        → recognition.raqamni_aniqlash(...)
0 chiqish
```
Oxirida: `if __name__ == "__main__": menyu()`

---

## 9. Yaxshilash: aniqlik va tezlik (darsda qo'shilgan)

Oddiy variant ishlagach, ikkita muammo chiqdi. Har biri alohida, ketma-ket tuzatiladi.

### 9.1. Raqam xato o'qiladi (`recognition.py`)

`70 A 444 AA` rasmini OCR `ZAGGGAA` deb o'qidi: raqam kadrda kichik, `4` esa `G` ga o'xshaydi.

Yozish tartibi:

1. `_kesib_oqish` — topilgan matn joyini asl kadrdan kesib, kattalashtiradi.
2. `_belgilarni_topish` — kesimni oq-qora qilib, 8 ta belgining joyini topadi.
3. `_guruhni_oqish` — guruhni faqat raqam yoki faqat harf deb o'qiydi (`70` | `A` | `444` | `AA`).
4. `_formatni_tanlash` — bo'shliqlarga qarab `01 A 123 AA` yoki `01 123 ABC` ni tanlaydi.
5. Ovoz berish — uch xil chekka bilan o'qib, eng ko'p mos kelganini oladi.
6. `_qatorlarga_birlashtirish` — ikki bo'lak bo'lib topilgan raqamni bitta qutiga qo'shadi.

**Sinov:** shu rasm → `('70A444AA', 0.86)`.

### 9.2. Kamera oynasi qotadi (`nazorat.py`, `camera.py`)

1. `recognition.tayyorlash()` — modelni sikldan oldin yuklaydi.
2. `class Aniqlovchi` — raqamni alohida oqimda (`threading`) o'qiydi; band bo'lsa yangi kadrni tashlab yuboradi.
3. `camera.harakat_bormi(oldingi, kadr)` — ikki kadrni solishtiradi. Raqam faqat harakat bo'lganda va undan keyin 3 soniya o'qiladi.
4. `kamerani_ochish` ga kadr o'lchami (`KADR_ENI`, `KADR_BOYI`) va `CAP_PROP_BUFFERSIZE` qo'shiladi.
5. `raqamni_aniqlash` matn joyini kichraytirilgan kadrdan (`ANIQLASH_ENI`) qidiradi.

Yakuniy sikl:
```
kameralarni och, modelni yukla
while True:
    kadr ol
    fonda o'qilgan natija tayyormi? → qayta_ishlash
    harakat bormi? → 3 soniyaga "faol"
    faol bo'lsa → kadrni fonga yubor
    oynada ko'rsat
    q bosilsa → break
finally: kameralarni yop
```

**Sinov:** oyna qotmaydi; kamera oldi tinch bo'lsa «Mashina kutilmoqda», harakat bo'lsa «Raqam o'qilmoqda...» chiqadi.

---

## Tekshiruv ro'yxati (yakuniy)

- [ ] Yangi mashina kirdi → sessiya ochildi, shlagbaum ochildi
- [ ] Shu mashina chiqdi → 6 daqiqa → 600 so'm
- [ ] Bazada yo'q mashina → yopiq
- [ ] Taqiqlangan mashina → yopiq
- [ ] 60 soniya ichida takroriy o'qish e'tiborga olinmadi
- [ ] Excel ochiq turganda yozish xatosi dasturni yiqitmadi
- [ ] Raqam o'qilayotganda kamera oynasi qotmadi
- [ ] Kamera oldi tinch turganda raqam o'qilmadi
- [ ] Yuridik raqam (`01123ABC`) qabul qilindi

## Qiyin joylar (ochiq aytiladi)

- Raqam o'qish bitta rasmda (`70 A 444 AA`) va jonli kamerada telefon ekranidagi shu rasm bilan sinalgan. Haqiqiy mashina, tun, qiya burchak sinalmagan.
- Raqam kadrda juda kichik bo'lsa (bo'yi ~22 pikseldan kam), xato o'qiladi yoki topilmaydi. Kamera yaqin turishi kerak.
- Bitta kameradagi "avto" rejimda mashina 60 soniyadan ortiq ko'rinib tursa, u chiqish deb o'qilib ketishi mumkin. Aniq ishlash uchun ikki kamera (`kirish`, `chiqish`) ishlating.
- Dastur qayta ishga tushsa takror himoyasi (`oxirgi_vaqt`) tozalanadi.
- To'lov faqat yoziladi, to'lov tizimi ulanmagan.
