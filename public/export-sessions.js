// Script để export sessions từ localStorage ra file JSON
// Cách dùng: Mở Browser Console (F12) → Copy paste đoạn này → Enter

(function() {
    console.log('🔍 Đang đọc sessions từ localStorage...');
    
    const sessionsData = localStorage.getItem('pediatric_training_sessions');
    
    if (!sessionsData) {
        console.error('❌ Không tìm thấy sessions trong localStorage');
        return;
    }
    
    try {
        const sessions = JSON.parse(sessionsData);
        console.log(`✅ Tìm thấy ${sessions.length} sessions`);
        
        // Tạo timestamp
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `chatbot-sessions-${timestamp}.json`;
        
        // Format đẹp
        const formattedData = {
            exportDate: new Date().toISOString(),
            totalSessions: sessions.length,
            sessions: sessions.map(s => ({
                id: s.id,
                createdAt: new Date(s.createdAt).toISOString(),
                updatedAt: new Date(s.updatedAt).toISOString(),
                status: s.status,
                isRAGMode: s.isRAGMode,
                
                // Case config
                disease: s.caseConfig?.diseaseName || s.caseConfig?.diseaseId,
                caseType: s.caseConfig?.caseType,
                
                // Patient info
                patientName: s.patientInfo?.name,
                patientAge: s.patientInfo?.age,
                patientGender: s.patientInfo?.gender,
                chiefComplaint: s.patientInfo?.chiefComplaint,
                
                // Messages
                messageCount: s.messages?.length || 0,
                messages: s.messages || [],
                
                // RAG Diagnosis (6 fields)
                ragDiagnosis: s.ragDiagnosis ? {
                    clinical: s.ragDiagnosis.clinical,
                    paraclinical: s.ragDiagnosis.paraclinical,
                    definitiveDiagnosis: s.ragDiagnosis.definitiveDiagnosis,
                    differentialDiagnosis: s.ragDiagnosis.differentialDiagnosis,
                    treatment: s.ragDiagnosis.treatment,
                    medication: s.ragDiagnosis.medication,
                    submittedAt: s.ragDiagnosis.submittedAt ? new Date(s.ragDiagnosis.submittedAt).toISOString() : null
                } : null,
                
                // RAG Evaluation (JSON result)
                ragEvaluation: s.ragEvaluation ? {
                    diem_so: s.ragEvaluation.diem_so,
                    diem_manh: s.ragEvaluation.diem_manh,
                    diem_yeu: s.ragEvaluation.diem_yeu,
                    da_co: s.ragEvaluation.da_co,
                    thieu: s.ragEvaluation.thieu,
                    dien_giai: s.ragEvaluation.dien_giai,
                    nhan_xet_tong_quan: s.ragEvaluation.nhan_xet_tong_quan,
                    standardAnswer: s.ragEvaluation.standardAnswer,
                    sources: s.ragEvaluation.sources
                } : null,
                
                // AI Diagnosis (for non-RAG mode)
                diagnosis: s.diagnosis,
                
                // AI Evaluation (for non-RAG mode)
                evaluation: s.evaluation
            }))
        };
        
        // Download file
        const blob = new Blob([JSON.stringify(formattedData, null, 2)], { 
            type: 'application/json' 
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log(`✅ Đã tải xuống file: ${filename}`);
        console.log('📊 Tổng quan:');
        console.log(`   - Tổng sessions: ${sessions.length}`);
        console.log(`   - RAG sessions: ${sessions.filter(s => s.isRAGMode).length}`);
        console.log(`   - AI sessions: ${sessions.filter(s => !s.isRAGMode).length}`);
        console.log(`   - Hoàn thành: ${sessions.filter(s => s.status === 'completed').length}`);
        console.log(`   - Đang xử lý: ${sessions.filter(s => s.status === 'in-progress').length}`);
        
        // In summary
        sessions.forEach((s, i) => {
            console.log(`\n📋 Session ${i + 1}:`);
            console.log(`   ID: ${s.id}`);
            console.log(`   Disease: ${s.caseConfig?.diseaseName || 'N/A'}`);
            console.log(`   Status: ${s.status}`);
            console.log(`   Messages: ${s.messages?.length || 0}`);
            if (s.ragEvaluation) {
                console.log(`   ⭐ Điểm số: ${s.ragEvaluation.diem_so}`);
            }
        });
        
    } catch (error) {
        console.error('❌ Lỗi parse JSON:', error);
    }
})();
