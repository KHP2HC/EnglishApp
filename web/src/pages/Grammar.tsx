import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Check, X } from 'lucide-react'
import { loadQuestionBank, type SeedQuestion } from '@/lib/seed-data'

interface Lesson {
  id: string
  title: string
  level: string
  summary: string
  body: string
  exercises: { question: string; options: string[]; answer: string; explanation: string }[]
}

const BUILT_IN_LESSONS: Lesson[] = [
  {
    id: 'present_simple',
    title: 'Present Simple',
    level: 'A1',
    summary: 'Used for habits, routines, facts and general truths.',
    body: `Structure: Subject + base verb (add -s/-es for he/she/it).

Examples:
• I work every day.
• She plays tennis on weekends.
• Water boils at 100°C.

Negative: do/does + not + base verb
• He doesn't like coffee.

Question: Do/Does + subject + base verb
• Do you speak English?`,
    exercises: [
      { question: 'She ___ to school by bus every morning.', options: ['go', 'goes', 'going', 'went'], answer: 'goes', explanation: 'Third-person singular adds -es.' },
      { question: '___ they play football on Sundays?', options: ['Do', 'Does', 'Is', 'Are'], answer: 'Do', explanation: 'Plural subject uses Do.' },
      { question: 'Water ___ at 100 degrees Celsius.', options: ['boil', 'boils', 'is boiling', 'boiled'], answer: 'boils', explanation: 'General truth → Present Simple.' },
    ],
  },
  {
    id: 'conditionals',
    title: 'Conditionals (0, 1st, 2nd)',
    level: 'B1',
    summary: 'If-clauses for real and hypothetical situations.',
    body: `Zero (facts): If + present, present
• If you heat ice, it melts.

First (likely): If + present, will + base
• If it rains, I will stay home.

Second (unlikely): If + past, would + base
• If I had money, I would travel the world.`,
    exercises: [
      { question: 'If I ___ rich, I would buy a house.', options: ['am', 'was', 'were', 'be'], answer: 'were', explanation: 'Second conditional uses were.' },
      { question: 'If you heat water to 100°C, it ___.', options: ['will boil', 'boils', 'boiled', 'is boiling'], answer: 'boils', explanation: 'Zero conditional.' },
      { question: 'If she studies hard, she ___ the exam.', options: ['passes', 'will pass', 'would pass', 'passed'], answer: 'will pass', explanation: 'First conditional.' },
    ],
  },
  {
    id: 'passive_voice',
    title: 'Passive Voice',
    level: 'B2',
    summary: 'Focus on the action or recipient, not the doer.',
    body: `Structure: be + past participle

• Active: They built the house in 1990.
• Passive: The house was built in 1990.

Tense changes affect the 'be' verb:
Present: is/are done | Past: was/were done
Future: will be done | Perfect: has/have been done`,
    exercises: [
      { question: 'The book ___ by millions of readers.', options: ['reads', 'is read', 'read', 'reading'], answer: 'is read', explanation: 'Present passive.' },
      { question: 'The bridge ___ in 1985.', options: ['built', 'was built', 'is built', 'builds'], answer: 'was built', explanation: 'Past passive.' },
    ],
  },
]

export function Grammar() {
  const [lessons, setLessons] = useState<Lesson[]>(BUILT_IN_LESSONS)
  const [selected, setSelected] = useState<Lesson>(BUILT_IN_LESSONS[0])
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [checked, setChecked] = useState<Record<number, boolean>>({})

  useEffect(() => {
    // Load additional questions from seed data and create a "Mixed Practice" lesson
    loadQuestionBank()
      .then((questions: SeedQuestion[]) => {
        if (questions.length > 0) {
          const mixedLesson: Lesson = {
            id: 'mixed-practice',
            title: 'Mixed Practice (From Question Bank)',
            level: 'All',
            summary: 'Adaptive questions across all CEFR levels from the question bank.',
            body: 'These questions are loaded from the built-in question bank. They cover vocabulary, grammar, and usage across all proficiency levels from A1 to C2.',
            exercises: questions.map((q) => ({
              question: q.question,
              options: q.options,
              answer: q.answer,
              explanation: `Correct answer: ${q.answer}. This is a ${q.level}-level question.`,
            })),
          }
          setLessons([...BUILT_IN_LESSONS, mixedLesson])
        }
      })
      .catch(() => {})
  }, [])

  const check = (idx: number) => {
    setChecked((c) => ({ ...c, [idx]: true }))
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold font-heading">📐 Grammar</h1>

      {/* Lesson selector */}
      <div className="flex flex-wrap gap-2">
        {lessons.map((l) => (
          <button
            key={l.id}
            onClick={() => { setSelected(l); setAnswers({}); setChecked({}) }}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              selected.id === l.id ? 'bg-accent text-white' : 'bg-surface-dark text-gray-400 hover:text-white'
            }`}
          >
            {l.level} — {l.title}
          </button>
        ))}
      </div>

      {/* Lesson content */}
      <Card>
        <CardHeader>
          <CardTitle>{selected.title} <span className="text-sm text-accent">[{selected.level}]</span></CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-400 mb-4">{selected.summary}</p>
          <pre className="text-sm font-mono whitespace-pre-wrap text-gray-300 bg-black/20 rounded-lg p-4">
            {selected.body}
          </pre>
        </CardContent>
      </Card>

      {/* Exercises */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold font-heading">Exercises</h2>
        {selected.exercises.map((ex, i) => (
          <Card key={i}>
            <CardContent className="py-4">
              <p className="font-medium mb-3">Q{i + 1}. {ex.question}</p>
              <div className="space-y-2">
                {ex.options.map((opt) => {
                  const isSelected = answers[i] === opt
                  const isCorrect = checked[i] && opt === ex.answer
                  const isWrong = checked[i] && isSelected && opt !== ex.answer
                  return (
                    <button
                      key={opt}
                      onClick={() => !checked[i] && setAnswers((a) => ({ ...a, [i]: opt }))}
                      className={`flex items-center gap-2 w-full text-left px-3 py-2 rounded-lg border transition-colors ${
                        isCorrect ? 'border-success bg-success/10' :
                        isWrong ? 'border-error bg-error/10' :
                        isSelected ? 'border-accent' : 'border-border'
                      } ${checked[i] ? 'cursor-default' : 'hover:border-accent'}`}
                    >
                      {isCorrect && <Check className="h-4 w-4 text-success" />}
                      {isWrong && <X className="h-4 w-4 text-error" />}
                      {opt}
                    </button>
                  )
                })}
              </div>
              {checked[i] && (
                <p className={`text-sm mt-2 ${answers[i] === ex.answer ? 'text-success' : 'text-error'}`}>
                  {answers[i] === ex.answer ? '✅ ' : '❅ '}{ex.explanation}
                </p>
              )}
              {!checked[i] && (
                <Button size="sm" className="mt-3" onClick={() => check(i)} disabled={!answers[i]}>
                  Check
                </Button>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
