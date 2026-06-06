# 🛡️ Gerçek Zamanlı IDS ve Ağ Analiz Paneli

Bu proje, Kaggle **CICIDS2017** veri seti üzerinden ağ trafiğini gerçek zamanlı olarak izleyen, anomali tespiti yapan ve tehditleri görselleştiren interaktif bir Güvenlik Operasyon Merkezi (SOC) panelidir. Python ve Streamlit kullanılarak geliştirilmiştir.

## ✨ Özellikler
* **Canlı Simülasyon:** Veri seti üzerinden anlık ağ trafiği simülasyonu.
* **Tehdit Tespiti:** Anormal paket boyutları ve kötü amaçlı IP'lerin anında filtrelenmesi.
* **Görselleştirme:** Canlı tehdit haritası ve ağ yoğunluk metrikleri.
* **Log ve Raporlama:** Tespit edilen tehditlerin anında `.csv` formatında dışa aktarılması.

## 🛠️ Kullanılan Teknolojiler
* **Python 3.8+**
* **Streamlit** (Kullanıcı Arayüzü ve Canlı Akış)
* **Pandas & NumPy** (Veri Analizi ve Zenginleştirme)

## ⚙️ Kurulum ve Çalıştırma

Projeyi yerel bilgisayarınızda çalıştırmak için aşağıdaki adımları sırasıyla izleyin:

### 1. Projeyi bilgisayarınıza klonlayın

### 2. Bağımlılıkları kurun

Projenin ihtiyaç duyduğu kütüphaneleri yüklemek için terminal (komut satırı) üzerinden aşağıdaki komutu çalıştırın:

```bash
pip install -r requirements.txt
```

### 3. Uygulamayı çalıştırın

Tüm kurulumlar tamamlandıktan sonra aynı terminal ekranında simülasyonu başlatmak için:

```bash
streamlit run app.py
```

> **Not:** Komutu girdikten sonra tarayıcınız otomatik olarak `http://localhost:8501` adresinde açılacaktır.
