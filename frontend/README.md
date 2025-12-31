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
│   │   ├── HomeView.vue       # Dashboard/home page
│   │   ├── LoginView.vue      # Login page
│   │   └── RegisterView.vue   # Registration page
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

- `login(data: LoginRequest)`: Authenticate user and get token
- `register(data: RegisterRequest)`: Register new user
- `getCurrentUser()`: Get current user information

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

### Usage

```typescript
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// Check if authenticated
if (authStore.isAuthenticated) {
  // User is logged in
}

// Login
const success = await authStore.login({
  email: 'user@example.com',
  password: 'password123'
})

// Logout
authStore.logout()
```

## State Management

### Pinia Stores

The project uses Pinia for state management. Currently implemented:

- **auth.ts**: Authentication state (token, user, login/register/logout)

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
  } else {
    next()
  }
})
```

### Route Meta Fields

- `requiresAuth`: Route requires authentication
- `guest`: Route is only for guests (not authenticated users)

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

## License

This project is part of the full-stack application and is licensed under the same license as the main project.