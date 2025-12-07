import { GoogleGenerativeAI } from "@google/generative-ai";
import { SYSTEM_INSTRUCTION, VIRTUAL_PATIENT_INSTRUCTION, EVALUATOR_INSTRUCTION, CLINICAL_SYSTEMS, DIFFICULTY_LEVELS } from "../constants";
import { Message, CaseConfig, PatientInfo, TrainingSession, DiagnosisSubmission, EvaluationResult, ClinicalSystem, DifficultyLevel, AgeGroup } from "../types";

const MODEL_NAME = 'gemini-2.5-flash';

let genAI: GoogleGenerativeAI | null = null;

const getClient = () => {
  if (!genAI) {
    const apiKey = import.meta.env.VITE_GEMINI_API_KEY;
    if (!apiKey) {
      console.error("API Key not found in environment variables");
      throw new Error("API Key missing");
    }
    genAI = new GoogleGenerativeAI(apiKey);
  }
  return genAI;
};

export const sendMessageStream = async (
  history: Message[],
  message: string,
  onChunk: (text: string) => void,
  patientInfo?: PatientInfo | null
) => {
  try {
    console.log('sendMessageStream called with:', { historyLength: history.length, message, hasPatientInfo: !!patientInfo });
    const client = getClient();
    console.log('Client obtained');
    
    // Build system instruction based on context
    let systemInstruction = SYSTEM_INSTRUCTION;
    
    if (patientInfo) {
      // Virtual patient mode
      const caseInfo = `
Thông tin bệnh nhân:
- Tên: ${patientInfo.name}
- Tuổi: ${patientInfo.age} ${patientInfo.ageUnit === 'years' ? 'tuổi' : patientInfo.ageUnit === 'months' ? 'tháng' : 'ngày'}
- Giới: ${patientInfo.gender === 'male' ? 'Nam' : 'Nữ'}
- Lý do khám: ${patientInfo.chiefComplaint}
- Hệ cơ quan: ${CLINICAL_SYSTEMS.find(s => s.value === patientInfo.clinicalSystem)?.label}
- Mức độ phức tạp: ${DIFFICULTY_LEVELS.find(d => d.value === patientInfo.difficulty)?.label}
`;
      systemInstruction = VIRTUAL_PATIENT_INSTRUCTION.replace('{CASE_INFO}', caseInfo);
    }

    const model = client.getGenerativeModel({ 
      model: MODEL_NAME,
      systemInstruction 
    });

    // Convert history to Gemini format
    // Gemini requires history to start with 'user' role, so we need to handle this
    let chatHistory = history
      .filter(m => !m.isError && m.content.trim() !== '')
      .map(m => ({
        role: m.role === 'user' ? 'user' : 'model' as const,
        parts: [{ text: m.content }]
      }));
    
    // If history starts with 'model', we need to prepend a dummy user message
    // or skip the first model message for chat context
    if (chatHistory.length > 0 && chatHistory[0].role === 'model') {
      // Skip the opening message from model for chat history, it's already in context
      chatHistory = chatHistory.slice(1);
    }
    
    console.log('Chat history:', chatHistory);

    const chat = model.startChat({ history: chatHistory });
    console.log('Chat started, sending message...');
    
    const result = await chat.sendMessageStream(message);
    console.log('Stream result obtained');

    for await (const chunk of result.stream) {
      const text = chunk.text();
      console.log('Received chunk:', text);
      if (text) {
        onChunk(text);
      }
    }
    console.log('Stream completed');
  } catch (error: any) {
    console.error("Error in stream:", error);
    console.error("Error details:", error?.message, error?.status, error?.statusText);
    throw error;
  }
};

// ============ Case Generation ============

interface GeneratedCase {
  patientInfo: PatientInfo;
  openingMessage: string;
}

const getRandomElement = <T>(arr: T[]): T => arr[Math.floor(Math.random() * arr.length)];

const generateRandomConfig = (): { system: ClinicalSystem; difficulty: DifficultyLevel; ageGroup: AgeGroup } => {
  const systems: ClinicalSystem[] = ['respiratory', 'gastrointestinal', 'infectious', 'neurological'];
  const difficulties: DifficultyLevel[] = ['easy', 'medium', 'hard'];
  const ageGroups: AgeGroup[] = ['infant', 'toddler', 'preschool', 'school-age', 'adolescent'];
  
  return {
    system: getRandomElement(systems),
    difficulty: getRandomElement(difficulties),
    ageGroup: getRandomElement(ageGroups),
  };
};

