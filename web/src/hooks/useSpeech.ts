import { useState, useCallback, useRef, useEffect } from 'react'

// ── Speech Synthesis (TTS) ───────────────────────────────────────────

export function useSpeech() {
  const [speaking, setSpeaking] = useState(false)

  const speak = useCallback((text: string, rate = 0.85) => {
    if (!('speechSynthesis' in window)) return
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'en-US'
    utterance.rate = rate
    utterance.onstart = () => setSpeaking(true)
    utterance.onend = () => setSpeaking(false)
    utterance.onerror = () => setSpeaking(false)
    window.speechSynthesis.speak(utterance)
  }, [])

  const stopSpeaking = useCallback(() => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
      setSpeaking(false)
    }
  }, [])

  return { speak, stopSpeaking, speaking }
}

// ── Speech Recognition (STT) ────────────────────────────────────────

export function useSpeechRecognition() {
  const [listening, setListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [error, setError] = useState<string | null>(null)
  const recognitionRef = useRef<any>(null)

  const isSupported =
    typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)

  const startListening = useCallback((): Promise<string> => {
    return new Promise((resolve, reject) => {
      if (!isSupported) {
        reject(new Error('SpeechRecognition not supported in this browser'))
        return
      }

      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      const recognition = new SpeechRecognition()
      recognition.lang = 'en-US'
      recognition.interimResults = false
      recognition.maxAlternatives = 1

      recognition.onresult = (e: any) => {
        const text = e.results[0][0].transcript
        setTranscript(text)
        resolve(text)
      }
      recognition.onerror = (e: any) => {
        setError(e.error || 'Recognition failed')
        setListening(false)
        reject(new Error(e.error || 'Recognition failed'))
      }
      recognition.onend = () => setListening(false)

      recognitionRef.current = recognition
      setListening(true)
      setError(null)
      recognition.start()
    })
  }, [isSupported])

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
      setListening(false)
    }
  }, [])

  // ── Pronunciation scoring ──────────────────────────────────────────

  const scorePronunciation = useCallback(
    (target: string, spoken: string) => {
      const targetWords = target.toLowerCase().split(/\s+/).filter(Boolean)
      const spokenWords = spoken.toLowerCase().split(/\s+/).filter(Boolean)
      const results: { word: string; correct: boolean; suggestion: string | null }[] = []

      for (const word of targetWords) {
        const cleanWord = word.replace(/[^a-z']/g, '')
        const found = spokenWords.find(
          (w) => w.replace(/[^a-z']/g, '') === cleanWord
        )
        if (found) {
          results.push({ word, correct: true, suggestion: null })
        } else {
          // Find closest match
          let bestMatch: string | null = null
          let bestScore = 0
          for (const sw of spokenWords) {
            const cleanSw = sw.replace(/[^a-z']/g, '')
            const len = Math.max(cleanWord.length, cleanSw.length)
            const matches = [...cleanWord].filter((c, i) => c === cleanSw[i]).length
            const score = matches / len
            if (score > bestScore && score > 0.5) {
              bestScore = score
              bestMatch = sw
            }
          }
          results.push({ word, correct: false, suggestion: bestMatch })
        }
      }

      const correctCount = results.filter((r) => r.correct).length
      const accuracy = targetWords.length > 0 ? (correctCount / targetWords.length) * 100 : 0

      return { results, accuracy, mismatches: results.filter((r) => !r.correct).map((r) => r.word) }
    },
    []
  )

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop()
        } catch {
          // Recognition may already be stopped — ignore
        }
      }
    }
  }, [])

  return {
    speak: useSpeech().speak,
    stopSpeaking: useSpeech().stopSpeaking,
    speaking: useSpeech().speaking,
    startListening,
    stopListening,
    listening,
    transcript,
    error,
    isSupported,
    scorePronunciation,
  }
}
