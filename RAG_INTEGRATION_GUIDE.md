# Hướng Dẫn Tích Hợp RAG vào Medical Chatbot

## 📋 Tổng quan

Hệ thống RAG (Retrieval-Augmented Generation) đã được tích hợp hoàn chỉnh vào chatbot y tế. Luồng hoạt động:

1. **Chọn ca bệnh** từ CSDL (BoYTe200, NHIKHOA2, PHACDODIEUTRI_2016)
2. **RAG tìm triệu chứng** và **Gemini tạo case** bệnh nhân
3. **User nhập form chẩn đoán** với 6 trường chi tiết
4. **RAG tìm đáp án chuẩn** và **so sánh với câu trả lời user**
5. **Hiển thị kết quả phân tích** lên UI

## 🚀 Cài Đặt và Chạy

### 1. Cài đặt Python dependencies

```powershell
cd rag_project
pip install -r requirements.txt
pip install -r requirements_api.txt
```

### 2. Build FAISS index (nếu chưa có)

```powershell
cd rag_project
python src\build_faiss.py
```

Lệnh này sẽ:
- Đọc 3 file JSON trong `data/`
- Tạo embeddings với VoVanPhuc/sup-SimCSE-VietNamese-phobert-base
- Lưu FAISS index vào `faiss_cache/faiss_index/`

### 3. Chạy RAG API Server

```powershell
cd rag_project
python api_server.py
```

Server sẽ chạy trên `http://localhost:5000`

Kiểm tra health: `http://localhost:5000/api/health`

### 4. Chạy React Frontend

Trong terminal khác:

```powershell
npm run dev
```

Frontend sẽ chạy trên `http://localhost:5173`

## 📊 Cấu Trúc API

### Endpoints

#### 1. GET `/api/health`
Kiểm tra trạng thái server

**Response:**
```json
{
  "status": "healthy",
  "message": "RAG API Server is running",
  "embedding_model": "VoVanPhuc/sup-SimCSE-VietNamese-phobert-base"
}
```

#### 2. GET `/api/diseases`
Lấy danh sách tất cả bệnh từ 3 file JSON

**Response:**
```json
{
  "success": true,
  "diseases": [
    {
      "id": "pediatrics_1",
      "name": "SUY TIM Ở TRẺ EM",
      "category": "pediatrics",
      "source": "NHIKHOA2.json",
      "sections": ["ĐẠI CƯƠNG", "TRIỆU CHỨNG", "ĐIỀU TRỊ", ...]
    },
    ...
  ],
  "total": 200
}
```

#### 3. POST `/api/start-case`
Tạo case bệnh từ tên bệnh

**Request:**
```json
{
  "disease": "SUY TIM Ở TRẺ EM",
  "sessionId": "rag_1234567890"
}
```

**Response:**
```json
{
  "success": true,
  "sessionId": "rag_1234567890",
  "case": "Bé An nhà chị Hương bữa nay bú kém hẳn...",
  "symptoms": "Triệu chứng: bú kém, gầy mòn, chậm tăng trưởng...",
  "sources": [
    {
      "file": "NHIKHOA2.json",
      "title": "SUY TIM Ở TRẺ EM",
      "section": "TRIỆU CHỨNG SUY TIM"
    }
  ]
}
```

#### 4. POST `/api/evaluate`
Đánh giá câu trả lời của user

**Request:**
```json
{
  "sessionId": "rag_1234567890",
  "diagnosis": {
    "clinical": "Triệu chứng lâm sàng...",
    "paraclinical": "Xét nghiệm cận lâm sàng...",
    "definitiveDiagnosis": "Chẩn đoán xác định...",
    "differentialDiagnosis": "Chẩn đoán phân biệt...",
    "treatment": "Cách điều trị...",
    "medication": "Thuốc sử dụng..."
  }
}
```

**Response:**
```json
{
  "success": true,
  "case": "Case bệnh nhân...",
  "standardAnswer": "ĐÁP ÁN CHUẨN:\n\nCHẨN ĐOÁN LÂM SÀNG:...",
  "evaluation": {
    "diem_manh": ["Nhận diện đúng triệu chứng..."],
    "diem_yeu": ["Thiếu chi tiết về cận lâm sàng..."],
    "da_co": ["Triệu chứng lâm sàng", "Điều trị"],
    "thieu": ["Cận lâm sàng", "Chẩn đoán phân biệt"],
    "dien_giai": "Bác sĩ đã nắm được...",
    "diem_so": "75/100",
    "nhan_xet_tong_quan": "Cần bổ sung thêm..."
  },
  "sources": [...]
}
```

## 💻 Luồng Frontend

### 1. User bắt đầu ca mới

```typescript
// App.tsx
const handleStartCase = async (config: CaseConfig) => {
  if (config.diseaseId) {
    // RAG Mode - mở disease selector
    setShowDiseaseSelector(true);
  } else {
    // AI Mode - tạo case bằng Gemini
    generateCase(config);
  }
};
```

