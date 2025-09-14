# Instagram & TikTok Video İndirici

Bu uygulama Instagram ve TikTok videolarını indirmenizi sağlayan basit bir web arayüzüdür.

## Kurulum

### Yöntem 1: Requirements dosyası ile
```bash
pip install -r requirements.txt
```

### Yöntem 2: Manuel kurulum (önerilen)
```bash
pip install streamlit
pip install yt-dlp
pip install ffmpeg-python
```

### FFmpeg Kurulumu (Video dönüştürme için gerekli)
Windows için:
1. https://ffmpeg.org/download.html adresinden FFmpeg indirin
2. Zip dosyasını çıkarın ve bin klasörünü PATH'e ekleyin
3. Veya Chocolatey ile: `choco install ffmpeg`

### Yöntem 3: Eğer numpy hatası alıyorsanız
```bash
pip install --upgrade pip
pip install streamlit --no-deps
pip install yt-dlp --no-deps
pip install altair blinker cachetools click importlib-metadata packaging pandas pillow protobuf pyarrow requests rich toml tornado typing-extensions tzlocal validators watchdog
```

## Çalıştırma

```bash
streamlit run app.py
```

Tarayıcınızda `http://localhost:8501` adresine gidin.

## Kullanım

1. Instagram veya TikTok video linkini girin
2. "Video İndir" butonuna tıklayın
3. Video önizlemesini görüntüleyin
4. "Bilgisayarına İndir" butonu ile videoyu kaydedin

## Desteklenen Platformlar

- Instagram
- TikTok
- YouTube
- Twitter/X
- Facebook
- Reddit
- Twitch

## Özellikler

- Video önizleme
- Otomatik dosya adlandırma
- Hata yönetimi
- Türkçe arayüz
- 720p kalite desteği