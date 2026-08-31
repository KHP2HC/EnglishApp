import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ReferenceLine, ResponsiveContainer,
} from 'recharts'

interface BandLineProps {
  data: { date: string; band: number }[]
  targetScore?: number
}

export function BandLine({ data, targetScore }: BandLineProps) {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2A2A3E" />
        <XAxis dataKey="date" tick={{ fill: '#9CA3AF', fontSize: 11 }} />
        <YAxis tick={{ fill: '#9CA3AF', fontSize: 11 }} />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1A1A2E',
            border: '1px solid #2A2A3E',
            borderRadius: '8px',
          }}
        />
        <Line
          type="monotone"
          dataKey="band"
          stroke="#4A90E2"
          strokeWidth={2}
          dot={{ fill: '#4A90E2', r: 4 }}
        />
        {targetScore && (
          <ReferenceLine
            y={targetScore}
            stroke="#F39C12"
            strokeDasharray="4 4"
            label={{ value: 'Target', fill: '#F39C12', fontSize: 11 }}
          />
        )}
      </LineChart>
    </ResponsiveContainer>
  )
}
