import axios, { type AxiosInstance, type AxiosError } from 'axios'

const api: AxiosInstance = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: {
    id: number
    email: string
    name: string
  }
}

export interface MessageResponse {
  id: number
  sender_id: number
  recipient_id: number
  content: string
  is_read: boolean
  conversation_id: string | null
  created_at: string
  updated_at: string
}

export interface ConversationResponse {
  conversation_id: string
  other_user_id: number
  other_user_name: string
  last_message: string
  last_message_at: string
  unread_count: number
}

export interface MessageCreate {
  recipient_id: number
  content: string
  conversation_id?: string
}

export interface MessageUpdate {
  content?: string
}

export const messageService = {
  async listMessages(skip = 0, limit = 100, unreadOnly = false): Promise<MessageResponse[]> {
    const response = await api.get<MessageResponse[]>('/messages', {
      params: { skip, limit, unread_only: unreadOnly }
    })
    return response.data
  },

  async getMessage(messageId: number): Promise<MessageResponse> {
    const response = await api.get<MessageResponse>(`/messages/${messageId}`)
    return response.data
  },

  async createMessage(data: MessageCreate): Promise<MessageResponse> {
    const response = await api.post<MessageResponse>('/messages', data)
    return response.data
  },

  async updateMessage(messageId: number, data: MessageUpdate): Promise<MessageResponse> {
    const response = await api.put<MessageResponse>(`/messages/${messageId}`, data)
    return response.data
  },

  async deleteMessage(messageId: number): Promise<void> {
    await api.delete(`/messages/${messageId}`)
  },

  async markAsRead(messageId: number): Promise<void> {
    await api.put(`/messages/${messageId}/read`)
  },

  async getUnreadCount(): Promise<{ unread_count: number }> {
    const response = await api.get<{ unread_count: number }>('/messages/unread/count')
    return response.data
  },

  async markAllAsRead(): Promise<void> {
    await api.put('/messages/read-all')
  },

  async listSentMessages(skip = 0, limit = 100): Promise<MessageResponse[]> {
    const response = await api.get<MessageResponse[]>('/messages/sent', {
      params: { skip, limit }
    })
    return response.data
  },

  async listReceivedMessages(skip = 0, limit = 100, unreadOnly = false): Promise<MessageResponse[]> {
    const response = await api.get<MessageResponse[]>('/messages/received', {
      params: { skip, limit, unread_only: unreadOnly }
    })
    return response.data
  }
}

export const authService = {
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/login', data)
    return response.data
  },

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/register', data)
    return response.data
  },

  async getCurrentUser() {
    const response = await api.get('/auth/me')
    return response.data
  },

  async getConversations(): Promise<ConversationResponse[]> {
    const response = await api.get<ConversationResponse[]>('/auth/conversations')
    return response.data
  },

  async getConversationMessages(conversationId: string, skip = 0, limit = 100): Promise<MessageResponse[]> {
    const response = await api.get<MessageResponse[]>(`/auth/conversations/${conversationId}/messages`, {
      params: { skip, limit }
    })
    return response.data
  },

  async sendMessage(conversationId: string, data: MessageCreate): Promise<MessageResponse> {
    const response = await api.post<MessageResponse>(`/auth/conversations/${conversationId}/messages`, data)
    return response.data
  },

  async markConversationRead(conversationId: string): Promise<void> {
    await api.put(`/auth/conversations/${conversationId}/read`)
  },
}

export default api