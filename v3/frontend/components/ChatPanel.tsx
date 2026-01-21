/**
 * ZoneWise V3 - ChatPanel Component
 * AI chat interface with conversation history and parcel context.
 */

'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Loader2, MapPin, FileText, Sparkles } from 'lucide-react';

import { usePanelSyncStore } from '@/stores/panelSyncStore';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    parcelId?: string;
    analysisType?: string;
    confidence?: number;
  };
}

interface ChatPanelProps {
  className?: string;
  onSendMessage?: (message: string, context: any) => Promise<string>;
}

export function ChatPanel({ className = '', onSendMessage }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Welcome to ZoneWise! I can help you with zoning lookups, property analysis, and market comparisons. Select a parcel on the map or ask me a question.',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const { selectedParcelId, mapViewport, conversationHistory, setConversationHistory } = usePanelSyncStore();

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle parcel selection - add context message
  useEffect(() => {
    if (selectedParcelId) {
      const contextMsg: Message = {
        id: `ctx-${Date.now()}`,
        role: 'system',
        content: `Selected parcel: ${selectedParcelId}`,
        timestamp: new Date(),
        metadata: { parcelId: selectedParcelId }
      };
      setMessages(prev => [...prev, contextMsg]);
    }
  }, [selectedParcelId]);

  // Handle send message
  const handleSend = useCallback(async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Build context
      const context = {
        parcelId: selectedParcelId,
        viewport: mapViewport,
        conversationHistory: messages.slice(-10).map(m => ({ role: m.role, content: m.content }))
      };

      // Call API
      let response: string;
      if (onSendMessage) {
        response = await onSendMessage(input.trim(), context);
      } else {
        response = await sendToAPI(input.trim(), context);
      }

      const assistantMessage: Message = {
        id: `asst-${Date.now()}`,
        role: 'assistant',
        content: response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Update conversation history in store
      setConversationHistory([...conversationHistory, userMessage, assistantMessage]);

    } catch (error) {
      const errorMessage: Message = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [input, isLoading, selectedParcelId, mapViewport, messages, onSendMessage, conversationHistory, setConversationHistory]);

  // Send to API
  const sendToAPI = async (message: string, context: any): Promise<string> => {
    const response = await fetch('/api/v1/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, context })
    });

    if (!response.ok) throw new Error('API error');
    
    const data = await response.json();
    return data.response || 'No response';
  };

  // Handle keyboard shortcuts
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Quick actions
  const quickActions = [
    { label: 'Zoning', icon: MapPin, query: 'What is the zoning for this parcel?' },
    { label: 'Value', icon: FileText, query: 'Estimate the value of this property' },
    { label: 'HBU', icon: Sparkles, query: 'What is the highest and best use?' }
  ];

  return (
    <div className={`flex flex-col h-full bg-white ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <h2 className="font-semibold text-gray-900">ZoneWise AI</h2>
        {selectedParcelId && (
          <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
            {selectedParcelId.slice(0, 15)}...
          </span>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(msg => (
          <div
            key={msg.id}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'system' ? (
              <div className="w-full text-center text-xs text-gray-500 py-2">
                {msg.content}
              </div>
            ) : (
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-2 ${
                  msg.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <div className="whitespace-pre-wrap text-sm">{msg.content}</div>
                <div className={`text-xs mt-1 ${msg.role === 'user' ? 'text-blue-100' : 'text-gray-400'}`}>
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            )}
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-2xl px-4 py-3">
              <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      {selectedParcelId && (
        <div className="px-4 py-2 border-t flex gap-2">
          {quickActions.map(action => (
            <button
              key={action.label}
              onClick={() => setInput(action.query)}
              className="flex items-center gap-1 px-3 py-1.5 text-xs bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
            >
              <action.icon className="w-3 h-3" />
              {action.label}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t">
        <div className="flex items-end gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about zoning, values, or development..."
            className="flex-1 resize-none rounded-xl border border-gray-200 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={1}
            style={{ minHeight: '48px', maxHeight: '120px' }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="p-3 bg-blue-500 text-white rounded-xl hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatPanel;
