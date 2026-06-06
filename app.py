import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime, timedelta

# --- 1. SAYFA AYARLARI VE TEMA ---
st.set_page_config(
    page_title="SOC | Gerçek Zamanlı IDS Paneli",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Profesyonel SOC CSS Teması (Karanlık, Neon Vurgular ve Glassmorphism)
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    div[data-testid="metric-container"] {
        background: rgba(30, 30, 30, 0.6);
        border: 1px solid #333;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00ff00;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        border-left: 5px solid #00bfff;
        transform: translateY(-2px);
    }
    [data-testid="stMetricValue"] {
        color: #00ff00; 
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
    }
    .kirmizi-alarm div[data-testid="metric-container"] {
        border-left: 5px solid #ff4b4b !important;
    }
    .kirmizi-alarm [data-testid="stMetricValue"] {
        color: #ff4b4b !important; 
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. BAŞLIK VE AÇIKLAMA ---
st.title("🛡️ Gerçek Zamanlı Tehdit Analizi")
st.markdown("*CICIDS2017 Veri Seti üzerinden anlık ağ trafiği izleme, anomali tespiti ve olay müdahale simülasyonu.*")
st.markdown("---")

# --- 3. VERİ YÜKLEME VE HAZIRLAMA ---
@st.cache_data
def veri_yukle():
    try:
        # 1. Veriyi Oku (1000 satır ile sınırla)
        df = pd.read_csv("kaggle_verisi.csv", nrows=1000) 
        
        # 2. Sütun Temizliği
        df.columns = df.columns.str.strip()
        
        # 3. İsimlendirme Standardizasyonu
        sozluk = {
            'Destination Port': 'Hedef_Port',
            'Total Fwd Packets': 'Paket_Boyutu',
            'Label': 'Durum',
            'Source IP': 'Kaynak_IP'
        }
        df = df.rename(columns=sozluk)
        
        # 4. Eksik Sütunları Akıllıca Tamamla
        satir_sayisi = len(df)
        if 'Kaynak_IP' not in df.columns:
            # Gerçekçi sahte IP blokları (Örn: İç ağ ve dış ağ simülasyonu)
            df['Kaynak_IP'] = [f"192.168.{random.randint(1,250)}.{random.randint(1,250)}" for _ in range(satir_sayisi)]
            
        if 'Hedef_Port' not in df.columns:
            # Sık kullanılan portları ağırlıklı olarak seç
            portlar = [80, 443, 22, 21, 3389, 53, 8080]
            df['Hedef_Port'] = [random.choice(portlar) for _ in range(satir_sayisi)]
            
        if 'Paket_Boyutu' not in df.columns:
            df['Paket_Boyutu'] = np.random.poisson(lam=500, size=satir_sayisi) # Gerçekçi paket boyutu dağılımı
            
        if 'Durum' not in df.columns:
            df['Durum'] = 'Normal'
            
        # 5. Durum Sütunu Temizliği ve Standardizasyonu
        df['Durum'] = df['Durum'].astype(str).str.strip()
        df['Durum'] = df['Durum'].replace({'BENIGN': 'Normal', 'normal': 'Normal'})
        
        # 6. Harita ve Zaman Simülasyonu (Zenginleştirme)
        np.random.seed(42)
        df['lat'] = np.random.uniform(36.0, 42.0, size=satir_sayisi) # Türkiye enlemleri
        df['lon'] = np.random.uniform(26.0, 45.0, size=satir_sayisi) # Türkiye boylamları
        
        # Simüle edilmiş canlı zaman damgası (Geçmişten şu ana doğru)
        baslangic_zamani = datetime.now() - timedelta(minutes=satir_sayisi)
        df['Zaman_Damgasi'] = [baslangic_zamani + timedelta(minutes=i) for i in range(satir_sayisi)]
        
        return df
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"Beklenmeyen bir hata oluştu: {e}")
        return None

tam_veri = veri_yukle()

if tam_veri is None:
    st.error("⚠️ HATA: 'kaggle_verisi.csv' bulunamadı veya okunamadı! Lütfen dosyanın dizinde olduğundan emin olun.")
    st.info("İpucu: Test etmek için kodun bulunduğu klasöre içi veri dolu bir 'kaggle_verisi.csv' oluşturun.")
    st.stop()

# --- 4. SİDEBAR (KONTROL PANELİ) ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/cyber-security.png", width=80)
    st.header("⚙️ Sistem Parametreleri")
    
    sim_hizi = st.slider("Ağ Akış Hızı (Sn/Paket)", min_value=0.01, max_value=2.0, value=0.1, step=0.05)
    
    if st.button("🔄 Sistemi ve Logları Sıfırla", use_container_width=True):
        st.session_state.gosterilen_satir = 1
        st.rerun()

    rapor_alani = st.empty()

# Session State Yönetimi
if "gosterilen_satir" not in st.session_state:
    st.session_state.gosterilen_satir = 1

# --- 5. EKRAN YERLEŞİM BÖLÜMLERİ ---
metrik_alani = st.empty()
harita_ve_grafik = st.empty()
tablo_alani = st.empty()

# --- 6. CANLI AKIŞ DÖNGÜSÜ ---
while st.session_state.gosterilen_satir <= len(tam_veri):
    # Veriyi anlık duruma göre filtrele
    anlik_df = tam_veri.head(st.session_state.gosterilen_satir)
    anomali_df = anlik_df[anlik_df["Durum"] != "Normal"]
    
    son_satir = anlik_df.iloc[-1]
    son_durum = son_satir["Durum"]
    
    toplam_paket = len(anlik_df)
    toplam_anomali = len(anomali_df)
    anomali_orani = (toplam_anomali / toplam_paket) * 100 if toplam_paket > 0 else 0

    # 1. CANLI METRİKLER PANELİ
    with metrik_alani.container():
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("İncelenen Trafik", f"{toplam_paket} Paket", f"Son: {son_satir['Zaman_Damgasi'].strftime('%H:%M:%S')}")
        col2.metric("Tespit Edilen Anomali", f"{toplam_anomali}", f"%{anomali_orani:.1f} Tehdit Oranı", delta_color="inverse")
        col3.metric("Son Kaynak IP", f"{son_satir['Kaynak_IP']}", f"Port: {son_satir['Hedef_Port']}")
        
        if son_durum != "Normal":
            # Kırmızı alarm CSS sınıfını entegre etmek için markdown hilesi
            st.markdown('<div class="kirmizi-alarm"></div>', unsafe_allow_html=True)
            col4.metric("🚨 SİSTEM DURUMU", f"{son_durum}", delta="Kritik Alarm - Müdahale Gerekiyor", delta_color="inverse")
        else:
            col4.metric("🛡️ SİSTEM DURUMU", "Temiz Trafik", delta="Bağlantı Güvenli", delta_color="normal")

    # 2. HARİTA VE GRAFİK BÖLÜMÜ
    with harita_ve_grafik.container():
        col_map, col_chart = st.columns([1, 1.5]) # Grafik kısmına biraz daha fazla alan verelim
        
        with col_map:
            st.subheader("🌍 Aktif Tehdit Vektörleri (Harita)")
            if not anomali_df.empty:
                st.map(anomali_df, latitude='lat', longitude='lon', color="#ff0000", zoom=4, size=8000)
            else:
                st.success("Haritada tespit edilen aktif bir anomali bulunmamaktadır.")
                
        with col_chart:
            st.subheader("📈 Ağ Yoğunluğu Monitörü (Son 100 Paket)")
            # Son 100 paketin boyutunu gösteren çizgi grafik
            grafik_verisi = anlik_df.tail(100).set_index("Zaman_Damgasi")["Paket_Boyutu"]
            st.line_chart(grafik_verisi, color="#00ff00")

    # 3. GÜVENLİK DUVARI LOGLARI
    def satir_renklendir(val):
        """Duruma göre satır renklerini belirler."""
        if val != "Normal":
            return 'background-color: rgba(255, 75, 75, 0.3); color: #ff4b4b; font-weight: bold;'
        return 'color: #00ff00;'

    with tablo_alani.container():
        st.subheader("📋 Güvenlik Duvarı Canlı Logları")
        # En yeni loglar en üstte görünsün
        ters_df = anlik_df.tail(12).iloc[::-1] 
        gosterilecek_df = ters_df[["Zaman_Damgasi", "Kaynak_IP", "Hedef_Port", "Paket_Boyutu", "Durum"]]
        
        # Tarih formatını sadece saat/dakika/saniye olarak kısaltalım
        gosterilecek_df["Zaman_Damgasi"] = gosterilecek_df["Zaman_Damgasi"].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        styled_df = gosterilecek_df.style.map(satir_renklendir, subset=['Durum'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # 4. TEHDİT RAPORU İNDİRME (Sadece anomali varsa çalışır)
    if not anomali_df.empty:
        # İndirilecek veriyi hazırla
        rapor_df = anomali_df[["Zaman_Damgasi", "Kaynak_IP", "Hedef_Port", "Paket_Boyutu", "Durum", "lat", "lon"]]
        csv_veri = rapor_df.to_csv(index=False).encode('utf-8')
        
        with rapor_alani.container():
            st.download_button(
                label="📥 Kötü Amaçlı IP Raporunu İndir",
                data=csv_veri,
                file_name=f'SOC_Anomali_Raporu_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                mime='text/csv',
                use_container_width=True
            )

    # Döngü İlerlemesi ve Simülasyon Hızı
    st.session_state.gosterilen_satir += 1
    time.sleep(sim_hizi)

# Tüm veri bittiğinde gösterilecek mesaj
st.success("✅ Veri setindeki tüm paketler analiz edildi. Simülasyon başarıyla tamamlandı.")
st.balloons()