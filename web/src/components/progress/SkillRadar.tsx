import {
  RadarChart, PolarGrid, PolarAngleAxis, Radar as RechartsRadar,
  ResponsiveContainer,
} from 'recharts'

interface SkillRadarProps {
  data: { skill: string; score: number }[]
}

export function SkillRadar({ data }: SkillRadarProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={data}>
        <PolarGrid stroke="#2A2A3E" />
        <PolarAngleAxis dataKey="skill" tick={{ fill: '#9CA3AF', fontSize: 12 }} />
        <RechartsRadar
          dataKey="score"
          stroke="#4A90E2"
          fill="#4A90E2"
          fillOpacity={0.4}
        />
      </RadarChart>
    </ResponsiveContainer>
  )
}
