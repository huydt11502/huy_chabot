import React from 'react';
import ReactMarkdown from 'react-markdown';
import { BotIcon, UserIcon } from './Icons';
import { Message } from '../types';

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`w-full flex ${isUser ? 'justify-end' : 'justify-start'} mb-6 px-4 md:px-0`}>
      <div className={`flex max-w-[85%] md:max-w-[75%] gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-sm mt-auto mb-1 
          ${isUser ? 'bg-brand-600' : 'bg-white border border-gray-200'}`}>
           {isUser ? <UserIcon className="w-5 h-5 text-white" /> : <BotIcon className="w-5 h-5 text-brand-600" />}
        </div>

        {/* Bubble */}
        <div 
          className={`
            relative px-5 py-3.5 shadow-sm text-sm md:text-base leading-relaxed overflow-hidden
            ${isUser 
              ? 'bg-primary-600 text-white rounded-2xl rounded-br-sm user-bubble' 
              : 'bg-white text-slate-800 border border-gray-100 rounded-2xl rounded-bl-sm'
            }
          `}
        >
          <div className="markdown-body">
            {message.content === '' && !isUser ? (
               <div className="flex items-center space-x-1 h-6">
                  <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
               </div>
            ) : (
              <ReactMarkdown 
                components={{
                  // Custom styling for markdown elements inside bubbles
                  a: ({node, ...props}) => <a {...props} className={`underline ${isUser ? 'text-white' : 'text-primary-600'}`} target="_blank" rel="noopener noreferrer" />,
                  code: ({node, ...props}) => <code {...props} className={`${isUser ? 'bg-primary-700 text-white' : 'bg-gray-100 text-pink-600'}`} />
                }}
              >
                {message.content}
              </ReactMarkdown>
            )}
            
            {message.isError && (
              <div className="mt-2 text-red-500 text-xs flex items-center gap-1 bg-red-50 p-2 rounded">
                 ⚠️ Lỗi phản hồi.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default React.memo(MessageBubble);