import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from datetime import datetime
import os

os.makedirs("grafikler", exist_ok=True)
plt.rcParams["figure.facecolor"] = "white"
plt.rcParams["axes.facecolor"] = "#f8f9fa"
plt.rcParams["font.family"] = "DejaVu Sans"

def grafik_olustur(veri, anomaliler):
    """4 panelli sensör grafiği oluşturur"""

    fig, axes = plt.subplots(4, 1, figsize=(14, 16))
    fig.suptitle(
        "🏢 KOSKİ — Akıllı Su Şebekesi Anomali Tespit Sistemi\n"
        f"Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        fontsize=14, fontweight="bold", y=0.98, color="#0D2149"
    )

    parametreler = [
        ("basinc_bar",  "Basınç (bar)",   "#2D5BE3", 2.0, 6.5),
        ("debi_m3h",    "Debi (m³/h)",    "#28a745", 50,  180),
        ("seviye_%",    "Depo Seviyesi (%)", "#fd7e14", 20, 95),
        ("klor_mgl",    "Klor (mg/L)",    "#6f42c1", 0.2, 1.5),
    ]

    for ax, (kolon, baslik, renk, alt_esik, ust_esik) in zip(axes, parametreler):
        zaman = veri["zaman"]
        deger = veri[kolon]

        # Normal çizgi
        ax.plot(zaman, deger, color=renk, linewidth=1.5, label="Sensör Değeri")

        # Eşik çizgileri
        ax.axhline(y=alt_esik, color="red",    linestyle="--", linewidth=1, alpha=0.7, label=f"Alt Eşik ({alt_esik})")
        ax.axhline(y=ust_esik, color="orange", linestyle="--", linewidth=1, alpha=0.7, label=f"Üst Eşik ({ust_esik})")

        # Anomali noktaları
        if not anomaliler.empty:
            param_anomali = anomaliler[anomaliler["parametre"] == kolon]
            if not param_anomali.empty:
                anomali_zamanlari = pd.to_datetime(param_anomali["zaman"])
                anomali_degerler  = param_anomali["deger"].values
                ax.scatter(anomali_zamanlari, anomali_degerler,
                          color="red", s=80, zorder=5, label="⚠ Anomali")

                # Kırmızı arka plan anomali bölgelerine
                for az in anomali_zamanlari:
                    ax.axvspan(az - pd.Timedelta(minutes=10),
                               az + pd.Timedelta(minutes=10),
                               alpha=0.15, color="red")

        ax.set_title(baslik, fontweight="bold", color="#0D2149", pad=8)
        ax.set_ylabel(baslik.split("(")[1].replace(")", "") if "(" in baslik else "")
        ax.legend(loc="upper right", fontsize=8)
        ax.grid(True, alpha=0.4)
        ax.tick_params(axis="x", rotation=30, labelsize=8)

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    dosya = f"grafikler/anomali_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(dosya, dpi=150, bbox_inches="tight")
    plt.show()

    print(f"✅ Grafik kaydedildi: {dosya}")
    return dosya


if __name__ == "__main__":
    from sensor_uretici import sensor_verisi_uret
    from anomali_tespit import anomali_tespit_et, anomali_ozeti_yazdir

    print("=" * 55)
    print("GRAFİK ÜRETİCİ ÇALIŞIYOR")
    print("=" * 55)

    veri, _        = sensor_verisi_uret(saat=24)
    anomaliler     = anomali_tespit_et(veri)
    anomali_ozeti_yazdir(anomaliler)
    grafik_olustur(veri, anomaliler)