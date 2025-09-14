import streamlit as st
import yt_dlp
import os
import re

def validate_url(url):
    """Validate if URL is from supported platforms"""
    supported_patterns = [
        r'(https?://)?(www\.)?(instagram\.com|instagr\.am)/.+',  # Instagram
        r'(https?://)?(www\.)?(tiktok\.com|vm\.tiktok\.com)/.+',  # TikTok
        r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+',  # YouTube
        r'(https?://)?(www\.)?(twitter\.com|x\.com)/.+',  # Twitter/X
        r'(https?://)?(www\.)?(facebook\.com|fb\.watch)/.+',  # Facebook
        r'(https?://)?(www\.)?(reddit\.com)/.+',  # Reddit
        r'(https?://)?(www\.)?(twitch\.tv)/.+',  # Twitch
    ]
    
    for pattern in supported_patterns:
        if re.match(pattern, url, re.IGNORECASE):
            return True
    return False

def sanitize_url(url):
    """Clean and prepare URL for processing"""
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

def ensure_downloads_dir():
    """Ensure downloads directory exists"""
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

def get_safe_filename(filename):
    """Generate safe filename avoiding duplicates"""
    if os.path.exists(filename):
        name, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(f"{name}_{counter}{ext}"):
            counter += 1
        return f"{name}_{counter}{ext}"
    return filename

def download_video(url):
    """Download video using yt-dlp"""
    output_path = "downloads"
    ensure_downloads_dir()
    
    # Simplified yt-dlp configuration - just download MP4
    ydl_opts = {
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'format': 'mp4[height<=720]/mp4/best[height<=720]/best',  # Prefer MP4 format
        'restrictfilenames': True,  # Use safe filenames
        'no_warnings': False,  # Show warnings for debugging
    }
    
    try:
        # Show loading message
        with st.spinner('Video indiriliyor... Lütfen bekleyin.'):
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract video info
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Unknown')
                
                # Download the video
                ydl.download([url])
                
                # Get the downloaded file path
                filename = ydl.prepare_filename(info)
                
                # Check if file actually exists
                if not os.path.exists(filename):
                    # Try with .mp4 extension
                    base_name = os.path.splitext(filename)[0]
                    mp4_filename = f"{base_name}.mp4"
                    if os.path.exists(mp4_filename):
                        filename = mp4_filename
                
                if os.path.exists(filename):
                    st.success(f"✅ Video başarıyla indirildi: {video_title}")
                    
                    # Store info in session state for preview and download
                    st.session_state.downloaded_file = filename
                    st.session_state.video_title = video_title
                else:
                    st.error(f"❌ Dosya bulunamadı: {filename}")
                    # List files in downloads directory for debugging
                    files = os.listdir(output_path)
                    st.write("Downloads klasöründeki dosyalar:", files)
                
    except yt_dlp.utils.DownloadError as e:
        if "Private video" in str(e) or "private" in str(e).lower():
            st.error("❌ Bu video özel (private) olduğu için indirilemez.")
        elif "not available" in str(e).lower():
            st.error("❌ Video bulunamadı veya artık mevcut değil.")
        else:
            st.error(f"❌ Video indirme hatası: {str(e)}")
    except yt_dlp.utils.UnsupportedError as e:
        st.error("❌ Bu platform desteklenmiyor. Lütfen Instagram veya TikTok linki kullanın.")
    except Exception as e:
        if "network" in str(e).lower() or "connection" in str(e).lower():
            st.error("❌ İnternet bağlantısı sorunu. Lütfen bağlantınızı kontrol edin.")
        else:
            st.error(f"❌ Beklenmeyen hata: {str(e)}")

def main():
    # Page configuration
    st.set_page_config(
        page_title="Video İndirici",
        page_icon="📥",
        layout="centered"
    )
    
    st.title("📥 Sosyal Medya Video İndirici")
    st.caption("Instagram, TikTok, YouTube, Twitter, Facebook ve daha fazlası...")
    
    # Ensure downloads directory exists
    ensure_downloads_dir()
    
    # URL input interface
    url = st.text_input("Video URL'sini buraya yapıştırın:", placeholder="Instagram, TikTok, YouTube, Twitter, Facebook linkini yapıştırın...")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        download_button = st.button("📥 Video İndir", type="primary")
    with col2:
        if st.button("🗑️ Temizle"):
            if hasattr(st.session_state, 'downloaded_file'):
                del st.session_state.downloaded_file
            if hasattr(st.session_state, 'video_title'):
                del st.session_state.video_title
            st.rerun()
    
    # Input validation
    if download_button and not url.strip():
        st.warning("⚠ Lütfen geçerli bir link gir.")
    elif download_button and url.strip():
        cleaned_url = sanitize_url(url)
        if validate_url(cleaned_url):
            download_video(cleaned_url)
        else:
            st.error("❌ Lütfen desteklenen bir platform linkini girin (Instagram, TikTok, YouTube, Twitter, Facebook, Reddit, Twitch).")
    
    # Show video preview if available
    if hasattr(st.session_state, 'downloaded_file') and st.session_state.downloaded_file:
        if os.path.exists(st.session_state.downloaded_file):
            st.subheader("🎬 Video Önizleme")
            st.write(f"**Video:** {st.session_state.video_title}")
            
            # Show file info for debugging
            file_size = os.path.getsize(st.session_state.downloaded_file) / (1024*1024)  # MB
            st.write(f"**Dosya:** {os.path.basename(st.session_state.downloaded_file)} ({file_size:.1f} MB)")
            
            try:
                st.video(st.session_state.downloaded_file)
            except Exception as e:
                st.warning(f"⚠ Video önizleme gösterilemiyor: {str(e)}")
                st.info("💡 Video dosyası indirildi, bilgisayarınıza indirip VLC Player ile açmayı deneyin.")
            
            # Download button for user device
            try:
                with open(st.session_state.downloaded_file, 'rb') as file:
                    file_data = file.read()
                    file_name = os.path.basename(st.session_state.downloaded_file)
                    
                    st.download_button(
                        label="💾 Bilgisayarına İndir",
                        data=file_data,
                        file_name=file_name,
                        mime="video/mp4"
                    )
            except Exception as e:
                st.error(f"❌ Dosya indirme hatası: {str(e)}")
        else:
            st.error("❌ İndirilen dosya bulunamadı.")

if __name__ == "__main__":
    main()