### 2. User chọn bệnh từ CSDL

```typescript
// DiseaseSelectorModal.tsx
const handleSelectDisease = async (disease: Disease) => {
  // Gọi RAG API
  const result = await ragService.generateCase(
    disease.name, 
    ragBackendSessionId
  );
  
  // Hiển thị case lên UI
  showMessage(result.case);
};
```

### 3. User nhập form chẩn đoán

```typescript
// RAGDiagnosisForm.tsx
interface RAGDiagnosisData {
  clinical: string;              // Lâm sàng
  paraclinical: string;          // Cận lâm sàng
  definitiveDiagnosis: string;   // Chẩn đoán xác định
  differentialDiagnosis: string; // Chẩn đoán phân biệt
  treatment: string;             // Cách điều trị
  medication: string;            // Thuốc
}
```

### 4. Submit và nhận kết quả

```typescript
// App.tsx
const handleSubmitRAGDiagnosis = async (diagnosis) => {
  const result = await ragService.evaluateAnswer(
    sessionId, 
    diagnosis
  );
  
  // Hiển thị evaluation lên FeedbackPanel
  showEvaluation(result.evaluation);
};
```

## 🔧 Cấu Trúc File

```
med_chat/
├── rag_project/
│   ├── api_server.py          # Flask API server
│   ├── requirements_api.txt   # Flask dependencies
│   ├── src/
│   │   ├── doctor_evaluator.py  # Logic đánh giá
│   │   ├── rag_chain.py         # RAG chain
│   │   ├── vector_store.py      # FAISS vector store
│   │   └── ...
│   ├── data/
│   │   ├── BoYTe200_v3.json
│   │   ├── NHIKHOA2.json
│   │   └── PHACDODIEUTRI_2016.json
│   └── faiss_cache/
│       └── faiss_index/
│           └── index.faiss
├── components/
│   ├── RAGDiagnosisForm.tsx      # Form 6 trường
│   ├── DiseaseSelectorModal.tsx  # Chọn bệnh
│   └── FeedbackPanel.tsx         # Hiển thị kết quả
├── services/
│   └── ragService.ts             # API client
├── types.ts                       # TypeScript types
└── App.tsx                        # Main app với RAG integration
```

## 🎯 Các Trường Trong Form

| Trường | Mô tả | Ví dụ |
|--------|-------|-------|
| **Cận lâm sàng** | Các xét nghiệm, chẩn đoán hình ảnh | X-quang, siêu âm tim, xét nghiệm máu |
| **Lâm sàng** | Triệu chứng, dấu hiệu khám | Bú kém, thở nhanh, tim nhanh, gan to |
| **Chẩn đoán xác định** | Chẩn đoán chính xác | Suy tim độ II theo Ross |
| **Chẩn đoán phân biệt** | Các bệnh cần phân biệt | Viêm phổi, suy hô hấp, loạn dưỡng |
| **Cách điều trị** | Phương pháp điều trị | Nghỉ ngơi, thở oxy, lợi tiểu, tăng co bóp |
| **Thuốc** | Thuốc và liều lượng | Furosemid 1mg/kg, Digoxin 0.01mg/kg |

## 📝 Kết Quả Đánh Giá

RAG system trả về JSON với các trường:

- **diem_manh**: Các điểm mạnh trong câu trả lời
- **diem_yeu**: Các điểm yếu, thiếu sót
- **da_co**: Những gì đã trả lời đúng
- **thieu**: Những gì còn thiếu
- **dien_giai**: Giải thích chi tiết
- **diem_so**: Điểm số (VD: "85/100")
- **nhan_xet_tong_quan**: Nhận xét tổng quan

## ⚠️ Lưu Ý

1. **RAG API phải chạy trước** khi start React app
2. **FAISS index** phải được build trước (chạy `build_faiss.py`)
3. **API Key** Gemini cần được cấu hình trong `rag_project/src/config.py`
4. Port mặc định:
   - RAG API: `5000`
   - React: `5173`

## 🐛 Troubleshooting

### Lỗi: "FAISS index not found"
```powershell
cd rag_project
python src\build_faiss.py
```

### Lỗi: "RAG API not available"
Kiểm tra:
1. RAG server có đang chạy không?
2. Port 5000 có bị chiếm không?
3. CORS có được cấu hình đúng không?

### Lỗi khi evaluate
Kiểm tra:
1. Session ID có đúng không?
2. Diagnosis data có đầy đủ không?
3. Gemini API key có hợp lệ không?

## 🎉 Hoàn Thành!

Bây giờ bạn có thể:
1. ✅ Chọn ca bệnh từ CSDL y khoa
2. ✅ Nhận case bệnh nhân được tạo tự động
3. ✅ Nhập câu trả lời qua form 6 trường
4. ✅ Nhận đánh giá chi tiết so với đáp án chuẩn

Chúc bạn phát triển thành công! 🚀
