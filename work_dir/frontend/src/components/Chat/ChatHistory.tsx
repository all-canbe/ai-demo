import { useRef, useEffect } from 'react';
import { MessageBubble } from './MessageBubble';
import { MessageLoading } from '../Loading';

export interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp?: string;
  source?: {
    title: string;
    url?: string;
  };
}

interface ChatHistoryProps {
  messages: Message[];
  isLoading: boolean;
}

export function ChatHistory({ messages, isLoading }: ChatHistoryProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto p-4 bg-gray-50 scrollbar-thin">
      <div className="max-w-4xl mx-auto space-y-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} {...message} />
        ))}
        {isLoading && <MessageLoading />}
        <div ref={scrollRef} />
      </div>
    </div>
  );
}
