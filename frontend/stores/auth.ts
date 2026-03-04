import { defineStore } from 'pinia'
import { api } from '~/utils/api'

interface User {
  id: string
  email: string
  full_name: string
  location: string
  credits: number
  onboarding_completed: boolean
  is_admin: boolean
}

interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

interface AuthState {
  token: string | null
  user: User | null
  loading: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: null,
    user: null,
    loading: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    needsOnboarding: (state) => state.user && !state.user.onboarding_completed
  },

  actions: {
    // Initialize from localStorage
    init() {
      if (process.client) {
        const token = localStorage.getItem('token')
        const user = localStorage.getItem('user')

        if (token) {
          this.token = token
        }

        if (user) {
          try {
            this.user = JSON.parse(user)
          } catch (e) {
            console.error('Failed to parse user from localStorage', e)
          }
        }
      }
    },

    // Set authentication data
    setAuth(token: string, user: User) {
      this.token = token
      this.user = user

      if (process.client) {
        localStorage.setItem('token', token)
        localStorage.setItem('user', JSON.stringify(user))
      }
    },

    // Update user data
    updateUser(user: User) {
      this.user = user

      if (process.client) {
        localStorage.setItem('user', JSON.stringify(user))
      }
    },

    // Clear authentication
    clearAuth() {
      this.token = null
      this.user = null

      if (process.client) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    },

    // Register
    async register(email: string, password: string, full_name: string, location: string) {
      try {
        this.loading = true

        const response = await api.post<TokenResponse>('/auth/register', {
          email,
          password,
          full_name,
          location
        })

        this.setAuth(response.access_token, response.user)

        return response
      } catch (error: any) {
        throw new Error(error.message || 'Registration failed')
      } finally {
        this.loading = false
      }
    },

    // Login
    async login(email: string, password: string) {
      try {
        this.loading = true

        const response = await api.post<TokenResponse>('/auth/login', {
          email,
          password
        })

        this.setAuth(response.access_token, response.user)

        return response
      } catch (error: any) {
        throw new Error(error.message || 'Login failed')
      } finally {
        this.loading = false
      }
    },

    // Logout
    logout() {
      this.clearAuth()
      navigateTo('/login')
    },

    // Fetch current user
    async fetchMe() {
      if (!this.token) return

      try {
        const response = await api.get<User>('/auth/me')
        this.updateUser(response)
      } catch (error) {
        // Token might be invalid
        this.clearAuth()
        throw error
      }
    }
  }
})
