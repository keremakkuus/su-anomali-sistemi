import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

os.makedirs("veri", exist_ok=True)
os.makedirs("raporlar", exist_ok=True)
os.makedirs("grafikler", exist_ok=True)

def sensor_verisi_uret(saat=24):
    """
    Gerçekçi su şebekesi sensör verisi üretir.
    KOSKİ'nin SCADA sistemindeki gibi basınç, debi ve seviye verileri.
    """
    np.random.seed(42)
    zaman_damgalari = [
        datetime.now() - timedelta(hours=saat) + timedelta(minutes=i*15)
        for i in range(saat * 4)  # 15 dakikada bir ölçüm
    ]

    n = len(zaman_damgalari)

    # ── Normal sensör değerleri ──
    basinc     = 4.5 + 0.3 * np.sin(np.linspace(0, 4*np.pi, n)) + np.random.normal(0, 0.1, n)
    debi       = 120 + 20 * np.sin(np.linspace(0, 4*np.pi, n)) + np.random.normal(0, 5, n)
    seviye     = 75 + 5 * np.sin(np.linspace(0, 2*np.pi, n)) + np.random.normal(0, 1, n)
    klor       = 0.5 + 0.1 * np.random.normal(0, 1, n)
    enerji     = 85 + 10 * np.random.normal(0, 1, n)

    # ── Anomaliler ekle (gerçekçi arızalar) ──
    # Basınç düşüşü (boru patlaması simülasyonu)
    basinc[40:45]  = 1.8   # Ani düşüş
    basinc[80:83]  = 6.9   # Ani yükselme

    # Debi anomalisi (kaçak simülasyonu)
    debi[60:67]    = 185   # Aşırı yüksek debi = kaçak

    # Seviye anomalisi (depo boşalması)
    seviye[90:95]  = 15    # Kritik düşük seviye

    # Klor anomalisi
    klor[70:73]    = 1.8   # Aşırı yüksek klor

    veri = pd.DataFrame({
        "zaman":         zaman_damgalari,
        "istasyon":      [f"IST-{(i % 10) + 1:02d}" for i in range(n)],
        "basinc_bar":    np.round(basinc, 3),
        "debi_m3h":      np.round(debi, 2),
        "seviye_%":      np.round(np.clip(seviye, 0, 100), 2),
        "klor_mgl":      np.round(np.clip(klor, 0, 3), 3),
        "enerji_kwh":    np.round(np.clip(enerji, 0, 200), 2),
    })

    # CSV olarak kaydet
    dosya = f"veri/sensor_verisi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    veri.to_csv(dosya, index=False, encoding="utf-8-sig")

    print(f"✅ {n} adet sensör ölçümü üretildi ({saat} saatlik veri)")
    print(f"📁 Kaydedildi: {dosya}")
    print(f"\n📊 Veri Özeti:")
    print(f"   Basınç    : Ort {veri['basinc_bar'].mean():.2f} bar  | Min {veri['basinc_bar'].min():.2f} | Maks {veri['basinc_bar'].max():.2f}")
    print(f"   Debi      : Ort {veri['debi_m3h'].mean():.1f} m³/h  | Min {veri['debi_m3h'].min():.1f} | Maks {veri['debi_m3h'].max():.1f}")
    print(f"   Seviye    : Ort {veri['seviye_%'].mean():.1f}%      | Min {veri['seviye_%'].min():.1f} | Maks {veri['seviye_%'].max():.1f}")

    return veri, dosya


if __name__ == "__main__":
    print("=" * 50)
    print("SCADA SENSÖR VERİSİ ÜRETİCİ")
    print("=" * 50)
    veri, dosya = sensor_verisi_uret(saat=24)