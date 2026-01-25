'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, MapPin, FileText, Brain } from 'lucide-react';
import { ThinkingDisplay } from '../ThinkingDisplay';
import { CitationDisplay } from '../CitationDisplay';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  intent?: string;
  thinking?: string[];
  citations?: Citation[];
  parcelId?: string;
}

interface Citation {
  source: string;
  url: string;
  title: string;
}

interface ChatPanelProps {
  sessionId: string;
  onParcelSelect: (parcelId: string) => void;
  onArtifact?: (artifact: any) => void;
}

const INTENT_COLORS: Record<string, string> = {
  FEASIBILITY: 'bg-green-100 text-green-800',
  CALCULATION: 'bg-blue-100 text-blue-800',
  LOOKUP: 'bg-purple-100 text-purple-800',
  HBU: 'bg-orange-100 text-orange-800',
  COMPARISON: 'bg-yellow-100 text-yellow-800',
  REPORT: 'bg-pink-100 text-pink-800',
};

export function ChatPanel({ sessionId, onParcelSelect, onArtifact }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentThinking, setCurrentThinking] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setCurrentThinking([]);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage.content,
          sessionId,
          history: messages.slice(-10),
        }),
      });

      if (!response.ok) throw new Error('Chat request failed');

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      const decoder = new TextDecoder();
      let assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: '',
        thinking: [],
        citations: [],
      };

      setMessages((prev) => [...prev, assistantMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter((line) => line.startsWith('data: '));

        for (const line of lines) {
          const data = line.slice(6);
          if (data === '[DONE]') continue;

          try {
            const parsed = JSON.parse(data);
            
            if (parsed.type === 'thinking') {
              setCurrentThinking((prev) => [...prev, parsed.value]);
              assistantMessage.thinking = [...(assistantMessage.thinking || []), parsed.value];
            } else if (parsed.type === 'intent') {
              assistantMessage.intent = parsed.value;
            } else if (parsed.type === 'content') {
              assistantMessage.content += parsed.value;
              setMessages((prev) => 
                prev.map((m) => m.id === assistantMessage.id ? { ...assistantMessage } : m)
              );
            } else if (parsed.type === 'citation') {
              assistantMessage.citations = [...(assistantMessage.citations || []), parsed.value];
            } else if (parsed.type === 'parcel') {
              assistantMessage.parcelId = parsed.value;
              onParcelSelect(parsed.value);
            } else if (parsed.type === 'artifact') {
              onArtifact?.(parsed.value);
            }
          } catch {
            // Plain text chunk
            assistantMessage.content += data;
            setMessages((prev) => 
              prev.map((m) => m.id === assistantMessage.id ? { ...assistantMessage } : m)
            );
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: 'Sorry, there was an error processing your request. Please try again.',
        },
      ]);
    } finally {
      setIsLoading(false);
      setCurrentThinking([]);
    }
  };

  return (
    <div className="flex h-full flex-col bg-white">
      {/* Header */}
      <div className="border-b px-4 py-3">
        <h2 className="text-lg font-semibold text-gray-900">ZoneWise Research</h2>
        <p className="text-sm text-gray-500">Ask about zoning, parcels, or feasibility</p>
      </div>

      {/* Thinking Display */}
      {currentThinking.length > 0 && (
        <ThinkingDisplay steps={currentThinking} isLoading={isLoading} />
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 py-8">
            <Brain className="mx-auto h-12 w-12 mb-4 opacity-50" />
            <p>Start by asking a zoning question</p>
            <div className="mt-4 space-y-2 text-sm">
              <p className="text-gray-500">"What can I build at 123 Main St?"</p>
              <p className="text-gray-500">"What are the setbacks for RS-1?"</p>
              <p className="text-gray-500">"Compare zoning in Melbourne vs Palm Bay"</p>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              {/* Intent Badge */}
              {message.intent && (
                <span
                  className={`inline-block px-2 py-0.5 rounded text-xs font-medium mb-2 ${
                    INTENT_COLORS[message.intent] || 'bg-gray-200 text-gray-700'
                  }`}
                >
                  {message.intent}
                </span>
              )}

              {/* Content */}
              <p className="whitespace-pre-wrap">{message.content}</p>

              {/* Parcel Link */}
              {message.parcelId && (
                <button
                  onClick={() => onParcelSelect(message.parcelId!)}
                  className="mt-2 flex items-center gap-1 text-sm text-blue-600 hover:underline"
                >
                  <MapPin className="h-4 w-4" />
                  View on map
                </button>
              )}

              {/* Citations */}
              {message.citations && message.citations.length > 0 && (
                <CitationDisplay citations={message.citations} />
              )}
            </div>
          </div>
        ))}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about zoning, parcels, or feasibility..."
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Send className="h-5 w-5" />
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

export default ChatPanel;
