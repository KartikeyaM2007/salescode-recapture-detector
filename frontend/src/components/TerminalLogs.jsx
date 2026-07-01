import { useEffect, useMemo, useRef } from 'react';
import { Activity } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const IDLE_LOGS = [
  "SalesCode Recapture Detector initialized.",
  "Loading Phone-Adapted XGBoost weights...",
  "System ready. Awaiting image input."
];

const LOADING_LOGS = [
  "Uploading image to analysis engine...",
  "Waiting for backend response..."
];

export function TerminalLogs({ logs, isLoading = false, isIdle = false }) {
  const scrollRef = useRef(null);

  const displayLogs = useMemo(() => {
    if (isIdle) return IDLE_LOGS;
    if (logs?.length > 0) return logs;
    return LOADING_LOGS;
  }, [logs, isIdle]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [displayLogs]);

  return (
    <div className="bg-zinc-950/80 backdrop-blur p-4 h-full flex flex-col font-mono text-[11px] overflow-hidden min-h-[250px] shadow-inner relative">
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-transparent pb-6"
      >
        <AnimatePresence>
          {displayLogs.map((log, i) => (
            <motion.div 
              key={i} 
              initial={{ opacity: 0, x: -5 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex gap-3 text-zinc-400 items-start"
            >
              <span className="text-zinc-600 select-none opacity-50 shrink-0 mt-0.5">{String(i + 1).padStart(2, '0')}</span>
              <span className={`leading-relaxed ${i === displayLogs.length - 1 && isLoading ? 'text-zinc-300' : 'text-zinc-400'}`}>
                {log}
              </span>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {isLoading && displayLogs.length > 0 && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-3 text-zinc-500 mt-2 items-center"
          >
            <span className="opacity-50 shrink-0">--</span>
            <span className="flex items-center gap-1">
              Processing<span className="animate-pulse">...</span>
              <Activity className="w-3 h-3 ml-2 text-primary animate-spin" />
            </span>
          </motion.div>
        )}

        {/* Blinking Cursor */}
        <div className="flex gap-3 text-primary mt-1">
          <span className="opacity-0">00</span>
          <span className="w-2 h-4 bg-primary animate-[pulse_1s_infinite]"></span>
        </div>
      </div>
      
      {/* Scanline overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_4px,3px_100%] pointer-events-none opacity-20"></div>
    </div>
  );
}
