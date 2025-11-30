import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface User {
  user_id: string
  email: string
  full_name: string
  role: string
  permissions: string[]
}

interface AuthState {
  user: User | null
  accessToken: string | null
  isAuthenticated: boolean
  login: (token: string, user: User) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      login: (token: string, user: User) => {
        set({
          accessToken: token,
          user,
          isAuthenticated: true,
        })
      },
      logout: () => {
        set({
          accessToken: null,
          user: null,
          isAuthenticated: false,
        })
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
)

