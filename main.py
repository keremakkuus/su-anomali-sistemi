import schedule
import time
import logging
import os
from datetime import datetime

from sensor_uretici import sensor_verisi_uret
from anomali_tespit import anomali_tespit_et, anomali_ozeti_yazdir
from grafik_uretici import grafik_olustur

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename=f"logs/log_{datetime.now().strftime('%Y%m%d')}.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def pipeline_calistir():
    print("\n" + "=" * 55)
    print(f"PIPELINE BASLADI: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    # 1. Veri Üret
    print("\n ADIM 1: Sensor Verisi Okunuyor...")
    veri, csv_dosya = sensor_verisi_uret(saat=24)

    # 2. Anomali Tespit
    print("\n ADIM 2: Anomaliler Tespit Ediliyor...")
    anomaliler = anomali_tespit_et(veri)
    anomali_ozeti_yazdir(anomaliler)

    # 3. Grafik Uret
    print("\n ADIM 3: Grafik Olusturuluyor...")
    grafik_dosya = grafik_olustur(veri, anomaliler)

    # 4. Ozet
    kritik_sayisi = len(anomaliler[anomaliler["tehlike"].str.contains("KRITIK")]) if not anomaliler.empty else 0

    print("\n" + "=" * 55)
    print("PIPELINE TAMAMLANDI!")
    print(f"   Toplam Anomali : {len(anomaliler)} adet")
    print(f"   Kritik         : {kritik_sayisi} adet")
    print(f"   CSV            : {csv_dosya}")
    print(f"   Grafik         : {grafik_dosya}")
    print("=" * 55)

    logging.info(f"Pipeline tamamlandi. {len(anomaliler)} anomali tespit edildi.")


schedule.every().hour.do(pipeline_calistir)

if __name__ == "__main__":
    print("=" * 55)
    print("  AKILLI SU SEBEKESI ANOMALİ TESPİT SİSTEMİ")
    print("       v1.0 - Mehmet Kerem Akkus")
    print("=" * 55)
    print("\n Sistem her saat otomatik calisacak")
    print(" Simdi ilk calistirma yapiliyor...\n")

    pipeline_calistir()

    print("\n Sistem beklemede... (durdurmak icin Ctrl+C)")
    while True:
        schedule.run_pending()
        time.sleep(60)