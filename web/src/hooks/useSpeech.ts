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

interface SpeakerVoicePlan {
  voice: SpeechSynthesisVoice
  pitch: number
}

// Pitch values used to differentiate speakers that share the same voice.
// Spans a natural-sounding range (0.7 = deep, 1.3 = higher).
const PITCH_STEPS = [1.0, 0.8, 1.2, 0.7, 1.3, 0.9, 1.1, 0.85, 1.15, 0.75]

/**
 * Assign a distinct voice + pitch to every unique speaker.
 *
 * Strategy:
 *  1. Filter for English voices (fall back to all voices if none).
 *  2. Sort so gender-matched voices come first for each speaker.
 *  3. Give each speaker a unique voice from the pool, cycling when
 *     the pool is exhausted.  When two speakers must share a voice,
 *     assign different pitch values so they still sound distinct.
 */
function mapSpeakersToVoices(
  speakers: string[],
  availableVoices: SpeechSynthesisVoice[]
): Map<string, SpeakerVoicePlan> {
  const englishVoices = availableVoices.filter((v) =>
    v.lang.toLowerCase().startsWith('en')
  )
  const pool = englishVoices.length > 0 ? englishVoices : availableVoices

  // If we have no voices at all, return empty map (caller falls back to default)
  if (pool.length === 0) return new Map()

  const assignment = new Map<string, SpeakerVoicePlan>()
  const usedVoices = new Set<SpeechSynthesisVoice>()

  // Track how many speakers have been assigned each voice so we can
  // give them different pitches when voices are reused.
  const voiceUseCount = new Map<SpeechSynthesisVoice, number>()

  for (const speaker of speakers) {
    const gender = guessGender(speaker)

    // Build a preference-ordered list of voices for this speaker:
    // gender-matched first, then neutral, then the rest.
    const preferred = pool
      .map((v) => ({
        voice: v,
        gender: classifyVoiceGender(v.name),
        used: usedVoices.has(v),
      }))
      .sort((a, b) => {
        // Unused voices first
        if (a.used !== b.used) return a.used ? 1 : -1
        // Then gender match
        const aMatch = a.gender === gender ? 0 : 1
        const bMatch = b.gender === gender ? 0 : 1
        if (aMatch !== bMatch) return aMatch - bMatch
        return 0
      })

    const chosen = preferred[0].voice
    const useIdx = voiceUseCount.get(chosen) ?? 0
    const pitch = PITCH_STEPS[useIdx % PITCH_STEPS.length]

    assignment.set(speaker, { voice: chosen, pitch })
    usedVoices.add(chosen)
    voiceUseCount.set(chosen, useIdx + 1)
  }

  return assignment
}

// ── Speech Synthesis (TTS) ───────────────────────────────────────────

export function useSpeech() {
  const [speaking, setSpeaking] = useState(false)
  const queueRef = useRef<SpeechSegment[]>([])
  const voiceMapRef = useRef<Map<string, SpeakerVoicePlan>>(new Map())
  const rateRef = useRef(0.85)
  const cancelledRef = useRef(false)
  const voicesRef = useRef<SpeechSynthesisVoice[]>([])

  // Load voices eagerly and keep cache in sync.  The Web Speech API populates
  // getVoices() asynchronously — on first call it often returns [], so we must
  // listen for the `voiceschanged` event and re-cache.
  useEffect(() => {
    if (!('speechSynthesis' in window)) return

    const updateVoices = () => {
      voicesRef.current = window.speechSynthesis.getVoices()
    }

    updateVoices()
    window.speechSynthesis.addEventListener('voiceschanged', updateVoices)

    return () => {
      window.speechSynthesis.removeEventListener('voiceschanged', updateVoices)
    }
  }, [])

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

    const plan = voiceMapRef.current.get(next.speaker)
    if (plan) {
      utterance.voice = plan.voice
      utterance.pitch = plan.pitch
    }

    utterance.onend = () => {
      // Small pause between segments so the conversation sounds natural
      // and to avoid Chrome's known bug where rapid speak() calls are dropped.
      setTimeout(() => playNext(), 250)
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
      // Use cached voices (getVoices() may return [] if called too early)
      let availableVoices =
        voicesRef.current.length > 0
          ? voicesRef.current
          : window.speechSynthesis.getVoices()

      // If voices are still empty, trigger a synchronous fetch by calling
      // getVoices() again after a brief tick — some browsers need this.
      if (availableVoices.length === 0) {
        window.speechSynthesis.getVoices()
        availableVoices = window.speechSynthesis.getVoices()
      }

      voiceMapRef.current = mapSpeakersToVoices(speakers, availableVoices)

      // Debug: log the assignment so we can verify distinct voices
      console.log(
        '[useSpeech] Multi-speaker playback:',
        speakers.length,
        'speakers →',
        [...voiceMapRef.current.entries()].map(([name, plan]) => ({
          speaker: name,
          voice: plan.voice.name,
          pitch: plan.pitch,
        }))
      )

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
