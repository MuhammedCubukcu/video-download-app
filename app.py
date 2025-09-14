import streamlit as st
import yt_dlp
import os
import re
import requests
import time

def validate_url(url):
    """Validate if URL is from supported platforms"""
    supported_patterns = [
        r'(https?://)?(www\.)?(instagram\.com|instagr\.am)/.+',  # Instagram (includes reels with params)
        r'(https?://)?(www\.)?(tiktok\.com|vm\.tiktok\.com|vt\.tiktok\.com).*',  # TikTok
        r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+',  # YouTube
        r'(https?://)?(www\.)?(twitter\.com|x\.com)/.+',  # Twitter/X
        r'(https?://)?(www\.)?(facebook\.com|fb\.watch)/.+',  # Facebook
        r'(https?://)?(www\.)?(reddit\.com)/.+',  # Reddit
        r'(https?://)?(www\.)?(twitch\.tv)/.+',  # Twitch
    ]
    
    # Clean URL for validation (remove parameters)
    clean_url = url.split('?')[0] if '?' in url else url
    
    for pattern in supported_patterns:
        if re.match(pattern, clean_url, re.IGNORECASE):
            return True
    return False

def sanitize_url(url):
    """Clean and prepare URL for processing"""
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Clean Instagram URLs - remove tracking parameters but keep essential parts
    if 'instagram.com' in url:
        # Remove tracking parameters like ?igsh= but preserve the core URL structure
        if '?' in url:
            base_url = url.split('?')[0]
            # Keep the URL as is, just remove tracking params
            url = base_url
        
        # Don't force trailing slash as it might break some URLs
        # Instagram URLs work fine without it
    
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
    
    # Check if it's Instagram and try different approaches
    is_instagram = 'instagram.com' in url.lower()
    
    if is_instagram:
        # Instagram-specific configuration with multiple strategies
        ydl_opts = {
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'format': 'best[ext=mp4]/best',
            'restrictfilenames': True,
            'no_warnings': False,
            'ignoreerrors': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 11; SM-A515F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36 Instagram 239.0.0.10.109 Android (30/11; 420dpi; 1080x2220; samsung; SM-A515F; a51; exynos9611; en_US; 380204311)',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'X-Requested-With': 'XMLHttpRequest',
                'X-Instagram-AJAX': '1',
                'X-CSRFToken': 'missing',
                'Referer': 'https://www.instagram.com/',
                'Origin': 'https://www.instagram.com',
            },
            'extractor_args': {
                'instagram': {
                    'api_version': 'v1',
                }
            },
            'retries': 5,
            'fragment_retries': 5,
            'sleep_interval': 1,
            'max_sleep_interval': 3,
        }
    else:
        # General configuration for other platforms
        ydl_opts = {
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'format': 'mp4[height<=720]/mp4/best[height<=720]/best',
            'restrictfilenames': True,
            'no_warnings': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            },
        }
    
    try:
        # Show loading message
        with st.spinner('Video indiriliyor... Lütfen bekleyin.'):
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # For Instagram, try multiple approaches with enhanced strategies
                if is_instagram:
                    success = False
                    last_error = None
                    
                    # Strategy 1: Mobile Instagram app simulation
                    try:
                        time.sleep(1)  # Rate limiting
                        info = ydl.extract_info(url, download=False)
                        video_title = info.get('title', 'Instagram Video')
                        ydl.download([url])
                        success = True
                    except Exception as e1:
                        last_error = e1
                        st.info("Mobil uygulama simülasyonu başarısız, web tarayıcı simülasyonu deneniyor...")
                    
                    # Strategy 2: Web browser simulation with different headers
                    if not success:
                        try:
                            ydl_opts_web = {
                                'outtmpl': f'{output_path}/%(title)s.%(ext)s',
                                'format': 'best[ext=mp4]/best',
                                'restrictfilenames': True,
                                'http_headers': {
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                                    'Accept-Language': 'en-US,en;q=0.9,tr;q=0.8',
                                    'Accept-Encoding': 'gzip, deflate, br',
                                    'Connection': 'keep-alive',
                                    'Upgrade-Insecure-Requests': '1',
                                    'Sec-Fetch-Dest': 'document',
                                    'Sec-Fetch-Mode': 'navigate',
                                    'Sec-Fetch-Site': 'none',
                                    'Sec-Fetch-User': '?1',
                                    'Cache-Control': 'max-age=0',
                                },
                                'retries': 3,
                                'sleep_interval': 2,
                            }
                            
                            with yt_dlp.YoutubeDL(ydl_opts_web) as ydl2:
                                time.sleep(2)  # Additional delay
                                info = ydl2.extract_info(url, download=False)
                                video_title = info.get('title', 'Instagram Video')
                                ydl2.download([url])
                                success = True
                        except Exception as e2:
                            last_error = e2
                            st.info("Web tarayıcı simülasyonu başarısız, alternatif extractor deneniyor...")
                    
                    # Strategy 3: Try with gallery-dl approach (generic extractor)
                    if not success:
                        try:
                            ydl_opts_generic = {
                                'outtmpl': f'{output_path}/instagram_%(id)s.%(ext)s',
                                'format': 'best',
                                'restrictfilenames': True,
                                'force_generic_extractor': True,
                                'http_headers': {
                                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                                    'Accept': '*/*',
                                    'Accept-Language': 'en-US,en;q=0.5',
                                    'Accept-Encoding': 'gzip, deflate',
                                    'Connection': 'keep-alive',
                                },
                                'extractor_args': {
                                    'generic': {
                                        'default_search': 'auto',
                                    }
                                }
                            }
                            
                            with yt_dlp.YoutubeDL(ydl_opts_generic) as ydl3:
                                time.sleep(3)  # Longer delay for generic extractor
                                info = ydl3.extract_info(url, download=False)
                                video_title = info.get('title', 'Instagram Video')
                                ydl3.download([url])
                                success = True
                        except Exception as e3:
                            last_error = e3
                    
                    # Strategy 4: Last resort - try with minimal options
                    if not success:
                        try:
                            ydl_opts_minimal = {
                                'outtmpl': f'{output_path}/instagram_video.%(ext)s',
                                'format': 'worst',  # Try worst quality as last resort
                                'no_warnings': True,
                                'ignoreerrors': True,
                                'http_headers': {
                                    'User-Agent': 'curl/7.68.0',
                                },
                            }
                            
                            with yt_dlp.YoutubeDL(ydl_opts_minimal) as ydl4:
                                info = ydl4.extract_info(url, download=False)
                                video_title = info.get('title', 'Instagram Video')
                                ydl4.download([url])
                                success = True
                        except Exception as e4:
                            last_error = e4
                    
                    if not success:
                        error_msg = str(last_error)
                        if "private" in error_msg.lower():
                            st.error("❌ Bu Instagram videosu özel (private) hesapta olduğu için indirilemez.")
                        elif "login" in error_msg.lower() or "authentication" in error_msg.lower():
                            st.error("❌ Bu Instagram videosu giriş gerektiriyor veya hesap korumalı.")
                            st.info("💡 Alternatif: Video linkini başka bir Instagram downloader sitesinde deneyin.")
                        elif "not found" in error_msg.lower() or "404" in error_msg:
                            st.error("❌ Video bulunamadı. Link doğru mu kontrol edin.")
                        elif "rate limit" in error_msg.lower() or "too many requests" in error_msg.lower():
                            st.error("❌ Instagram rate limit. Birkaç dakika bekleyip tekrar deneyin.")
                        else:
                            st.error(f"❌ Instagram video indirilemedi. Instagram'ın güvenlik önlemleri nedeniyle bazı videolar indirilemeyebilir.")
                            st.info("💡 Alternatif çözümler: Video sahibinden direkt paylaşım isteyin veya ekran kaydı alın.")
                        raise last_error
                else:
                    # Standard approach for other platforms
                    info = ydl.extract_info(url, download=False)
                    video_title = info.get('title', 'Unknown')
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
    url = st.text_input("Video URL'sini buraya yapıştırın:", placeholder="Instagram, TikTok (mobil linkler de desteklenir), YouTube, Twitter, Facebook...")
    
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