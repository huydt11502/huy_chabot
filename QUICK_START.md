# 🚀 Quick Start Guide - RAG Medical Chatbot

## Bước 1: Build FAISS Index (Chỉ chạy 1 lần đầu)

```powershell
cd rag_project
python src\build_faiss.py
```

⏱️ Mất khoảng 5-10 phút để build index từ 3 file JSON.

## Bước 2: Khởi động RAG API Server

### Cách 1: Dùng Batch File (Khuyến nghị)
```powershell
cd rag_project
.\start_server.bat
```

### Cách 2: Dùng Python trực tiếp
```powershell
cd rag_project
python api_server.py
```

⏱️ Mất 30-60 giây để load embedding model lần đầu.

✅ Khi thấy dòng này là thành công:
```
✅ RAG system ready!
🌟 Starting Flask API Server...
📡 Server will run on http://localhost:5000
* Running on http://0.0.0.0:5000
```

## Bước 3: Test API (Optional)

Mở browser hoặc Postman:
```
http://localhost:5000/api/health
```

Kết quả:
```json
{
  "status": "healthy",
  "message": "RAG API Server is running",
  "embedding_model": "VoVanPhuc/sup-SimCSE-VietNamese-phobert-base"
}
```

## Bước 4: Khởi động React Frontend

**Terminal mới:**
```powershell
npm run dev
```

Frontend: `http://localhost:5173`

## 🎮 Sử dụng

1. Mở `http://localhost:5173`
2. Click **"Bắt đầu ca mới"**
3. Chọn **"Ca bệnh từ CSDL"** (RAG mode)
4. Chọn bệnh từ danh sách (VD: "SUY TIM Ở TRẺ EM")
5. Đọc case bệnh nhân được tạo tự động
6. Click **"Tiến hành chẩn đoán"**
7. Điền 6 trường trong form
8. Click **"Nộp Bài"**
9. Xem kết quả đánh giá chi tiết

## ⚠️ Troubleshooting

### Lỗi: "FAISS index not found"
```powershell
cd rag_project
python src\build_faiss.py
```

### Lỗi: "The system cannot find the path specified"
Đã fix! File `vector_store.py` đã được cập nhật dùng đường dẫn tương đối.

### Server khởi động chậm
Bình thường! Lần đầu load embedding model mất 30-60 giây.

### Port 5000 bị chiếm
Đổi port trong `api_server.py` dòng cuối:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Đổi 5000 → 5001
```

Và cập nhật `services/ragService.ts`:
```typescript
const RAG_API_URL = 'http://localhost:5001/api';
```

## 📊 Kiểm tra hệ thống

### RAG API Server đang chạy?
```powershell
curl http://localhost:5000/api/health
```

### Có bao nhiêu bệnh trong CSDL?
```powershell
curl http://localhost:5000/api/diseases
```

### Frontend có kết nối được API?
Mở browser console, phải thấy request thành công đến `/api/health`

## ✅ Checklist

- [ ] Python packages đã cài (`pip install -r requirements.txt -r requirements_api.txt`)
- [ ] FAISS index đã build (`python src\build_faiss.py`)
- [ ] RAG API server đang chạy (`.\start_server.bat`)
- [ ] React app đang chạy (`npm run dev`)
- [ ] Test API health check thành công

## 🎉 Hoàn tất!

Bây giờ bạn có thể luyện tập với 200+ ca bệnh từ CSDL y khoa!

---

**Lưu ý**: 
- RAG mode và AI mode hoạt động song song
- Chọn "Ngẫu nhiên" để dùng AI mode (Gemini tạo case tự do)
- Chọn "Ca bệnh từ CSDL" để dùng RAG mode (Case chuẩn từ JSON)
