Dưới đây là **README.md** cập nhật, hướng dẫn người dùng cách sử dụng dự án chỉ cần **tạo virtual environment (venv)**, cài đặt thư viện, và **chạy file Python** mà không cần cấu hình thêm gì.

---

# Google Cloud Speech-to-Text Project

Dự án này sử dụng **API Google Cloud Speech-to-Text** để chuyển đổi file âm thanh thành văn bản và tạo phụ đề.

## Tính năng

* **Chuyển đổi đa định dạng**: Hỗ trợ các định dạng âm thanh phổ biến như `.mp3`, `.wav`, `.flac`, `.ogg`, `.amr`, và `.awb`.
* **Nhận diện giọng nói chính xác**: Sử dụng mô hình nhận diện giọng nói của Google với ngôn ngữ Tiếng Việt (`vi-VN`).
* **Tự động thêm dấu câu**: Kích hoạt tính năng tự động thêm dấu câu cho văn bản đầu ra.
* **Tạo file văn bản (.txt)**: Lưu toàn bộ nội dung đã nhận diện thành một file `.txt`.
* **Tạo file phụ đề (.srt)**: Tạo file phụ đề `.srt` với thời gian cho từng cụm từ (mặc định là 5 từ một dòng).
* **Quản lý file trên Cloud**: Tự động tải file âm thanh lên **Google Cloud Storage (GCS)** và xóa sau khi xử lý xong để tiết kiệm dung lượng.
* **Đo lường hiệu suất**: Theo dõi và báo cáo tổng thời gian xử lý của quá trình.

## Yêu cầu

1. **Python 3.x**
2. **Các thư viện Python cần thiết**: Cài đặt thư viện bằng `pip` (đã liệt kê trong `requirements.txt`).
3. **File JSON credentials**: Đảm bảo bạn đã có **file JSON credentials** từ **Google Cloud Service Account** (cung cấp sẵn). giải nén file zip ra là xong, pass giải nén [ib t gửi cho]([url](https://www.facebook.com/nguyen.ngoc.phuc.511590/)).

## Cài đặt và sử dụng

### 1. Tạo Virtual Environment (venv)

Trước khi bắt đầu, hãy tạo một **virtual environment** để quản lý các thư viện Python.

#### Trên Windows:

```bash
python -m venv venv
```

#### Trên macOS/Linux:

```bash
python3 -m venv venv
```

### 2. Kích hoạt Virtual Environment

#### Trên Windows:

```bash
.\venv\Scripts\activate
```

#### Trên macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Cài đặt các thư viện cần thiết

Sau khi kích hoạt **virtual environment**, cài đặt các thư viện cần thiết bằng lệnh sau:

```bash
pip install -r requirements.txt
```

### 4. Đặt file JSON credentials vào thư mục dự án

* Đặt file **JSON credentials** (mà bạn đã nhận được từ Google Cloud Service Account) vào cùng thư mục với **`main.py`**.

### 5. Chạy mã Python

Khi tất cả đã được cài đặt và cấu hình, chỉ cần chạy file Python để thực hiện nhận diện giọng nói từ file âm thanh.

```bash
python main.py
```

### 6. Đầu ra

Sau khi quá trình nhận diện kết thúc, bạn sẽ nhận được 2 file trong thư mục dự án:

1. **`recognized_text.txt`**: Chứa toàn bộ văn bản được chuyển đổi từ file âm thanh.
2. **`recognized_subtitles.srt`**: File phụ đề được định dạng theo chuẩn SRT, có thời gian cho từng cụm từ.

---

### Tóm tắt các bước:

1. Tạo **virtual environment (venv)**.
2. Kích hoạt **virtual environment**.
3. Cài đặt **thư viện Python** từ `requirements.txt`.
4. Đặt **file JSON credentials** vào thư mục với **`main.py`**.
5. Chạy file **`main.py`** để nhận diện âm thanh và lưu kết quả.

### Lợi ích:

* **Không cần cài Google Cloud SDK**.
* **Không cần cấu hình phức tạp**.
* Chỉ cần **file JSON credentials** và **chạy script Python**.

Chúc bạn thành công! Nếu có bất kỳ câu hỏi nào, đừng ngần ngại hỏi thêm!
