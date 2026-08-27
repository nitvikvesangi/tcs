import React, { useState, useRef, useEffect } from 'react';
import { generateChatResponse } from '../services/chatService';
import { MessageSquare, X, Send, Sparkles, Loader2 } from 'lucide-react';
import { cn } from './ActionBadge';

export const AIChatbot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<{role: 'user'|'ai', text: string}[]>([
    { role: 'ai', text: "Hi! I can help you understand promotion opportunities, inventory risks and AI recommendations." }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestedQuestions = [
    "Which products should I promote?",
    "Which products have stockout risk?",
    "Show me high-demand products.",
    "Which products need clearance?",
    "Which store has the most promotion opportunities?"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) scrollToBottom();
  }, [messages, isOpen, isTyping]);

  const handleSend = async (text: string) => {
    if (!text.trim()) return;
    
    setMessages(prev => [...prev, { role: 'user', text }]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await generateChatResponse(text);
      setMessages(prev => [...prev, { role: 'ai', text: response }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'ai', text: "Sorry, I encountered an error analyzing the data." }]);
    } finally {
      setIsTyping(false);
    }
  };

  // Format basic markdown (bold)
  const formatText = (text: string) => {
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="font-semibold text-slate-900">{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <button 
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 bg-slate-900 text-white px-5 py-3 rounded-full shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 flex items-center gap-2 font-medium border border-slate-700"
        >
          <Sparkles size={18} className="text-purple-400" /> QuickAI Assistant
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-[380px] max-w-[calc(100vw-32px)] bg-white rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden animate-in slide-in-from-bottom-5 h-[600px] max-h-[80vh]">
          {/* Header */}
          <div className="bg-slate-900 p-4 text-white flex justify-between items-center shrink-0">
            <div>
              <div className="flex items-center gap-2 font-semibold text-lg">
                <Sparkles size={18} className="text-purple-400" /> QuickAI Assistant
              </div>
              <div className="text-xs text-slate-400 mt-1">Your quick-commerce intelligence assistant</div>
            </div>
            <button onClick={() => setIsOpen(false)} className="p-1.5 hover:bg-slate-800 rounded-lg transition-colors text-slate-400 hover:text-white">
              <X size={20} />
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50">
            {messages.map((msg, idx) => (
              <div key={idx} className={cn("flex", msg.role === 'user' ? 'justify-end' : 'justify-start')}>
                <div className={cn(
                  "max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-sm",
                  msg.role === 'user' 
                    ? "bg-purple-600 text-white rounded-br-sm" 
                    : "bg-white border border-slate-200 text-slate-700 rounded-bl-sm"
                )}>
                  {formatText(msg.text)}
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-sm px-4 py-3 flex gap-1 shadow-sm">
                  <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce delay-150" />
                  <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce delay-300" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Questions */}
          {messages.length < 3 && !isTyping && (
            <div className="px-4 pb-2 bg-slate-50/50 shrink-0">
              <div className="text-xs font-semibold text-slate-500 mb-2 uppercase tracking-wide">Suggested</div>
              <div className="flex gap-2 overflow-x-auto pb-2 hide-scrollbar">
                {suggestedQuestions.map((q, idx) => (
                  <button 
                    key={idx}
                    onClick={() => handleSend(q)}
                    className="shrink-0 bg-white border border-slate-200 hover:border-purple-300 text-xs text-slate-600 hover:text-purple-700 px-3 py-1.5 rounded-full transition-colors whitespace-nowrap shadow-sm"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="p-4 bg-white border-t border-slate-200 shrink-0">
            <form 
              onSubmit={(e) => { e.preventDefault(); handleSend(input); }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="Ask about recommendations..."
                className="flex-1 bg-slate-100 border-transparent rounded-full px-4 py-2.5 text-sm outline-none focus:bg-white focus:border-purple-400 focus:ring-2 focus:ring-purple-100 transition-all"
              />
              <button 
                type="submit" 
                disabled={!input.trim() || isTyping}
                className="w-10 h-10 rounded-full bg-slate-900 text-white flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed hover:bg-purple-600 transition-colors"
              >
                <Send size={16} className="ml-1" />
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
};
