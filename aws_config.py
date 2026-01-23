"""
AWS Polly Configuration
Cấu hình cho AWS Polly Text-to-Speech service
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables từ .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# ========== AWS CREDENTIALS ==========
# ⚠️ CẢNH BÁO: Đây là thông tin nhạy cảm!
# Chỉ dùng trong môi trường phát triển/test
# Không commit lên GitHub/public repository!
# Lấy từ environment variables hoặc .env file

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = "ap-southeast-2"

# ========== POLLY VOICES ==========
# Ánh xạ giữa ngôn ngữ và giọng người đọc

VOICE_MAPPING = {
    # English
    "en": "Joanna",      # Female
    "en-US": "Joanna",   # Female - US
    "en-GB": "Amy",      # Female - British
    "en-AU": "Olivia",   # Female - Australian
    
    # Chinese (Mandarin)
    "zh": "Zhiyu",       # Male - Simplified
    "zh-CN": "Zhiyu",    # Male - Simplified
    "zh-TW": "Mizuki",   # Japanese (fallback for Traditional Chinese)
    
    # Japanese
    "ja": "Mizuki",      # Female
    "ja-JP": "Mizuki",   # Female
    
    # Vietnamese (fallback to gTTS)
    "vi": "none",        # Use gTTS instead
    "vi-VN": "none",     # Use gTTS instead
}

# ========== AUDIO SETTINGS ==========

# Output format
OUTPUT_FORMAT = "mp3"  # "mp3", "ogg_vorbis", "pcm"

# Voice engine
ENGINE = "neural"  # "standard" or "neural" (higher quality)

# Supported sample rates (Hz)
SAMPLE_RATES = {
    "mp3": [8000, 16000, 22050, 24000],
    "ogg_vorbis": [8000, 16000, 22050, 24000],
    "pcm": [8000, 16000],
}

SAMPLE_RATE = 24000  # Default

# ========== TIMEOUT & RETRY ==========

CONNECTION_TIMEOUT = 10  # seconds
READ_TIMEOUT = 30        # seconds
MAX_RETRIES = 2
RETRY_DELAY = 1          # second

# ========== TEST ==========

if __name__ == "__main__":
    print("✅ AWS Polly Configuration Loaded")
    print(f"   Region: {AWS_REGION}")
    print(f"   Engine: {ENGINE}")
    print(f"   Format: {OUTPUT_FORMAT}")
    print(f"   Sample Rate: {SAMPLE_RATE} Hz")
    print()
    print("Supported Languages:")
    for lang, voice in VOICE_MAPPING.items():
        if voice != "none":
            print(f"   {lang}: {voice}")
