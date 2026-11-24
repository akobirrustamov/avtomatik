"""Avtomatik nazorat: kirish va chiqish qarorlari + kamera sikli."""
import threading
from datetime import datetime

import billing
import camera
import database
import gate
import recognition
from config import (KAMERALAR, MIN_ISHONCH, TAKROR_SONIYA, RUXSAT,
                    HARAKATDAN_KEYIN_SONIYA)

oxirgi_vaqt = {}   # raqam -> oxirgi marta qachon qayta ishlangan


def takror_mi(raqam, hozir):
    """Bir mashina kamera oldida turganda yuzlab kadr keladi, ularni o'tkazib yuboramiz."""
    oldingi = oxirgi_vaqt.get(raqam)
    return oldingi is not None and (hozir - oldingi).total_seconds() < TAKROR_SONIYA


def qayta_ishlash(raqam, yonalish, kadr, hozir=None):
    """Bitta aniqlangan raqam uchun qaror qiladi. Ekranga chiqadigan matnni qaytaradi."""
    hozir = hozir or datetime.now()
    if takror_mi(raqam, hozir):
        return None

    avtomobil = database.avtomobil_qidirish(raqam)
    # if avtomobil is None:
    #     oxirgi_vaqt[raqam] = hozir
    #     gate.shlagbaum_yopiq_qoldirish(raqam, "bazada yo'q")
    #     return f"{raqam}: bazada yo'q"
    if avtomobil["holati"] != RUXSAT:
        oxirgi_vaqt[raqam] = hozir
        gate.shlagbaum_yopiq_qoldirish(raqam, "taqiqlangan")
        return f"{raqam}: taqiqlangan"

    sessiya = database.ochiq_sessiya(raqam)
    if yonalish == "avto":
        yonalish = "chiqish" if sessiya else "kirish"

    if yonalish == "kirish":
        if sessiya:
            gate.shlagbaum_yopiq_qoldirish(raqam, "allaqachon ichkarida")
            return f"{raqam}: allaqachon ichkarida"
        yol = camera.rasm_saqlash(kadr, raqam, "kirish", hozir)
        database.kirish_yozish(raqam, hozir, yol)
        oxirgi_vaqt[raqam] = hozir
        gate.shlagbaum_ochish("kirish", raqam)
        return f"KIRDI: {raqam} ({avtomobil['model']}, {avtomobil['egasi']})"

    # chiqish
    if not sessiya:
        gate.shlagbaum_yopiq_qoldirish(raqam, "kirish yozuvi topilmadi")
        return f"{raqam}: kirish yozuvi yo'q"
    daqiqa = billing.daqiqani_hisoblash(sessiya["kirish"], hozir)
    summa = billing.summani_hisoblash(daqiqa)
    yol = camera.rasm_saqlash(kadr, raqam, "chiqish", hozir)
    database.chiqish_yozish(sessiya["id"], hozir, daqiqa, summa, yol)
    oxirgi_vaqt[raqam] = hozir
    gate.shlagbaum_ochish("chiqish", raqam)
    return f"CHIQDI: {raqam} | {daqiqa} daqiqa | {summa} so'm"


class Aniqlovchi:
    """Raqamni alohida oqimda (fonda) o'qiydi, shunda kamera oynasi qotib qolmaydi."""

    def __init__(self):
        self.band = False      # hozir kadr o'qilyaptimi
        self.natija = None     # (raqam, ishonch, kadr) — tayyor, hali olinmagan natija

    def yuborish(self, kadr):
        """Bo'sh bo'lsa kadrni o'qishga oladi. Band bo'lsa kadr tashlab yuboriladi."""
        if self.band:
            return
        self.band = True
        threading.Thread(target=self._oqish, args=(kadr.copy(),), daemon=True).start()

    def _oqish(self, kadr):
        try:
            raqam, ishonch = recognition.raqamni_aniqlash(kadr)
            self.natija = (raqam, ishonch, kadr)
        except Exception as xato:
            print(f"Raqamni o'qishda xato: {xato}")
        finally:
            self.band = False

    def natijani_olish(self):
        natija, self.natija = self.natija, None
        return natija


def avtomatik_nazorat():
    """Kameralardan kadr o'qiydi, mashina kelganda raqamni topadi. Q — to'xtatish."""
    database.bazani_yaratish()
    ochiq = []
    for yonalish, indeks in KAMERALAR:
        kamera = camera.kamerani_ochish(indeks)
        if kamera is not None:
            ochiq.append((yonalish, indeks, kamera))
    if not ochiq:
        return

    try:
        print("Raqam o'qish modeli yuklanmoqda...")
        if not recognition.tayyorlash():
            return
        print("Avtomatik nazorat ishga tushdi. To'xtatish uchun kamera oynasida Q bosing.")
        holat = {indeks: {"aniqlovchi": Aniqlovchi(), "oldingi": None,
                          "faol_gacha": None, "xabar": None}
                 for _, indeks, _ in ochiq}
        while True:
            for yonalish, indeks, kamera in ochiq:
                kadr = camera.kadr_olish(kamera)
                if kadr is None:
                    continue
                h = holat[indeks]
                hozir = datetime.now()

                # 1. Fonda o'qilgan natija tayyor bo'lsa, qaror qilamiz.
                natija = h["aniqlovchi"].natijani_olish()
                if natija:
                    raqam, ishonch, oqilgan_kadr = natija
                    if raqam and ishonch >= MIN_ISHONCH:
                        xabar = qayta_ishlash(raqam, yonalish, oqilgan_kadr, hozir)
                        if xabar:
                            print(xabar)
                            h["xabar"] = xabar

                # 2. Harakat bo'lsa (mashina keldi) — shu paytdan boshlab raqam o'qiymiz.
                harakat, h["oldingi"] = camera.harakat_bormi(h["oldingi"], kadr)
                if harakat:
                    h["faol_gacha"] = hozir.timestamp() + HARAKATDAN_KEYIN_SONIYA
                faol = h["faol_gacha"] is not None and hozir.timestamp() <= h["faol_gacha"]
                if faol:
                    h["aniqlovchi"].yuborish(kadr)

                oyna = f"{yonalish} (kamera {indeks})"
                matn = h["xabar"] or ("Raqam o'qilmoqda..." if faol else "Mashina kutilmoqda")
                if camera.oynada_korsatish(oyna, kadr, matn) == "q":
                    return
    finally:
        camera.kamerani_yopish([k for _, _, k in ochiq])
        print("Nazorat to'xtatildi.")
