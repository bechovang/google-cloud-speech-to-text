import os
import time
from google.cloud import storage, speech
from google.oauth2 import service_account

# === Tự động thiết lập xác thực từ file JSON (file nằm cùng thư mục với main.py) ===
def set_google_credentials():
    # Lấy đường dẫn tuyệt đối tới file JSON credentials (nằm cùng thư mục với main.py)
    json_credentials_path = os.path.join(os.path.dirname(__file__), "speech-stt-sa.json")
    
    # Kiểm tra xem file JSON có tồn tại không
    if not os.path.exists(json_credentials_path):
        raise FileNotFoundError(f"Không tìm thấy file JSON credentials tại {json_credentials_path}. Vui lòng kiểm tra lại file credentials.")

    # Tự động thiết lập các thông tin xác thực cho Google Cloud
    credentials = service_account.Credentials.from_service_account_file(
        json_credentials_path
    )
    return credentials

# === Tìm file âm thanh có tên chứa "audio" ===
def find_audio_file():
    """Tìm file âm thanh có tên chứa 'audio' trong thư mục hiện tại"""
    supported_extensions = ['.mp3', '.wav', '.flac', '.ogg', '.amr', '.awb']
    
    # Tìm tất cả file trong thư mục hiện tại
    for file in os.listdir('.'):
        if os.path.isfile(file):
            # Kiểm tra xem tên file có chứa "audio" và có định dạng âm thanh được hỗ trợ
            if 'audio' in file.lower() and any(file.lower().endswith(ext) for ext in supported_extensions):
                return file
    
    return None

# === Kiểm tra kích thước file ===
def get_file_size_mb(file_path):
    """Lấy kích thước file theo MB"""
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / (1024 * 1024)
    return size_mb

# === Xác định loại file âm thanh ===
def get_audio_encoding(file_name):
    _, ext = os.path.splitext(file_name)
    encodings = {
        ".mp3": speech.RecognitionConfig.AudioEncoding.MP3,
        ".wav": speech.RecognitionConfig.AudioEncoding.LINEAR16,
        ".flac": speech.RecognitionConfig.AudioEncoding.FLAC,
        ".ogg": speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        ".amr": speech.RecognitionConfig.AudioEncoding.AMR,
        ".awb": speech.RecognitionConfig.AudioEncoding.AMR_WB,
    }
    if ext.lower() not in encodings:
        raise ValueError(f"Định dạng file '{ext}' chưa được hỗ trợ.")
    return encodings[ext.lower()]


# === Upload file âm thanh lên GCS ===
def upload_to_gcs(credentials, bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} đã được upload lên GCS.")
    return f"gs://{bucket_name}/{destination_blob_name}"


# === Xóa file trên GCS ===
def delete_from_gcs(credentials, bucket_name, blob_name):
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.delete()

    print(f"File {blob_name} đã được xóa khỏi bucket {bucket_name}.")


# === Nhận diện giọng nói từ URI GCS ===
def transcribe_gcs(credentials, gcs_uri, language_code="vi-VN"):
    client = speech.SpeechClient(credentials=credentials)

    # Lấy tên file từ gcs_uri và xác định encoding
    file_name = os.path.basename(gcs_uri)
    encoding = get_audio_encoding(file_name)

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=encoding,
        language_code=language_code,
        enable_automatic_punctuation=True,
        enable_word_time_offsets=True  # Bật để lấy thời gian từng từ cho .srt
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    print("Đang xử lý... Vui lòng đợi.")
    
    try:
        # Tăng timeout lên 10 phút cho file lớn
        response = operation.result(timeout=600)
    except Exception as e:
        print(f"🔴 Lỗi trong quá trình nhận diện: {e}")
        print("💡 Gợi ý: File âm thanh có thể quá lớn hoặc định dạng không tương thích")
        raise e

    full_transcript = ""
    srt_lines = []
    line_index = 1

    for result in response.results:
        alternative = result.alternatives[0]
        full_transcript += alternative.transcript + "\n"

        words = alternative.words
        for word_info in words:
            start_sec = word_info.start_time.total_seconds()
            end_sec = word_info.end_time.total_seconds()
            text = word_info.word

            srt_lines.append(f"{line_index}")
            srt_lines.append(f"{to_srt_time(start_sec)} --> {to_srt_time(end_sec)}")
            srt_lines.append(text)
            srt_lines.append("")
            line_index += 1

    return full_transcript, srt_lines


# === Chuyển đổi giây sang định dạng SRT ===
def to_srt_time(seconds):
    millisec = int((seconds % 1) * 1000)
    seconds = int(seconds)
    mins = seconds // 60
    secs = seconds % 60
    hrs = mins // 60
    mins = mins % 60
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millisec:03d}"


