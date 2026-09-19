import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getAlerts, acknowledgeAlert } from '@/services/api'
import { Alert } from '@/types'
import { Check, AlertTriangle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { formatDistanceToNow } from 'date-fns'
import { useEffect, useRef } from 'react'

function playAlertSound() {
  try {
    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)()
    const oscillator = ctx.createOscillator()
    const gain = ctx.createGain()
    oscillator.connect(gain)
    gain.connect(ctx.destination)
    oscillator.frequency.value = 880
    oscillator.type = 'sine'
    gain.gain.setValueAtTime(0.3, ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5)
    oscillator.start(ctx.currentTime)
    oscillator.stop(ctx.currentTime + 0.5)
  } catch (e) {
    console.log('Sound play failed', e)
  }
}

export default function AlertsPage() {
  const queryClient = useQueryClient()
  const prevCount = useRef(0)

  const { data: alerts = [], isLoading } = useQuery<Alert[]>({
    queryKey: ['alerts'],
    queryFn: () => getAlerts(),
    refetchInterval: 10000,
  })

  useEffect(() => {
    const unacked = alerts.filter((a) => !a.is_acknowledged).length
    if (unacked > prevCount.current && unacked > 0) {
      playAlertSound()
    }
    prevCount.current = unacked
  }, [alerts])

  const ackMutation = useMutation({
    mutationFn: (id: number) => acknowledgeAlert(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      queryClient.invalidateQueries({ queryKey: ['summary'] })
    },
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Alerts</h1>
        <p className="text-slate-400 mt-1">Hotspot detection alerts requiring attention</p>
      </div>

      <div className="space-y-3">
        {isLoading ? (
          <div className="text-slate-500 py-8 text-center">Loading alerts...</div>
        ) : alerts.length === 0 ? (
          <div className="bg-slate-900 border border-slate-800 rounded-xl py-12 text-center text-slate-500">
            No alerts yet
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className={cn(
                'bg-slate-900 border rounded-xl p-4 flex items-start gap-4',
                alert.is_acknowledged ? 'border-slate-800 opacity-60' : 'border-slate-700'
              )}
            >
              <div
                className={cn(
                  'p-2 rounded-lg shrink-0',
                  alert.severity === 'high'
                    ? 'bg-red-500/15 text-red-400'
                    : alert.severity === 'medium'
                    ? 'bg-amber-500/15 text-amber-400'
                    : 'bg-blue-500/15 text-blue-400'
                )}
              >
                <AlertTriangle className="w-5 h-5" />
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="font-medium text-white">{alert.title}</h3>
                    {alert.message && (
                      <p className="text-sm text-slate-400 mt-0.5">{alert.message}</p>
                    )}
                  </div>
                  <span className="text-xs text-slate-500 whitespace-nowrap">
                    {formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}
                  </span>
                </div>

                <div className="flex items-center gap-3 mt-3">
                  <span className="text-xs text-slate-500">
                    Confidence: {(alert.confidence * 100).toFixed(1)}%
                  </span>
                  <span
                    className={cn(
                      'text-xs px-2 py-0.5 rounded-full font-medium',
                      alert.severity === 'high'
                        ? 'bg-red-500/15 text-red-400'
                        : 'bg-amber-500/15 text-amber-400'
                    )}
                  >
                    {alert.severity}
                  </span>

                  {!alert.is_acknowledged && (
                    <button
                      onClick={() => ackMutation.mutate(alert.id)}
                      disabled={ackMutation.isPending}
                      className="ml-auto inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-blue-600/15 text-blue-400 hover:bg-blue-600/25 text-xs font-medium transition-colors"
                    >
                      <Check className="w-3.5 h-3.5" />
                      Acknowledge
                    </button>
                  )}
                  {alert.is_acknowledged && (
                    <span className="ml-auto text-xs text-emerald-500">Acknowledged</span>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}