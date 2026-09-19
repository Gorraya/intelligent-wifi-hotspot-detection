import { useQuery } from '@tanstack/react-query'
import { getSummary, getTimeline } from '@/services/api'
import { SummaryStats, TimelinePoint } from '@/types'
import { Activity, AlertTriangle, Monitor, ShieldAlert } from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

function StatCard({ title, value, icon: Icon, color }: { title: string; value: number | string; icon: any; color: string }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-400">{title}</p>
          <p className="text-2xl font-bold text-white mt-1">{value}</p>
        </div>
        <div className={`p-2.5 rounded-lg ${color}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const { data: summary, isLoading: summaryLoading } = useQuery<SummaryStats>({
    queryKey: ['summary'],
    queryFn: getSummary,
    refetchInterval: 15000,
  })

  const { data: timeline } = useQuery<TimelinePoint[]>({
    queryKey: ['timeline'],
    queryFn: () => getTimeline(24),
    refetchInterval: 30000,
  })

  if (summaryLoading) {
    return <div className="text-slate-400">Loading dashboard...</div>
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-slate-400 mt-1">Real-time overview of network hotspot activity</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Devices" value={summary?.total_devices ?? 0} icon={Monitor} color="bg-blue-500/15 text-blue-400" />
        <StatCard title="Hotspot Devices" value={summary?.hotspot_devices ?? 0} icon={ShieldAlert} color="bg-red-500/15 text-red-400" />
        <StatCard title="Unacknowledged Alerts" value={summary?.unacknowledged_alerts ?? 0} icon={AlertTriangle} color="bg-amber-500/15 text-amber-400" />
        <StatCard title="Detections (24h)" value={summary?.detections_last_24h ?? 0} icon={Activity} color="bg-emerald-500/15 text-emerald-400" />
      </div>

      {/* Chart */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        <h2 className="text-lg font-semibold text-white mb-4">Detection Timeline (Last 24h)</h2>
        <div className="h-72">
          {timeline && timeline.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timeline}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="hour" stroke="#64748b" fontSize={12} tickFormatter={(v) => v.slice(11, 16)} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }}
                  labelStyle={{ color: '#94a3b8' }}
                />
                <Legend />
                <Area type="monotone" dataKey="normal" stackId="1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} name="Normal" />
                <Area type="monotone" dataKey="hotspot" stackId="1" stroke="#ef4444" fill="#ef4444" fillOpacity={0.4} name="Hotspot" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-slate-500">
              No detection data yet
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
