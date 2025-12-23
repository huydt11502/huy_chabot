# 🎯 TEST LUỒNG CHATBOT HOÀN CHỈNH

## ✅ BACKEND RAG (Port 5000)

### Kiểm tra Backend đang chạy
```bash
# Terminal 1: Kiểm tra backend
curl http://localhost:5000/api/health
```

Kết quả mong đợi:
```json
{
  "status": "healthy",
  "message": "FastAPI RAG Server is running",
  "embedding_model": "models/embedding-001"
}
```

### API Endpoints

#### 1. `/api/diseases` - Lấy danh sách bệnh
```bash
curl http://localhost:5000/api/diseases
```

**Luồng xử lý:**
- Đọc 3 file JSON: `BoYTe200_v3.json`, `NHIKHOA2.json`, `PHACDODIEUTRI_2016.json`
- Lấy field "Index" từ mỗi item → Tên bệnh
- Map sang categories:
  - BoYTe200_v3.json → `procedures`
  - NHIKHOA2.json → `pediatrics`
  - PHACDODIEUTRI_2016.json → `treatment`

**Response format:**
```json
{
  "success": true,
  "total": 150,
  "diseases": [
    {
      "id": "pediatrics_1",
      "name": "SUY TIM Ở TRẺ EM",
      "category": "pediatrics",
      "source": "NHIKHOA2.json",
      "sections": ["ĐẠI CƯƠNG", "LÂM SÀNG", "CHẨN ĐOÁN", ...]
    }
  ]
}
```

#### 2. `/api/start-case` - Tạo case bệnh
```bash
curl -X POST http://localhost:5000/api/start-case \
  -H "Content-Type: application/json" \
  -d '{"disease": "SUY TIM Ở TRẺ EM", "sessionId": "test_123"}'
```

**Luồng xử lý (theo main.py):**
1. **find_symptoms(disease)** - RAG tìm triệu chứng
   - Query: "SUY TIM Ở TRẺ EM triệu chứng"
   - Hybrid search trong FAISS index
   - Trả về: Danh sách triệu chứng từ tài liệu

2. **generate_case(disease, symptoms)** - Gemini tạo case
   - Input: Tên bệnh + Triệu chứng từ RAG
   - Gemini tạo lời thoại mẹ bệnh nhân tự nhiên
   - Output: "Bé Minh nhà chị thở nhanh, bú kém..."

3. **get_detailed_standard_knowledge(disease)** - RAG lấy đáp án chuẩn
   - Query nhiều sections:
     - Lâm sàng
     - Cận lâm sàng
     - Chẩn đoán xác định
     - Chẩn đoán phân biệt
     - Điều trị
   - Lưu vào session để dùng cho /evaluate

**Response format:**
```json
{
  "success": true,
  "sessionId": "test_123",
  "case": "Bé Minh nhà chị thở nhanh, bú kém...",
  "symptoms": "Triệu chứng: thở nhanh, bú kém...",
  "sources": [
    {
      "file": "NHIKHOA2.json",
      "title": "SUY TIM Ở TRẺ EM",
      "section": "TRIỆU CHỨNG"
    }
  ]
}
```

#### 3. `/api/evaluate` - Đánh giá câu trả lời
```bash
curl -X POST http://localhost:5000/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test_123",
    "diagnosis": {
      "clinical": "Thở nhanh, bú kém...",
      "paraclinical": "X-quang tim to...",
      "definitiveDiagnosis": "Suy tim",
      "differentialDiagnosis": "Viêm phổi",
      "treatment": "Điều trị nội khoa",
      "medication": "Digoxin, Furosemide"
    }
  }'
```

**Luồng xử lý:**
1. Lấy session từ `active_sessions[sessionId]` (đã lưu từ /start-case)
2. Format câu trả lời user thành text
3. **detailed_evaluation(user_answer, standard_answer)** - Gemini so sánh
   - Input: Câu trả lời user + Đáp án chuẩn từ RAG
   - Gemini phân tích theo format JSON:
     ```json
     {
       "diem_so": "85/100",
       "diem_manh": ["Đúng chẩn đoán", "Đúng thuốc"],
       "diem_yeu": ["Thiếu liều lượng"],
       "da_co": ["Chẩn đoán xác định", "Thuốc điều trị"],
       "thieu": ["Liều lượng cụ thể", "Thời gian điều trị"],
       "dien_giai": ["Bạn đã chẩn đoán đúng..."],
       "nhan_xet_tong_quan": "Tốt, cần bổ sung liều lượng"
     }
     ```

**Response format:**
```json
{
  "success": true,
  "case": "Bé Minh nhà chị...",
  "standardAnswer": {
    "content": "CHẨN ĐOÁN LÂM SÀNG: ...",
    "disease": "SUY TIM Ở TRẺ EM"
  },
  "evaluation": {
    "diem_so": "85/100",
    "diem_manh": ["..."],
    "diem_yeu": ["..."],
    "da_co": ["..."],
    "thieu": ["..."],
    "dien_giai": ["..."],
    "nhan_xet_tong_quan": "..."
  },
  "sources": [...]
}
```

