import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  CalendarRange,
  Loader2,
  Zap,
  ToggleLeft,
  ToggleRight,
  ArrowRight,
} from 'lucide-react'
import FileDropzone from '@/components/FileDropzone'
import { uploadFile, uploadText, generatePreview } from '@/lib/api'

export default function UploadPage() {
  const navigate = useNavigate()
  const [mode, setMode] = useState<'file' | 'text'>('file')
  const [file, setFile] = useState<File | null>(null)
  const [text, setText] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [skipWeekends, setSkipWeekends] = useState(true)
  const [skipHolidays, setSkipHolidays] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const canSubmit = (mode === 'file' ? !!file : text.trim().length > 10) && dateFrom && dateTo

  const handleGenerate = async () => {
    if (!canSubmit) return
    setLoading(true)
    setError('')

    try {
      // Step 1: Upload
      let uploadId: string
      if (mode === 'file' && file) {
        const res = await uploadFile(file)
        uploadId = res.upload_id
      } else {
        const res = await uploadText(text)
        uploadId = res.upload_id
      }

      // Step 2: Generate preview
      const dateRange = `${dateFrom} to ${dateTo}`
      const preview = await generatePreview(uploadId, dateRange, skipWeekends, skipHolidays)

      // Store in sessionStorage and navigate
      sessionStorage.setItem('preview_data', JSON.stringify(preview))
      navigate('/preview')
    } catch (e: any) {
      setError(e.message || 'Generation failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8 max-w-3xl mx-auto">
      <div>
        <h1 className="text-2xl font-black tracking-tight">Feed the Machine</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Upload anything. It will figure out the rest.
        </p>
      </div>

      {/* Mode toggle */}
      <div className="flex gap-2">
        {(['file', 'text'] as const).map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
              mode === m
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground hover:text-foreground'
            }`}
          >
            {m === 'file' ? 'File Upload' : 'Paste Text'}
          </button>
        ))}
      </div>

      {/* Input area */}
      <motion.div
        key={mode}
        initial={{ opacity: 0, x: mode === 'file' ? -20 : 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.2 }}
      >
        {mode === 'file' ? (
          <FileDropzone file={file} onFile={setFile} />
        ) : (
          <div className="relative">
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste your notes, git log output, meeting minutes, anything..."
              className="w-full h-48 bg-card border border-border rounded-xl p-4 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary/50 placeholder:text-muted-foreground/40"
            />
            <div className="absolute bottom-3 right-3 text-[10px] text-muted-foreground/50">
              {text.split(/\s+/).filter(Boolean).length} words
            </div>
          </div>
        )}
      </motion.div>

      {/* Date range */}
      <div className="border border-border rounded-xl p-5 bg-card space-y-4">
        <div className="flex items-center gap-2">
          <CalendarRange className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm font-medium">Date Range</span>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-muted-foreground mb-1 block">From</label>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="w-full bg-muted rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>
          <div>
            <label className="text-xs text-muted-foreground mb-1 block">To</label>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="w-full bg-muted rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>
        </div>

        <div className="flex gap-6">
          <button
            onClick={() => setSkipWeekends(!skipWeekends)}
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            {skipWeekends ? (
              <ToggleRight className="w-5 h-5 text-primary" />
            ) : (
              <ToggleLeft className="w-5 h-5" />
            )}
            Skip weekends
          </button>
          <button
            onClick={() => setSkipHolidays(!skipHolidays)}
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            {skipHolidays ? (
              <ToggleRight className="w-5 h-5 text-primary" />
            ) : (
              <ToggleLeft className="w-5 h-5" />
            )}
            Skip holidays
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-destructive/10 border border-destructive/30 text-destructive rounded-lg px-4 py-3 text-sm"
        >
          {error}
        </motion.div>
      )}

      {/* Generate button */}
      <button
        onClick={handleGenerate}
        disabled={!canSubmit || loading}
        className={`
          w-full flex items-center justify-center gap-3 py-4 rounded-xl text-sm font-bold
          transition-all duration-300
          ${
            canSubmit && !loading
              ? 'bg-gradient-to-r from-red-600 to-orange-500 text-white hover:shadow-lg hover:shadow-red-500/25 hover:scale-[1.01]'
              : 'bg-muted text-muted-foreground cursor-not-allowed'
          }
        `}
      >
        {loading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            AI is generating entries...
          </>
        ) : (
          <>
            <Zap className="w-4 h-4" />
            Generate Entries
            <ArrowRight className="w-4 h-4" />
          </>
        )}
      </button>
    </div>
  )
}
