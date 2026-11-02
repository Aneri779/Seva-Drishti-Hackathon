/**
 * Toast notification system — replaces all alert() calls.
 * Usage: import { showToast } from '../components/common/Toast';
 *        showToast('Message', 'error' | 'success' | 'info' | 'warning');
 */
import { useState, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';

let toastQueue = [];
let toastListeners = [];

export function showToast(message, type = 'info', durationMs = 5000) {
  const id = Date.now() + Math.random();
  const toast = { id, message, type, durationMs };
  toastQueue = [...toastQueue, toast];
  toastListeners.forEach(fn => fn(toastQueue));
}

export function useToasts() {
  const [toasts, setToasts] = useState(toastQueue);
  useEffect(() => {
    const handler = (q) => setToasts([...q]);
    toastListeners.push(handler);
    return () => { toastListeners = toastListeners.filter(f => f !== handler); };
  }, []);
  
  const dismiss = useCallback((id) => {
    toastQueue = toastQueue.filter(t => t.id !== id);
    toastListeners.forEach(fn => fn(toastQueue));
  }, []);
  
  return { toasts, dismiss };
}

const ICONS = {
  success: 'check_circle',
  error: 'error',
  warning: 'warning',
  info: 'info',
};

const COLORS = {
  success: 'bg-green-700 text-white border-green-500',
  error: 'bg-error text-white border-red-400',
  warning: 'bg-amber-700 text-white border-amber-400',
  info: 'bg-surface-container-high text-on-surface border-outline-variant',
};

function ToastItem({ toast, onDismiss }) {
  useEffect(() => {
    const t = setTimeout(() => onDismiss(toast.id), toast.durationMs);
    return () => clearTimeout(t);
  }, [toast.id, toast.durationMs, onDismiss]);
  
  return (
    <div className={`flex items-start gap-3 px-4 py-3 rounded border shadow-lg max-w-sm w-full ${COLORS[toast.type]}`}>
      <span className="material-symbols-outlined text-base shrink-0 mt-0.5">{ICONS[toast.type]}</span>
      <p className="text-sm flex-1">{toast.message}</p>
      <button onClick={() => onDismiss(toast.id)} className="shrink-0 opacity-70 hover:opacity-100">
        <span className="material-symbols-outlined text-base">close</span>
      </button>
    </div>
  );
}

export default function ToastContainer() {
  const { toasts, dismiss } = useToasts();
  if (toasts.length === 0) return null;
  return createPortal(
    <div className="fixed bottom-6 right-6 z-[9999] flex flex-col gap-3 pointer-events-none">
      {toasts.map(t => (
        <div key={t.id} className="pointer-events-auto">
          <ToastItem toast={t} onDismiss={dismiss} />
        </div>
      ))}
    </div>,
    document.body
  );
}

