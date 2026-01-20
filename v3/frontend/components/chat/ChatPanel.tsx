'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  Send,
  Loader2,
  Map,
  FileText,
  Sparkles,
  Settings,
  MessageSquare,
  Mic,
  Paperclip,
} from 'lucide-react';
import { useChatStore } from '@/stores/chatStore';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  intent?: string;
  mapActions?: MapAction[];
  suggestions?: string[];
  isLoading?: boolean;
}

interface MapAction {
  type: 'highlight' | 'zoom' | 'filter' | 'layer';
  payload: Record<string, any>;
  label: string;
}

interface Parcel {
  id: string;
  address: string;
  zone_code: string;
}

interface ChatContext {
  current_parcel?: string;
  current_address?: string;
  current_zone?: string;
  visible_parcels?: string[];
  active_layers?: string[];
}

interface ChatPanelProps {
  selectedParcel?: Parcel | null;
  context?: ChatContext;
  onMapAction: (action: MapAction) => void;
  className?: string;
}

export function ChatPanel({
  selectedParcel,
  context,
  onMapAction,
  className,
}: ChatPanelProps) {
  const [input, setInput] = useState('');
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const { messages, isLoading, sendMessage, clearMessages } = useChatStore();

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  // Auto-focus input when parcel is selected
  useEffect(() => {
    if (selectedParcel) {
      setInput(`Tell me about ${selectedParcel.address}`);
      inputRef.current?.focus();
    }
  }, [selectedParcel]);

  const handleSend = useCallback(async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');

    await sendMessage(userMessage, {
      ...context,
      selected_parcel: selectedParcel?.id,
    });
  }, [input, isLoading, sendMessage, context, selectedParcel]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
    inputRef.current?.focus();
  };

  const handleMapActionClick = (action: MapAction) => {
    onMapAction(action);
  };

  return (
    <div className={cn('flex flex-col bg-background', className)}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-primary" />
          </div>
          <div>
            <h2 className="font-semibold text-sm">AI Zoning Expert</h2>
            {selectedParcel && (
              <p className="text-xs text-muted-foreground">
                Analyzing {selectedParcel.address}
              </p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" onClick={clearMessages}>
            <MessageSquare className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="icon">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
        <div className="space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-8">
              <Sparkles className="w-12 h-12 mx-auto text-muted-foreground/50 mb-4" />
              <h3 className="font-medium text-lg mb-2">
                Welcome to ZoneWise AI
              </h3>
              <p className="text-sm text-muted-foreground max-w-sm mx-auto">
                Ask me about zoning, permitted uses, or click on a parcel on the
                map to get started.
              </p>
              <div className="mt-6 flex flex-wrap justify-center gap-2">
                {[
                  'What can I build at 123 Main St?',
                  'Show me R-2 zones in Satellite Beach',
                  'What is FAR?',
                ].map((suggestion) => (
                  <Button
                    key={suggestion}
                    variant="outline"
                    size="sm"
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    {suggestion}
                  </Button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              onMapAction={handleMapActionClick}
              onSuggestionClick={handleSuggestionClick}
            />
          ))}

          {isLoading && (
            <div className="flex items-start gap-3">
              <Avatar className="w-8 h-8">
                <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                  AI
                </AvatarFallback>
              </Avatar>
              <div className="flex items-center gap-2 px-4 py-2 bg-muted rounded-2xl rounded-tl-none">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm text-muted-foreground">
                  Analyzing...
                </span>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Suggested actions (if last message has them) */}
      {messages.length > 0 &&
        messages[messages.length - 1].suggestions &&
        messages[messages.length - 1].suggestions!.length > 0 && (
          <div className="px-4 py-2 border-t bg-muted/30">
            <p className="text-xs text-muted-foreground mb-2">
              Suggested follow-ups:
            </p>
            <div className="flex flex-wrap gap-2">
              {messages[messages.length - 1].suggestions!.map((suggestion, i) => (
                <Button
                  key={i}
                  variant="outline"
                  size="sm"
                  className="text-xs"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          </div>
        )}

      {/* Input */}
      <div className="p-4 border-t">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" className="shrink-0">
            <Paperclip className="w-4 h-4" />
          </Button>
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              selectedParcel
                ? `Ask about ${selectedParcel.address}...`
                : 'Ask about any property or zoning question...'
            }
            className="flex-1"
            disabled={isLoading}
          />
          <Button variant="ghost" size="icon" className="shrink-0">
            <Mic className="w-4 h-4" />
          </Button>
          <Button
            size="icon"
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}

// Message bubble component
function MessageBubble({
  message,
  onMapAction,
  onSuggestionClick,
}: {
  message: Message;
  onMapAction: (action: MapAction) => void;
  onSuggestionClick: (suggestion: string) => void;
}) {
  const isUser = message.role === 'user';

  return (
    <div className={cn('flex items-start gap-3', isUser && 'flex-row-reverse')}>
      <Avatar className="w-8 h-8">
        <AvatarFallback
          className={cn(
            'text-xs',
            isUser
              ? 'bg-secondary text-secondary-foreground'
              : 'bg-primary text-primary-foreground'
          )}
        >
          {isUser ? 'You' : 'AI'}
        </AvatarFallback>
      </Avatar>

      <div
        className={cn(
          'max-w-[80%] space-y-2',
          isUser ? 'items-end' : 'items-start'
        )}
      >
        <div
          className={cn(
            'px-4 py-2 rounded-2xl',
            isUser
              ? 'bg-primary text-primary-foreground rounded-tr-none'
              : 'bg-muted rounded-tl-none'
          )}
        >
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        </div>

        {/* Intent badge */}
        {message.intent && (
          <Badge variant="outline" className="text-xs">
            {message.intent}
          </Badge>
        )}

        {/* Map actions */}
        {message.mapActions && message.mapActions.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {message.mapActions.map((action, i) => (
              <Button
                key={i}
                variant="secondary"
                size="sm"
                className="text-xs"
                onClick={() => onMapAction(action)}
              >
                <Map className="w-3 h-3 mr-1" />
                {action.label}
              </Button>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <p className="text-xs text-muted-foreground">
          {new Date(message.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}

export default ChatPanel;
