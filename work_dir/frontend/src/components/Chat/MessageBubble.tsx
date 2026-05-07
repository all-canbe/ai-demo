import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { FileText, Quote } from 'lucide-react';

export interface MessageBubbleProps {
  content: string;
  isUser: boolean;
  timestamp?: string;
  source?: {
    title: string;
    url?: string;
  };
}

export function MessageBubble({ content, isUser, timestamp, source }: MessageBubbleProps) {
  return (
    <div className={`flex items-end gap-3 mb-4 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-sm font-semibold ${
          isUser ? 'bg-primary-500 text-white' : 'bg-gray-200 text-gray-700'
        }`}
      >
        {isUser ? 'You' : 'AI'}
      </div>
      <div className={`max-w-[70%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`px-4 py-3 rounded-2xl ${
            isUser
              ? 'bg-primary-500 text-white rounded-br-md'
              : 'bg-white text-gray-800 rounded-bl-md shadow-sm border border-gray-100'
          }`}
        >
          <div className={`markdown-content ${isUser ? 'text-white' : ''}`}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {content}
            </ReactMarkdown>
          </div>
          
          {source && (
            <div className="mt-3 pt-3 border-t border-gray-200 flex items-center gap-2">
              <Quote className="w-4 h-4 text-gray-400" />
              <div className="flex items-center gap-1 text-sm text-gray-500">
                <FileText className="w-3.5 h-3.5" />
                <span>{source.title}</span>
              </div>
            </div>
          )}
        </div>
        {timestamp && (
          <p className="text-xs text-gray-400 mt-1 px-1">
            {timestamp}
          </p>
        )}
      </div>
    </div>
  );
}
