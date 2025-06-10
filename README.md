# google-cloud-speech-to-text


Tuyệt vời! Để tự động hóa việc chuyển đổi file audio sang text bằng Python với Google Cloud Speech-to-Text, bạn cần làm theo các bước sau. Đoạn code này sẽ xử lý file audio dài hơn 1 phút, phù hợp với file 6-7 phút của bạn.

**Bước 0: Điều kiện tiên quyết (Quan trọng!)**

1.  **Tài khoản Google Cloud và Dự án:**
    *   Đảm bảo bạn đã có [Tài khoản Google Cloud](https://cloud.google.com/).
    *   Tạo một [Dự án (Project)](https://console.cloud.google.com/projectcreate) mới hoặc chọn một dự án hiện có.
    *   Ghi lại **Project ID** của bạn.
2.  **Bật API Cloud Speech-to-Text:**
    *   Trong Google Cloud Console, đi đến "APIs & Services" -> "Library".
    *   Tìm "Cloud Speech-to-Text API" và **Enable** nó cho dự án của bạn.
3.  **Bật Thanh toán (Billing):**
    *   Speech-to-Text có một bậc miễn phí (60 phút/tháng), nhưng bạn vẫn cần [bật thanh toán](https://cloud.google.com/billing/docs/how-to/modify-project) cho dự án. Bạn sẽ không bị tính phí nếu không vượt quá giới hạn miễn phí.
4.  **Cài đặt Google Cloud SDK (gcloud CLI):**
    *   Nếu chưa có, hãy [cài đặt Google Cloud SDK](https://cloud.google.com/sdk/docs/install). Công cụ này giúp bạn xác thực và quản lý tài nguyên Google Cloud.
5.  **Xác thực:**
    *   Cách dễ nhất để xác thực cho môi trường phát triển cục bộ là sử dụng Application Default Credentials (ADC). Chạy lệnh sau trong terminal/command prompt của bạn và làm theo hướng dẫn để đăng nhập:
        ```bash
        gcloud auth application-default login
        ```
6.  **Tải file audio lên Google Cloud Storage (GCS):**
    *   Speech-to-Text API hoạt động hiệu quả nhất với các file audio được lưu trữ trên GCS, đặc biệt là cho các file dài.
    *   Tạo một Bucket trong GCS:
        *   Đi đến Google Cloud Console -> Cloud Storage -> Browser.
        *   Nhấp "Create Bucket", đặt tên (tên bucket là duy nhất trên toàn cầu), chọn vị trí và các cài đặt mặc định.
    *   Tải file audio của bạn lên bucket này.
    *   Ghi lại **URI của file trên GCS**. Nó sẽ có dạng `gs://YOUR_BUCKET_NAME/YOUR_AUDIO_FILE_NAME`.
7.  **Cài đặt thư viện Python của Google Cloud:**
    *   Trong terminal hoặc command prompt, chạy:
        ```bash
        pip install google-cloud-speech
        ```

**Bước 1: Viết Code Python**

Dưới đây là đoạn code Python mẫu. Bạn cần thay thế `YOUR_GCS_BUCKET_NAME` và `YOUR_AUDIO_FILE_NAME` bằng thông tin thực tế của bạn.

```python
from google.cloud import speech

def transcribe_gcs_long_audio(gcs_uri: str, language_code: str = "vi-VN") -> str:
    """
    Transcribes a long audio file from Google Cloud Storage.

    Args:
        gcs_uri: The Google Cloud Storage URI of the audio file.
                 (e.g., "gs://your-bucket-name/your-audio-file.wav")
        language_code: The language of the speech in the audio.
                       (e.g., "en-US", "vi-VN")

    Returns:
        The transcribed text.
    """
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)

    # --- Cấu hình nhận dạng ---
    # Bạn có thể cần điều chỉnh các thông số này tùy thuộc vào file audio của mình
    # Ví dụ: file_format (nếu không phải là WAV, LINEAR16) hoặc sample_rate_hertz
    # Speech-to-Text thường có thể tự động phát hiện nhiều định dạng phổ biến như MP3, FLAC, WAV.
    config = speech.RecognitionConfig(
        # encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16, # Cần thiết nếu là WAV thuần
        # sample_rate_hertz=16000, # Tần số mẫu của audio, ví dụ 16000, 44100
        language_code=language_code,
        enable_automatic_punctuation=True,  # Tự động thêm dấu câu
        # model="video", # Có thể chọn model khác nếu phù hợp, vd: "phone_call", "medical_transcription"
                         # Model "default" (nếu không chỉ định) thường hoạt động tốt.
                         # Đối với Tiếng Việt, "latest_long" có thể cho kết quả tốt cho file dài.
        model="latest_long", # Thử model này cho file Tiếng Việt dài.
        # audio_channel_count=1, # Mặc định là 1, nếu audio của bạn là stereo và muốn xử lý riêng thì chỉnh
        enable_speaker_diarization=False, # Đặt True nếu muốn nhận diện người nói (tốn thêm phí)
        # diarization_speaker_count=2, # Chỉ định số lượng người nói nếu bật diarization
    )

    print(f"Bắt đầu xử lý file: {gcs_uri}")
    operation = client.long_running_recognize(config=config, audio=audio)

    print("Đang chờ quá trình xử lý hoàn tất...")
    response = operation.result(timeout=7200)  # Timeout sau 2 giờ (7200 giây) nếu cần

    transcript_builder = []
    for result in response.results:
        # Phần đầu tiên của kết quả thường chứa bản ghi tốt nhất.
        transcript_builder.append(result.alternatives[0].transcript)

    full_transcript = "\n".join(transcript_builder)
    print("Hoàn tất phiên âm!")
    return full_transcript

# --- Cách sử dụng ---
if __name__ == "__main__":
    # THAY THẾ CÁC GIÁ TRỊ SAU:
    gcs_file_uri = "gs://YOUR_GCS_BUCKET_NAME/YOUR_AUDIO_FILE_NAME"  # Ví dụ: "gs://my-audio-files-bucket/meeting_recording.mp3"
    output_text_file = "transcript_output.txt"

    if gcs_file_uri == "gs://YOUR_GCS_BUCKET_NAME/YOUR_AUDIO_FILE_NAME":
        print("VUI LÒNG CẬP NHẬT GIÁ TRỊ 'gcs_file_uri' TRONG CODE!")
    else:
        try:
            transcript = transcribe_gcs_long_audio(gcs_file_uri, language_code="vi-VN")
            print("\nNội dung phiên âm:")
            print(transcript)

            # Lưu kết quả ra file text
            with open(output_text_file, "w", encoding="utf-8") as f:
                f.write(transcript)
            print(f"\nĐã lưu bản ghi vào file: {output_text_file}")

        except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")
            print("Hãy kiểm tra các bước sau:")
            print("1. Đã cài đặt 'pip install google-cloud-speech' chưa?")
            print("2. Đã chạy 'gcloud auth application-default login' chưa?")
            print("3. Project ID có đúng và API Speech-to-Text đã được bật chưa?")
            print("4. Bucket GCS và file audio có tồn tại và đúng đường dẫn URI không?")
            print("5. Tài khoản Google Cloud của bạn có đang hoạt động và đã bật billing không?")

```

**Bước 2: Chạy Code**

1.  Lưu đoạn code trên vào một file Python (ví dụ: `transcribe_audio.py`).
2.  **Cập nhật `gcs_file_uri`** trong phần `if __name__ == "__main__":` với đường dẫn URI GCS chính xác đến file audio của bạn.
3.  Mở terminal hoặc command prompt, điều hướng đến thư mục chứa file Python của bạn.
4.  Chạy script:
    ```bash
    python transcribe_audio.py
    ```

**Giải thích Code:**

*   `transcribe_gcs_long_audio(gcs_uri, language_code)`: Hàm chính thực hiện việc gọi API.
*   `speech.SpeechClient()`: Tạo một client để tương tác với API.
*   `speech.RecognitionAudio(uri=gcs_uri)`: Chỉ định nguồn audio từ GCS.
*   `speech.RecognitionConfig(...)`: Cấu hình các thông số nhận dạng:
    *   `language_code="vi-VN"`: Quan trọng, đặt là "vi-VN" cho Tiếng Việt.
    *   `enable_automatic_punctuation=True`: Yêu cầu API tự động thêm dấu câu.
    *   `model="latest_long"`: Model này thường được khuyên dùng cho các file audio dài và không phải cuộc gọi điện thoại. Nó có thể cho chất lượng tốt hơn với Tiếng Việt. Nếu gặp vấn đề, bạn có thể thử bỏ dòng này để dùng model mặc định, hoặc thử `model="video"`.
    *   Bạn có thể cần uncomment và đặt `encoding` và `sample_rate_hertz` nếu API không tự động nhận diện đúng định dạng file audio của bạn (ít gặp với các định dạng phổ biến như MP3, WAV, FLAC).
*   `client.long_running_recognize(...)`: Gọi API để xử lý các file audio dài. Thao tác này là bất đồng bộ, nghĩa là nó trả về một "operation" mà bạn cần chờ đợi để có kết quả.
*   `operation.result(timeout=7200)`: Đợi cho đến khi quá trình xử lý hoàn tất hoặc hết thời gian chờ (ở đây là 2 giờ).
*   `response.results`: Kết quả trả về chứa nhiều phần, mỗi phần có thể có nhiều lựa chọn phiên âm (`alternatives`). Chúng ta lấy lựa chọn đầu tiên (`alternatives`) vì nó thường là tốt nhất.
*   Script sẽ in ra nội dung phiên âm và lưu vào file `transcript_output.txt`.

**Xử lý lỗi:**

*   Đảm bảo bạn đã hoàn thành tất cả các bước "Điều kiện tiên quyết".
*   Kiểm tra kỹ URI của file GCS.
*   Xem thông báo lỗi chi tiết nếu có để xác định vấn đề.

Đây là cách tự động hóa mạnh mẽ và hiệu quả nhất bằng công nghệ của Google. Chúc bạn thành công!
