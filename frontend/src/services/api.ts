import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach token automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.status, error.response?.data)
    // Temporary: redirect band — error dekhne ke liye
    return Promise.reject(error)
  }
)

export default api

// Auth
export const login = async (email: string, password: string) => {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)
  const { data } = await api.post('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data
}

export const getMe = async () => {
  const { data } = await api.get('/auth/me')
  return data
}

// Devices
export const getDevices = async (params?: { label?: string; search?: string }) => {
  const { data } = await api.get('/devices/', { params })  // slash add ki
  return data
}

export const updateDevice = async (id: number, payload: { is_whitelisted?: boolean; notes?: string }) => {
  const { data } = await api.patch(`/devices/${id}`, payload)
  return data
}

// Alerts
export const getAlerts = async (params?: { acknowledged?: boolean; severity?: string }) => {
  const { data } = await api.get('/alerts/', { params })  // slash add ki
  return data
}

export const acknowledgeAlert = async (id: number) => {
  const { data } = await api.post(`/alerts/${id}/acknowledge`)
  return data
}

// Analytics
export const getSummary = async () => {
  const { data } = await api.get('/analytics/summary')
  return data
}

export const getTimeline = async (hours = 24) => {
  const { data } = await api.get('/analytics/timeline', { params: { hours } })
  return data
}