const getAgeFromGroup = (ageGroup: AgeGroup): { age: number; ageUnit: 'days' | 'months' | 'years' } => {
  switch (ageGroup) {
    case 'neonatal':
      return { age: Math.floor(Math.random() * 28) + 1, ageUnit: 'days' };
    case 'infant':
      return { age: Math.floor(Math.random() * 11) + 1, ageUnit: 'months' };
    case 'toddler':
      return { age: Math.floor(Math.random() * 2) + 1, ageUnit: 'years' };
    case 'preschool':
      return { age: Math.floor(Math.random() * 2) + 3, ageUnit: 'years' };
    case 'school-age':
      return { age: Math.floor(Math.random() * 6) + 6, ageUnit: 'years' };
    case 'adolescent':
      return { age: Math.floor(Math.random() * 5) + 13, ageUnit: 'years' };
    default:
      return { age: Math.floor(Math.random() * 10) + 2, ageUnit: 'years' };
  }
};

const vietnameseNames = {
  male: ['Minh', 'Hùng', 'Dũng', 'Tuấn', 'Nam', 'Quang', 'Đức', 'Phong', 'Bảo', 'Khang'],
  female: ['Linh', 'Hương', 'Ngọc', 'Mai', 'Lan', 'Hà', 'Thu', 'Hạnh', 'Vy', 'Trang']
};

export const generateCase = async (config: CaseConfig): Promise<GeneratedCase> => {
  const client = getClient();
  
  // Determine case parameters
  let clinicalSystem = config.clinicalSystem;
  let difficulty = config.difficulty;
  let ageGroup = config.ageGroup;

  if (config.caseType === 'random') {
    const randomConfig = generateRandomConfig();
    clinicalSystem = clinicalSystem || randomConfig.system;
    difficulty = difficulty || randomConfig.difficulty;
    ageGroup = ageGroup || randomConfig.ageGroup;
  }

  // Defaults
  clinicalSystem = clinicalSystem || 'respiratory';
  difficulty = difficulty || 'medium';
  ageGroup = ageGroup || 'school-age';

  const gender = Math.random() > 0.5 ? 'male' : 'female';
  const name = getRandomElement(vietnameseNames[gender]);
  const { age, ageUnit } = getAgeFromGroup(ageGroup);

  const systemLabel = CLINICAL_SYSTEMS.find(s => s.value === clinicalSystem)?.label || 'Hô hấp';
  const difficultyLabel = DIFFICULTY_LEVELS.find(d => d.value === difficulty)?.label || 'Trung bình';

  // Generate case details using AI
  const prompt = `Bạn là hệ thống tạo ca bệnh nhi khoa để huấn luyện sinh viên y.

Hãy tạo một ca bệnh với các thông số sau:
- Hệ cơ quan: ${systemLabel}
- Mức độ khó: ${difficultyLabel}
- Tuổi: ${age} ${ageUnit === 'years' ? 'tuổi' : ageUnit === 'months' ? 'tháng' : 'ngày'}
- Giới: ${gender === 'male' ? 'Nam' : 'Nữ'}
- Tên: ${name}

Trả về JSON với format sau (chỉ trả về JSON, không có text khác):
{
  "chiefComplaint": "Lý do đến khám ngắn gọn (1-2 câu)",
  "openingMessage": "Lời chào và mô tả triệu chứng ban đầu từ góc nhìn phụ huynh/bệnh nhân (2-3 câu, tự nhiên như đang nói chuyện)"
}`;

  try {
    const model = client.getGenerativeModel({ model: MODEL_NAME });
    console.log('Generating case with Gemini...');
    
    const result = await model.generateContent(prompt);
    const text = result.response.text();
    console.log('Generated text:', text);
    
    // Extract JSON from response
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error('Invalid response format');
    }

    const caseData = JSON.parse(jsonMatch[0]);

    const patientInfo: PatientInfo = {
      caseId: `CASE-${Date.now().toString(36).toUpperCase()}`,
      name,
      age,
      ageUnit,
      gender,
      chiefComplaint: caseData.chiefComplaint,
      clinicalSystem: clinicalSystem!,
      difficulty: difficulty!,
      caseType: config.caseType,
    };

    return {
      patientInfo,
      openingMessage: caseData.openingMessage,
    };
  } catch (error) {
    console.error('Case generation error:', error);
    // Fallback case
    const patientInfo: PatientInfo = {
      caseId: `CASE-${Date.now().toString(36).toUpperCase()}`,
      name,
      age,
      ageUnit,
      gender,
      chiefComplaint: 'Sốt và ho 3 ngày',
      clinicalSystem: clinicalSystem!,
      difficulty: difficulty!,
      caseType: config.caseType,
    };

    return {
      patientInfo,
      openingMessage: `Chào bác sĩ, con ${name} của tôi bị sốt và ho được 3 ngày rồi. Tôi rất lo lắng vì cháu không chịu ăn uống gì cả.`,
    };
  }
};

