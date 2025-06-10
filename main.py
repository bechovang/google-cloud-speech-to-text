import os
import time
from google.cloud import storage, speech


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
def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} đã được upload lên GCS.")
    return f"gs://{bucket_name}/{destination_blob_name}"


# === Xóa file trên GCS ===
def delete_from_gcs(bucket_name, blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.delete()

    print(f"File {blob_name} đã được xóa khỏi bucket {bucket_name}.")


# === Nhận diện giọng nói từ URI GCS ===
def transcribe_gcs(gcs_uri, language_code="vi-VN"):
    client = speech.SpeechClient()

    # Tự động xác định encoding dựa trên đuôi file
    encoding = get_audio_encoding(gcs_uri)

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=encoding,
        language_code=language_code,
        enable_automatic_punctuation=True,
        enable_word_time_offsets=True  # Bật để lấy thời gian từng từ cho .srt
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    print("Đang xử lý... Vui lòng đợi.")
    response = operation.result(timeout=300)

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
    print(f"Kết quả nhận diện đã được lưu vào: {output_file}")


# === Lưu nội dung thành file SRT ===
def save_srt(srt_lines, output_file="recognized_subtitles.srt"):
    with open(output_file, "w", encoding="utf-8") as f:
        for line in srt_lines:
            f.write(line + "\n")
    print(f"Phụ đề đã được lưu vào: {output_file}")


# === CHẠY TOÀN BỘ ===
if __name__ == "__main__":
    # Thêm: Đo thời gian bắt đầu
    start_time = time.time()

    # Thông tin dự án và bucket
    PROJECT_ID = "speach-to-text-462517"
    BUCKET_NAME = "bechovang-speach-to-text"
    LOCAL_AUDIO_FILE = "audio.wav"
    GCS_BLOB_NAME = "uploaded_audio" + os.path.splitext(LOCAL_AUDIO_FILE)[1]

    # Kiểm tra file âm thanh tồn tại
    if not os.path.exists(LOCAL_AUDIO_FILE):
        print(f"Lỗi: Không tìm thấy file âm thanh '{LOCAL_AUDIO_FILE}'")
    else:
        print(f"Đang bắt đầu xử lý file âm thanh: {LOCAL_AUDIO_FILE}")

        try:
            # Bước 1: Upload lên GCS
            gcs_uri = upload_to_gcs(BUCKET_NAME, LOCAL_AUDIO_FILE, GCS_BLOB_NAME)

            # Bước 2: Nhận diện giọng nói
            print("Đang gửi yêu cầu nhận diện giọng nói...")
            transcript, srt_lines = transcribe_gcs(gcs_uri, language_code="vi-VN")

            # Bước 3: Lưu kết quả
            save_txt(transcript, "recognized_text.txt")
            save_srt(srt_lines, "recognized_subtitles.srt")

        finally:
            # Bước 4: Luôn xóa file trên GCS sau khi hoàn tất
            delete_from_gcs(BUCKET_NAME, GCS_BLOB_NAME)

            # Tính và in thời gian xử lý
            end_time = time.time()
            elapsed_time = end_time - start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)

            print(f"✅ Hoàn tất toàn bộ quá trình!")
            print(f"⏱️ Tổng thời gian xử lý: {minutes} phút {seconds} giây")