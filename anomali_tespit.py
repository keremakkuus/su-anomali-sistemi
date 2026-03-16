import pandas as pd
import numpy as np
from datetime import datetime
import logging
import os

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename=f"logs/log_{datetime.now().strftime('%Y%m%d')}.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# ── Eşik Değerleri (KOSKİ standartlarına göre) ──
ESIKLER = {
    "basinc_bar":  {"min": 2.0,  "max": 6.5,  "birim": "bar"},
    "debi_m3h":    {"min": 50.0, "max": 180.0, "birim": "m³/h"},
    "seviye_%":    {"min": 20.0, "max": 95.0,  "birim": "%"},
    "klor_mgl":    {"min": 0.2,  "max": 1.5,   "birim": "mg/L"},
    "enerji_kwh":  {"min": 40.0, "max": 150.0, "birim": "kWh"},
}

def anomali_tespit_et(veri):
    """Eşik değer aşımlarını tespit eder"""
    anomaliler = []

    for _, satir in veri.iterrows():
        for parametre, esik in ESIKLER.items():
            deger = satir[parametre]

            if deger < esik["min"]:
                seviye, mesaj = tehlike_seviyesi(parametre, deger, esik, "dusuk")
                anomaliler.append({
                    "zaman":      satir["zaman"],
                    "istasyon":   satir["istasyon"],
                    "parametre":  parametre,
                    "deger":      deger,
                    "birim":      esik["birim"],
                    "durum":      "DÜŞÜK",
                    "esik_min":   esik["min"],
                    "esik_max":   esik["max"],
                    "tehlike":    seviye,
                    "mesaj":      mesaj,
                })

            elif deger > esik["max"]:
                seviye, mesaj = tehlike_seviyesi(parametre, deger, esik, "yuksek")
                anomaliler.append({
                    "zaman":      satir["zaman"],
                    "istasyon":   satir["istasyon"],
                    "parametre":  parametre,
                    "deger":      deger,
                    "birim":      esik["birim"],
                    "durum":      "YÜKSEK",
                    "esik_min":   esik["min"],
                    "esik_max":   esik["max"],
                    "tehlike":    seviye,
                    "mesaj":      mesaj,
                })

    df = pd.DataFrame(anomaliler)
    logging.info(f"{len(df)} anomali tespit edildi")
    return df


def tehlike_seviyesi(parametre, deger, esik, yon):
    """Anomalinin tehlike seviyesini ve açıklamasını belirler"""

    sapma = abs(deger - esik["min"] if yon == "dusuk" else deger - esik["max"])

    if parametre == "basinc_bar":
        if yon == "dusuk":
            return "🔴 KRİTİK", f"Boru patlaması veya kaçak riski! Basınç {deger} bar"
        else:
            return "🟠 UYARI", f"Aşırı basınç! Boru hasarı riski. Basınç {deger} bar"

    elif parametre == "debi_m3h":
        if yon == "yuksek":
            return "🔴 KRİTİK", f"Aşırı debi! Su kaçağı tespit edildi. Debi {deger} m³/h"
        else:
            return "🟡 BİLGİ", f"Düşük debi. Tıkanma olabilir. Debi {deger} m³/h"

    elif parametre == "seviye_%":
        if yon == "dusuk":
            return "🔴 KRİTİK", f"Depo seviyesi kritik! Acil müdahale gerekli. Seviye %{deger}"
        else:
            return "🟡 BİLGİ", f"Depo doluluk yüksek. Seviye %{deger}"

    elif parametre == "klor_mgl":
        if yon == "yuksek":
            return "🟠 UYARI", f"Aşırı klor! Halk sağlığı riski. Klor {deger} mg/L"
        else:
            return "🟡 BİLGİ", f"Yetersiz dezenfeksiyon. Klor {deger} mg/L"

    else:
        return "🟡 BİLGİ", f"{parametre} değeri sınır dışı: {deger}"


def anomali_ozeti_yazdir(anomaliler):
    """Tespit edilen anomalilerin özetini yazdırır"""
    if anomaliler.empty:
        print("✅ Anomali tespit edilmedi!")
        return

    print(f"\n🚨 TOPLAM {len(anomaliler)} ANOMALİ TESPİT EDİLDİ!")
    print("=" * 55)

    kritik = anomaliler[anomaliler["tehlike"].str.contains("KRİTİK")]
    uyari  = anomaliler[anomaliler["tehlike"].str.contains("UYARI")]
    bilgi  = anomaliler[anomaliler["tehlike"].str.contains("BİLGİ")]

    print(f"   🔴 Kritik  : {len(kritik)} adet")
    print(f"   🟠 Uyarı   : {len(uyari)} adet")
    print(f"   🟡 Bilgi   : {len(bilgi)} adet")
    print("=" * 55)

    print("\n🔴 KRİTİK ANOMALİLER:")
    for _, a in kritik.iterrows():
        print(f"   [{a['istasyon']}] {a['mesaj']}")
        print(f"   ⏰ {a['zaman']}")
        print()

    if not uyari.empty:
        print("🟠 UYARILAR:")
        for _, a in uyari.iterrows():
            print(f"   [{a['istasyon']}] {a['mesaj']}")


if __name__ == "__main__":
    from sensor_uretici import sensor_verisi_uret

    print("=" * 55)
    print("AKILLİ SU ŞEBEKESİ ANOMALİ TESPİT SİSTEMİ")
    print("=" * 55)

    veri, _ = sensor_verisi_uret(saat=24)
    anomaliler = anomali_tespit_et(veri)
    anomali_ozeti_yazdir(anomaliler)