// ============ Session Evaluation ============

export const evaluateSession = async (
  session: TrainingSession,
  diagnosis: DiagnosisSubmission
): Promise<EvaluationResult> => {
  const client = getClient();
  
  const conversationText = session.messages
    .map(m => `${m.role === 'user' ? 'Sinh viên' : 'Bệnh nhân'}: ${m.content}`)
    .join('\n');

  const patientInfo = session.patientInfo;
  const systemLabel = CLINICAL_SYSTEMS.find(s => s.value === patientInfo?.clinicalSystem)?.label;
  const difficultyLabel = DIFFICULTY_LEVELS.find(d => d.value === patientInfo?.difficulty)?.label;

  const prompt = `${EVALUATOR_INSTRUCTION}

=== THÔNG TIN CA BỆNH ===
- Mã ca: ${patientInfo?.caseId}
- Bệnh nhân: ${patientInfo?.name}, ${patientInfo?.age} ${patientInfo?.ageUnit === 'years' ? 'tuổi' : patientInfo?.ageUnit === 'months' ? 'tháng' : 'ngày'}, ${patientInfo?.gender === 'male' ? 'Nam' : 'Nữ'}
- Lý do khám: ${patientInfo?.chiefComplaint}
- Hệ cơ quan: ${systemLabel}
- Mức độ phức tạp: ${difficultyLabel}

=== CUỘC HỘI THOẠI ===
${conversationText}

=== CHẨN ĐOÁN CỦA SINH VIÊN ===
- Chẩn đoán sơ bộ: ${diagnosis.provisionalDiagnosis}
- Chẩn đoán phân biệt: ${diagnosis.differentialDiagnoses.join(', ') || 'Không có'}
- Kế hoạch xử trí: ${diagnosis.managementPlan}

Hãy đánh giá và trả về JSON với format sau (chỉ trả về JSON):
{
  "overallScore": <số từ 0-100>,
  "subScores": {
    "historyTaking": <số từ 0-25>,
    "physicalExamination": <số từ 0-25>,
    "diagnosis": <số từ 0-25>,
    "managementPlan": <số từ 0-25>
  },
  "strengths": ["<điểm mạnh 1>", "<điểm mạnh 2>"],
  "weaknesses": ["<điểm yếu 1>", "<điểm yếu 2>"],
  "suggestions": ["<gợi ý cải thiện 1>", "<gợi ý cải thiện 2>"],
  "detailedFeedback": "<nhận xét chi tiết 3-5 câu>"
}`;

  try {
    const model = client.getGenerativeModel({ model: MODEL_NAME });
    console.log('Evaluating session with Gemini...');
    
    const result = await model.generateContent(prompt);
    const text = result.response.text();
    console.log('Evaluation response:', text);
    
    // Extract JSON from response
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error('Invalid response format');
    }

    const evalData = JSON.parse(jsonMatch[0]);
    
    return {
      overallScore: evalData.overallScore || 0,
      maxScore: 100,
      subScores: {
        historyTaking: evalData.subScores?.historyTaking || 0,
        physicalExamination: evalData.subScores?.physicalExamination || 0,
        diagnosis: evalData.subScores?.diagnosis || 0,
        managementPlan: evalData.subScores?.managementPlan || 0,
      },
      strengths: evalData.strengths || [],
      weaknesses: evalData.weaknesses || [],
      suggestions: evalData.suggestions || [],
      detailedFeedback: evalData.detailedFeedback || '',
      evaluatedAt: Date.now(),
    };
  } catch (error) {
    console.error('Evaluation error:', error);
    // Fallback evaluation
    return {
      overallScore: 50,
      maxScore: 100,
      subScores: {
        historyTaking: 15,
        physicalExamination: 10,
        diagnosis: 15,
        managementPlan: 10,
      },
      strengths: ['Có nỗ lực hoàn thành bài tập'],
      weaknesses: ['Không thể đánh giá chi tiết do lỗi hệ thống'],
      suggestions: ['Vui lòng thử lại sau'],
      detailedFeedback: 'Đánh giá tự động gặp sự cố. Đây là điểm mặc định.',
      evaluatedAt: Date.now(),
    };
  }
};
