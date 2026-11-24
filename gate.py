"""Shlagbaum. Hozircha faqat ekranga yozadi.
Haqiqiy shlagbaum ulanganda (masalan, Arduino/Raspberry Pi) faqat shu fayl o'zgaradi."""


def shlagbaum_ochish(yonalish, raqam):
    print(f"   🟢 SHLAGBAUM OCHILDI ({yonalish}): {raqam}")


def shlagbaum_yopiq_qoldirish(raqam, sabab):
    print(f"   🔴 Shlagbaum yopiq: {raqam} — {sabab}")
