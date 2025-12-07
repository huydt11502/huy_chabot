import React from 'react';
import { EvaluationResult, DiagnosisSubmission, PatientInfo } from '../types';
import { XMarkIcon, StarIcon, CheckIcon, ArrowLeftIcon } from './Icons';
import { CLINICAL_SYSTEMS, DIFFICULTY_LEVELS } from '../constants';

interface FeedbackPanelProps {
  isOpen: boolean;
  onClose: () => void;
  evaluation: EvaluationResult | null;
  diagnosis: DiagnosisSubmission | null;
  patientInfo: PatientInfo | null;
  isLoading?: boolean;
  onBackToHome: () => void;
}

const ScoreBar: React.FC<{ score: number; maxScore: number; label: string }> = ({ score, maxScore, label }) => {
  const percentage = (score / maxScore) * 100;
  const getColor = () => {
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 60) return 'bg-amber-500';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-gray-600">{label}</span>
        <span className="font-semibold text-gray-800">{score}/{maxScore}</span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${getColor()} transition-all duration-500 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

const FeedbackPanel: React.FC<FeedbackPanelProps> = ({
  isOpen,
  onClose,
  evaluation,
  diagnosis,
  patientInfo,
  isLoading = false,
  onBackToHome,
}) => {
  if (!isOpen) return null;

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-amber-600';
    return 'text-red-600';
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'from-green-500 to-emerald-600';
    if (score >= 60) return 'from-amber-500 to-orange-600';
    return 'from-red-500 to-rose-600';
  };

  const systemLabel = patientInfo?.clinicalSystem 
    ? CLINICAL_SYSTEMS.find(s => s.value === patientInfo.clinicalSystem)?.label 
    : '';
  const difficultyLabel = patientInfo?.difficulty 
    ? DIFFICULTY_LEVELS.find(d => d.value === patientInfo.difficulty)?.label 
    : '';

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col animate-in fade-in zoom-in duration-200">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
              <StarIcon className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Kết quả đánh giá</h2>
              {patientInfo && (
                <p className="text-sm text-gray-500">
                  {patientInfo.caseId} • {systemLabel} • {difficultyLabel}
                </p>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <XMarkIcon className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="w-16 h-16 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mb-4" />
              <p className="text-gray-600 font-medium">Đang đánh giá kết quả...</p>
              <p className="text-sm text-gray-400 mt-1">Vui lòng đợi trong giây lát</p>
            </div>
          ) : evaluation ? (
            <div className="space-y-6">
              {/* Overall Score */}
              <div className="text-center py-6">
                <div className={`inline-flex items-center justify-center w-32 h-32 rounded-full bg-gradient-to-br ${getScoreBg(evaluation.overallScore)} shadow-lg mb-4`}>
                  <div className="text-center">
                    <span className="text-4xl font-bold text-white">{evaluation.overallScore}</span>
                    <span className="text-white/80 text-lg">/{evaluation.maxScore}</span>
                  </div>
                </div>
                <h3 className={`text-2xl font-bold ${getScoreColor(evaluation.overallScore)}`}>
                  {evaluation.overallScore >= 80 ? 'Xuất sắc!' : 
                   evaluation.overallScore >= 60 ? 'Khá tốt' : 'Cần cải thiện'}
                </h3>
              </div>

              {/* Sub Scores */}
              <div className="bg-gray-50 rounded-xl p-5 space-y-4">
                <h4 className="font-semibold text-gray-800 mb-3">Điểm chi tiết</h4>
                <ScoreBar 
                  score={evaluation.subScores.historyTaking} 
                  maxScore={30} 
                  label="Kỹ năng hỏi bệnh" 
                />
                <ScoreBar 
                  score={evaluation.subScores.physicalExamination} 
                  maxScore={20} 
                  label="Khám thực thể" 
                />
                <ScoreBar 
                  score={evaluation.subScores.diagnosis} 
                  maxScore={30} 
                  label="Chẩn đoán" 
                />
                <ScoreBar 
                  score={evaluation.subScores.managementPlan} 
                  maxScore={20} 
                  label="Kế hoạch xử trí" 
                />
              </div>

              {/* Your Diagnosis */}
              {diagnosis && (
                <div className="bg-blue-50 rounded-xl p-5">
                  <h4 className="font-semibold text-blue-800 mb-3">Chẩn đoán của bạn</h4>
                  <div className="space-y-2 text-sm">
                    <p><span className="text-blue-600 font-medium">Chẩn đoán sơ bộ:</span> {diagnosis.provisionalDiagnosis}</p>
                    {diagnosis.differentialDiagnoses.length > 0 && (
                      <p><span className="text-blue-600 font-medium">Chẩn đoán phân biệt:</span> {diagnosis.differentialDiagnoses.join(', ')}</p>
                    )}
                  </div>
                </div>
              )}

              {/* Strengths */}
              {evaluation.strengths.length > 0 && (
                <div className="bg-green-50 rounded-xl p-5">
                  <h4 className="font-semibold text-green-800 mb-3 flex items-center gap-2">
                    <CheckIcon className="w-5 h-5" />
                    Điểm mạnh
                  </h4>
                  <ul className="space-y-2">
                    {evaluation.strengths.map((s, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-green-700">
                        <span className="text-green-500 mt-0.5">✓</span>
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Weaknesses */}
              {evaluation.weaknesses.length > 0 && (
                <div className="bg-red-50 rounded-xl p-5">
                  <h4 className="font-semibold text-red-800 mb-3">Cần cải thiện</h4>
                  <ul className="space-y-2">
                    {evaluation.weaknesses.map((w, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-red-700">
                        <span className="text-red-500 mt-0.5">•</span>
                        {w}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Suggestions */}
              {evaluation.suggestions.length > 0 && (
                <div className="bg-amber-50 rounded-xl p-5">
                  <h4 className="font-semibold text-amber-800 mb-3">Gợi ý</h4>
                  <ul className="space-y-2">
                    {evaluation.suggestions.map((s, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-amber-700">
                        <span className="text-amber-500 mt-0.5">💡</span>
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Detailed Feedback */}
              {evaluation.detailedFeedback && (
                <div className="bg-gray-50 rounded-xl p-5">
                  <h4 className="font-semibold text-gray-800 mb-3">Nhận xét chi tiết</h4>
                  <p className="text-sm text-gray-600 whitespace-pre-line">{evaluation.detailedFeedback}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12">
              <p className="text-gray-500">Không có dữ liệu đánh giá</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 pt-0 flex gap-3">
          <button
            onClick={onBackToHome}
            className="flex-1 px-4 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors flex items-center justify-center gap-2"
          >
            <ArrowLeftIcon className="w-5 h-5" />
            Về trang chủ
          </button>
        </div>
      </div>
    </div>
  );
};

export default FeedbackPanel;
