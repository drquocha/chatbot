# Simple Chatbot Demo

Chatbot đơn giản sử dụng Python, OpenAI API và Flask.

## Cài đặt

1. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

2. Tạo file `.env` từ `.env.example`:
```bash
cp .env.example .env
```

3. Thêm OpenAI API key vào file `.env`:
```
OPENAI_API_KEY=your_api_key_here
```

## Sử dụng

### Chạy chatbot console:
```bash
python chatbot.py
```

### Chạy web interface:
```bash
python app.py
```

Sau đó truy cập: http://localhost:5000

## Tính năng

- Hội thoại với AI qua console hoặc web
- Lưu lịch sử hội thoại
- Xóa lịch sử hội thoại
- Giao diện web thân thiện