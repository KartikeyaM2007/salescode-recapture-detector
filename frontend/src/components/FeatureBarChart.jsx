import { motion } from 'framer-motion'
import { Info } from 'lucide-react'

// Define scale and threshold logic for honest scaling
const featureConfig = {
  'fft hf ratio': { max: 1.0, warning: 0.3, danger: 0.6 },
  'moiré score': { max: 1.0, warning: 0.2, danger: 0.5 },
  'banding': { max: 1.0, warning: 0.2, danger: 0.5 },
  'edge density': { max: 0.5, warning: 0.1, danger: 0.2 },
  'laplacian sharpness': { max: 2000, warning: 500, danger: 1000 },
  'sobel mag': { max: 100, warning: 30, danger: 60 },
  'brightness': { max: 255, warning: 200, danger: 240 },
  'contrast': { max: 100, warning: 70, danger: 90 },
  'glare ratio': { max: 0.1, warning: 0.02, danger: 0.05 },
  'bezel score': { max: 1.0, warning: 0.2, danger: 0.5 },
  'paper texture': { max: 1.0, warning: 0.2, danger: 0.5 },
  'perspective': { max: 1.0, warning: 0.2, danger: 0.5 },
  'blockiness': { max: 1.0, warning: 0.3, danger: 0.6 },
  'compression diff': { max: 1.0, warning: 0.2, danger: 0.4 }
}

export function FeatureBarChart({ data, finalScore = 0 }) {
  if (!data || Object.keys(data).length === 0) return null

  const getInterpretation = (name, val) => {
    const key = name.toLowerCase()
    const conf = featureConfig[key] || { warning: 0.3, danger: 0.6, max: 1.0 }
    
    // Normalize for bar width
    const norm = Math.min(Math.max((val / conf.max) * 100, 0), 100)

    let status = 'normal'
    if (val >= conf.danger) status = 'suspicious'
    else if (val >= conf.warning) status = 'elevated'

    // Contextual downgrades (Honesty pass)
    // If model predicts real (< 0.5), high CV features are likely natural textures
    if (status === 'suspicious' && finalScore < 0.5) {
      status = 'contextual'
    }

    // Compression alone shouldn't be strongly suspicious without other cues
    if (key.includes('block') || key.includes('compress')) {
       if (status === 'suspicious' && finalScore < 0.65) status = 'elevated'
    }

    return { norm, status, confMax: conf.max }
  }

  const getStyles = (status) => {
    switch (status) {
      case 'suspicious': return { bar: 'bg-danger shadow-[0_0_8px_rgba(239,68,68,0.6)]', text: 'text-danger' }
      case 'elevated': return { bar: 'bg-warning shadow-[0_0_8px_rgba(245,158,11,0.4)]', text: 'text-warning' }
      case 'contextual': return { bar: 'bg-zinc-500 shadow-[0_0_8px_rgba(113,113,122,0.4)]', text: 'text-zinc-400' }
      default: return { bar: 'bg-primary/80 shadow-[0_0_8px_rgba(16,185,129,0.3)]', text: 'text-zinc-300' }
    }
  }

  const getLabel = (status) => {
    switch(status) {
      case 'suspicious': return 'Suspicious'
      case 'elevated': return 'Elevated'
      case 'contextual': return 'Contextual / Organic'
      default: return 'Normal / Low'
    }
  }

  return (
    <div className="flex flex-col gap-4 w-full">
      {Object.entries(data).map(([key, val], index) => {
        const value = typeof val === 'number' ? Number(val.toFixed(4)) : val
        const { norm, status, confMax } = getInterpretation(key, value)
        const styles = getStyles(status)

        return (
          <div key={index} className="flex flex-col gap-1.5 w-full group relative">
            <div className="flex justify-between items-center text-[10px] uppercase font-mono tracking-wider">
              <span className="text-zinc-400 flex items-center gap-1.5 cursor-help">
                {key}
                <div className="group/tooltip relative z-50">
                  <Info className="w-3 h-3 text-zinc-600 hover:text-zinc-300 transition-colors" />
                  <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 hidden group-hover/tooltip:block w-52 bg-zinc-900 border border-zinc-700 text-zinc-300 text-[10px] p-2.5 rounded shadow-xl normal-case pointer-events-none text-left">
                    <p className="font-bold text-zinc-100 border-b border-zinc-800 pb-1 mb-1">Raw: {value} <span className="text-zinc-500 font-normal">(Scale: 0 - {confMax})</span></p>
                    <p className="text-zinc-400">Interpretation: <span className={`font-bold ${styles.text}`}>{getLabel(status)}</span></p>
                    {status === 'contextual' && <p className="mt-1 text-primary">High magnitude, but model context suggests this is natural texture.</p>}
                    {status === 'suspicious' && <p className="mt-1 text-danger">Strong signal contributing to screen probability.</p>}
                    <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-zinc-900 border-b border-r border-zinc-700 rotate-45"></div>
                  </div>
                </div>
              </span>
              <span className={`font-bold ${styles.text}`}>
                {value}
              </span>
            </div>
            <div className="w-full h-1.5 bg-zinc-800/80 rounded-full overflow-visible">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: `${norm}%` }}
                transition={{ duration: 0.8, delay: index * 0.05, ease: "easeOut" }}
                className={`h-full rounded-full ${styles.bar}`}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}
