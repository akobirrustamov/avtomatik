"""Dasturni shu fayldan ishga tushiring:  python main.py"""
import billing
import camera
import database
import nazorat
import recognition


def avtomobil_qoshish_menyu():
    raqam = recognition.raqamni_tozalash(input("Davlat raqami: "))
    if not recognition.togri_formatmi(raqam):
        print("Raqam formati noto'g'ri! Masalan: 01A123AA yoki 01123ABC")
        return
    egasi = input("Egasi: ").strip()
    model = input("Model: ").strip()
    if database.avtomobil_qoshish(raqam, egasi, model):
        print("Avtomobil qo'shildi!")
    else:
        print("Bu raqam bazada allaqachon bor!")


def avtomobillarni_korsatish():
    print("\n====== AVTOMOBILLAR ======")
    for a in database.barcha_avtomobillar():
        print(f"{a['id']}. {a['raqam']} | {a['egasi']} | {a['model']} | {a['holati']}")


def sessiyalarni_korsatish():
    print("\n====== KIRISH-CHIQISH ======")
    for s in database.barcha_sessiyalar():
        _, raqam, kirish, chiqish, daqiqa, summa, _, _ = s
        holat = f"{daqiqa} daqiqa, {summa} so'm" if chiqish else "ichkarida"
        print(f"{raqam} | kirish: {kirish} | chiqish: {chiqish or '-'} | {holat}")


def rasmdan_sinash():
    """Kamerasiz sinash: rasm fayldan raqamni o'qiydi."""
    yol = input("Rasm fayli yo'li: ").strip()
    kadr = camera.rasmni_oqish(yol)
    if kadr is None:
        print("Rasmni o'qib bo'lmadi!")
        return
    raqam, ishonch = recognition.raqamni_aniqlash(kadr)
    print(f"Natija: {raqam}, ishonch: {ishonch:.2f}" if raqam else "Raqam topilmadi.")


def menyu():
    database.bazani_yaratish()
    while True:
        print(f"""
        ==============================
        AVTOMOBILLAR KIRISH TIZIMI
        Tarif: {billing.summani_hisoblash(1)} so'm / daqiqa
        ==============================
        1. Avtomatik nazoratni boshlash
        2. Avtomobil qo'shish
        3. Barcha avtomobillar
        4. Kirish-chiqish tarixi
        5. Rasmdan raqamni sinash
        0. Chiqish
        """)
        tanlov = input("Tanlov: ").strip()
        if tanlov == "1":
            nazorat.avtomatik_nazorat()
        elif tanlov == "2":
            avtomobil_qoshish_menyu()
        elif tanlov == "3":
            avtomobillarni_korsatish()
        elif tanlov == "4":
            sessiyalarni_korsatish()
        elif tanlov == "5":
            rasmdan_sinash()
        elif tanlov == "0":
            print("Dastur yakunlandi!")
            break
        else:
            print("Noto'g'ri tanlov!")


if __name__ == "__main__":
    menyu()
