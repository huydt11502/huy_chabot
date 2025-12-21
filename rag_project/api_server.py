"""
Flask API Server để tích hợp RAG vào Chatbot
Endpoints:
- GET /api/diseases - Lấy danh sách bệnh từ JSON
- POST /api/start-case - Nhận bệnh, tạo case với triệu chứng
- POST /api/evaluate - Nhận đáp án user, trả về kết quả so sánh
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import DataLoader
from config import Config
from doctor_evaluator import DoctorEvaluator
from vector_store import VectorStoreManager
from rag_chain import RAGChain

app = Flask(__name__)
CORS(app)  # Enable CORS for React app

# Initialize RAG system
print("🚀 Initializing RAG system...")
vs_manager = VectorStoreManager()
if not vs_manager.vector_store:
    print("❌ FAISS index not found. Run: python build_faiss.py")
    sys.exit(1)

rag = RAGChain(vs_manager)
evaluator = DoctorEvaluator(rag)
print("✅ RAG system ready!")

# Store active sessions
active_sessions = {}


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'RAG API Server is running',
        'embedding_model': Config.EMBEDDING_MODEL
    })


@app.route('/api/diseases', methods=['GET'])
def get_diseases():
    """
    Lấy danh sách bệnh từ 3 file JSON (Index field)
    Returns: { diseases: [{ id, name, category, source }] }
    """
    try:
        diseases = []
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        # Mapping files to categories
        files = [
            ('BoYTe200_v3.json', 'procedures'),
            ('NHIKHOA2.json', 'pediatrics'),
            ('PHACDODIEUTRI_2016.json', 'treatment')
        ]
        
        for filename, category in files:
            filepath = os.path.join(data_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    diseases.append({
                        'id': f"{category}_{item['id']}",
                        'name': item['Index'],
                        'category': category,
                        'source': filename,
                        'sections': item.get('level1_items', [])
                    })
        
        return jsonify({
            'success': True,
            'diseases': diseases,
            'total': len(diseases)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/start-case', methods=['POST'])
def start_case():
    """
    Nhận tên bệnh, tìm triệu chứng và tạo case
    Input: { disease: string, sessionId: string }
    Output: { case: string, symptoms: string, sessionId: string }
    """
    try:
        data = request.json
        disease = data.get('disease', '').strip()
        session_id = data.get('sessionId')
        
        if not disease:
            return jsonify({
                'success': False,
                'error': 'Disease name is required'
            }), 400
        
        print(f"📋 Starting case for disease: {disease}")
        
        # 1. RAG tìm triệu chứng
        print("🔍 Finding symptoms...")
        symptoms, symptom_sources = evaluator.find_symptoms(disease)
        
        # 2. Gemini tạo case
        print("✍️ Generating patient case...")
        patient_case = evaluator.generate_case(disease, symptoms)
        
        # Store session data
        session_data = {
            'disease': disease,
            'symptoms': symptoms,
            'case': patient_case,
            'symptom_sources': [
                {
                    'file': doc.metadata.get('source_file', ''),
                    'title': doc.metadata.get('main_title', ''),
                    'section': doc.metadata.get('sub_title', '')
                }
                for doc in symptom_sources[:3]
            ]
        }
        active_sessions[session_id] = session_data
        
        return jsonify({
            'success': True,
            'sessionId': session_id,
            'case': patient_case,
            'symptoms': symptoms[:300] + "...",  # Truncate for display
            'sources': session_data['symptom_sources']
        })
    
    except Exception as e:
        print(f"❌ Error in start_case: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/evaluate', methods=['POST'])
def evaluate_diagnosis():
    """
    Nhận câu trả lời user, so sánh với đáp án chuẩn
    Input: { 
        sessionId: string,
        diagnosis: {
            clinical: string,
            paraclinical: string,
            definitiveDiagnosis: string,
            differentialDiagnosis: string,
            treatment: string,
            medication: string
        }
    }
    Output: {
        standardAnswer: { ... },
        evaluation: { ... },
        sources: [ ... ]
    }
    """
    try:
        data = request.json
        session_id = data.get('sessionId')
        diagnosis = data.get('diagnosis', {})
        
        if not session_id or session_id not in active_sessions:
            return jsonify({
                'success': False,
                'error': 'Invalid session ID'
            }), 400
        
        session_data = active_sessions[session_id]
        disease = session_data['disease']
        
        print(f"📊 Evaluating diagnosis for: {disease}")
        
        # Format user's answer
        user_answer = f"""
CHẨN ĐOÁN:
- Lâm sàng: {diagnosis.get('clinical', 'Không có')}
- Cận lâm sàng: {diagnosis.get('paraclinical', 'Không có')}
- Chẩn đoán xác định: {diagnosis.get('definitiveDiagnosis', 'Không có')}
- Chẩn đoán phân biệt: {diagnosis.get('differentialDiagnosis', 'Không có')}

KẾ HOẠCH ĐIỀU TRỊ:
- Cách điều trị: {diagnosis.get('treatment', 'Không có')}
- Thuốc: {diagnosis.get('medication', 'Không có')}
"""
        
        print("🔍 Finding standard answer...")
        # Get standard answer from RAG
        standard_data, all_sources = evaluator.get_detailed_standard_knowledge(disease)
        
        print("🤖 Evaluating with Gemini...")
        # Evaluate with Gemini
        evaluation_json = evaluator.detailed_evaluation(user_answer, standard_data)
        
        # Parse JSON from evaluation
        try:
            # Extract JSON from markdown code blocks if present
            eval_text = evaluation_json.strip()
            if eval_text.startswith('```'):
                eval_text = eval_text.split('```')[1]
                if eval_text.startswith('json'):
                    eval_text = eval_text[4:]
            evaluation_obj = json.loads(eval_text.strip())
        except:
            # If parsing fails, return as text
            evaluation_obj = {
                'evaluation_text': evaluation_json,
                'diem_so': 'N/A'
            }
        
        # Format sources
        formatted_sources = [
            {
                'file': doc.metadata.get('source_file', ''),
                'title': doc.metadata.get('main_title', ''),
                'section': doc.metadata.get('sub_title', ''),
                'content': doc.page_content[:200] + "..."
            }
            for doc in all_sources[:5]
        ]
        
        return jsonify({
            'success': True,
            'case': session_data['case'],
            'standardAnswer': standard_data,
            'evaluation': evaluation_obj,
            'sources': formatted_sources
        })
    
    except Exception as e:
        print(f"❌ Error in evaluate: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("🌟 Starting Flask API Server...")
    print(f"📡 Server will run on http://localhost:5000")
    print(f"🔑 Using API Key: {Config.GOOGLE_API_KEY[:20]}...")
    app.run(debug=True, host='0.0.0.0', port=5000)
