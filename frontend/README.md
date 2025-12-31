# Frontend - Vue.js + TypeScript + Vuetify + Vite

A modern frontend application built with Vue.js 3, TypeScript, Vuetify 3, and Vite. This application provides a complete user interface for interacting with the backend API, including authentication, dashboard, and responsive design.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Development](#development)
- [Build for Production](#build-for-production)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [API Integration](#api-integration)
- [Authentication](#authentication)
- [State Management](#state-management)
- [Routing](#routing)
- [Customization](#customization)

## Features

- **Authentication System**: Complete login and registration flow with JWT token management
- **Protected Routes**: Route guards to restrict access to authenticated users
- **Responsive Design**: Mobile-first UI using Vuetify 3 components
- **State Management**: Pinia stores for centralized state management
- **TypeScript Support**: Full TypeScript integration for type safety
- **API Integration**: Axios-based HTTP client with interceptors
- **Material Design Icons**: MDI icon set integration
- **Dark/Light Themes**: Built-in theme support
- **User Management**: Admin interface for managing users (superuser only)

## Prerequisites

- Node.js 18.0 or higher
- npm 9.0 or higher (or yarn)
- A running backend server (default: http://localhost:8000)

## Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

   Or if using yarn:
   ```bash
   yarn install
   ```

## Development

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Development Features

- Hot Module Replacement (HMR) for instant updates
- Source map generation for debugging
- Type checking in development mode
- ESLint integration

## Build for Production

Build the application for production deployment:

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Production Build Features

- TypeScript compilation
- Minification and optimization
- Code splitting
- Asset optimization

Preview the production build locally:

```bash
npm run preview
```

## Project Structure

```
frontend/
├── public/                 # Static public assets
│   └── vite.svg           # Favicon
├── src/                   # Source code
│   ├── assets/            # Application assets
│   ├── components/        # Reusable Vue components
│   ├── router/            # Vue Router configuration
│   │   └── index.ts       # Router setup with guards
│   ├── services/          # API services
│   │   └── api.ts         # Axios instance and API methods
│   ├── stores/            # Pinia stores
│   │   └── auth.ts        # Authentication store
│   ├── views/             # Page components
│   │   ├── HomeView.vue           # Dashboard/home page
│   │   ├── LoginView.vue          # Login page
│   │   ├── RegisterView.vue       # Registration page
│   │   ├── ConversationsView.vue  # Messages/Conversations page
│   │   └── UserManagementView.vue # User Management (superuser only)
│   ├── App.vue            # Root component
│   ├── env.d.ts           # TypeScript declarations
│   ├── main.ts            # Application entry point
│   └── vuetify.ts         # Vuetify configuration
├── index.html             # HTML entry point
├── package.json           # Project dependencies
├── tsconfig.json          # TypeScript configuration
├── tsconfig.node.json     # Node TypeScript configuration
├── vite.config.ts         # Vite configuration
└── README.md              # This file
```

## Configuration

### Vite Configuration

The `vite.config.ts` file contains the following configurations:

- **Proxy**: API requests to `/api` are proxied to `http://localhost:8000`
- **Aliases**: `@` alias points to the `src` directory
- **Port**: Development server runs on port 3000

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

### TypeScript Configuration

The project uses two TypeScript configuration files:

- `tsconfig.json`: Main configuration for application code
- `tsconfig.node.json`: Configuration for Node.js-specific code (Vite config)

Key settings:
- `strict: true` - Enable all strict type checking options
- `jsx: preserve` - Preserve JSX for Vue templates
- `paths` - Configure path aliases

### Vuetify Configuration

The `vuetify.ts` file configures:

- **Components**: All Vuetify components are imported
- **Directives**: All Vuetify directives are imported
- **Icons**: Material Design Icons (MDI) set
- **Themes**: Light and dark themes with custom colors

## API Integration

### Axios Setup

The API service is configured in [`src/services/api.ts`](src/services/api.ts):

```typescript
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})
```

### Request Interceptor

Automatically adds the JWT token to outgoing requests:

```typescript
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

### Response Interceptor

Handles 401 Unauthorized responses by clearing auth data and redirecting to login:

```typescript
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
```

### API Service Methods

The `authService` object provides the following methods:

- `login(data: LoginRequest)`: Authenticate user and get token (returns AuthResponse with user data)
- `register(data: RegisterRequest)`: Register new user
- `getCurrentUser()`: Get current user information
- `getConversations()`: Get all conversations for current user
- `getConversationMessages(conversationId, skip, limit)`: Get messages for a conversation
- `sendMessage(conversationId, data)`: Send a message in a conversation
- `markConversationRead(conversationId)`: Mark all messages in a conversation as read

### User Service Methods

The `userService` object provides user management operations (superuser only):

- `listUsers(skip, limit)`: List all users
- `getUser(userId)`: Get a specific user
- `createUser(data)`: Create a new user
- `deleteUser(userId)`: Delete a user
- `disableUser(userId)`: Disable a user
- `enableUser(userId)`: Enable a user
- `toggleSuperuser(userId, isSuperuser)`: Toggle superuser status

### Message Service Methods

The `messageService` object provides full CRUD operations for messages:

- `listMessages(skip, limit, unreadOnly)`: List all messages with optional filters
- `getMessage(messageId)`: Get a specific message by ID
- `createMessage(data)`: Send a new message
- `updateMessage(messageId, data)`: Update message content (sender only)
- `deleteMessage(messageId)`: Delete a message
- `markAsRead(messageId)`: Mark a message as read (recipient only)
- `getUnreadCount()`: Get count of unread messages
- `markAllAsRead()`: Mark all received messages as read
- `listSentMessages(skip, limit)`: List sent messages
- `listReceivedMessages(skip, limit, unreadOnly)`: List received messages

## Authentication

### Auth Store

The authentication state is managed by Pinia store in [`src/stores/auth.ts`](src/stores/auth.ts):

```typescript
export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)
  const isSuperuser = computed(() => user.value?.is_superuser ?? false)

  async function login(data: LoginRequest) { ... }
  async function register(data: RegisterRequest) { ... }
  function logout() { ... }
  function initializeAuth() { ... }
})
```

### Auth State

The store maintains:
- **token**: JWT access token
- **user**: Current user information
- **loading**: Loading state for async operations
- **error**: Error messages

### Superuser Access

The auth store provides an `isSuperuser` computed property that checks if the current user has superuser privileges:

```typescript
const isSuperuser = computed(() => user.value?.is_superuser ?? false)
```

This is used in the dashboard to conditionally show the User Management link:

```vue
<v-btn v-if="authStore.isSuperuser" to="/users" variant="text">
  <v-icon left>mdi-account-group</v-icon>
  Users
</v-btn>
```

The User Management route (`/users`) is protected by both authentication and superuser checks in the router.

### Usage

```typescript
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// Check if authenticated
if (authStore.isAuthenticated) {
  // User is logged in
}

// Check if superuser
if (authStore.isSuperuser) {
  // User has admin privileges
}

// Login
const success = await authStore.login({
  username: 'user',
  password: 'password123'
})

// Logout
authStore.logout()
```

## State Management

### Pinia Stores

The project uses Pinia for state management. Currently implemented:

- **auth.ts**: Authentication state (token, user, login/register/logout, isSuperuser)

### Store Structure

Each store follows this pattern:

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useStoreName = defineStore('storeName', () => {
  // State (refs)
  const state = ref(initialValue)

  // Getters (computed)
  const getter = computed(() => ...)

  // Actions
  function action() { ... }

  return { state, getter, action }
})
```

## Routing

### Router Configuration

The router is configured in [`src/router/index.ts`](src/router/index.ts):

```typescript
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true },
    },
    {
      path: '/conversations',
      name: 'conversations',
      component: ConversationsView,
      meta: { requiresAuth: true },
    },
    {
      path: '/users',
      name: 'users',
      component: UserManagementView,
      meta: { requiresAuth: true, requiresSuperuser: true },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { guest: true },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { guest: true },
    },
  ],
})
```

### Route Guards

The router includes navigation guards:

```typescript
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.guest && authStore.isAuthenticated) {
    next('/')
  } else if (to.meta.requiresSuperuser && !authStore.isSuperuser) {
    next('/')
  } else {
    next()
  }
})
```

### Route Meta Fields

- `requiresAuth`: Route requires authentication
- `guest`: Route is only for guests (not authenticated users)
- `requiresSuperuser`: Route requires superuser privileges

### Superuser Routes

Routes that require superuser access should include the `requiresSuperuser` meta field:

```typescript
{
  path: '/users',
  name: 'users',
  component: UserManagementView,
  meta: { requiresAuth: true, requiresSuperuser: true },
}
```

The router guard checks this and redirects non-superusers:

```typescript
} else if (to.meta.requiresSuperuser && !authStore.isSuperuser) {
  next('/')
}
```

## User Management (Superuser)

The User Management view provides a complete interface for managing users:

### Features

- **User List**: View all users with search functionality
- **User Status**: See active/disabled status
- **User Roles**: Identify superusers vs regular users
- **Create User**: Add new users with username, email, password
- **Disable/Enable**: Toggle user account status
- **Toggle Superuser**: Grant or revoke admin privileges
- **Delete User**: Remove users (cannot delete self)

### Accessing User Management

The User Management link appears in the navigation bar only for superusers:

```vue
<v-btn v-if="authStore.isSuperuser" to="/users" variant="text">
  <v-icon left>mdi-account-group</v-icon>
  Users
</v-btn>
```

### User Table Columns

| Column | Description |
|--------|-------------|
| Username | User's unique username |
| Email | User's email address |
| Full Name | User's full name (optional) |
| Status | Active or Disabled |
| Role | Superuser or User |
| Created | Account creation date |
| Actions | Management buttons |

### Actions

| Action | Description | Restrictions |
|--------|-------------|--------------|
| Disable | Disable user account | Cannot disable self |
| Enable | Enable disabled account | - |
| Toggle Superuser | Grant/remove admin | Cannot change self |
| Delete | Permanently delete user | Cannot delete self |

## Customization

### Theming

Modify the theme in [`src/vuetify.ts`](src/vuetify.ts):

```typescript
export default createVuetify({
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1976D2',
          secondary: '#424242',
          accent: '#82B1FF',
          error: '#FF5252',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FFC107',
        },
      },
      dark: {
        colors: {
          primary: '#2196F3',
          // ... dark theme colors
        },
      },
    },
  },
})
```

### Adding New Views

1. Create a new Vue component in `src/views/`
2. Add the route in `src/router/index.ts`:

```typescript
{
  path: '/new-page',
  name: 'new-page',
  component: () => import('@/views/NewPageView.vue'),
  meta: { requiresAuth: true },
}
```

### Adding New Stores

1. Create a new file in `src/stores/`
2. Define the store using Pinia
3. Import and use in components

### Adding API Endpoints

Add new methods to [`src/services/api.ts`](src/services/api.ts):

```typescript
export const apiService = {
  async getData() {
    const response = await api.get('/endpoint')
    return response.data
  },
  
  async postData(data: any) {
    const response = await api.post('/endpoint', data)
    return response.data
  },
}
```

## Backend Integration

The frontend is configured to proxy API requests to the backend:

- **Frontend URL**: http://localhost:3000
- **Backend URL**: http://localhost:8000
- **API Base Path**: /api

All requests to `/api/*` are proxied to `http://localhost:8000/api/*`

### CORS Configuration

Ensure the backend allows CORS requests from the frontend origin (http://localhost:3000).

## Troubleshooting

### TypeScript Errors

If you see TypeScript errors about missing modules, ensure:
1. Dependencies are installed: `npm install`
2. TypeScript is working: `npx tsc --noEmit`

### Module Not Found

If you get "Cannot find module" errors:
1. Check the import path is correct
2. Ensure the file exists at the specified path
3. Restart the development server

### API Requests Failing

1. Ensure the backend server is running
2. Check the proxy configuration in `vite.config.ts`
3. Verify the API endpoints match the backend routes

### User Management Not Visible

If the User Management link doesn't appear in the navigation:
1. Ensure you are logged in as a superuser
2. Check that the backend login returns user data with `is_superuser: true`
3. Verify the auth store is properly initialized with user data

## License

This project is part of the full-stack application and is licensed under the same license as the main project.