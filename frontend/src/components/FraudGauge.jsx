import { motion } from 'framer-motion'

export function FraudGauge({ score, threshold = 0.65 }) {
  const percentage = Math.round(score * 100)
  const threshPercent = Math.round(threshold * 100)
  
  let colorClass = 'text-success'
  if (score >= 0.35 && score < threshold) colorClass = 'text-warning'
  if (score >= threshold) colorClass = 'text-danger'
  
  return (
    <div className="flex flex-col items-center justify-center w-full relative">
      <div className="relative w-40 h-40 flex items-center justify-center">
        {/* Background Track */}
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          {/* Base Track */}
          <circle 
            cx="50" cy="50" r="45" 
            fill="none" stroke="currentColor" strokeWidth="6" 
            className="text-zinc-800/80"
          />
          {/* Animated Value Track */}
          <motion.circle
            cx="50" cy="50" r="45"
            fill="none" stroke="currentColor" strokeWidth="6"
            className={`${colorClass} drop-shadow-md`}
            strokeLinecap="round"
            initial={{ strokeDasharray: "0 283" }}
            animate={{ strokeDasharray: `${percentage * 2.83} 283` }}
            transition={{ duration: 1.5, ease: [0.16, 1, 0.3, 1] }} // smooth apple-like ease
          />
        </svg>

        {/* Threshold Marker */}
        <div 
          className="absolute inset-0 pointer-events-none"
          style={{ transform: `rotate(${threshPercent * 3.6 - 90}deg)` }}
        >
          <div className="absolute top-[2px] left-[50%] w-1 h-3 bg-zinc-300 -translate-x-1/2 rounded-full shadow-[0_0_5px_rgba(255,255,255,0.5)]"></div>
        </div>
        
        {/* Inner Text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-4xl font-black tracking-tighter ${colorClass} drop-shadow-sm`}>
            <motion.span
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              {percentage}%
            </motion.span>
          </span>
          <span className="text-[9px] text-zinc-500 uppercase tracking-widest mt-1 font-bold">Fraud Risk</span>
        </div>
      </div>
    </div>
  )
}

