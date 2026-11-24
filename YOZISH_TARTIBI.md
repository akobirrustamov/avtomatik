# Avtomatik avtoturargoh: noldan yozish tartibi

Qoida: **pastdan yuqoriga yoziladi.** Boshqa fayllarga tayanmaydigan fayl birinchi yoziladi, hammasini ulaydigan `main.py` oxirgi yoziladi. Har qadamda fayl alohida sinab ko'riladi, keyin keyingisiga o'tiladi.

```
config → billing → database → gate → camera → recognition → nazorat → main
 (1)       (2)        (3)       (4)     (5)        (6)          (7)      (8)
```

Tayyor loyiha `avtomatik/` papkasida. Quyida har fayl nima uchun va nima bilan boshlanishi yozilgan.

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
HAR_NECHTA_KADR = 15
MIN_ISHONCH = 0.5
TAKROR_SONIYA = 60
VAQT_FORMATI = "%Y-%m-%d %H:%M:%S"
RUXSAT = "Ruxsat berilgan"
TAQIQ = "Taqiqlangan"
```

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
    print(f"[SHLAGBAUM] OCHILDI ({yonalish}): {raqam}")

def shlagbaum_yopiq_qoldirish(raqam, sabab):
    print(f"[SHLAGBAUM] YOPIQ: {raqam} — {sabab}")
```

Keyin haqiqiy qurilma ulansa, faqat shu fayl o'zgaradi.

---

## 5. `camera.py` — kamera bilan ishlash

`cv2` ni fayl boshida emas, `try/except` ichida import qiling. Shunda kutubxona yo'q bo'lsa ham dastur yiqilmaydi.

Funksiyalar: `kutubxona_bormi`, `kamerani_ochish(indeks)`, `kadr_olish(kamera)`, `kamerani_yopish(kameralar)`, `rasmni_oqish(yol)`, `rasm_saqlash(kadr, raqam, yonalish, vaqt)`, `oynada_korsatish(oyna, kadr, matn)`.

**Sinov:** kamera ochilib, oynada tasvir chiqsin, `q` bosilganda yopilsin.

---

## 6. `recognition.py` — raqamni o'qish

Ikki qism, tartib bilan:

1. **Matn tozalash (OCRsiz sinab ko'riladi):**
   - `raqamni_tozalash(matn)` — bo'sh joy va belgilarni olib tashlaydi, katta harfga o'tkazadi.
   - `togri_formatmi(raqam)` — `01A123AA` yoki `01123ABC` shakliga mos keladimi.
2. **OCR:**
   - `raqamni_aniqlash(kadr)` → `(raqam yoki None, ishonch)`.

**Sinov:** avval faqat 1-qism (`"01 a 123 aa"` → `01A123AA`). Keyin rasmdan: menyudagi "rasmdan raqamni sinash".

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

Keyin `avtomatik_nazorat()`:
```
kameralarni och
while True:
    kadr ol
    har 15-kadrda raqamni aniqla
    raqam topilsa → qayta_ishlash
    oynada ko'rsat
    q bosilsa → break
finally: kameralarni yop
```

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

## Tekshiruv ro'yxati (yakuniy)

- [ ] Yangi mashina kirdi → sessiya ochildi, shlagbaum ochildi
- [ ] Shu mashina chiqdi → 6 daqiqa → 600 so'm
- [ ] Bazada yo'q mashina → yopiq
- [ ] Taqiqlangan mashina → yopiq
- [ ] 60 soniya ichida takroriy o'qish e'tiborga olinmadi
- [ ] Excel ochiq turganda yozish xatosi dasturni yiqitmadi

## Qiyin joylar (ochiq aytiladi)

- Bitta kameradagi "avto" rejimda mashina 60 soniyadan ortiq ko'rinib tursa, u chiqish deb o'qilib ketishi mumkin. Aniq ishlash uchun ikki kamera (`kirish`, `chiqish`) ishlating.
- Dastur qayta ishga tushsa takror himoyasi (`oxirgi_vaqt`) tozalanadi.
- `cv2` va `easyocr` real kamerada hali sinalmagan.
- To'lov faqat yoziladi, to'lov tizimi ulanmagan.
