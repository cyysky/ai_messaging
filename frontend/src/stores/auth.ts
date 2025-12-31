import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService, type LoginRequest, type RegisterRequest, type AuthResponse } from '@/services/api'

export interface User {
  id: number
  email: string
  username: string
  is_superuser: boolean
  is_active: boolean
  full_name: string | null
  bio: string | null
  phone_number: string | null
  created_at: string
  updated_at: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)
  const isSuperuser = computed(() => user.value?.is_superuser ?? false)

  async function login(data: LoginRequest) {
    loading.value = true
    error.value = null
    try {
      const response = await authService.login(data)
      token.value = response.access_token
      user.value = response.user
      localStorage.setItem('token', response.access_token)
      localStorage.setItem('user', JSON.stringify(response.user))
      return true
    } catch (e: unknown) {
      const axiosError = e as { response?: { data?: { detail?: string } } }
      error.value = axiosError.response?.data?.detail || 'Login failed'
      return false
    } finally {
      loading.value = false
    }
  }

  async function register(data: RegisterRequest) {
    loading.value = true
    error.value = null
    try {
      const response = await authService.register(data)
      token.value = response.access_token
      user.value = response.user
      localStorage.setItem('token', response.access_token)
      localStorage.setItem('user', JSON.stringify(response.user))
      return true
    } catch (e: unknown) {
      const axiosError = e as { response?: { data?: { detail?: string } } }
      error.value = axiosError.response?.data?.detail || 'Registration failed'
      return false
    } finally {
      loading.value = false
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  function initializeAuth() {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')
    if (storedToken) {
      token.value = storedToken
    }
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch {
        user.value = null
      }
    }
  }

  initializeAuth()

  return {
    token,
    user,
    loading,
    error,
    isAuthenticated,
    isSuperuser,
    login,
    register,
    logout,
    initializeAuth,
  }
})