---

## ✅ FRONTEND (Port 3012)

### Khởi động Frontend
```bash
# Terminal 2
npm run dev
```

Mở browser: http://localhost:3012

### Luồng UI - TEST THEO BƯỚC

#### Bước 1: Màn hình Home
- Hiển thị: "Mocha - Luyện tập Khám Bệnh Nhi Ảo"
- Button: **"Bắt đầu ca mới (RAG Mode)"**
- Click button này

#### Bước 2: DiseaseSelectorModal
**Component:** `components/DiseaseSelectorModal.tsx`

**Chức năng:**
- Gọi API: `GET /api/diseases`
- Hiển thị danh sách bệnh theo category:
  - 🔬 Thủ thuật (procedures)
  - 👶 Nhi khoa (pediatrics)
  - 💊 Phác đồ điều trị (treatment)
- Search box: Tìm theo tên bệnh
- Category filter: Lọc theo loại

**Test:**
1. Click tab "Nhi khoa"
2. Search "SUY TIM"
3. Click vào "SUY TIM Ở TRẺ EM"

**Xử lý khi chọn bệnh (handleSelectRAGDisease):**
```typescript
// App.tsx line ~135
- Tạo sessionId mới
- Gọi API: POST /api/start-case
- Nhận case từ backend
- Hiển thị case lên chat
- Tắt modal
```

#### Bước 3: Chat hiển thị Case
**Component:** `MessageBubble` trong `App.tsx`

**Nội dung hiển thị:**
```
🤖 Bot: 
"Bé Minh nhà chị 6 tháng tuổi, mấy hôm nay bé thở nhanh phì phò, 
bú kém lắm, người lạnh tay chân. Chị lo lắm!"
```

**Case Header hiển thị:**
- 👶 Bệnh nhân • 5 tuổi • Nam
- Tag: **CSDL Y khoa** (màu xanh)
- Tên bệnh: **SUY TIM Ở TRẺ EM**
- Button: **"Tiến hành chẩn đoán"**

#### Bước 4: Điền Form Chẩn Đoán
**Component:** `components/RAGDiagnosisForm.tsx`

**6 trường bắt buộc:**

1. **Lâm sàng** (clinical)
   ```
   VD: Thở nhanh 60 lần/phút, bú kém, da xanh, gan to
   ```

2. **Cận lâm sàng** (paraclinical)
   ```
   VD: X-quang tim to, ECG nhịp nhanh, SpO2 thấp
   ```

3. **Chẩn đoán xác định** (definitiveDiagnosis)
   ```
   VD: Suy tim sung huyết ở trẻ em
   ```

4. **Chẩn đoán phân biệt** (differentialDiagnosis)
   ```
   VD: Viêm phổi, hen phế quản, bệnh tim bẩm sinh
   ```

5. **Cách điều trị** (treatment)
   ```
   VD: Điều trị nội khoa, hạn chế dịch, theo dõi SpO2
   ```

6. **Thuốc** (medication)
   ```
   VD: Digoxin 0.01mg/kg, Furosemide 1mg/kg
   ```

**Click "Gửi đánh giá"**

#### Bước 5: FeedbackPanel - Kết quả đánh giá
**Component:** `components/FeedbackPanel.tsx`

**Hiển thị JSON kết quả:**

```
✅ Điểm số: 85/100

📊 Điểm mạnh:
✓ Chẩn đoán xác định đúng bệnh suy tim
✓ Đề xuất thuốc đúng nhóm (lợi tiểu, Digoxin)
✓ Có chẩn đoán phân biệt

⚠️ Điểm cần cải thiện:
• Thiếu liều lượng cụ thể theo cân nặng
• Chưa đề cập thời gian điều trị
• Thiếu theo dõi lâm sàng

✅ Đã có trong câu trả lời:
- Chẩn đoán xác định: Suy tim
- Thuốc: Digoxin, Furosemide
- Cận lâm sàng: X-quang, ECG

❌ Còn thiếu:
- Liều lượng chi tiết theo kg
- Thời gian điều trị
- Chế độ ăn, tư thế

💬 Diễn giải:
"Bạn đã chẩn đoán đúng bệnh suy tim và chọn đúng nhóm thuốc.
Tuy nhiên, cần bổ sung liều lượng cụ thể..."

📚 Đáp án chuẩn:
CHẨN ĐOÁN LÂM SÀNG:
- Thở nhanh > 60 lần/phút
- Gan to > 2cm
...
```

---

## 🔍 DEBUG LOGS

