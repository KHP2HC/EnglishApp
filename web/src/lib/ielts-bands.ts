/**
 * Official IELTS band score conversion tables.
 *
 * Source: British Council / IDP IELTS official raw-score-to-band conversion.
 * Raw scores are out of 40 questions.
 */

// ── Academic Reading (out of 40) ────────────────────────────────────
const READING_BAND_TABLE: [number, number][] = [
  [40, 9.0],
  [39, 9.0],
  [37, 8.5],
  [35, 8.0],
  [33, 7.5],
  [30, 7.0],
  [27, 6.5],
  [23, 6.0],
  [19, 5.5],
  [15, 5.0],
  [13, 4.5],
  [10, 4.0],
  [8, 3.5],
  [6, 3.0],
  [4, 2.5],
  [3, 2.0],
  [2, 1.5],
  [1, 1.0],
  [0, 0],
]

// ── Listening (out of 40) ───────────────────────────────────────────
const LISTENING_BAND_TABLE: [number, number][] = [
  [40, 9.0],
  [39, 8.5],
  [37, 8.0],
  [35, 7.5],
  [32, 7.0],
  [30, 6.5],
  [26, 6.0],
  [23, 5.5],
  [19, 5.0],
  [15, 4.5],
  [12, 4.0],
  [8, 3.5],
  [6, 3.0],
  [4, 2.5],
  [3, 2.0],
  [2, 1.5],
  [1, 1.0],
  [0, 0],
]

/**
 * Convert a raw score to an IELTS band.
 *
 * If the test has fewer than 40 questions, the raw score is scaled
 * to a 40-question equivalent before lookup (same approach as the
 * desktop app's `raw_to_band`).
 */
export function rawToBand(
  raw: number,
  total: number,
  table: 'reading' | 'listening' = 'reading'
): number {
  if (total <= 0) return 0
  const scaled = Math.round((raw / total) * 40)
  const lookup = table === 'listening' ? LISTENING_BAND_TABLE : READING_BAND_TABLE
  for (const [threshold, band] of lookup) {
    if (scaled >= threshold) return band
  }
  return 0
}

export function rawToReadingBand(raw: number, total: number): number {
  return rawToBand(raw, total, 'reading')
}

export function rawToListeningBand(raw: number, total: number): number {
  return rawToBand(raw, total, 'listening')
}

/**
 * Compute an overall IELTS band from individual section bands.
 * The official rule rounds to the nearest 0.5.
 */
export function overallBand(bands: number[]): number {
  if (bands.length === 0) return 0
  const avg = bands.reduce((a, b) => a + b, 0) / bands.length
  // Round to nearest 0.5
  return Math.round(avg * 2) / 2
}

// ── Band descriptors (for display) ──────────────────────────────────
export const BAND_LABELS: Record<string, string> = {
  '9': 'Expert User',
  '8.5': 'Very Good User',
  '8': 'Very Good User',
  '7.5': 'Good User',
  '7': 'Good User',
  '6.5': 'Competent User',
  '6': 'Competent User',
  '5.5': 'Modest User',
  '5': 'Modest User',
  '4.5': 'Limited User',
  '4': 'Limited User',
  '3.5': 'Extremely Limited User',
  '3': 'Extremely Limited User',
  '2.5': 'Intermittent User',
  '2': 'Intermittent User',
  '1': 'Non User',
  '0': 'Did not attempt',
}

export function bandLabel(band: number): string {
  return BAND_LABELS[String(band)] || '—'
}
