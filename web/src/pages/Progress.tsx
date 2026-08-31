import { useAuthStore } from '@/stores/auth.store'
import { useProgressStats, useDailyActivity } from '@/hooks/useProgress'
import { Heatmap } from '@/components/progress/Heatmap'
import { SkillRadar } from '@/components/progress/SkillRadar'
import { ErrorJournal } from '@/components/progress/ErrorJournal'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export function Progress() {
  const { user } = useAuthStore()
  const { data: stats } = useProgressStats(user?.id)
  const { data: activity } = useDailyActivity(user?.id, 365)

  if (!user) return <p>Loading…</p>

  const radarData = Object.entries(stats?.skill_accuracy || {}).map(([skill, s]) => ({
    skill: skill.charAt(0) + skill.slice(1).toLowerCase(),
    score: s.total > 0 ? Math.round((s.correct / s.total) * 100) : 0,
  }))

  const barData = Object.entries(stats?.time_by_skill || {}).map(([skill, mins]) => ({
    skill: skill.charAt(0) + skill.slice(1).toLowerCase(),
    minutes: mins,
  }))

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold font-heading">📊 Progress</h1>

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="charts">Charts</TabsTrigger>
          <TabsTrigger value="errors">Error Journal</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <StatBox label="Words Learned" value={stats?.words_learned || 0} />
            <StatBox label="Words Mastered" value={stats?.words_mastered || 0} />
            <StatBox label="Total XP" value={stats?.total_xp || 0} />
            <StatBox label="Sessions" value={stats?.total_sessions || 0} />
          </div>

          <Card>
            <CardHeader><CardTitle>Activity Heatmap (Last 52 Weeks)</CardTitle></CardHeader>
            <CardContent>
              <Heatmap activity={activity || {}} weeks={52} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="charts" className="space-y-4">
          <Card>
            <CardHeader><CardTitle>Time per Skill (Last 30 Days)</CardTitle></CardHeader>
            <CardContent>
              {barData.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={barData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2A2A3E" />
                    <XAxis dataKey="skill" tick={{ fill: '#9CA3AF', fontSize: 11 }} />
                    <YAxis tick={{ fill: '#9CA3AF', fontSize: 11 }} unit="m" />
                    <Tooltip contentStyle={{ backgroundColor: '#1A1A2E', border: '1px solid #2A2A3E', borderRadius: '8px' }} />
                    <Bar dataKey="minutes" fill="#4A90E2" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-sm text-gray-400 text-center py-8">No session data yet.</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Skill Balance (Accuracy %)</CardTitle></CardHeader>
            <CardContent>
              {radarData.length > 0 ? (
                <SkillRadar data={radarData} />
              ) : (
                <p className="text-sm text-gray-400 text-center py-8">No skill data yet.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="errors">
          <ErrorJournal userId={user.id} />
        </TabsContent>
      </Tabs>
    </div>
  )
}

function StatBox({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-border bg-surface-light dark:bg-surface-dark p-4 text-center">
      <p className="text-2xl font-bold text-accent">{value}</p>
      <p className="text-xs text-gray-400">{label}</p>
    </div>
  )
}
