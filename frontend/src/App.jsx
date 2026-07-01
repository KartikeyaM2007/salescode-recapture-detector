import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { UploadCloud, ShieldAlert, Activity, Terminal, Shield, FileImage, Database, LayoutList, Fingerprint, RefreshCcw, FolderOpen, Info } from 'lucide-react'
import { FraudGauge } from './components/FraudGauge'
import { FeatureBarChart } from './components/FeatureBarChart'
import { TerminalLogs } from './components/TerminalLogs'
import { WorkflowAnimation } from './components/WorkflowAnimation'
import ForensicBackground from './components/ForensicBackground'
import { MethodologyDrawer } from './components/MethodologyDrawer'

export default function App() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  
  const [manifest, setManifest] = useState([])
  const [sampleTab, setSampleTab] = useState('real')
  const [selectedSample, setSelectedSample] = useState(null)
  const [isMethodologyOpen, setIsMethodologyOpen] = useState(false)
  
  const fileInputRef = useRef(null)

  const [systemInfo, setSystemInfo] = useState(null)

  useEffect(() => {
    fetch('/sample_photos/manifest.json')
      .then(r => r.json())
      .then(data => setManifest(data))
      .catch(e => console.error("Failed to load sample manifest", e))

    fetch('/api/health')
      .then(r => r.json())
      .then(data => setSystemInfo(data))
      .catch(e => console.error("Failed to load system info", e))
  }, [])

  const handleFile = (selected) => {
    if (selected) {
      setFile(selected)
      setPreview(URL.createObjectURL(selected))
      setResult(null)
      setError(null)
      setSelectedSample(null)
    }
  }

  const handleFileChange = (e) => {
    handleFile(e.target.files[0])
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleSampleClick = async (sample) => {
    try {
      const response = await fetch(sample.path)
      const blob = await response.blob()
      const sampleFile = new File([blob], sample.id + '.jpg', { type: blob.type })
      
      setFile(sampleFile)
      setPreview(sample.path)
      setResult(null)
      setError(null)
      setSelectedSample(sample)
    } catch {
      setError("Failed to load sample image")
    }
  }

  const handleAnalyze = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        body: formData
      })
      if (!response.ok) throw new Error("Analysis failed")
      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message || "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getRiskBand = (score) => {
    if (score === null || score === undefined) return null
    if (score >= 0.65) return 'screen'
    if (score >= 0.35) return 'borderline'
    return 'real'
  }

  const riskBand = result ? getRiskBand(result.score) : null
  const isHighRisk = riskBand === 'screen'
  const isSuspicious = riskBand === 'borderline'
  
  const sampleMatch = result && selectedSample 
    ? (selectedSample.label === 'screen' && result.score >= 0.65) || (selectedSample.label === 'real' && result.score < 0.65)
    : null;

  const formatThreshold = (val) => {
    if (val === null || val === undefined) return 'N/A'
    return parseFloat(val).toFixed(2)
  }

  return (
    <div className="min-h-screen pb-12 relative overflow-hidden">
      <ForensicBackground />

      {/* App Shell Topbar */}
      <header className="sticky top-0 z-50 glass-panel border-x-0 border-t-0 rounded-none shadow-sm">
        <div className="max-w-[1536px] mx-auto px-6 py-3 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-zinc-900 border border-zinc-700 flex items-center justify-center text-primary shadow-lg shadow-primary/10">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight text-zinc-100 leading-none">SalesCode Recapture Detector</h1>
              <p className="text-xs text-zinc-400 mt-1 font-mono tracking-tight">Hybrid CV + Frequency Analysis + Lightweight ML</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setIsMethodologyOpen(true)}
              className="bg-zinc-900/80 hover:bg-zinc-800 border border-zinc-700 text-zinc-300 text-[10px] uppercase tracking-wider px-3 py-1.5 rounded-md flex items-center gap-2 backdrop-blur-sm transition-colors shadow-sm cursor-pointer"
            >
              <Info className="w-3 h-3 text-primary" /> Methodology
            </button>
            <div className="bg-zinc-900/80 border border-zinc-800 text-zinc-400 text-[10px] uppercase tracking-wider px-3 py-1.5 rounded-md items-center gap-2 backdrop-blur-sm hidden lg:flex">
              <Activity className="w-3 h-3 text-primary animate-pulse" /> Full ICL + Phone-Adapted Model Active
            </div>
            <div className="font-mono text-[11px] text-zinc-500 bg-zinc-900/50 px-3 py-1.5 rounded-md border border-zinc-800/50 hidden sm:block">
              CLI: python predict.py image.jpg
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Grid */}
      <main className="max-w-[1536px] mx-auto px-6 mt-8 grid grid-cols-1 md:grid-cols-12 gap-6 relative z-10">
        
        {/* ROW 1 */}
        {/* Target Image Card */}
        <motion.div 
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="col-span-1 md:col-span-12 lg:col-span-4 soc-card-interactive flex flex-col"
        >
          <div className="bg-zinc-900/60 px-4 py-3 border-b border-zinc-800/80 flex items-center gap-2 backdrop-blur-md">
            <FileImage className="w-4 h-4 text-zinc-400" />
            <h2 className="text-xs font-bold text-zinc-300 uppercase tracking-widest">Target Image</h2>
          </div>
          <div className="p-4 flex-1 flex flex-col">
            <div 
              className={`w-full flex-1 border-2 border-dashed ${isDragging ? 'border-primary bg-primary/5' : file ? 'border-zinc-700 bg-zinc-900/30' : 'border-zinc-800 hover:border-zinc-600 hover:bg-zinc-900/40'} rounded-lg flex items-center justify-center cursor-pointer transition-all duration-300 relative min-h-[220px] overflow-hidden group`}
              onClick={() => fileInputRef.current?.click()}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <input type="file" className="hidden" ref={fileInputRef} onChange={handleFileChange} accept="image/*" />
              <AnimatePresence mode="wait">
                {preview ? (
                  <motion.img 
                    key="preview"
                    initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
                    src={preview} alt="Preview" 
                    className="w-full h-full object-contain p-2" 
                  />
                ) : (
                  <motion.div 
                    key="placeholder"
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                    className="text-center group-hover:scale-105 transition-transform duration-300"
                  >
                    <UploadCloud className={`w-10 h-10 mx-auto mb-3 ${isDragging ? 'text-primary scale-110' : 'text-zinc-600 group-hover:text-primary'} transition-all duration-300`} />
                    <p className="text-sm font-medium text-zinc-400">Drop image to inspect</p>
                    <p className="text-[10px] text-zinc-600 mt-2 uppercase tracking-widest font-mono">JPEG / PNG</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            
            <div className="mt-4 flex items-center justify-between gap-4">
              <div className="flex-1 truncate bg-zinc-900/50 border border-zinc-800 rounded-md px-3 py-2 flex flex-col justify-center h-12">
                {file ? (
                  <>
                    <p className="text-[11px] text-zinc-300 font-mono truncate">{file.name}</p>
                    <p className="text-[10px] text-zinc-500 font-mono">{formatFileSize(file.size)}</p>
                  </>
                ) : (
                  <p className="text-[11px] text-zinc-600 uppercase tracking-widest font-semibold">No File Selected</p>
                )}
              </div>
              <button 
                onClick={handleAnalyze} 
                disabled={!file || loading}
                className="bg-primary hover:bg-emerald-500 disabled:opacity-50 disabled:hover:bg-primary text-zinc-950 font-bold py-2 px-6 rounded-md text-xs tracking-wider uppercase transition-all duration-300 flex items-center gap-2 h-12 shadow-lg shadow-primary/20 active:scale-95"
              >
                {loading ? <RefreshCcw className="w-4 h-4 animate-spin" /> : "Analyze"}
              </button>
            </div>
            {error && <div className="mt-3 p-3 bg-danger/10 border border-danger/20 text-danger text-[11px] rounded-md font-mono">{error}</div>}
          </div>
        </motion.div>

        {/* Risk Score Card */}
        <motion.div 
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          className="col-span-1 md:col-span-12 lg:col-span-4 soc-card-interactive flex flex-col relative"
        >
          {loading && <div className="absolute top-0 left-0 right-0 h-1 bg-primary/20 overflow-hidden"><div className="h-full bg-primary w-1/3 animate-[translateX_1s_infinite_linear]"></div></div>}
          <div className="bg-zinc-900/60 px-4 py-3 border-b border-zinc-800/80 flex items-center gap-2 backdrop-blur-md">
            <ShieldAlert className="w-4 h-4 text-zinc-400" />
            <h2 className="text-xs font-bold text-zinc-300 uppercase tracking-widest">Fraud Assessment</h2>
          </div>
          <div className="p-4 flex-1 flex flex-col items-center justify-center relative">
            <AnimatePresence mode="wait">
              {result ? (
                <motion.div key="result" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="flex flex-col items-center w-full">
                  <FraudGauge score={result.score} threshold={result.threshold ?? 0.65} />
                  
                  <div className="mt-4 flex flex-col items-center w-full">
                    {/* Risk band label */}
                    <div className={`px-4 py-1.5 border rounded-md text-xs font-bold tracking-widest uppercase shadow-sm
                      ${isHighRisk ? 'border-danger/40 text-danger bg-danger/10 shadow-danger/10' : 
                        isSuspicious ? 'border-warning/40 text-warning bg-warning/10 shadow-warning/10' : 
                        'border-success/40 text-success bg-success/10 shadow-success/10'}
                    `}>
                      {isHighRisk ? 'Likely Recaptured/Screen' : isSuspicious ? 'Borderline / Needs Review' : 'Likely Real'}
                    </div>

                    {selectedSample && (
                      <div className="mt-3 flex flex-col items-center gap-1 bg-zinc-900/80 px-3 py-2 border border-zinc-800 rounded-md text-center w-full max-w-[240px]">
                         <p className="text-[10px] uppercase text-zinc-500 tracking-wider">Ground Truth: <span className="text-zinc-300">{selectedSample.label}</span></p>
                         <p className={`text-[10px] font-bold uppercase tracking-wider ${sampleMatch ? 'text-success' : 'text-danger'}`}>
                           {sampleMatch ? '✓ Correct Match' : '✗ Incorrect Prediction'}
                         </p>
                      </div>
                    )}

                    {/* Score breakdown */}
                    <div className="mt-5 w-full max-w-[240px] border border-zinc-800/80 bg-zinc-950/60 rounded-md overflow-hidden">
                      <div className="w-full px-3 py-2 border-b border-zinc-800/80 flex justify-between items-center text-[10px] uppercase tracking-wider">
                        <span className="text-zinc-500">Raw Model Score</span>
                        <span className="text-zinc-300 font-mono">{(result.raw_model_score ?? 0).toFixed(4)}</span>
                      </div>
                      <div className="w-full px-3 py-2 border-b border-zinc-800/80 flex justify-between items-center text-[10px] uppercase tracking-wider bg-zinc-900/30">
                        <span className="text-zinc-500">Rule Boost</span>
                        <span className={`font-mono font-bold ${(result.rule_boost_total ?? 0) > 0 ? 'text-danger' : (result.rule_boost_total ?? 0) < 0 ? 'text-success' : 'text-zinc-500'}`}>
                          {(result.rule_boost_total ?? 0) > 0 ? '+' : ''}{(result.rule_boost_total ?? 0).toFixed(4)}
                        </span>
                      </div>
                      <div className="w-full px-3 py-2 border-b border-zinc-800/80 flex justify-between items-center text-[11px] uppercase tracking-wider bg-zinc-800/40">
                        <span className="text-zinc-300 font-bold">Final Score</span>
                        <span className="text-zinc-100 font-bold font-mono">{(result.score ?? 0).toFixed(4)}</span>
                      </div>
                      <div className="w-full px-3 py-2 flex justify-between items-center text-[9px] uppercase tracking-wider">
                        <span className="text-zinc-600">Threshold</span>
                        <span className="text-zinc-500 font-mono">{formatThreshold(result.threshold)}</span>
                      </div>
                    </div>

                  </div>
                </motion.div>
              ) : (
                <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="text-center text-zinc-600 flex flex-col items-center justify-center h-full">
                  <Activity className="w-12 h-12 mb-4 opacity-20" />
                  <p className="text-xs uppercase tracking-widest font-semibold">Awaiting Telemetry</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>

        {/* System Log Card */}
        <motion.div 
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          className="col-span-1 md:col-span-12 lg:col-span-4 soc-card-interactive flex flex-col h-full min-h-[300px]"
        >
          <div className="bg-zinc-900/60 px-4 py-3 border-b border-zinc-800/80 flex items-center justify-between backdrop-blur-md">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-zinc-400" />
              <h2 className="text-xs font-bold text-zinc-300 uppercase tracking-widest">System Log</h2>
            </div>
            <div className={`w-2 h-2 rounded-full ${loading ? 'bg-primary animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]' : 'bg-zinc-700'}`} />
          </div>
          <div className="flex-1 overflow-hidden p-0 m-0">
            <TerminalLogs logs={result?.analysis_logs} isLoading={loading} isIdle={!result && !loading} />
          </div>
        </motion.div>

        {/* ROW 2 */}
        {/* Sample Library */}
        <motion.div 
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
          className="col-span-1 md:col-span-12 lg:col-span-12 soc-card-interactive flex flex-col"
        >
          <div className="bg-zinc-900/60 px-4 py-3 border-b border-zinc-800/80 flex flex-col sm:flex-row items-center justify-between gap-3 backdrop-blur-md">
            <div className="flex items-center gap-2 self-start sm:self-auto">
              <FolderOpen className="w-4 h-4 text-zinc-400" />
              <h2 className="text-xs font-bold text-zinc-300 uppercase tracking-widest">Known Sample Library</h2>
            </div>
            <div className="flex bg-zinc-950 p-1 rounded-md border border-zinc-800 shadow-inner">
              <button 
                className={`px-4 py-1.5 text-[10px] font-bold uppercase tracking-wider rounded transition-colors ${sampleTab === 'real' ? 'bg-zinc-800 text-zinc-100 shadow-sm' : 'text-zinc-500 hover:text-zinc-300'}`}
                onClick={() => setSampleTab('real')}
              >
                Real Photos
              </button>
              <button 
                className={`px-4 py-1.5 text-[10px] font-bold uppercase tracking-wider rounded transition-colors ${sampleTab === 'screen' ? 'bg-zinc-800 text-zinc-100 shadow-sm' : 'text-zinc-500 hover:text-zinc-300'}`}
                onClick={() => setSampleTab('screen')}
              >
                Screen Photos
              </button>
            </div>
          </div>
          <div className="p-5 grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-4 bg-zinc-950/30">
             {manifest.filter(m => m.label === sampleTab).map(sample => (
               <motion.div 
                 key={sample.id}
                 whileHover={{ scale: 1.02, y: -1 }}
                 whileTap={{ scale: 0.98 }}
                 onClick={() => handleSampleClick(sample)}
                 className={`cursor-pointer rounded-lg overflow-hidden border-2 transition-all relative group ${selectedSample?.id === sample.id ? 'border-primary shadow-[0_0_15px_rgba(16,185,129,0.3)] z-10' : 'border-zinc-800 hover:border-zinc-600 hover:shadow-lg hover:shadow-black/50'}`}
               >
                 <img src={sample.path} alt={sample.title} className="w-full h-24 object-cover opacity-80 group-hover:opacity-100 transition-opacity" />
                 <div className="absolute inset-x-0 bottom-0 p-2 bg-gradient-to-t from-black via-black/80 to-transparent flex flex-col items-center">
                   <p className="text-[10px] text-zinc-300 font-mono truncate">{sample.id}</p>
                 </div>
                 {selectedSample?.id === sample.id && (
                   <div className="absolute top-1 right-1">
                     <span className="flex h-2 w-2">
                       <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                       <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
                     </span>
                   </div>
                 )}
               </motion.div>
             ))}
             {manifest.length === 0 && <p className="text-xs text-zinc-500 col-span-full text-center py-6 uppercase tracking-widest font-semibold">No samples found.</p>}
          </div>
        </motion.div>

        {/* ROW 3 */}
        {/* Analysis Pipeline */}
        <motion.div 
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
          className="col-span-1 md:col-span-12 lg:col-span-4 soc-card-interactive flex flex-col min-h-[380px]"
        >
          <div className="bg-zinc-900/60 px-4 py-3 border-b border-zinc-800/80 flex items-center gap-2 backdrop-blur-md">
            <LayoutList className="w-4 h-4 text-zinc-400" />
            <h2 className="text-xs font-bold text-zinc-300 uppercase tracking-widest">Analysis Pipeline</h2>
          </div>
          <div className="p-4 flex-1 flex flex-col justify-center">
            <WorkflowAnimation isAnalyzing={loading} isComplete={!!result} />
          </div>
        </motion.div>

        {/* Feature Telemetry */}
        <motion.div 
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}
          className="col-span-1 md:col-span-12 lg:col-span-4 soc-card-interactive flex flex-col min-h-[380px]"
        >
          <div className="bg-zinc-900/60 px-4 py-3 border-b border-zinc-800/80 flex items-center gap-2 backdrop-blur-md">
            <Fingerprint className="w-4 h-4 text-zinc-400" />
            <h2 className="text-xs font-bold text-zinc-300 uppercase tracking-widest">Feature Telemetry</h2>
          </div>
          <div className="flex-1 relative">
            <AnimatePresence mode="wait">
              {result ? (
                Object.keys(result.feature_groups || {}).length > 0 ? (
                  <motion.div key="data" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="absolute inset-4 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-transparent space-y-6 pb-6">
                    
                    {/* Top Evidence Section */}
                    <div className="bg-zinc-950/50 border border-zinc-800/80 rounded-md p-3">
                      <div className="flex justify-between items-center border-b border-zinc-800 pb-2 mb-2">
                        <span className="text-[10px] uppercase font-bold text-zinc-400 tracking-widest">Interpretation</span>
                        <span className="text-[9px] text-zinc-500 font-mono flex items-center gap-1"><Info className="w-3 h-3" /> Context Applied</span>
                      </div>
                      <p className="text-[9.5px] text-zinc-500 leading-relaxed mb-3">Feature telemetry visualizes raw magnitudes. Screen detection relies on holistic context and thresholding.</p>
                      
                      <div className="space-y-1.5 text-[10px] font-mono">
                        <div className="flex gap-2 text-success">
                          <span className="shrink-0 font-bold">✓ Supports Real:</span>
                          <span className="text-zinc-400 leading-tight">
                            {result.rule_boost_total < 0 ? "Natural-scene correction applied. " : ""}
                            {(result.features?.bezel_score || 0) < 0.1 ? "No bezel detected. " : ""}
                            {(result.features?.perspective_score || 0) < 0.1 ? "No screen contour. " : ""}
                            {((result.features?.bezel_score || 0) >= 0.1 && (result.features?.perspective_score || 0) >= 0.1 && result.rule_boost_total >= 0) ? "None strongly." : ""}
                          </span>
                        </div>
                        <div className="flex gap-2 text-danger">
                          <span className="shrink-0 font-bold">⚠ Supports Screen:</span>
                          <span className="text-zinc-400 leading-tight">
                            {(result.features?.moire_score || 0) > 0.5 ? "Elevated moiré. " : ""}
                            {(result.features?.blockiness || 0) > 0.5 ? "Elevated blockiness. " : ""}
                            {result.rule_boost_total > 0 ? "Screen context rules triggered. " : ""}
                            {(!((result.features?.moire_score || 0) > 0.5) && !((result.features?.blockiness || 0) > 0.5) && result.rule_boost_total <= 0) ? "Minimal screen indicators." : ""}
                          </span>
                        </div>
                        <div className="flex gap-2 mt-2 pt-2 border-t border-zinc-800/50">
                          <span className="shrink-0 font-bold text-primary">➜ Final Decision:</span>
                          <span className="text-zinc-300">
                            Model score is <span className="font-bold">{result.score >= (result.threshold || 0.65) ? "ABOVE" : "BELOW"}</span> threshold.
                          </span>
                        </div>
                      </div>
                    </div>

                    {Object.entries(result.feature_groups).map(([groupName, features], i) => (
                        <motion.div key={groupName} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }} className="flex flex-col">
                          <div className="flex items-center gap-2 mb-4">
                            <div className="w-1 h-3 bg-zinc-600 rounded-full"></div>
                            <h4 className="text-[10px] font-bold text-zinc-300 uppercase tracking-widest">{groupName}</h4>
                          </div>
                          <FeatureBarChart data={features} finalScore={result.score} />
                        </motion.div>
                      ))}
                  </motion.div>
                ) : (
                  <motion.div key="no-features" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="absolute inset-0 flex flex-col items-center justify-center">
                    <p className="text-xs text-zinc-500 uppercase tracking-widest font-semibold text-center px-4">Feature vector not returned by backend.</p>
                  </motion.div>
                )
              ) : (
                <motion.div key="nodata" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 flex flex-col items-center justify-center">
                  <Fingerprint className="w-12 h-12 mb-3 text-zinc-800" />
                  <p className="text-sm text-zinc-300 font-bold uppercase tracking-widest mb-1">Awaiting feature vector</p>
                  <p className="text-xs text-zinc-500 text-center max-w-[200px] leading-relaxed">Upload or select an image to extract CV and frequency features.</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>

        {/* Model Status */}
        <motion.div 
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}
          className="col-span-1 md:col-span-12 lg:col-span-4 soc-card-interactive flex flex-col min-h-[380px]"
        >
          <div className="bg-zinc-900/60 px-4 py-3 border-b border-zinc-800/80 flex items-center gap-2 backdrop-blur-md">
            <Database className="w-4 h-4 text-zinc-400" />
            <h2 className="text-xs font-bold text-zinc-300 uppercase tracking-widest">System Architecture</h2>
          </div>
          <div className="p-5 flex-1 flex flex-col justify-center space-y-5">
            <div>
              <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold mb-2">Active Classifier</p>
              <div className="bg-zinc-950/60 p-4 rounded-md border border-zinc-800 shadow-inner">
                <p className="text-sm font-bold text-primary font-mono tracking-tight flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
                  {result?.model_type || systemInfo?.metadata?.model_type || "Phone-Adapted XGBoost"}
                </p>
                <div className="mt-3 flex items-center justify-between text-xs border-t border-zinc-800 pt-3">
                  <span className="text-zinc-500 uppercase tracking-wider text-[10px]">Decision Threshold</span>
                  <span className="text-zinc-300 font-mono font-bold bg-zinc-800 px-2 py-0.5 rounded">{formatThreshold(result?.threshold ?? systemInfo?.metadata?.threshold ?? 0.65)}</span>
                </div>
              </div>
            </div>
            
            <div>
              <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold mb-2">Validation Integrity</p>
              <div className="bg-zinc-950/40 p-3 rounded-md border border-zinc-800 flex justify-between items-center mb-2">
                <div>
                  <p className="text-[11px] font-bold text-zinc-300 uppercase tracking-wider">ICL Grouped Split</p>
                  <p className="text-[9px] text-zinc-500 mt-0.5">Leakage-Free Context</p>
                </div>
                <div className="text-right">
                  <p className="text-xs font-bold text-emerald-400 font-mono">
                    {systemInfo?.metadata?.icl_metrics?.accuracy 
                      ? (systemInfo.metadata.icl_metrics.accuracy * 100).toFixed(1) + "%" 
                      : "~98.9%"}
                  </p>
                </div>
              </div>
              <div className="bg-zinc-950/40 p-3 rounded-md border border-zinc-800 flex justify-between items-center">
                <div>
                  <p className="text-[11px] font-bold text-zinc-300 uppercase tracking-wider">Phone 5-Fold CV</p>
                  <p className="text-[9px] text-zinc-500 mt-0.5">Honest Generalization (F1)</p>
                </div>
                <div className="text-right">
                  <p className="text-xs font-bold text-emerald-400 font-mono">~79.5%</p>
                </div>
              </div>
            </div>
            
            <div className="pt-2">
              <div className="bg-warning/10 border border-warning/20 p-3 rounded-md flex items-start gap-2">
                <ShieldAlert className="w-4 h-4 text-warning shrink-0 mt-0.5" />
                <p className="text-[10px] text-warning/90 leading-relaxed font-medium">
                  Phone evaluation is on a small set ({systemInfo?.phone_metrics?.total_tested || 53} images). No production-scale independent benchmark claim is made.
                </p>
              </div>
            </div>
          </div>
        </motion.div>
        
      </main>

      <MethodologyDrawer isOpen={isMethodologyOpen} onClose={() => setIsMethodologyOpen(false)} />
    </div>
  )
}
