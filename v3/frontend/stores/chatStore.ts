/**
 * ZoneWise V3 - Chat Store
 * Manages chat messages and conversation state.
 */

import { create } from 'zustand';
import axios from 'axios';

interface MapAction {
  type: 'highlight' | 'zoom' | 'filter' | 'layer';
  payload: Record<string, unknown>;
  label: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  intent?: string;
  confidence?: number;
  mapActions?: MapAction[];
  suggestions?: string[];
  isLoading?: boolean;
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  sessionId: string;
  
  sendMessage: (content: string, context?: Record<string, unknown>) => Promise<void>;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  clearMessages: () => void;
  setLoading: (loading: boolean) => void;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  sessionId: typeof window !== 'undefined' 
    ? localStorage.getItem('chat_session_id') || crypto.randomUUID()
    : crypto.randomUUID(),

  sendMessage: async (content, context) => {
    const { sessionId, addMessage, setLoading } = get();
    
    // Add user message
    addMessage({
      role: 'user',
      content,
    });
    
    setLoading(true);
    
    try {
      const response = await axios.post(`${API_URL}/api/v1/chat`, {
        message: content,
        session_id: sessionId,
        context: context || {},
      });
      
      const data = response.data;
      
      // Add assistant message
      addMessage({
        role: 'assistant',
        content: data.content,
        intent: data.intent,
        confidence: data.confidence,
        mapActions: data.map_actions,
        suggestions: data.suggestions,
      });
      
    } catch (error) {
      console.error('Chat error:', error);
      addMessage({
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
      });
    } finally {
      setLoading(false);
    }
  },

  addMessage: (message) => {
    const newMessage: Message = {
      ...message,
      id: crypto.randomUUID(),
      timestamp: new Date(),
    };
    
    set((state) => ({
      messages: [...state.messages, newMessage],
    }));
  },

  clearMessages: () => set({ messages: [] }),
  
  setLoading: (loading) => set({ isLoading: loading }),
}));
