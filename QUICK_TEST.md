# 🎯 HƯỚNG DẪN TEST NHANH - LUỒNG CHATBOT HOÀN CHỈNH

## 🚀 CÁCH CHẠY

### Bước 1: Khởi động Backend (Terminal 1)
```bash
cd d:\Storage\med_chat\rag_project
python api_server_fastapi.py
```

Đợi thấy:
```
[OK] RAG system ready!
[*] Starting FastAPI Server...
[*] Server: http://localhost:5000
[*] Docs: http://localhost:5000/docs
```

### Bước 2: Test Backend API (Terminal 2)
```bash
cd d:\Storage\med_chat
python test_api_flow.py
```

Xem kết quả test các endpoints:
- ✅ `/api/health`
- ✅ `/api/diseases`
- ✅ `/api/start-case`
- ✅ `/api/evaluate`

### Bước 3: Khởi động Frontend (Terminal 3)
```bash
cd d:\Storage\med_chat
npm run dev
```

Đợi thấy:
```
VITE ready in ... ms
Local: http://localhost:3012
```

### Bước 4: Test UI Flow
1. Mở browser: **http://localhost:3012**
2. Nhấn **Ctrl+Shift+R** (hard refresh)
3. Click **"Bắt đầu ca mới (RAG Mode)"**
4. Chọn category **"Nhi khoa"**
5. Search **"SUY TIM"**
6. Click vào **"SUY TIM Ở TRẺ EM"**
7. Đọc case được tạo ra trong chat
8. Click **"Tiến hành chẩn đoán"**
9. Điền 6 trường trong form:
   - **Lâm sàng**: Thở nhanh 60 lần/phút, bú kém, gan to
   - **Cận lâm sàng**: X-quang tim to, ECG nhịp nhanh
   - **Chẩn đoán xác định**: Suy tim sung huyết ở trẻ em
   - **Chẩn đoán phân biệt**: Viêm phổi, hen phế quản
   - **Cách điều trị**: Hạn chế dịch, theo dõi SpO2
   - **Thuốc**: Digoxin 0.01mg/kg, Furosemide 1mg/kg
10. Click **"Gửi đánh giá"**
11. Xem kết quả JSON hiển thị:
    - ✅ **Điểm số**: 85/100
    - ✅ **Điểm mạnh**: ["Chẩn đoán đúng", ...]
    - ✅ **Điểm yếu**: ["Thiếu liều lượng", ...]
    - ✅ **Đã có**: ["Chẩn đoán xác định", ...]
    - ✅ **Thiếu**: ["Thời gian điều trị", ...]
    - ✅ **Diễn giải**: ["Bạn đã...", ...]
    - ✅ **Nhận xét tổng quan**: "Tốt, cần cải thiện..."
    - ✅ **Đáp án chuẩn**: "CHẨN ĐOÁN LÂM SÀNG: ..."

---

## 🔍 KIỂM TRA LOGS

### Backend Console (Terminal 1)
```
[INFO] Starting case for disease: SUY TIM Ở TRẺ EM
[INFO] Session ID: rag_1703234567890
[INFO] Step 1: Finding symptoms...
🔍 Query: SUY TIM Ở TRẺ EM triệu chứng
📋 Tìm thấy triệu chứng: Thở nhanh, bú kém...
[INFO] Step 2: Generating patient case...
[INFO] Generated case (first 200 chars): Bé Minh nhà chị...
[INFO] Step 3: Getting standard knowledge...
[INFO] Standard data retrieved (length: 2500 chars)
```

### Frontend Console (Browser DevTools F12 → Console)
```
[ragService] getDiseases called
[ragService] Loaded diseases: 150

[App] Selected disease: SUY TIM Ở TRẺ EM
[RAG] Calling generateCase...
[RAG] generateCase result: { case: "Bé Minh...", ... }

[App] Calling RAG evaluate API...
[App] RAG evaluate result: { evaluation: {...}, standard: "..." }
[App] Parsed evaluation obj: { diem_so: "85/100", ... }
[App] Final evaluation object to save: {...}
[App] Evaluation saved to session
```

---

## ✅ CHECKLIST

- [ ] Backend running on port 5000
- [ ] Frontend running on port 3012
- [ ] `test_api_flow.py` pass tất cả tests
- [ ] DiseaseSelectorModal hiển thị diseases
- [ ] Case được tạo và hiển thị trong chat
- [ ] RAGDiagnosisForm có 6 trường
- [ ] FeedbackPanel hiển thị đầy đủ JSON:
  - [ ] diem_so
  - [ ] diem_manh
  - [ ] diem_yeu
  - [ ] da_co
  - [ ] thieu
  - [ ] dien_giai
  - [ ] nhan_xet_tong_quan
  - [ ] standardAnswer

---

## 🐛 TROUBLESHOOTING

### Lỗi: "FAISS index not found"
```bash
cd rag_project
python src/build_faiss.py
```

### Lỗi: "Failed to fetch diseases"
- Kiểm tra backend đang chạy: `curl http://localhost:5000/api/health`
- Xem terminal backend có lỗi không

### Lỗi: "Timeout" khi tạo case
- Kiểm tra Gemini API key còn quota
- Xem backend logs có lỗi không

### FeedbackPanel không hiển thị JSON
- Mở Browser DevTools → Console
- Xem logs `[App] Final evaluation object to save`
- Kiểm tra format JSON từ backend

---

## 📚 TÀI LIỆU CHI TIẾT

- [TEST_FLOW.md](TEST_FLOW.md) - Hướng dẫn test chi tiết đầy đủ
- [CHANGELOG_LUONG_HOAN_CHINH.md](CHANGELOG_LUONG_HOAN_CHINH.md) - Tổng kết thay đổi

---

## 🎉 HOÀN THÀNH!

Luồng chatbot hoàn chỉnh đã sẵn sàng test:
1. ✅ Backend RAG (Port 5000)
2. ✅ Frontend UI (Port 3012)
3. ✅ 3 API endpoints hoạt động đúng
4. ✅ Flow: Chọn bệnh → Case → Điền form → Đánh giá
5. ✅ JSON kết quả hiển thị đầy đủ
