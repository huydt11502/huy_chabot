# 📁 CÁCH KIỂM TRA DỮ LIỆU CHATBOT

## 1️⃣ XEM TRỰC TIẾP TRONG BROWSER

### Cách 1: Dùng DevTools
1. Mở chatbot: http://localhost:3012
2. Nhấn **F12** để mở DevTools
3. Chọn tab **Application** (hoặc **Storage** trên Firefox)
4. Sidebar bên trái → **Local Storage** → `http://localhost:3012`
5. Tìm key: **`pediatric_training_sessions`**
6. Click vào để xem JSON data

### Cách 2: Dùng Console
1. Mở chatbot: http://localhost:3012
2. Nhấn **F12** → Tab **Console**
3. Gõ lệnh:
```javascript
JSON.parse(localStorage.getItem('pediatric_training_sessions'))
```
4. Xem kết quả hiển thị

---

## 2️⃣ EXPORT RA FILE JSON

### Cách A: Tự động export (Khuyên dùng)
1. Mở chatbot: http://localhost:3012
2. Nhấn **F12** → Tab **Console**
3. Copy toàn bộ nội dung file `public/export-sessions.js`
4. Paste vào Console → Enter
5. File JSON sẽ tự động download: `chatbot-sessions-YYYY-MM-DD.json`

### Cách B: Manual copy
1. Mở chatbot: http://localhost:3012
2. Nhấn **F12** → Tab **Console**
3. Gõ:
```javascript
copy(localStorage.getItem('pediatric_training_sessions'))
```
4. Mở notepad → Ctrl+V
5. Save as `sessions.json`

---

## 3️⃣ CẤU TRÚC DỮ LIỆU

File JSON chứa array các **sessions**, mỗi session có:

```json
{
  "exportDate": "2025-12-22T13:45:00.000Z",
  "totalSessions": 3,
  "sessions": [
    {
      "id": "1703234567890",
      "createdAt": "2025-12-22T13:30:00.000Z",
      "updatedAt": "2025-12-22T13:35:00.000Z",
      "status": "completed",
      "isRAGMode": true,
      
      // Thông tin bệnh
      "disease": "SUY TIM Ở TRẺ EM",
      "caseType": "customised",
      
      // Thông tin bệnh nhân
      "patientName": "Bệnh nhân",
      "patientAge": 5,
      "patientGender": "male",
      "chiefComplaint": "SUY TIM Ở TRẺ EM",
      
      // Lịch sử chat
      "messageCount": 5,
      "messages": [
        {
          "id": "1703234567891",
          "role": "model",
          "content": "Bé Minh nhà chị thở nhanh, bú kém...",
          "timestamp": 1703234567891
        },
        {
          "id": "1703234567892",
          "role": "user",
          "content": "Bé bị sao?",
          "timestamp": 1703234567892
        }
      ],
      
      // 📝 Câu trả lời của user (6 trường)
      "ragDiagnosis": {
        "clinical": "Thở nhanh 60 lần/phút, bú kém, gan to",
        "paraclinical": "X-quang tim to, ECG nhịp nhanh",
        "definitiveDiagnosis": "Suy tim sung huyết ở trẻ em",
        "differentialDiagnosis": "Viêm phổi, hen phế quản",
        "treatment": "Hạn chế dịch, theo dõi SpO2",
        "medication": "Digoxin 0.01mg/kg, Furosemide 1mg/kg",
        "submittedAt": "2025-12-22T13:33:00.000Z"
      },
      
      // ⭐ Kết quả đánh giá (JSON từ Gemini)
      "ragEvaluation": {
        "diem_so": "85/100",
        "diem_manh": [
          "Chẩn đoán xác định đúng bệnh suy tim",
          "Đề xuất thuốc đúng nhóm (lợi tiểu, Digoxin)"
        ],
        "diem_yeu": [
          "Thiếu liều lượng cụ thể theo cân nặng",
          "Chưa đề cập thời gian điều trị"
        ],
        "da_co": [
          "Chẩn đoán xác định: Suy tim",
          "Thuốc: Digoxin, Furosemide"
        ],
        "thieu": [
          "Liều lượng chi tiết theo kg",
          "Thời gian điều trị"
        ],
        "dien_giai": [
          "Bạn đã chẩn đoán đúng bệnh suy tim...",
          "Cần bổ sung liều lượng cụ thể..."
        ],
        "nhan_xet_tong_quan": "Tốt, cần cải thiện liều lượng",
        "standardAnswer": "CHẨN ĐOÁN LÂM SÀNG:\n- Thở nhanh > 60 lần/phút...",
        "sources": [
          {
            "file": "NHIKHOA2.json",
            "title": "SUY TIM Ở TRẺ EM",
            "section": "TRIỆU CHỨNG"
          }
        ]
      }
    }
  ]
}
```

