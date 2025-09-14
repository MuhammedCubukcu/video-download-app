# Design Document

## Overview

The video downloader application is a web-based tool built with Python using Streamlit for the user interface and yt-dlp for video extraction and downloading. The application provides a simple, single-page interface where users can input video URLs from Instagram and TikTok, download the videos, preview them, and save them to their local device.

## Architecture

The application follows a simple monolithic architecture with a single Python file containing all functionality:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│  Streamlit App   │◄──►│    yt-dlp       │
│   (Frontend)    │    │   (Backend)      │    │   (Extractor)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Local File      │
                       │ System          │
                       │ (downloads/)    │
                       └─────────────────┘
```

### Technology Stack
- **Python 3.9+**: Core runtime environment
- **Streamlit**: Web framework for creating the user interface
- **yt-dlp**: Video extraction and downloading library
- **OS module**: File system operations

## Components and Interfaces

### 1. User Interface Component
**Responsibility**: Handle user interactions and display feedback

**Key Elements**:
- Title display: "📥 Instagram & TikTok Video İndirici"
- URL input field for video links
- Download button to trigger the process
- Success/warning/error message display
- Video preview component
- Download button for local file saving

**Streamlit Components Used**:
- `st.title()` - Application header
- `st.text_input()` - URL input field
- `st.button()` - Action triggers
- `st.success()`, `st.warning()` - User feedback
- `st.video()` - Video preview
- `st.download_button()` - File download

### 2. Video Processing Component
**Responsibility**: Extract and download videos using yt-dlp

**Key Functions**:
- URL validation and processing
- Video metadata extraction
- File downloading with proper naming
- Error handling for unsupported URLs or network issues

**Configuration**:
```python
ydl_opts = {
    'outtmpl': f'{output_path}/%(title)s.%(ext)s'
}
```

### 3. File Management Component
**Responsibility**: Handle local file operations

**Key Functions**:
- Create downloads directory if it doesn't exist
- Manage downloaded file paths
- Provide file data for browser downloads
- Handle file naming and extensions

## Data Models

### Video Information Model
```python
# Extracted from yt-dlp info dictionary
{
    'title': str,           # Video title
    'ext': str,             # File extension
    'url': str,             # Original video URL
    'filename': str,        # Generated filename
    'filepath': str         # Full local file path
}
```

### Application State Model
```python
# Streamlit session state (implicit)
{
    'url_input': str,       # Current URL in input field
    'download_status': str, # Current operation status
    'current_file': str     # Path to currently processed file
}
```

## Error Handling

### Input Validation
- **Empty URL**: Display warning "⚠ Lütfen geçerli bir link gir."
- **Invalid URL format**: yt-dlp will handle and raise appropriate exceptions
- **Unsupported platforms**: yt-dlp error handling will catch and report

### Download Process Errors
- **Network connectivity issues**: Catch yt-dlp exceptions and display user-friendly messages
- **Video unavailable**: Handle private/deleted video scenarios
- **File system errors**: Handle permission issues or disk space problems

### Error Display Strategy
```python
try:
    # Video download process
    pass
except Exception as e:
    st.error(f"❌ Video indirilemedi: {str(e)}")
```

## Testing Strategy

### Unit Testing Approach
1. **URL Validation Tests**
   - Test valid Instagram URLs
   - Test valid TikTok URLs
   - Test invalid URL formats
   - Test empty input handling

2. **File Operations Tests**
   - Test directory creation
   - Test file naming conventions
   - Test file download functionality
   - Test file cleanup scenarios

3. **Integration Tests**
   - Test complete download workflow
   - Test video preview functionality
   - Test browser download feature
   - Test error scenarios end-to-end

### Manual Testing Scenarios
1. **Happy Path Testing**
   - Download public Instagram video
   - Download public TikTok video
   - Preview downloaded video
   - Download file to local device

2. **Edge Case Testing**
   - Private videos
   - Deleted videos
   - Very long video titles
   - Special characters in titles
   - Large video files

### Performance Considerations
- **Download Progress**: Consider adding progress indicators for large files
- **Concurrent Downloads**: Current design handles one download at a time
- **File Cleanup**: Consider implementing automatic cleanup of old downloads
- **Memory Usage**: Large videos are streamed, not loaded entirely into memory

## Security Considerations

### Input Sanitization
- yt-dlp handles URL validation and sanitization
- File naming uses yt-dlp's built-in sanitization
- No direct file path manipulation from user input

### File System Security
- Downloads are restricted to the designated `downloads/` directory
- No arbitrary file system access
- File extensions are controlled by yt-dlp

### Network Security
- All network requests handled by yt-dlp
- No direct HTTP requests from application code
- Relies on yt-dlp's security measures for external API calls

## Deployment Considerations

### Local Development
```bash
pip install streamlit yt-dlp
streamlit run app.py
```

### Production Deployment
- Consider containerization with Docker
- Ensure sufficient disk space for downloads
- Configure appropriate file cleanup policies
- Consider rate limiting for heavy usage scenarios