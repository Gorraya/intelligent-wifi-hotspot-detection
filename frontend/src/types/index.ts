export interface User {
  id: number
  email: string
  full_name: string
  is_active: boolean
  is_superuser: boolean
}

export interface Device {
  id: number
  ip_address: string
  mac_address: string | null
  current_label: 'normal' | 'hotspot' | 'suspicious'
  last_confidence: number
  first_seen: string
  last_seen: string
  total_detections: number
  hotspot_count: number
  is_whitelisted: boolean
  notes: string | null
}

export interface Alert {
  id: number
  device_id: number
  event_id: number | null
  severity: 'low' | 'medium' | 'high'
  title: string
  message: string | null
  confidence: number
  is_acknowledged: boolean
  acknowledged_at: string | null
  created_at: string
}

export interface SummaryStats {
  total_devices: number
  hotspot_devices: number
  normal_devices: number
  total_alerts: number
  unacknowledged_alerts: number
  detections_last_24h: number
}

export interface TimelinePoint {
  hour: string
  normal: number
  hotspot: number
}
