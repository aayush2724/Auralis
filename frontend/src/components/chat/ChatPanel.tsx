import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useChat } from '../../api/hooks/useChat';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import DiagnosticsPanel from './DiagnosticsPanel';
import TypingIndicator from './TypingIndicator';
import { Button } from '../ui/Button';

export default function ChatPanel({ sessionId: initialSessionId }: { sessionId: string }) {
  const [currentSessionId, setCurrentSessionId] = useState(initialSessionId);
  const { messages, sendMessage, isLoading, lastResponse, clearMessages } = useChat(currentSessionId);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleNewSession = () => {
    setCurrentSessionId(crypto.randomUUID());
    clearMessages();
  };

  const handleSubmit = () => {
    if (!input.trim() || isLoading) return;
    sendMessage(input.trim());
    setInput('');
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

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  };

  return (
    <div className="flex flex-row h-full w-full bg-white">
      {/* Left Area: Chat */}
      <div className="flex flex-col flex-1 h-full min-w-0 relative">
        {/* Top Bar */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-auralis-frost bg-white/50 backdrop-blur-sm z-10 sticky top-0">
          <div className="flex items-center space-x-2 truncate">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="font-mono text-xs text-auralis-mist truncate">
              {currentSessionId}
            </span>
          </div>
          <Button 
            variant="outline"
            onClick={handleNewSession}
            className="flex-shrink-0"
          >
            New Session
          </Button>
        </div>

        {/* Message List */}
        <div className="flex-1 overflow-y-auto px-6 py-6 pb-32">
          <div className="max-w-3xl mx-auto flex flex-col space-y-6">
            <AnimatePresence initial={false}>
              {messages.map((msg) => {
                const isUser = msg.role === 'user';
                return (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, scale: 0.9, x: isUser ? 20 : -20, y: 10 }}
                    animate={{ opacity: 1, scale: 1, x: 0, y: 0 }}
                    transition={{ type: "spring", stiffness: 500, damping: 30, mass: 0.8 }}
                    className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} space-x-3`}
                  >
                    {!isUser && (
                      <div className="flex-shrink-0 mt-1">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-auralis-sage to-auralis-green flex items-center justify-center">
                          <Mic className="w-4 h-4 text-white" />
                        </div>
                      </div>
                    )}
                    
                    <div className={`
                      px-5 py-4 max-w-[80%] text-sm leading-relaxed shadow-sm font-sans font-light
                      ${isUser 
                        ? 'bg-auralis-green text-white rounded-2xl rounded-tr-sm' 
                        : 'bg-auralis-frost text-auralis-green rounded-2xl rounded-tl-sm'}
                    `}>
                      {isUser ? (
                        <div className="whitespace-pre-wrap">{msg.content}</div>
                      ) : (
                        <ReactMarkdown 
                          remarkPlugins={[remarkGfm]}
                          components={{
                            p: ({node, ...props}) => <p className="mb-3 last:mb-0" {...props} />,
                            ul: ({node, ...props}) => <ul className="list-disc pl-5 mb-3 last:mb-0 space-y-1.5 marker:text-auralis-sage" {...props} />,
                            ol: ({node, ...props}) => <ol className="list-decimal pl-5 mb-3 last:mb-0 space-y-1.5 marker:text-auralis-sage" {...props} />,
                            li: ({node, ...props}) => <li className="pl-1" {...props} />,
                            strong: ({node, ...props}) => <strong className="font-semibold text-current" {...props} />,
                            a: ({node, ...props}) => <a className="underline hover:opacity-80 underline-offset-2" {...props} />
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      )}
                    </div>

                    {isUser && (
                      <div className="flex-shrink-0 mt-1">
                        <div className="w-8 h-8 rounded-full bg-auralis-frost border border-auralis-cream flex items-center justify-center">
                          <span className="text-auralis-mist text-xs font-bold">U</span>
                        </div>
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </AnimatePresence>
            {isLoading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Bar */}
        <div className="absolute bottom-0 inset-x-0 bg-white border-t border-auralis-frost p-4">
          <div className="max-w-3xl mx-auto flex items-end space-x-3 bg-white">
            <textarea
              ref={textareaRef}
              rows={1}
              value={input}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              className="flex-1 rounded-2xl border border-auralis-frost px-4 py-3 resize-none outline-none focus:border-auralis-sage bg-auralis-paper focus:bg-white transition-colors text-sm max-h-[120px] font-sans font-light"
            />
            <Button
              variant="primary"
              onClick={handleSubmit}
              disabled={!input.trim() || isLoading}
              className="flex-shrink-0 w-12 h-[46px] p-0 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </div>

      {/* Right Area: Diagnostics */}
      <DiagnosticsPanel data={lastResponse} />
    </div>
  );
}
