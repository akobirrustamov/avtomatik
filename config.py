"""Hamma sozlamalar bitta joyda. Qiymatni shu yerda o'zgartiring."""

# --- Fayllar va papkalar ---
EXCEL_FILE = "avtomobillar.xlsx"

RASMLAR_PAPKASI = "rasmlar"

# --- Narx ---
TARIF_DAQIQAGA = 100          # so'm; har boshlangan daqiqa uchun

# --- Kameralar: (yo'nalish, kamera raqami) ---
# Ikkita kamera bo'lsa:  [("kirish", 0), ("chiqish", 1)]
# Bitta kamera bo'lsa:   [("avto", 0)]  -> ichkarida bo'lsa chiqish, bo'lmasa kirish
KAMERALAR = [("avto", 0)]
KADR_ENI, KADR_BOYI = 1280, 720   # kameradan so'raladigan kadr o'lchami

# --- Raqamni aniqlash ---
# Raqam doim emas, faqat kadrda harakat bo'lganda (mashina kelganda) o'qiladi.
HARAKAT_CHEGARASI = 0.01      # kadrning shuncha ulushi o'zgarsa — harakat bor (0.01 = 1%)
HARAKATDAN_KEYIN_SONIYA = 3   # harakat to'xtagach yana shuncha soniya o'qishda davom etamiz
ANIQLASH_ENI = 960            # matn joyini qidirishda kadr shu enga kichraytiriladi (tezlik)
MIN_ISHONCH = 0.5             # shundan past ishonchli natija e'tiborga olinmaydi
TAKROR_SONIYA = 60            # bir mashinani shuncha soniya ichida qayta ishlamaymiz

# --- Excel jadvallari ---
VARAQ_AVTO = "Avtomobillar"
VARAQ_SESSIYA = "Sessiyalar"
SARLAVHA_AVTO = ["ID", "Davlat raqami", "Egasi", "Model", "Holati"]
SARLAVHA_SESSIYA = ["ID", "Davlat raqami", "Kirish vaqti", "Chiqish vaqti", "Daqiqa", 
                    "Summa (so'm)", "Kirish rasmi", "Chiqish rasmi"]

VAQT_FORMATI = "%Y-%m-%d %H:%M:%S"
RUXSAT = "Ruxsat berilgan"
TAQIQ = "Taqiqlangan"
