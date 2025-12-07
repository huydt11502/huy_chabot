import React from 'react';
import { TrainingSession } from '../types';
import { PlusIcon, HistoryIcon, TrashIcon, HeartPulseIcon, StarIcon, FolderIcon, BookIcon } from './Icons';
import { CLINICAL_SYSTEMS, DIFFICULTY_LEVELS } from '../constants';

interface SidebarProps {
  sessions: TrainingSession[];
  currentSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
  onDeleteSession: (id: string, e: React.MouseEvent) => void;
  onGoHome: () => void;
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  isAdmin?: boolean;
}

const formatDate = (timestamp: number) => {
  const date = new Date(timestamp);
  const now = new Date();
  const isToday = date.toDateString() === now.toDateString();
  
  if (isToday) {
    return date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
  }
  return date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });
};

const getStatusColor = (status: TrainingSession['status']) => {
  switch (status) {
    case 'completed': return 'bg-green-100 text-green-700';
    case 'in-progress': return 'bg-blue-100 text-blue-700';
    case 'pending-evaluation': return 'bg-amber-100 text-amber-700';
    default: return 'bg-gray-100 text-gray-700';
  }
};

const getStatusLabel = (status: TrainingSession['status']) => {
  switch (status) {
    case 'completed': return 'Hoàn thành';
    case 'in-progress': return 'Đang khám';
    case 'pending-evaluation': return 'Chờ đánh giá';
    default: return status;
  }
};

const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  currentSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
  onGoHome,
  isOpen,
  setIsOpen,
  isAdmin = false,
}) => {
  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-brand-900/80 backdrop-blur-sm z-20 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar Container */}
      <div className={`
        fixed inset-y-0 left-0 z-30 w-[300px] bg-brand-950 text-white transform transition-transform duration-300 ease-in-out md:relative md:translate-x-0 border-r border-brand-800 flex flex-col
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
          {/* Header */}
          <div className="p-5 pb-0">
             <div 
                className="flex items-center gap-3 mb-6 px-1 cursor-pointer hover:opacity-80 transition-opacity"
                onClick={onGoHome}
             >
                <div className="w-8 h-8 bg-gradient-to-tr from-primary-600 to-primary-400 rounded-lg flex items-center justify-center shadow-lg">
                    <HeartPulseIcon className="w-5 h-5 text-white" />
                </div>
                <h1 className="font-bold text-xl tracking-wide text-gray-100">
                  Mocha
                </h1>
             </div>

            <button
              onClick={() => {
                onNewSession();
                if (window.innerWidth < 768) setIsOpen(false);
              }}
              className="group w-full flex items-center gap-3 px-4 py-3 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-xl border border-primary-500 hover:border-primary-400 transition-all shadow-md"
            >
              <PlusIcon className="w-5 h-5 text-white" />
              <span>Phiên luyện tập mới</span>
            </button>
          </div>

          {/* Training History List */}
          <div className="flex-1 overflow-y-auto px-3 py-6 scrollbar-thin">
            <div className="text-xs font-bold text-brand-400 uppercase tracking-wider px-4 mb-3 flex items-center gap-2">
              <HistoryIcon className="w-4 h-4" />
              Lịch sử luyện tập
            </div>
            {sessions.length === 0 ? (
                <div className="px-4 py-4 text-sm text-brand-500 italic text-center">
                    <p>Chưa có phiên luyện tập nào</p>
                    <p className="text-xs mt-1">Bắt đầu ca mới để luyện tập</p>
                </div>
            ) : (
                <div className="space-y-2">
                {sessions.map((session) => {
                    const systemLabel = session.patientInfo?.clinicalSystem 
                      ? CLINICAL_SYSTEMS.find(s => s.value === session.patientInfo?.clinicalSystem)?.label 
                      : 'Đang tạo...';
                    const difficultyLabel = session.patientInfo?.difficulty
                      ? DIFFICULTY_LEVELS.find(d => d.value === session.patientInfo?.difficulty)?.label
                      : '';
                    
                    return (
                      <div
                        key={session.id}
                        onClick={() => {
                            onSelectSession(session.id);
                            if (window.innerWidth < 768) setIsOpen(false);
                        }}
                        className={`
                            group relative flex flex-col gap-1.5 px-4 py-3 text-sm rounded-xl cursor-pointer transition-all duration-200
                            ${currentSessionId === session.id 
                                ? 'bg-brand-800 shadow-md ring-1 ring-primary-500/50' 
                                : 'hover:bg-brand-900'}
                        `}
                      >
                        {/* Top row: Date & Status */}
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-brand-400">
                            {formatDate(session.createdAt)}
                          </span>
                          <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${getStatusColor(session.status)}`}>
                            {getStatusLabel(session.status)}
                          </span>
                        </div>
                        
                        {/* System & Difficulty */}
                        <div className="flex items-center gap-2">
                          <span className={`font-medium truncate ${currentSessionId === session.id ? 'text-white' : 'text-brand-200'}`}>
                            {systemLabel}
                          </span>
                          {difficultyLabel && (
                            <span className="text-xs text-brand-400">• {difficultyLabel}</span>
                          )}
                        </div>

                        {/* Score (if completed) */}
                        {session.status === 'completed' && session.evaluation && (
                          <div className="flex items-center gap-1.5 mt-1">
                            <StarIcon className="w-4 h-4 text-amber-400" />
                            <span className="text-sm font-semibold text-amber-400">
                              {session.evaluation.overallScore}/{session.evaluation.maxScore}
                            </span>
                          </div>
                        )}
                        
                        {/* Delete Button */}
                        <button
                            onClick={(e) => onDeleteSession(session.id, e)}
                            className={`
                            absolute right-2 top-2 p-1.5 rounded-lg hover:bg-red-500/20 hover:text-red-400 text-brand-500 opacity-0 group-hover:opacity-100 transition-all
                            `}
                            title="Xóa phiên"
                        >
                            <TrashIcon className="w-4 h-4" />
                        </button>
                      </div>
                    );
                })}
                </div>
            )}
          </div>

          {/* Admin Menu (optional) */}
          {isAdmin && (
            <div className="px-3 py-3 border-t border-brand-800">
              <div className="text-xs font-bold text-brand-400 uppercase tracking-wider px-4 mb-2">
                Công cụ quản trị
              </div>
              <button className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-brand-300 hover:bg-brand-800/50 rounded-xl transition-colors">
                <FolderIcon className="w-4 h-4" />
                <span>Kho ca bệnh</span>
              </button>
              <button className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-brand-300 hover:bg-brand-800/50 rounded-xl transition-colors">
                <BookIcon className="w-4 h-4" />
                <span>Hướng dẫn</span>
              </button>
            </div>
          )}

          {/* User Profile */}
          <div className="p-4 border-t border-brand-800 bg-brand-950/50">
             <div className="flex items-center gap-3 px-2 py-1 cursor-pointer hover:bg-brand-800/50 rounded-lg p-2 transition-colors">
                 <div className="w-9 h-9 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center shadow-inner border border-white/10">
                    <span className="font-bold text-xs text-white">SV</span>
                 </div>
                 <div className="flex flex-col">
                    <span className="font-semibold text-sm text-gray-200">Sinh viên Y</span>
                    <span className="text-[10px] text-brand-400">Junior Doctor</span>
                 </div>
             </div>
          </div>
      </div>
    </>
  );
};

export default Sidebar;