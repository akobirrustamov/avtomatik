"""Pul hisoblash. Faqat hisob-kitob, na Excel, na kamera."""
import math

from config import TARIF_DAQIQAGA


def daqiqani_hisoblash(kirish, chiqish):
    """Turgan vaqt (daqiqa). Har boshlangan daqiqa to'liq, kamida 1."""
    soniya = (chiqish - kirish).total_seconds()
    return max(1, math.ceil(soniya / 60))


def summani_hisoblash(daqiqa):
    return daqiqa * TARIF_DAQIQAGA
