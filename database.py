"""Excel bazasi bilan ishlash: avtomobillar va kirish-chiqish yozuvlari."""
import os
from datetime import datetime
import openpyxl

from config import (EXCEL_FILE, VARAQ_AVTO, VARAQ_SESSIYA, 
                    SARLAVHA_AVTO, SARLAVHA_SESSIYA, VAQT_FORMATI, 
                    RUXSAT, TAQIQ)

def vaqt_matni(vaqt):
    return vaqt.strftime(VAQT_FORMATI)


def vaqtni_oqish(matn):
    return datetime.strptime(matn, VAQT_FORMATI)


def bazani_yaratish():
    """Fayl yo'q bo'lsa yaratadi; kerakli varaqlar yo'q bo'lsa qo'shadi."""
    if os.path.exists(EXCEL_FILE):
        kitob = openpyxl.load_workbook(EXCEL_FILE)
    else:
        kitob = openpyxl.Workbook()
        kitob.active.title = VARAQ_AVTO
        kitob[VARAQ_AVTO].append(SARLAVHA_AVTO)
        kitob[VARAQ_AVTO].append([1, "01A123AA", "Ali", "Cobalt", RUXSAT])
        kitob[VARAQ_AVTO].append([2, "80B456BB", "Vali", "Gentra", RUXSAT])
        kitob[VARAQ_AVTO].append([3, "90C789CC", "Sardor", "Nexia 3", TAQIQ])
    if VARAQ_SESSIYA not in kitob.sheetnames:
        kitob.create_sheet(VARAQ_SESSIYA).append(SARLAVHA_SESSIYA)
    kitob.save(EXCEL_FILE)
    kitob.close()


# ---------- Avtomobillar ----------

def avtomobil_qidirish(raqam):
    kitob = openpyxl.load_workbook(EXCEL_FILE)
    varaq = kitob[VARAQ_AVTO]
    natija = None
    for qator in varaq.iter_rows(min_row=2, values_only=True):
        if qator[1] == raqam:
            natija = {"id": qator[0], "raqam": qator[1], "egasi": qator[2],
                      "model": qator[3], "holati": qator[4]}
            break
    kitob.close()
    return natija


def avtomobil_qoshish(raqam, egasi, model, holati=RUXSAT):
    """True — qo'shildi, False — bunday raqam allaqachon bor."""
    if avtomobil_qidirish(raqam) is not None:
        return False
    kitob = openpyxl.load_workbook(EXCEL_FILE)
    varaq = kitob[VARAQ_AVTO]
    varaq.append([varaq.max_row, raqam, egasi, model, holati])
    kitob.save(EXCEL_FILE)
    kitob.close()
    return True


def barcha_avtomobillar():
    kitob = openpyxl.load_workbook(EXCEL_FILE)
    royxat = []
    for q in kitob[VARAQ_AVTO].iter_rows(min_row=2, values_only=True):
        royxat.append({"id": q[0], "raqam": q[1], "egasi": q[2],
                       "model": q[3], "holati": q[4]})
    kitob.close()
    return royxat


# ---------- Kirish / chiqish yozuvlari ----------

def ochiq_sessiya(raqam):
    """Ichkarida turgan (chiqmagan) mashinaning yozuvi, yo'q bo'lsa None."""
    kitob = openpyxl.load_workbook(EXCEL_FILE)
    topildi = None
    for q in kitob[VARAQ_SESSIYA].iter_rows(min_row=2, values_only=True):
        if q[1] == raqam and not q[3]:
            topildi = {"id": q[0], "raqam": q[1], "kirish": vaqtni_oqish(q[2])}
    kitob.close()
    return topildi


def kirish_yozish(raqam, vaqt, rasm_yoli):
    kitob = openpyxl.load_workbook(EXCEL_FILE)
    varaq = kitob[VARAQ_SESSIYA]
    varaq.append([varaq.max_row, raqam, vaqt_matni(vaqt), "", "", "", rasm_yoli, ""])
    kitob.save(EXCEL_FILE)
    kitob.close()


def chiqish_yozish(sessiya_id, vaqt, daqiqa, summa, rasm_yoli):
    kitob = openpyxl.load_workbook(EXCEL_FILE)
    for qator in kitob[VARAQ_SESSIYA].iter_rows(min_row=2):
        if qator[0].value == sessiya_id:
            qator[3].value = vaqt_matni(vaqt)
            qator[4].value = daqiqa
            qator[5].value = summa
            qator[7].value = rasm_yoli
            break
    kitob.save(EXCEL_FILE)
    kitob.close()


def barcha_sessiyalar():
    kitob = openpyxl.load_workbook(EXCEL_FILE)
    royxat = [list(q) for q in kitob[VARAQ_SESSIYA].iter_rows(min_row=2, values_only=True)]
    kitob.close()
    return royxat
