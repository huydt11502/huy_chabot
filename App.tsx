import React, { useState, useEffect, useCallback } from 'react';
import { Message, TrainingSession, CaseConfig, DiagnosisSubmission } from './types';
import { MIN_INTERACTION_TURNS, CLINICAL_SYSTEMS, DIFFICULTY_LEVELS } from './constants';
import { sendMessageStream, generateCase, evaluateSession } from './services/geminiService';
import Sidebar from './components/Sidebar';
import MessageBubble from './components/MessageBubble';
import InputArea from './components/InputArea';
import CaseTypeModal from './components/CaseTypeModal';
import DiagnosisForm from './components/DiagnosisForm';
import FeedbackPanel from './components/FeedbackPanel';
import { MenuIcon, HeartPulseIcon, ChildIcon, PlayIcon, HistoryIcon, DocumentTextIcon } from './components/Icons';

const App: React.FC = () => {
  const [sessions, setSessions] = useState<TrainingSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  // Modal states
  const [showCaseModal, setShowCaseModal] = useState(false);
  const [showDiagnosisForm, setShowDiagnosisForm] = useState(false);
  const [showFeedbackPanel, setShowFeedbackPanel] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);

  // Load from local storage on mount
  useEffect(() => {
    const saved = localStorage.getItem('pediatric_training_sessions');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setSessions(parsed);
      } catch (e) {
        console.error("Failed to load sessions", e);
      }
    }
  }, []);

  // Save to local storage whenever sessions change
  useEffect(() => {
    localStorage.setItem('pediatric_training_sessions', JSON.stringify(sessions));
  }, [sessions]);

  const currentSession = sessions.find(s => s.id === currentSessionId);
  const messages = currentSession?.messages || [];
  const interactionCount = messages.filter(m => m.role === 'user').length;

  // Start a new case
  const handleStartCase = useCallback(async (config: CaseConfig) => {
    setShowCaseModal(false);
    setIsLoading(true);

    const newSession: TrainingSession = {
      id: Date.now().toString(),
      caseConfig: config,
      patientInfo: null,
      messages: [],
      diagnosis: null,
      evaluation: null,
      status: 'in-progress',
      interactionCount: 0,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };

    setSessions(prev => [newSession, ...prev]);
    setCurrentSessionId(newSession.id);

    try {
      // Generate case from AI
      const { patientInfo, openingMessage } = await generateCase(config);
      
      const initialMessage: Message = {
        id: Date.now().toString(),
        role: 'model',
        content: openingMessage,
        timestamp: Date.now(),
      };

      setSessions(prev => prev.map(s => 
        s.id === newSession.id 
          ? { ...s, patientInfo, messages: [initialMessage], updatedAt: Date.now() }
          : s
      ));
    } catch (error) {
      console.error('Failed to generate case:', error);
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'model',
        content: 'Xin lỗi, không thể tạo ca bệnh lúc này. Vui lòng thử lại sau.',
        timestamp: Date.now(),
        isError: true,
      };
      setSessions(prev => prev.map(s => 
        s.id === newSession.id 
          ? { ...s, messages: [errorMessage] }
          : s
      ));
    } finally {
      setIsLoading(false);
    }
  }, []);

  const deleteSession = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setSessions(prev => prev.filter(s => s.id !== id));
    if (currentSessionId === id) {
      setCurrentSessionId(null);
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!currentSessionId || !currentSession) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: Date.now()
    };

    setSessions(prev => prev.map(session => {
      if (session.id === currentSessionId) {
        return {
          ...session,
          messages: [...session.messages, userMsg],
          interactionCount: session.interactionCount + 1,
          updatedAt: Date.now()
        };
      }
      return session;
    }));

    setIsLoading(true);

    const botMsgId = (Date.now() + 1).toString();
    const botMsgPlaceholder: Message = {
      id: botMsgId,
      role: 'model',
      content: '',
      timestamp: Date.now()
    };

    setSessions(prev => prev.map(s => 
      s.id === currentSessionId 
        ? { ...s, messages: [...s.messages, botMsgPlaceholder] } 
        : s
    ));

    try {
      const historyMessages = currentSession.messages;
      
      await sendMessageStream(
        historyMessages, 
        text, 
        (chunkText) => {
          setSessions(prev => prev.map(s => {
            if (s.id === currentSessionId) {
              const updatedMessages = s.messages.map(m => {
                if (m.id === botMsgId) {
                  return { ...m, content: m.content + chunkText };
                }
                return m;
              });
              return { ...s, messages: updatedMessages };
            }
            return s;
          }));
        },
        currentSession.patientInfo // Pass patient context
      );
    } catch (error) {
      setSessions(prev => prev.map(s => {
        if (s.id === currentSessionId) {
          const updatedMessages = s.messages.map(m => {
            if (m.id === botMsgId) {
              return { ...m, isError: true, content: m.content || "Xin lỗi, có lỗi xảy ra." };
            }
            return m;
          });
          return { ...s, messages: updatedMessages };
        }
        return s;
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitDiagnosis = async (diagnosis: DiagnosisSubmission) => {
    if (!currentSession) return;

    setShowDiagnosisForm(false);
    setShowFeedbackPanel(true);
    setIsEvaluating(true);

    // Update session with diagnosis
    setSessions(prev => prev.map(s => 
      s.id === currentSessionId 
        ? { ...s, diagnosis, status: 'pending-evaluation', updatedAt: Date.now() }
        : s
    ));

    try {
      // Call AI evaluator
      const evaluation = await evaluateSession(currentSession, diagnosis);
      
      setSessions(prev => prev.map(s => 
        s.id === currentSessionId 
          ? { ...s, evaluation, status: 'completed', updatedAt: Date.now() }
          : s
      ));
    } catch (error) {
      console.error('Evaluation failed:', error);
      // Keep pending status, allow retry later
    } finally {
      setIsEvaluating(false);
    }
  };

  const handleBackToHome = () => {
    setShowFeedbackPanel(false);
    setCurrentSessionId(null);
  };

  const handleViewHistory = () => {
    // Just open sidebar on mobile, sessions are already visible
    setSidebarOpen(true);
  };

  // Get labels for display
  const getSystemLabel = (system?: string) => 
    CLINICAL_SYSTEMS.find(s => s.value === system)?.label || '';
  const getDifficultyLabel = (diff?: string) => 
    DIFFICULTY_LEVELS.find(d => d.value === diff)?.label || '';

  return (
    <div className="flex h-full w-full bg-[#f8fafc] overflow-hidden">
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelectSession={(id) => {
          setCurrentSessionId(id);
          const session = sessions.find(s => s.id === id);
          if (session?.status === 'completed' && session.evaluation) {
            setShowFeedbackPanel(true);
          }
        }}
        onNewSession={() => setShowCaseModal(true)}
        onDeleteSession={deleteSession}
        onGoHome={() => setCurrentSessionId(null)}
        isOpen={sidebarOpen}
        setIsOpen={setSidebarOpen}
      />

      <div className="flex-1 flex flex-col h-full relative w-full">
        {/* Mobile Header */}
        <div className="md:hidden flex items-center justify-between p-4 border-b border-gray-200 bg-white shadow-sm z-10">
          <div className="flex items-center">
             <button onClick={() => setSidebarOpen(true)} className="p-2 -ml-2 text-brand-700 hover:bg-gray-100 rounded-lg">
                <MenuIcon />
             </button>
             <span className="font-semibold text-brand-900 ml-2 cursor-pointer" onClick={() => setCurrentSessionId(null)}>Mocha</span>
          </div>
          <HeartPulseIcon className="w-6 h-6 text-primary-600" />
        </div>

        {/* Case Header (when in consultation) */}
        {currentSession && currentSession.patientInfo && (
          <div className="bg-white border-b border-gray-200 px-4 py-3 shadow-sm">
            <div className="max-w-3xl mx-auto flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
                  <ChildIcon className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-gray-900">
                      {currentSession.patientInfo.name}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      currentSession.caseConfig.caseType === 'random' 
                        ? 'bg-blue-100 text-blue-700' 
                        : 'bg-purple-100 text-purple-700'
                    }`}>
                      {currentSession.caseConfig.caseType === 'random' ? 'Ngẫu nhiên' : 'Tùy chỉnh'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <span>{currentSession.patientInfo.age} {currentSession.patientInfo.ageUnit === 'years' ? 'tuổi' : currentSession.patientInfo.ageUnit === 'months' ? 'tháng' : 'ngày'}</span>
                    <span>•</span>
                    <span>{currentSession.patientInfo.gender === 'male' ? 'Nam' : 'Nữ'}</span>
                    <span>•</span>
                    <span>{getSystemLabel(currentSession.patientInfo.clinicalSystem)}</span>
                    <span>•</span>
                    <span className={`font-medium ${
                      currentSession.patientInfo.difficulty === 'easy' ? 'text-green-600' :
                      currentSession.patientInfo.difficulty === 'medium' ? 'text-amber-600' : 'text-red-600'
                    }`}>
                      {getDifficultyLabel(currentSession.patientInfo.difficulty)}
                    </span>
                  </div>
                </div>
              </div>
              
              {/* Proceed to Diagnosis button */}
              {currentSession.status === 'in-progress' && (
                <button
                  onClick={() => setShowDiagnosisForm(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-xl font-medium hover:bg-green-700 transition-colors text-sm"
                >
                  <DocumentTextIcon className="w-4 h-4" />
                  <span className="hidden sm:inline">Tiến hành chẩn đoán</span>
                  <span className="sm:hidden">Chẩn đoán</span>
                </button>
              )}
            </div>
          </div>
        )}

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto scroll-smooth">
          <div className="max-w-3xl mx-auto h-full w-full">
            {!currentSession ? (
                // Welcome Screen / Home
                <div className="h-full flex flex-col items-center justify-center p-6 text-center">
                    <div className="w-24 h-24 bg-gradient-to-br from-primary-500 to-blue-600 rounded-3xl shadow-2xl flex items-center justify-center mb-8 rotate-3">
                        <ChildIcon className="w-12 h-12 text-white" />
                    </div>
                    
                    <h2 className="text-3xl md:text-4xl font-bold text-brand-900 mb-4 tracking-tight">
                      Mocha - Luyện tập Khám Bệnh Nhi Ảo
                    </h2>
                    <p className="text-slate-500 max-w-lg mb-10 text-lg leading-relaxed">
                      Thực hành khám lâm sàng với bệnh nhân nhi ảo, sau đó nhận phản hồi chi tiết từ AI chuyên gia.
                    </p>
                    
                    <div className="flex flex-col sm:flex-row gap-4 w-full max-w-md">
                      <button 
                        onClick={() => setShowCaseModal(true)}
                        className="flex-1 flex items-center justify-center gap-3 px-6 py-4 bg-primary-600 text-white rounded-2xl hover:bg-primary-700 transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 font-semibold text-lg"
                      >
                        <PlayIcon className="w-6 h-6" />
                        Bắt đầu ca mới
                      </button>
                      <button 
                        onClick={handleViewHistory}
                        className="flex-1 flex items-center justify-center gap-3 px-6 py-4 bg-white border-2 border-gray-200 text-gray-700 rounded-2xl hover:border-primary-300 hover:bg-primary-50 transition-all shadow-md font-semibold text-lg"
                      >
                        <HistoryIcon className="w-6 h-6" />
                        Lịch sử luyện tập
                      </button>
                    </div>

                    {/* Quick Info Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-2xl mt-12">
                      <div className="p-4 bg-white border border-gray-200 rounded-xl text-left">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mb-3">
                          <span className="text-xl">🩺</span>
                        </div>
                        <h3 className="font-semibold text-gray-800 mb-1">Hỏi bệnh</h3>
                        <p className="text-sm text-gray-500">Khai thác tiền sử và triệu chứng từ bệnh nhân ảo</p>
                      </div>
                      <div className="p-4 bg-white border border-gray-200 rounded-xl text-left">
                        <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mb-3">
                          <span className="text-xl">📋</span>
                        </div>
                        <h3 className="font-semibold text-gray-800 mb-1">Chẩn đoán</h3>
                        <p className="text-sm text-gray-500">Đưa ra chẩn đoán và kế hoạch điều trị</p>
                      </div>
                      <div className="p-4 bg-white border border-gray-200 rounded-xl text-left">
                        <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center mb-3">
                          <span className="text-xl">⭐</span>
                        </div>
                        <h3 className="font-semibold text-gray-800 mb-1">Đánh giá</h3>
                        <p className="text-sm text-gray-500">Nhận feedback chi tiết từ AI chuyên gia</p>
                      </div>
                    </div>
                </div>
            ) : (
                // Consultation Chat
                <div className="flex flex-col py-6 w-full">
                  {messages.length === 0 && isLoading ? (
                    <div className="flex flex-col items-center justify-center py-12">
                      <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mb-4" />
                      <p className="text-gray-500">Đang tạo ca bệnh...</p>
                    </div>
                  ) : (
                    messages.map((msg) => (
                      <MessageBubble key={msg.id} message={msg} />
                    ))
                  )}
                  <div ref={(el) => { if(el) el.scrollIntoView({ behavior: 'smooth' }) }} />
                </div>
            )}
          </div>
        </div>

        {/* Input Area (only show when in consultation) */}
        {currentSession && currentSession.status === 'in-progress' && (
          <InputArea onSendMessage={handleSendMessage} isLoading={isLoading} />
        )}
      </div>

      {/* Modals */}
      <CaseTypeModal
        isOpen={showCaseModal}
        onClose={() => setShowCaseModal(false)}
        onStartCase={handleStartCase}
      />

      <DiagnosisForm
        isOpen={showDiagnosisForm}
        onClose={() => setShowDiagnosisForm(false)}
        onSubmit={handleSubmitDiagnosis}
        interactionCount={interactionCount}
        minInteractions={MIN_INTERACTION_TURNS}
      />

      <FeedbackPanel
        isOpen={showFeedbackPanel}
        onClose={() => setShowFeedbackPanel(false)}
        evaluation={currentSession?.evaluation || null}
        diagnosis={currentSession?.diagnosis || null}
        patientInfo={currentSession?.patientInfo || null}
        isLoading={isEvaluating}
        onBackToHome={handleBackToHome}
      />
    </div>
  );
};

export default App;