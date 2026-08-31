import { Button } from '@/components/ui/button'
import type { Quality } from '@/lib/srs'

interface QualityButtonsProps {
  onRate: (quality: Quality) => void
  disabled?: boolean
}

const buttons: { quality: Quality; label: string; variant: 'destructive' | 'secondary' | 'default' | 'success' }[] = [
  { quality: 0, label: 'Again', variant: 'destructive' },
  { quality: 2, label: 'Hard', variant: 'secondary' },
  { quality: 3, label: 'Good', variant: 'default' },
  { quality: 5, label: 'Easy', variant: 'success' },
]

export function QualityButtons({ onRate, disabled }: QualityButtonsProps) {
  return (
    <div className="grid grid-cols-4 gap-2">
      {buttons.map((b) => (
        <Button
          key={b.quality}
          variant={b.variant}
          onClick={() => onRate(b.quality)}
          disabled={disabled}
          className="w-full"
        >
          {b.label}
        </Button>
      ))}
    </div>
  )
}
