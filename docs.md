
📑 Dökümantasyon

Proje: Instagram & TikTok Video İndirici & Meta Ads library video indirici

1. Amaç

Bu proje, kullanıcıların Instagram ve TikTok videolarını link vererek indirmesine olanak sağlayan basit bir web uygulamasıdır.
Python’un Streamlit kütüphanesi ile arayüz geliştirilmiş, yt-dlp kütüphanesi ile video indirme işlemleri yapılmaktadır.


---

2. Kullanılan Teknolojiler

Python 3.9+

Streamlit → Web arayüzü için

yt-dlp → Video indirme işlemleri için



---

3. Kurulum Adımları

3.1. Gerekli kütüphanelerin kurulumu

pip install streamlit yt-dlp

3.2. Proje klasör yapısı

video_downloader/
│
├── app.py          # Ana uygulama
├── requirements.txt # Deploy için kütüphane listesi
└── downloads/       # Videoların kaydedileceği klasör

requirements.txt içeriği:

streamlit
yt-dlp


---

4. Kod Açıklaması (app.py)

import streamlit as st
import yt_dlp
import os

# Başlık
st.title("📥 Instagram & TikTok Video İndirici")

# Kullanıcıdan link al
url = st.text_input("Video linkini yapıştır:")

if st.button("Videoyu İndir"):
    if url:
        # Videolar için klasör oluştur
        output_path = "downloads"
        os.makedirs(output_path, exist_ok=True)

        # İndirme ayarları
        ydl_opts = {
            'outtmpl': f'{output_path}/%(title)s.%(ext)s'
        }

        # Video indirme işlemi
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # Kullanıcıya çıktı ver
        st.success("✅ Video başarıyla indirildi!")
        st.video(file_path)  # Streamlit içinde video oynat
        with open(file_path, "rb") as f:
            st.download_button(
                label="💾 Bilgisayara indir",
                data=f,
                file_name=os.path.basename(file_path),
                mime="video/mp4"
            )
    else:
        st.warning("⚠ Lütfen geçerli bir link gir.")


---

5. Çalıştırma

streamlit run app.py

Tarayıcıda otomatik olarak http://localhost:8501 açılır.


---

6. Kullanım

1. Tarayıcıdan uygulamayı aç.


2. Instagram veya TikTok video linkini kutuya yapıştır.


3. "Videoyu İndir" butonuna bas.


4. Video indirilir, önizlemesi gösterilir ve “Bilgisayara indir” butonu ile cihazına kaydedebilirsin.





