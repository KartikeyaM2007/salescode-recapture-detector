import { motion } from 'framer-motion';
import { CheckCircle2, Loader2, Image as ImageIcon, Search, Activity, Cpu, ShieldCheck, Flag } from 'lucide-react';
import { useState, useEffect } from 'react';

const WORKFLOW_STEPS = [
  { label: "Image Input", icon: ImageIcon, desc: "Load & Preprocess" },
  { label: "CV Extraction", icon: Search, desc: "Edge, Blur, Lighting" },
  { label: "Freq Analysis", icon: Activity, desc: "FFT, Moiré, Banding" },
  { label: "XGBoost", icon: Cpu, desc: "Phone-Adapted Model" },
  { label: "Rule Layer", icon: ShieldCheck, desc: "Contextual Corrections" },
  { label: "Final Score", icon: Flag, desc: "Risk Band Assigned" }
];

export function WorkflowAnimation({ isAnalyzing, isComplete }) {
  const [currentStep, setCurrentStep] = useState(-1);

  useEffect(() => {
    if (!isAnalyzing && !isComplete) {
      setCurrentStep(-1);
      return;
    }
    
    if (isComplete) {
      setCurrentStep(WORKFLOW_STEPS.length);
      return;
    }

    if (isAnalyzing) {
      setCurrentStep(0); // Honest log: wait on step 0 until backend returns
    }
  }, [isAnalyzing, isComplete]);

  return (
    <div className="flex flex-col h-full w-full justify-center px-4">
      <div className="relative">
        {/* Connector Line Background */}
        <div className="absolute left-[19px] top-4 bottom-4 w-[2px] bg-zinc-800/80 rounded-full"></div>
        
        {/* Animated Active Connector Line */}
        {currentStep >= 0 && (
          <motion.div 
            className="absolute left-[19px] top-4 w-[2px] bg-primary rounded-full shadow-[0_0_8px_rgba(16,185,129,0.8)]"
            initial={{ height: 0 }}
            animate={{ height: `${Math.min((currentStep / (WORKFLOW_STEPS.length - 1)) * 100, 100)}%` }}
            transition={{ duration: 0.5, ease: "linear" }}
          ></motion.div>
        )}

        <div className="flex flex-col gap-5 relative z-10">
          {WORKFLOW_STEPS.map((step, index) => {
            const isPast = currentStep > index;
            const isCurrent = currentStep === index;
            const isFuture = currentStep < index;
            const Icon = step.icon;

            return (
              <motion.div 
                key={step.label}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: isFuture ? 0.3 : 1, x: 0, scale: isCurrent ? 1.02 : 1 }}
                transition={{ duration: 0.3 }}
                className={`flex items-center gap-4 py-1 ${isPast ? 'text-zinc-400' : isCurrent ? 'text-zinc-200' : 'text-zinc-600'}`}
              >
                <div className={`relative flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors duration-300 ${isPast ? 'bg-zinc-900 border-primary text-primary' : isCurrent ? 'bg-primary/20 border-primary text-primary shadow-[0_0_15px_rgba(16,185,129,0.4)]' : 'bg-zinc-900 border-zinc-800 text-zinc-600'}`}>
                  {isCurrent ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : isPast ? (
                    <CheckCircle2 className="w-5 h-5" />
                  ) : (
                    <Icon className="w-5 h-5" />
                  )}
                </div>
                <div className="flex flex-col">
                  <span className={`text-[11px] uppercase tracking-widest ${isCurrent ? 'font-bold text-primary drop-shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'font-semibold'}`}>
                    {step.label}
                  </span>
                  <span className="text-[10px] text-zinc-500 font-mono mt-0.5">{step.desc}</span>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
