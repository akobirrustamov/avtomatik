"""Web kamera bilan ishlash (opencv)."""
import os
from datetime import datetime

from config import RASMLAR_PAPKASI, KADR_ENI, KADR_BOYI, HARAKAT_CHEGARASI

try:
    import cv2
except ImportError:
    cv2 = None


def kutubxona_bormi():
    if cv2 is None:
        print("opencv o'rnatilmagan. Terminalda: pip install opencv-python")
        return False
    return True


def kamerani_ochish(indeks):
    if not kutubxona_bormi():
        return None
    kamera = cv2.VideoCapture(indeks)
    if not kamera.isOpened():
        print(f"{indeks}-kamerani ochib bo'lmadi!")
        return None
    kamera.set(cv2.CAP_PROP_FRAME_WIDTH, KADR_ENI)
    kamera.set(cv2.CAP_PROP_FRAME_HEIGHT, KADR_BOYI)
    kamera.set(cv2.CAP_PROP_BUFFERSIZE, 1)   # eski kadrlar to'planib qolmasin
    return kamera


def harakat_bormi(oldingi, kadr):
    """Kadr oldingisidan sezilarli farq qilsa True. (harakat, kichik_kadr) qaytaradi.

    kichik_kadr ni keyingi chaqiruvda `oldingi` sifatida bering."""
    kichik = cv2.cvtColor(cv2.resize(kadr, (160, 90)), cv2.COLOR_BGR2GRAY)
    kichik = cv2.GaussianBlur(kichik, (5, 5), 0)
    if oldingi is None:
        return True, kichik
    ozgargan = (cv2.absdiff(oldingi, kichik) > 25).mean()
    return ozgargan > HARAKAT_CHEGARASI, kichik


def kadr_olish(kamera):
    holat, kadr = kamera.read()
    return kadr if holat else None


def kamerani_yopish(kameralar):
    for kamera in kameralar:
        kamera.release()
    cv2.destroyAllWindows()


def rasmni_oqish(fayl_yoli):
    return cv2.imread(fayl_yoli) if kutubxona_bormi() else None


def rasm_saqlash(kadr, raqam, yonalish, vaqt):
    """Kadrni rasmlar/ ga yozadi va fayl yo'lini qaytaradi."""
    os.makedirs(RASMLAR_PAPKASI, exist_ok=True)
    nom = f"{yonalish}_{raqam}_{vaqt.strftime('%Y%m%d_%H%M%S')}.jpg"
    yol = os.path.join(RASMLAR_PAPKASI, nom)
    if cv2 is not None and kadr is not None:
        cv2.imwrite(yol, kadr)
    return yol


def oynada_korsatish(oyna_nomi, kadr, matn):
    """Kadrni matn bilan ko'rsatadi. Bosilgan tugmani qaytaradi (q — chiqish)."""
    cv2.putText(kadr, matn, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imshow(oyna_nomi, kadr)
    return chr(cv2.waitKey(1) & 0xFF)
