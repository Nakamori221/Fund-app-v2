import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

const apiBaseURL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const apiVersion = import.meta.env.VITE_API_VERSION || 'v1'

const api = axios.create({
  baseURL: `${apiBaseURL}/api/${apiVersion}`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30秒
})

// リクエストインターセプター: トークンを自動的に追加
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// レスポンスインターセプター: 401エラー時にログアウト
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

