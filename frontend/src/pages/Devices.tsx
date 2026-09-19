import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getDevices, updateDevice } from '@/services/api'
import { Device } from '@/types'
import { Search, Shield, ShieldOff } from 'lucide-react'
import { cn } from '@/lib/utils'
import { formatDistanceToNow } from 'date-fns'

function isPrivateIp(ip: string): boolean {
  if (!ip) return false
  if (ip.startsWith('192.168.')) return true
  if (ip.startsWith('10.')) return true
  return /^172\.(1[6-9]|2[0-9]|3[0-1])\./.test(ip)
}

export default function DevicesPage() {
  const [search, setSearch] = useState('')
  const [labelFilter, setLabelFilter] = useState<string>('')
  const queryClient = useQueryClient()

  const { data: devices = [], isLoading } = useQuery<Device[]>({
    queryKey: ['devices', search, labelFilter],
    queryFn: () => getDevices({ search: search || undefined, label: labelFilter || undefined }),
    refetchInterval: 10000,
  })

  const localDevices = devices.filter((d) => isPrivateIp(d.ip_address))

  const whitelistMutation = useMutation({
    mutationFn: ({ id, value }: { id: number; value: boolean }) =>
      updateDevice(id, { is_whitelisted: value }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['devices'] }),
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Devices</h1>
        <p className="text-slate-400 mt-1">
          Local network devices only (Wi-Fi / private IPs)
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search IP or MAC..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-slate-900 border border-slate-800 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <select
          value={labelFilter}
          onChange={(e) => setLabelFilter(e.target.value)}
          className="px-4 py-2.5 rounded-lg bg-slate-900 border border-slate-800 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Labels</option>
          <option value="normal">Normal</option>
          <option value="hotspot">Hotspot</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-left">
                <th className="px-4 py-3 font-medium">IP Address</th>
                <th className="px-4 py-3 font-medium">Label</th>
                <th className="px-4 py-3 font-medium">Confidence</th>
                <th className="px-4 py-3 font-medium">Hotspot Count</th>
                <th className="px-4 py-3 font-medium">Last Seen</th>
                <th className="px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                    Loading...
                  </td>
                </tr>
              ) : localDevices.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                    No local devices found
                  </td>
                </tr>
              ) : (
                localDevices.map((d) => (
                  <tr key={d.id} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                    <td className="px-4 py-3 font-mono text-white">{d.ip_address}</td>
                    <td className="px-4 py-3">
                      <span
                        className={cn(
                          'inline-flex px-2 py-0.5 rounded-full text-xs font-medium',
                          d.current_label === 'hotspot'
                            ? 'bg-red-500/15 text-red-400'
                            : 'bg-emerald-500/15 text-emerald-400'
                        )}
                      >
                        {d.current_label}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-300">
                      {(d.last_confidence * 100).toFixed(1)}%
                    </td>
                    <td className="px-4 py-3 text-slate-300">{d.hotspot_count}</td>
                    <td className="px-4 py-3 text-slate-400">
                      {formatDistanceToNow(new Date(d.last_seen), { addSuffix: true })}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() =>
                          whitelistMutation.mutate({ id: d.id, value: !d.is_whitelisted })
                        }
                        className={cn(
                          'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition-colors',
                          d.is_whitelisted
                            ? 'bg-amber-500/15 text-amber-400 hover:bg-amber-500/25'
                            : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                        )}
                        title={d.is_whitelisted ? 'Remove from whitelist' : 'Add to whitelist'}
                      >
                        {d.is_whitelisted ? (
                          <Shield className="w-3.5 h-3.5" />
                        ) : (
                          <ShieldOff className="w-3.5 h-3.5" />
                        )}
                        {d.is_whitelisted ? 'Whitelisted' : 'Whitelist'}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}