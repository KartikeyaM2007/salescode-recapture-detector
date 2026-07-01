import { motion, AnimatePresence } from 'framer-motion'
import { X, Microscope, AlertTriangle, CheckCircle } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Cell } from 'recharts'

export function MethodologyDrawer({ isOpen, onClose }) {
  if (!isOpen) return null

  const metricsData = [
    { name: 'ICL Accuracy', value: 98.9, type: 'ICL' },
    { name: 'ICL F1', value: 99.2, type: 'ICL' },
    { name: 'Phone 5-Fold CV (Honest)', value: 79.5, type: 'Honest' },
    { name: 'Phone Calibration*', value: 100, type: 'Calibration' }
  ]

  const getBarColor = (type) => {
    if (type === 'ICL') return '#10b981'
    if (type === 'Honest') return '#f59e0b'
    return '#3f3f46'
  }

  // Mini Pipeline Diagram Animation Variants
  const nodeVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: i => ({ opacity: 1, scale: 1, transition: { delay: i * 0.2, duration: 0.4 } })
  }

  const pipelineSteps = [
    "Image Input", 
    "Preprocessing (1024px, Denoise)", 
    "CV Extraction (21 features)", 
    "Frequency / FFT Analysis", 
    "XGBoost Score", 
    "Rule Boost / Context", 
    "Final Risk Score"
  ]

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[100]"
            onClick={onClose}
          />
          <motion.div 
            initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed top-0 right-0 h-full w-full max-w-2xl bg-zinc-950 border-l border-zinc-800 shadow-2xl z-[101] overflow-y-auto scrollbar-thin scrollbar-thumb-zinc-700 flex flex-col"
          >
            {/* Header */}
            <div className="sticky top-0 bg-zinc-950/90 backdrop-blur-md border-b border-zinc-800 p-4 flex justify-between items-center z-10">
              <div className="flex items-center gap-2">
                <Microscope className="w-5 h-5 text-primary" />
                <h2 className="text-sm font-bold text-zinc-100 uppercase tracking-widest">Methodology & Info</h2>
              </div>
              <button onClick={onClose} className="p-2 hover:bg-zinc-800 rounded-full transition-colors">
                <X className="w-5 h-5 text-zinc-400" />
              </button>
            </div>
            
            {/* Body */}
            <div className="p-6 flex flex-col gap-10 text-zinc-300 text-sm leading-relaxed pb-20">
              
              {/* 1. Overview */}
              <section className="space-y-3">
                <h3 className="text-lg font-bold text-zinc-100 border-b border-zinc-800 pb-2">1. Overview</h3>
                <p>The goal is to classify whether an image is a direct physical photo or a recaptured screen/printout image.</p>
                <div className="bg-zinc-900 border border-zinc-800 p-4 rounded-md font-mono text-xs">
                  <p className="text-zinc-500 mb-1">// Evaluator Command</p>
                  <p className="text-primary mb-3">$ python predict.py image.jpg</p>
                  <p className="text-zinc-500 mb-1">// Example Output (1 = Screen, 0 = Real)</p>
                  <p className="text-zinc-300">0.4870</p>
                </div>
              </section>

              {/* 2. Why this approach */}
              <section className="space-y-3">
                <h3 className="text-lg font-bold text-zinc-100 border-b border-zinc-800 pb-2">2. Why This Hybrid Approach?</h3>
                <p>Deep CNNs (ResNet, MobileNet) require significant compute, large datasets, and heavy libraries (PyTorch/TF). This assignment rewards practical, interpretable signals.</p>
                <ul className="list-disc pl-5 space-y-1 text-zinc-400">
                  <li>Fast CPU inference (~1ms for model, ~1s for CV).</li>
                  <li>No GPU required for deployment.</li>
                  <li>Interpretable feature telemetry (no black box).</li>
                  <li>Small ~360KB model footprint.</li>
                  <li>Highly suitable for future phone deployment.</li>
                </ul>
              </section>

              {/* 3. Pipeline Diagram */}
              <section className="space-y-3">
                <h3 className="text-lg font-bold text-zinc-100 border-b border-zinc-800 pb-2">3. Processing Pipeline</h3>
                <div className="bg-zinc-900/50 border border-zinc-800 p-6 rounded-md flex flex-col items-center gap-2">
                  {pipelineSteps.map((step, i) => (
                    <motion.div 
                      key={step} custom={i} variants={nodeVariants} initial="hidden" animate="visible"
                      className="flex flex-col items-center"
                    >
                      <div className="bg-zinc-950 border border-zinc-700 px-4 py-2 rounded-md text-xs font-mono text-zinc-300 shadow-lg text-center w-64">
                        {step}
                      </div>
                      {i < pipelineSteps.length - 1 && (
                        <div className="h-6 border-l-2 border-dashed border-zinc-700 my-1"></div>
                      )}
                    </motion.div>
                  ))}
                </div>
              </section>

              {/* 4. Features */}
              <section className="space-y-3">
                <h3 className="text-lg font-bold text-zinc-100 border-b border-zinc-800 pb-2">4. Feature Extraction</h3>
                <p className="text-xs text-zinc-500 italic mb-2">Note: High raw feature values are not automatically fraud. The model evaluates them contextually.</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="bg-zinc-900/40 p-3 rounded-md border border-zinc-800/60">
                    <h4 className="font-bold text-zinc-200 mb-1 text-xs uppercase">A. Color & Lighting</h4>
                    <p className="text-xs text-zinc-400">Brightness, contrast, saturation, overexposure/glare patches.</p>
                  </div>
                  <div className="bg-zinc-900/40 p-3 rounded-md border border-zinc-800/60">
                    <h4 className="font-bold text-zinc-200 mb-1 text-xs uppercase">B. Edge & Blur</h4>
                    <p className="text-xs text-zinc-400">Laplacian sharpness, Sobel magnitude, edge density.</p>
                  </div>
                  <div className="bg-zinc-900/40 p-3 rounded-md border border-zinc-800/60">
                    <h4 className="font-bold text-zinc-200 mb-1 text-xs uppercase">C. Frequency & Texture</h4>
                    <p className="text-xs text-zinc-400">FFT HF ratio, local patch FFT, moiré score, banding cues.</p>
                  </div>
                  <div className="bg-zinc-900/40 p-3 rounded-md border border-zinc-800/60">
                    <h4 className="font-bold text-zinc-200 mb-1 text-xs uppercase">D. Screen & Print Cues</h4>
                    <p className="text-xs text-zinc-400">Bezel score, perspective contour, printout paper texture.</p>
                  </div>
                  <div className="bg-zinc-900/40 p-3 rounded-md border border-zinc-800/60 sm:col-span-2">
                    <h4 className="font-bold text-zinc-200 mb-1 text-xs uppercase">E. Compression</h4>
                    <p className="text-xs text-zinc-400">JPEG blockiness, compression diff.</p>
                  </div>
                </div>
              </section>

              {/* 5. Trained Model */}
              <section className="space-y-3">
                <h3 className="text-lg font-bold text-zinc-100 border-b border-zinc-800 pb-2">5. ML Classification Layer</h3>
                <div className="bg-zinc-900 p-4 rounded-md border border-zinc-800 text-sm">
                  <p><span className="text-zinc-500 font-mono">Algorithm:</span> Phone-Adapted XGBoost Classifier</p>
                  <p><span className="text-zinc-500 font-mono">Features:</span> 21</p>
                  <p><span className="text-zinc-500 font-mono">Threshold:</span> 0.65</p>
                  <div className="mt-3 bg-black/50 p-2 rounded font-mono text-xs text-primary">
                    final_score = clamp(raw_model_score + rule_boost_total, 0, 1)
                  </div>
                </div>
                
                {/* Risk Bands */}
                <div className="mt-4">
                  <p className="text-xs font-bold text-zinc-400 uppercase mb-2">Risk Bands</p>
                  <div className="w-full h-8 flex rounded-md overflow-hidden text-black font-bold text-[10px] items-center text-center">
                    <div className="bg-success w-[35%] h-full flex items-center justify-center">0.0 - 0.35 (Real)</div>
                    <div className="bg-warning w-[30%] h-full flex items-center justify-center">0.35 - 0.65 (Review)</div>
                    <div className="bg-danger w-[35%] h-full flex items-center justify-center">0.65 - 1.0 (Screen)</div>
                  </div>
                </div>
              </section>

              {/* 6. Metrics */}
              <section className="space-y-3">
                <h3 className="text-lg font-bold text-zinc-100 border-b border-zinc-800 pb-2">6. Model Metrics</h3>
                <div className="h-64 w-full bg-zinc-900/50 border border-zinc-800 rounded-md p-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={metricsData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#27272a" />
                      <XAxis type="number" domain={[0, 100]} tick={{ fill: '#71717a' }} />
                      <YAxis dataKey="name" type="category" width={140} tick={{ fill: '#a1a1aa', fontSize: 10 }} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#18181b', border: '1px solid #3f3f46', borderRadius: '4px' }}
                        itemStyle={{ color: '#fff' }}
                      />
                      <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={16}>
                        {metricsData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={getBarColor(entry.type)} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-3">
                  <div className="bg-zinc-900/40 p-3 rounded border border-zinc-800">
                    <p className="text-[10px] uppercase text-zinc-500 font-bold mb-1">ICL Dataset</p>
                    <p className="text-xs">GroupShuffleSplit applied to ensure Leakage-Free evaluation across scenes.</p>
                  </div>
                  <div className="bg-zinc-900/40 p-3 rounded border border-zinc-800">
                    <p className="text-[10px] uppercase text-zinc-500 font-bold mb-1">Phone CV (Honest)</p>
                    <p className="text-xs">5-fold stratified cross-validation on small phone dataset.</p>
                  </div>
                  <div className="bg-zinc-900/40 p-3 rounded border border-zinc-800">
                    <p className="text-[10px] uppercase text-zinc-500 font-bold mb-1">*Calibration Set</p>
                    <p className="text-xs text-warning">100% score is on the same 53 images used to tune the threshold. Not independent.</p>
                  </div>
                </div>
              </section>

              {/* 8. Challenges */}
              <section className="space-y-3">
                <h3 className="text-lg font-bold text-zinc-100 border-b border-zinc-800 pb-2">7. Project Challenges</h3>
                <ul className="list-disc pl-5 space-y-1 text-zinc-400">
                  <li>Real photos contain text, books, screens (off), windows, and shiny patterns.</li>
                  <li>Screen recaptures often lack a visible physical bezel.</li>
                  <li>Organic textures (flowers, fabric) heavily mimic moiré and high-frequency noise.</li>
                  <li>WhatsApp/JPEG compression creates blockiness identical to digital screen pixels.</li>
                  <li>Bright sunlight patches mimic display glare.</li>
                </ul>
              </section>

              {/* 9. Feature Audit */}
              <section className="space-y-3">
                <h3 className="text-lg font-bold text-zinc-100 border-b border-zinc-800 pb-2">8. Feature Contextualization</h3>
                <p>We built an ablation suite to fix false positives on natural images:</p>
                <div className="space-y-2">
                  <div className="flex gap-2 items-start"><CheckCircle className="w-4 h-4 text-primary shrink-0 mt-0.5" /><p><strong>Moiré Flatness Penalty:</strong> Moiré is downweighted if the surrounding texture is dense/organic.</p></div>
                  <div className="flex gap-2 items-start"><CheckCircle className="w-4 h-4 text-primary shrink-0 mt-0.5" /><p><strong>Contour Requirement:</strong> Bezel and Glare rules now demand a rectangular screen contour.</p></div>
                  <div className="flex gap-2 items-start"><CheckCircle className="w-4 h-4 text-primary shrink-0 mt-0.5" /><p><strong>FFT Downweighting:</strong> Reduced naive global FFT influence to prevent flagging real sharpness as fraud.</p></div>
                  <div className="flex gap-2 items-start"><CheckCircle className="w-4 h-4 text-primary shrink-0 mt-0.5" /><p><strong>Multi-Cue Rules:</strong> Made rule boosts conservative and multi-cue only.</p></div>
                </div>
              </section>

              {/* 10. Why small and fast */}
              <section className="space-y-3">
                <h3 className="text-lg font-bold text-zinc-100 border-b border-zinc-800 pb-2">9. Why This Can Run On A Phone</h3>
                <p>The design is phone-deployable in principle because the model is lightweight.</p>
                <p className="text-xs text-zinc-400">It uses C++ backed OpenCV operations and a tiny XGBoost tree structure on 21 numeric features instead of heavy GPU tensors or cloud API calls. Future implementations can convert the logic to ONNX/TFLite or native mobile C++.</p>
              </section>

              {/* 11. Improvements */}
              <section className="space-y-3">
                <h3 className="text-lg font-bold text-zinc-100 border-b border-zinc-800 pb-2">10. What Could Be Improved</h3>
                <ul className="list-disc pl-5 space-y-1 text-zinc-400 text-xs">
                  <li>Collect massive, diverse WhatsApp-compressed real/screen datasets.</li>
                  <li>Collect more diverse printout photos and lighting conditions.</li>
                  <li>Establish a true, large-scale held-out phone test set for independent validation.</li>
                  <li>Optionally train a tiny MobileNetV3/CNN as a secondary ensemble feature.</li>
                  <li>Implement SHAP values for true causal feature attribution.</li>
                </ul>
              </section>

              {/* 12. Honesty Box */}
              <section className="mt-4">
                <div className="bg-warning/10 border border-warning/30 p-4 rounded-md flex gap-3">
                  <AlertTriangle className="w-6 h-6 text-warning shrink-0 mt-1" />
                  <p className="text-xs text-warning/90 leading-relaxed font-bold">
                    Phone metrics are limited because the phone dataset is small. The 100% phone calibration score is not an independent benchmark. The honest phone-domain CV score is around 79.5% F1. No production accuracy claim is made.
                  </p>
                </div>
              </section>

            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
