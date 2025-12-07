import React, { useRef, useEffect, useState } from 'react';
import { SendIcon } from './Icons';

interface InputAreaProps {
  onSendMessage: (text: string) => void;
  isLoading: boolean;
}

const InputArea: React.FC<InputAreaProps> = ({ onSendMessage, isLoading }) => {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [text]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!text.trim() || isLoading) return;
    onSendMessage(text);
    setText('');
    if (textareaRef.current) {
       textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full bg-transparent pb-6 pt-2 px-4 md:px-6">
      <div className="max-w-3xl mx-auto">
        <div className="relative flex items-end w-full p-2 bg-white border border-gray-300 rounded-3xl shadow-lg focus-within:ring-2 focus-within:ring-primary-500/20 focus-within:border-primary-500 transition-all">
          <textarea
            ref={textareaRef}
            rows={1}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Nhập câu hỏi khám bệnh..."
            className="w-full max-h-[150px] py-3 pl-4 pr-12 bg-transparent border-none resize-none focus:ring-0 text-slate-800 placeholder-slate-400 text-base"
            disabled={isLoading}
          />
          <button
            onClick={() => handleSubmit()}
            disabled={!text.trim() || isLoading}
            className={`absolute right-2 bottom-2 p-2 rounded-full transition-all duration-200 ${
              text.trim() && !isLoading 
                ? 'bg-primary-600 text-white hover:bg-primary-700 shadow-md transform hover:scale-105' 
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            }`}
          >
            <SendIcon className="w-5 h-5" />
          </button>
        </div>
        <p className="text-center text-[10px] md:text-xs text-slate-400 mt-3 font-medium">
          Đây là bệnh nhân ảo để luyện tập. Câu trả lời chỉ mang tính tham khảo.
        </p>
      </div>
    </div>
  );
};

export default InputArea;