### Backend Console (Terminal running FastAPI)
```
[INFO] Starting case for disease: SUY TIM Ở TRẺ EM
[INFO] Session ID: rag_1703234567890
[INFO] Step 1: Finding symptoms...
🔍 Query: SUY TIM Ở TRẺ EM triệu chứng
📋 Tìm thấy triệu chứng: Thở nhanh, bú kém...
[INFO] Step 2: Generating patient case...
[INFO] Generated case: Bé Minh nhà chị...
[INFO] Step 3: Getting standard knowledge...
[INFO] Standard data retrieved (length: 2500 chars)
[INFO] Session saved

...

[INFO] Evaluating diagnosis for: SUY TIM Ở TRẺ EM
[INFO] Step 1: Evaluating with Gemini...
[INFO] Step 2: Evaluation result (first 500 chars): {...
[INFO] Step 3: Parsing JSON evaluation...
[INFO] Successfully parsed JSON: {...
[INFO] Step 4: Formatting response...
```

### Frontend Console (Browser DevTools)
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

## 📝 CHECKLIST TEST

- [ ] Backend chạy trên port 5000
- [ ] Frontend chạy trên port 3012
- [ ] GET /api/health trả về status healthy
- [ ] GET /api/diseases trả về list 3 categories
- [ ] DiseaseSelectorModal hiển thị đúng categories
- [ ] Search filter hoạt động
- [ ] Click bệnh → Case được tạo và hiển thị
- [ ] Button "Tiến hành chẩn đoán" xuất hiện
- [ ] RAGDiagnosisForm hiển thị 6 trường
- [ ] Điền form → Click "Gửi đánh giá"
- [ ] FeedbackPanel hiển thị JSON đầy đủ:
  - [ ] diem_so
  - [ ] diem_manh (array)
  - [ ] diem_yeu (array)
  - [ ] da_co (array)
  - [ ] thieu (array)
  - [ ] dien_giai (array/string)
  - [ ] nhan_xet_tong_quan
  - [ ] standardAnswer
  - [ ] sources (array)

---

## 🚀 QUICK START

### Terminal 1: Backend
```bash
cd d:\Storage\med_chat\rag_project
python api_server_fastapi.py
```

### Terminal 2: Frontend
```bash
cd d:\Storage\med_chat
npm run dev
```

### Terminal 3: Test API
```bash
# Test health
curl http://localhost:5000/api/health

# Test diseases
curl http://localhost:5000/api/diseases | jq '.diseases | length'

# Test full flow
curl -X POST http://localhost:5000/api/start-case \
  -H "Content-Type: application/json" \
  -d '{"disease": "SUY TIM Ở TRẺ EM", "sessionId": "test_123"}'
```

### Browser
```
http://localhost:3012
Ctrl+Shift+R (hard refresh)
Click "Bắt đầu ca mới"
```

---

## 🐛 TROUBLESHOOTING

### Lỗi: "FAISS index not found"
```bash
cd rag_project
python src/build_faiss.py
```

### Lỗi: "Failed to fetch diseases"
- Kiểm tra backend đang chạy: `curl http://localhost:5000/api/health`
- Kiểm tra CORS: Browser console không có lỗi CORS

### Lỗi: "Failed to parse JSON evaluation"
- Xem backend console: `[ERROR] Failed to parse JSON`
- Kiểm tra Gemini API key còn quota
- Xem raw evaluation text trong log

### FeedbackPanel không hiển thị đầy đủ
- Mở Browser DevTools → Console
- Xem `[App] Final evaluation object to save`
- Kiểm tra `ragEvaluation` trong session state

---

## ✅ LUỒNG HOÀN CHỈNH TÓM TẮT

```
User clicks "Bắt đầu ca mới"
    ↓
DiseaseSelectorModal.tsx
    ↓ GET /api/diseases
Backend trả về list bệnh từ 3 JSON
    ↓
User chọn bệnh → handleSelectRAGDisease()
    ↓ POST /api/start-case
Backend:
  1. find_symptoms() - RAG
  2. generate_case() - Gemini
  3. get_detailed_standard_knowledge() - RAG
  → Lưu session
    ↓
Frontend hiển thị case lên chat
    ↓
User click "Tiến hành chẩn đoán"
    ↓
RAGDiagnosisForm.tsx - Điền 6 trường
    ↓
User click "Gửi đánh giá"
    ↓ POST /api/evaluate
Backend:
  1. Lấy session
  2. detailed_evaluation() - Gemini so sánh
  3. Parse JSON
  → Trả kết quả
    ↓
FeedbackPanel.tsx hiển thị JSON:
  ✅ diem_so, diem_manh, diem_yeu
  ✅ da_co, thieu, dien_giai
  ✅ nhan_xet_tong_quan
  ✅ standardAnswer
```

---

🎉 **HOÀN THÀNH!** Luồng chatbot hoàn chỉnh theo đúng yêu cầu.
