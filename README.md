# Google Cloud Speech-to-Text Project

Dự án này sử dụng API Google Cloud Speech-to-Text để chuyển đổi file âm thanh thành văn bản và tạo phụ đề.

## Tính năng

-   **Chuyển đổi đa định dạng**: Hỗ trợ các định dạng âm thanh phổ biến như `.mp3`, `.wav`, `.flac`, `.ogg`, `.amr`, và `.awb`.
-   **Nhận diện giọng nói chính xác**: Sử dụng mô hình nhận diện giọng nói của Google với ngôn ngữ Tiếng Việt (`vi-VN`).
-   **Tự động thêm dấu câu**: Kích hoạt tính năng tự động thêm dấu câu cho văn bản đầu ra.
-   **Tạo file văn bản (.txt)**: Lưu toàn bộ nội dung đã nhận diện thành một file `.txt`.
-   **Tạo file phụ đề (.srt)**: Tạo file phụ đề `.srt` với thời gian cho từng cụm từ (mặc định là 5 từ một dòng).
-   **Quản lý file trên Cloud**: Tự động tải file âm thanh lên Google Cloud Storage (GCS) và xóa sau khi xử lý xong để tiết kiệm dung lượng.
-   **Đo lường hiệu suất**: Theo dõi và báo cáo tổng thời gian xử lý của quá trình.

## Yêu cầu

1.  **Python 3.x**
2.  **Tài khoản Google Cloud**:
    -   Một Project đã được tạo.
    -   API Speech-to-Text đã được kích hoạt.
    -   Một bucket trên Google Cloud Storage.
3.  **Google Cloud SDK**: Đã cài đặt và xác thực. Chạy lệnh sau trên terminal để xác thực:
    ```bash
    gcloud auth application-default login
    ```
4.  **Các thư viện Python**: Cài đặt các thư viện cần thiết bằng lệnh:
    ```bash
    pip install -r requirements.txt
    ```

## Cấu hình

Trước khi chạy, bạn cần cập nhật các thông tin sau trong file `main.py`:

-   `PROJECT_ID`: ID của Google Cloud Project của bạn.
-   `BUCKET_NAME`: Tên của bucket trên Google Cloud Storage.
-   `LOCAL_AUDIO_FILE`: Đường dẫn đến file âm thanh trên máy tính của bạn.

```python
# main.py

# ...

# Thông tin dự án và bucket
PROJECT_ID = "your-gcp-project-id"
BUCKET_NAME = "your-gcs-bucket-name"
LOCAL_AUDIO_FILE = "path/to/your/audio.wav"  # Thay bằng tên file của bạn

# ...
```

## Cách sử dụng

1.  Đặt file âm thanh của bạn vào cùng thư mục với dự án hoặc cập nhật đường dẫn trong `LOCAL_AUDIO_FILE`.
2.  Chạy script từ terminal:
    ```bash
    python main.py
    ```
3.  Script sẽ bắt đầu quá trình tải file lên GCS, gửi yêu cầu nhận diện, và lưu kết quả.

## Đầu ra

Sau khi chạy xong, bạn sẽ nhận được 2 file trong thư mục dự án:

1.  `recognized_text.txt`: Chứa toàn bộ văn bản được chuyển đổi từ file âm thanh.
2.  `recognized_subtitles.srt`: File phụ đề được định dạng theo chuẩn SRT.

## Mẹo: Cải thiện phụ đề theo từng câu

File `recognized_subtitles.srt` được tạo ra bằng cách nhóm các từ lại với nhau (ví dụ: 5 từ một dòng). Để có được file phụ đề được chia theo từng câu hoàn chỉnh và tự nhiên hơn, bạn có thể sử dụng các công cụ AI hoặc các dịch vụ xử lý ngôn ngữ.

**Cách thực hiện:**

1.  **Sử dụng `recognized_text.txt`**: File này chứa văn bản đã được nhận diện đầy đủ và có dấu câu.
2.  **Sử dụng `recognized_subtitles.srt`**: File này chứa thông tin thời gian của từng từ/cụm từ.
3.  **Đưa lên AI**: Cung cấp cả hai file này cho một mô hình AI hoặc công cụ chỉnh sửa phụ đề nâng cao. Yêu cầu AI sử dụng văn bản trong file `.txt` để chia lại nội dung và áp dụng thời gian từ file `.srt` để tạo ra một file phụ đề mới, khớp với từng câu hoàn chỉnh.
