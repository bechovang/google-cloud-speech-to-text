# Hướng dẫn Bảo trì Dự án

Tài liệu này cung cấp hướng dẫn cho các nhà phát triển để bảo trì và cập nhật dự án Speech-to-Text này.

## Tổng quan kiến trúc

Dự án bao gồm một script Python duy nhất (`main.py`) thực hiện một chuỗi các tác vụ:
1.  **Tải file lên (Upload)**: Tải một file âm thanh cục bộ lên Google Cloud Storage (GCS).
2.  **Nhận diện (Transcribe)**: Gửi yêu cầu đến API Google Cloud Speech-to-Text để xử lý file âm thanh từ GCS.
3.  **Xử lý kết quả**:
    -   Tạo một bản ghi văn bản đầy đủ.
    -   Tạo một file phụ đề SRT bằng cách nhóm các từ đã được nhận diện.
4.  **Lưu trữ**: Lưu văn bản và phụ đề thành các file `.txt` và `.srt`.
5.  **Dọn dẹp (Cleanup)**: Xóa file âm thanh đã tải lên khỏi GCS để tránh chi phí lưu trữ không cần thiết.

## Cấu trúc file

-   `main.py`: Script chính chứa toàn bộ logic của ứng dụng.
-   `requirements.txt`: Chứa danh sách các thư viện Python cần thiết.
-   `README.md`: Hướng dẫn sử dụng cho người dùng cuối.
-   `MAINTAIN.md`: (Tài liệu này) Hướng dẫn cho nhà phát triển.

## Phụ thuộc (Dependencies)

Các thư viện Python chính được sử dụng là:
-   `google-cloud-storage`: Để tương tác với Google Cloud Storage (tải lên, xóa file).
-   `google-cloud-speech`: Để tương tác với API Speech-to-Text.

Để cập nhật các thư viện lên phiên bản mới nhất, bạn có thể chạy:
```bash
pip install --upgrade google-cloud-storage google-cloud-speech
```
Sau đó, cập nhật file `requirements.txt` với phiên bản mới bằng cách chạy:
```bash
pip freeze > requirements.txt
```

## Chi tiết về mã nguồn (`main.py`)

### `get_audio_encoding(file_name)`
-   **Chức năng**: Xác định `encoding` cần thiết cho API Speech-to-Text dựa trên phần mở rộng của file.
-   **Bảo trì**: Nếu muốn hỗ trợ thêm định dạng âm thanh mới, bạn cần thêm một cặp `key: value` mới vào từ điển `encodings`.
    -   Key: Phần mở rộng của file (ví dụ: `.m4a`).
    -   Value: Hằng số `AudioEncoding` tương ứng từ thư viện `google.cloud.speech`. (Ví dụ: `speech.RecognitionConfig.AudioEncoding.WEBM_OPUS` nếu là webm).

### `transcribe_gcs(gcs_uri, language_code)`
-   **Chức năng**: Đây là hàm cốt lõi, gửi yêu cầu nhận dạng đến Google.
-   **`RecognitionConfig`**: Đây là nơi cấu hình các tùy chọn nhận dạng.
    -   `enable_automatic_punctuation=True`: Bật dấu câu tự động.
    -   `enable_word_time_offsets=True`: Rất quan trọng. Tùy chọn này cho phép API trả về thời gian bắt đầu và kết thúc của mỗi từ, là cơ sở để tạo file `.srt`.
-   **`client.long_running_recognize`**: Sử dụng phương thức này vì nó được thiết kế cho các file audio dài (hơn 1 phút).
-   **Logic tạo SRT**:
    -   Vòng lặp `for i in range(0, len(words), 5)` nhóm 5 từ thành một dòng phụ đề.
    -   Để thay đổi số lượng từ mỗi dòng, hãy thay đổi số `5` trong vòng lặp.
    -   Thời gian bắt đầu/kết thúc được lấy từ từ đầu tiên và từ cuối cùng trong mỗi nhóm.

### `if __name__ == "__main__"`
-   **Chức năng**: Điều phối toàn bộ quy trình.
-   **Biến cấu hình**: `PROJECT_ID`, `BUCKET_NAME`, `LOCAL_AUDIO_FILE` được định nghĩa ở đây.
-   **Xử lý `try...finally`**: Cấu trúc này đảm bảo rằng hàm `delete_from_gcs` luôn được gọi để dọn dẹp file trên GCS, ngay cả khi quá trình nhận dạng gặp lỗi.

## Gỡ lỗi và các vấn đề tiềm ẩn

1.  **Lỗi xác thực (Authentication Errors)**:
    -   **Triệu chứng**: `PermissionDenied`, `403 Forbidden`, hoặc các lỗi liên quan đến credentials.
    -   **Giải pháp**: Đảm bảo đã chạy `gcloud auth application-default login` và đăng nhập bằng tài khoản có quyền truy cập vào project và bucket.

2.  **API Not Enabled**:
    -   **Triệu chứng**: Lỗi thông báo rằng API `speech.googleapis.com` chưa được kích hoạt.
    -   **Giải pháp**: Truy cập Google Cloud Console, vào mục "APIs & Services", và kích hoạt "Cloud Speech-to-Text API" cho dự án của bạn.

3.  **Định dạng không được hỗ trợ**:
    -   **Triệu chứng**: Lỗi `ValueError` từ hàm `get_audio_encoding`.
    -   **Giải pháp**: Thêm định dạng file mới vào từ điển `encodings` trong hàm `get_audio_encoding` như đã hướng dẫn ở trên.

4.  **Hết thời gian chờ (Timeout)**:
    -   **Triệu chứng**: Lỗi `TimeoutError` trong dòng `response = operation.result(timeout=300)`.
    -   **Giải pháp**: Đối với các file âm thanh rất dài (ví dụ: > 1 giờ), bạn có thể cần tăng giá trị `timeout` (tính bằng giây). Ví dụ: `timeout=3600` cho 1 giờ. 