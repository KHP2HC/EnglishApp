import { useState, useCallback, useRef, useEffect } from 'react'

// ── Conversation Parsing ────────────────────────────────────────────

interface SpeechSegment {
  speaker: string
  text: string
}

/**
 * Parse a multi-speaker transcript into individual speech segments.
 * Lines in the form "Name: dialogue" are split into speaker + text.
 * Lines without a speaker prefix are attributed to "Narrator".
 */
function parseConversation(transcript: string): {
  segments: SpeechSegment[]
  speakers: string[]
} {
  const lines = transcript.split(/\r?\n/).map((l) => l.trim()).filter(Boolean)
  const segments: SpeechSegment[] = []
  const speakerSet = new Set<string>()

  const speakerLineRe = /^([A-Za-z0-9\s'.&-]+):\s*(.*)$/

  for (const line of lines) {
    const match = line.match(speakerLineRe)
    if (match) {
      const speaker = match[1].trim()
      const text = match[2].trim()
      if (text) {
        segments.push({ speaker, text })
        speakerSet.add(speaker)
      }
    } else {
      // No speaker prefix — treat as Narrator
      segments.push({ speaker: 'Narrator', text: line })
      speakerSet.add('Narrator')
    }
  }

  return { segments, speakers: [...speakerSet] }
}

// ── Voice Gender Classification ──────────────────────────────────────

type Gender = 'male' | 'female' | 'neutral'

const MALE_NAME_HINTS = [
  'james', 'john', 'tom', 'david', 'daniel', 'michael', 'robert',
  'william', 'richard', 'joseph', 'charles', 'thomas', 'boy', 'man',
  'mr', 'sir', 'guy',
]

const FEMALE_NAME_HINTS = [
  'maria', 'sarah', 'mary', 'jane', 'elizabeth', 'susan', 'lisa',
  'emma', 'olivia', 'sophia', 'anna', 'girl', 'woman', 'receptionist',
  'mrs', 'ms', 'miss', 'lady',
]

/**
 * Guess the gender of a speaker based on their name.
 */
function guessGender(name: string): Gender {
  const lower = name.toLowerCase()
  if (MALE_NAME_HINTS.some((h) => lower.includes(h))) return 'male'
  if (FEMALE_NAME_HINTS.some((h) => lower.includes(h))) return 'female'
  return 'neutral'
}

/**
 * Classify a TTS voice as male or female based on its display name.
 */
function classifyVoiceGender(voiceName: string): Gender {
  const lower = voiceName.toLowerCase()
  const femaleHints = [
    'samantha', 'zira', 'victoria', 'karen', 'moira', 'tessa', 'fiona',
    'veena', 'amelie', 'anna', 'ellen', 'kyoko', 'yuna', 'woman',
    'female', 'girl', 'serena', 'catherine', 'stephanie',
  ]
  const maleHints = [
    'daniel', 'david', 'alex', 'fred', 'tom', 'oliver', 'arthur',
    'rishi', 'james', 'man', 'male', 'boy', 'george', 'mark',
  ]
  if (femaleHints.some((h) => lower.includes(h))) return 'female'
  if (maleHints.some((h) => lower.includes(h))) return 'male'
  return 'neutral'
}

// ── Speaker → Voice Mapping ──────────────────────────────────────────

/**
 * Map each unique speaker to a distinct SpeechSynthesisVoice when possible.
 * English voices are filtered and assigned by gender preference.
 */
function mapSpeakersToVoices(
  speakers: string[],
  availableVoices: SpeechSynthesisVoice[]
): Map<string, SpeechSynthesisVoice> {
  const englishVoices = availableVoices.filter((v) =>
    v.lang.toLowerCase().startsWith('en')
  )
  const pool = englishVoices.length > 0 ? englishVoices : availableVoices

  const maleVoices = pool.filter((v) => classifyVoiceGender(v.name) === 'male')
  const femaleVoices = pool.filter((v) => classifyVoiceGender(v.name) === 'female')
  const neutralVoices = pool.filter(
    (v) => classifyVoiceGender(v.name) === 'neutral'
  )

  const assignment = new Map<string, SpeechSynthesisVoice>()
  const usedVoices = new Set<SpeechSynthesisVoice>()

  const pickFrom = (list: SpeechSynthesisVoice[]): SpeechSynthesisVoice | undefined => {
    return list.find((v) => !usedVoices.has(v)) ?? list[0]
  }

  // First pass: assign gender-matched voices
  for (const speaker of speakers) {
    const gender = guessGender(speaker)
    let chosen: SpeechSynthesisVoice | undefined

    if (gender === 'male' && maleVoices.length > 0) {
      chosen = pickFrom(maleVoices)
    } else if (gender === 'female' && femaleVoices.length > 0) {
      chosen = pickFrom(femaleVoices)
    }

    if (chosen) {
      assignment.set(speaker, chosen)
      usedVoices.add(chosen)
    }
  }

  // Second pass: fill in any speakers not yet assigned (neutral or fallback)
  const fallbackPool = [
    ...neutralVoices.filter((v) => !usedVoices.has(v)),
    ...pool.filter((v) => !usedVoices.has(v)),
  ]
  let fallbackIdx = 0

  for (const speaker of speakers) {
    if (assignment.has(speaker)) continue
    const chosen =
      fallbackPool[fallbackIdx] ?? pool[fallbackIdx % pool.length]
    fallbackIdx++
    assignment.set(speaker, chosen)
    usedVoices.add(chosen)
  }

  return assignment
}

// ── Speech Synthesis (TTS) ───────────────────────────────────────────

export function useSpeech() {
  const [speaking, setSpeaking] = useState(false)
  const queueRef = useRef<SpeechSegment[]>([])
  const voiceMapRef = useRef<Map<string, SpeechSynthesisVoice>>(new Map())
  const rateRef = useRef(0.85)
  const cancelledRef = useRef(false)

  const playNext = useCallback(() => {
    if (cancelledRef.current) return

    const next = queueRef.current.shift()
    if (!next) {
      setSpeaking(false)
      return
    }

    const utterance = new SpeechSynthesisUtterance(next.text)
    utterance.lang = 'en-US'
    utterance.rate = rateRef.current

    const voice = voiceMapRef.current.get(next.speaker)
    if (voice) {
      utterance.voice = voice
    }

    utterance.onend = () => {
      playNext()
    }
    utterance.onerror = () => {
      setSpeaking(false)
    }

    window.speechSynthesis.speak(utterance)
  }, [])

  const speak = useCallback(
    (text: string, rate = 0.85) => {
      if (!('speechSynthesis' in window)) return

      // Stop any current playback and reset
      window.speechSynthesis.cancel()
      cancelledRef.current = false
      queueRef.current = []
      rateRef.current = rate

      const { segments, speakers } = parseConversation(text)

      // If there's only one segment with no real speaker, speak it directly
      const hasMultipleSpeakers =
        speakers.length > 1 ||
        (speakers.length === 1 && speakers[0] !== 'Narrator') ||
        segments.length > 1

      if (!hasMultipleSpeakers) {
        // Simple single-utterance path (preserves existing behaviour for words/phrases)
        const utterance = new SpeechSynthesisUtterance(text)
        utterance.lang = 'en-US'
        utterance.rate = rate
        utterance.onstart = () => setSpeaking(true)
        utterance.onend = () => setSpeaking(false)
        utterance.onerror = () => setSpeaking(false)
        setSpeaking(true)
        window.speechSynthesis.speak(utterance)
        return
      }

      // Multi-speaker conversation path
      const availableVoices = window.speechSynthesis.getVoices()
      voiceMapRef.current = mapSpeakersToVoices(speakers, availableVoices)
      queueRef.current = [...segments]

      setSpeaking(true)
      playNext()
    },
    [playNext]
  )

  const stopSpeaking = useCallback(() => {
    if ('speechSynthesis' in window) {
      cancelledRef.current = true
      window.speechSynthesis.cancel()
      queueRef.current = []
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