# === Lưu nội dung thành file TXT ===
def save_txt(text, output_file="recognized_text.txt"):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"📄 Kết quả nhận diện đã được lưu vào: {output_file}")


# === Lưu nội dung thành file SRT ===
def save_srt(srt_lines, output_file="recognized_subtitles.srt"):
    with open(output_file, "w", encoding="utf-8") as f:
        for line in srt_lines:
            f.write(line + "\n")
    print(f"📝 Phụ đề đã được lưu vào: {output_file}")


# === CHỌN NGÔN NGỮ ===
def select_language():
    """Cho phép người dùng chọn ngôn ngữ"""
    print("\n🌐 CHỌN NGÔN NGỮ:")
    print("0 - Tiếng Việt (vi-VN)")
    print("1 - Tiếng Anh (en-US)")
    
    while True:
        try:
            choice = input("Nhập lựa chọn (0 hoặc 1): ").strip()
            if choice == "0":
                return "vi-VN", "Tiếng Việt"
            elif choice == "1":
                return "en-US", "Tiếng Anh"
            else:
                print("❌ Lựa chọn không hợp lệ. Vui lòng nhập 0 hoặc 1.")
        except KeyboardInterrupt:
            print("\n👋 Tạm biệt!")
            exit(0)

# === CHẠY TOÀN BỘ ===
if __name__ == "__main__":
    # Thêm: Đo thời gian bắt đầu
    start_time = time.time()

    # Thông tin dự án và bucket
    PROJECT_ID = "speach-to-text-462517"
    BUCKET_NAME = "bechovang-speach-to-text"
    
    # Tìm file âm thanh có tên chứa "audio"
    LOCAL_AUDIO_FILE = find_audio_file()
    
    # Chọn ngôn ngữ
    language_code, language_name = select_language()
    print(f"✅ Đã chọn: {language_name}")

    # Thiết lập xác thực từ file JSON (file nằm cùng thư mục với main.py)
    try:
        credentials = set_google_credentials()
    except FileNotFoundError as e:
        print(f"🔴 Lỗi: {e}")
        exit(1)

    # Kiểm tra file âm thanh tồn tại
    if not LOCAL_AUDIO_FILE:
        print(f"Lỗi: Không tìm thấy file âm thanh có tên chứa 'audio' trong thư mục hiện tại")
        print("Các định dạng được hỗ trợ: .mp3, .wav, .flac, .ogg, .amr, .awb")
        exit(1)
    else:
        # Kiểm tra kích thước file
        file_size_mb = get_file_size_mb(LOCAL_AUDIO_FILE)
        print(f"Đang bắt đầu xử lý file âm thanh: {LOCAL_AUDIO_FILE}")
        print(f"📁 Kích thước file: {file_size_mb:.2f} MB")
        
        if file_size_mb > 10:
            print("⚠️ Cảnh báo: File âm thanh khá lớn, có thể mất nhiều thời gian xử lý")
            print("💡 Gợi ý: Nếu gặp timeout, hãy thử với file nhỏ hơn (< 5MB)")
        
        # Tạo tên file cho GCS
        GCS_BLOB_NAME = "uploaded_audio" + os.path.splitext(LOCAL_AUDIO_FILE)[1]

        try:
            # Bước 1: Upload lên GCS
            gcs_uri = upload_to_gcs(credentials, BUCKET_NAME, LOCAL_AUDIO_FILE, GCS_BLOB_NAME)

            # Bước 2: Nhận diện giọng nói
            print(f"Đang gửi yêu cầu nhận diện giọng nói ({language_name})...")
            transcript, srt_lines = transcribe_gcs(credentials, gcs_uri, language_code=language_code)

            # Bước 3: Lưu kết quả
            save_txt(transcript, f"recognized_text_{language_code}.txt")
            save_srt(srt_lines, f"recognized_subtitles_{language_code}.srt")
            
            print(f"✅ Hoàn tất toàn bộ quá trình!")
            
        except Exception as e:
            print(f"🔴 Lỗi trong quá trình xử lý: {e}")
            print("💡 Vui lòng kiểm tra lại file âm thanh và thử lại")
        finally:
            # Bước 4: Luôn xóa file trên GCS sau khi hoàn tất
            try:
                delete_from_gcs(credentials, BUCKET_NAME, GCS_BLOB_NAME)
            except Exception as e:
                print(f"⚠️ Không thể xóa file trên GCS: {e}")

            # Tính và in thời gian xử lý
            end_time = time.time()
            elapsed_time = end_time - start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)

            print(f"⏱️ Tổng thời gian xử lý: {minutes} phút {seconds} giây")