---

## 4️⃣ SCRIPT TEST TỰ ĐỘNG

Chạy script test để tạo session mẫu:

```bash
# Đảm bảo backend đang chạy
cd d:\Storage\med_chat
python test_api_flow.py
```

Script sẽ:
1. ✅ Test `/api/health`
2. ✅ Test `/api/diseases` - Lấy danh sách bệnh
3. ✅ Test `/api/start-case` - Tạo case bệnh
4. ✅ Test `/api/evaluate` - Đánh giá câu trả lời
5. 💾 Lưu kết quả vào `test_results.json`

---

## 5️⃣ VỊ TRÍ CÁC FILE QUAN TRỌNG

### Frontend (localStorage)
- **Key**: `pediatric_training_sessions`
- **Location**: Browser localStorage của `http://localhost:3012`
- **Format**: JSON array of sessions
- **Capacity**: ~10MB (giới hạn của localStorage)

### Backend (session memory)
- **Variable**: `active_sessions` trong `api_server_fastapi.py`
- **Format**: Python dict `{sessionId: sessionData}`
- **Lifetime**: Mất khi restart server
- **Content**: 
  - `disease`: Tên bệnh
  - `case`: Case đã tạo
  - `symptoms`: Triệu chứng từ RAG
  - `standard`: Đáp án chuẩn từ RAG
  - `sources`: Tài liệu tham khảo

### Test Results
- **File**: `d:\Storage\med_chat\test_results.json`
- **Created by**: `test_api_flow.py`
- **Contains**: Kết quả test API endpoints

---

## 6️⃣ CÁCH BACKUP DỮ LIỆU

### Manual Backup
1. Mở http://localhost:3012
2. F12 → Console
3. Run:
```javascript
const backup = localStorage.getItem('pediatric_training_sessions');
console.log(backup); // Copy này
```
4. Save vào file `backup-YYYY-MM-DD.json`

### Auto Backup Script
Thêm vào `public/export-sessions.js` (đã tạo sẵn):
- Tự động download JSON file
- Format đẹp, dễ đọc
- Include summary statistics

---

## 7️⃣ KHÔI PHỤC DỮ LIỆU

Nếu muốn khôi phục data cũ:

```javascript
// Mở Console (F12)
const oldData = `[{...}]`; // Paste JSON backup
localStorage.setItem('pediatric_training_sessions', oldData);
location.reload(); // Refresh page
```

---

## 🎯 TÓM TẮT

| Dữ liệu | Vị trí | Cách xem |
|---------|--------|----------|
| Sessions hiện tại | Browser localStorage | F12 → Application → Local Storage |
| Backend sessions | Memory (api_server_fastapi.py) | Check logs hoặc add API endpoint |
| Test results | `test_results.json` | Open file |
| Export full data | Download JSON | Run `export-sessions.js` script |

---

## 📖 CÁCH DÙNG NHANH

1. **Tương tác với chatbot** trên http://localhost:3012
2. **F12 → Console** → Copy script từ `public/export-sessions.js`
3. **Paste → Enter** → File JSON tự động download
4. **Mở file JSON** để xem toàn bộ dữ liệu:
   - Lịch sử chat
   - Câu trả lời 6 trường
   - Kết quả đánh giá JSON
   - Điểm số, điểm mạnh, điểm yếu
   - Đáp án chuẩn

✅ Hoàn tất!
