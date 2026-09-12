import React, { useState, useEffect } from 'react';
import { cn } from './ActionBadge';

export const Toast: React.FC = () => {
  return null; // Will be implemented in context or via state if needed. Wait, simple toast event listener is better.
};

// Global toast utility
export const toast = (message: string) => {
  const event = new CustomEvent('show-toast', { detail: { message } });
  window.dispatchEvent(event);
};

export const ToastContainer: React.FC = () => {
  const [messages, setMessages] = useState<{ id: number; text: string }[]>([]);

  useEffect(() => {
    const handleToast = (e: Event) => {
      const customEvent = e as CustomEvent;
      const id = Date.now();
      setMessages(prev => [...prev, { id, text: customEvent.detail.message }]);
      setTimeout(() => {
        setMessages(prev => prev.filter(msg => msg.id !== id));
      }, 3000);
    };

    window.addEventListener('show-toast', handleToast);
    return () => window.removeEventListener('show-toast', handleToast);
  }, []);

  if (messages.length === 0) return null;

  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 flex flex-col gap-2">
      {messages.map(msg => (
        <div key={msg.id} className="bg-slate-800 text-white px-4 py-2 rounded-lg shadow-lg text-sm flex items-center gap-2 animate-in slide-in-from-bottom-5">
          <span className="w-2 h-2 bg-green-400 rounded-full"></span>
          {msg.text}
        </div>
      ))}
    </div>
  );
};
