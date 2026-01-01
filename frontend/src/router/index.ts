import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import ConversationsView from '@/views/ConversationsView.vue'
import UserManagementView from '@/views/UserManagementView.vue'
import UserReportView from '@/views/UserReportView.vue'
import SuperuserReportView from '@/views/SuperuserReportView.vue'

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
      path: '/reports',
      name: 'reports',
      component: UserReportView,
      meta: { requiresAuth: true },
    },
    {
      path: '/admin/reports',
      name: 'admin-reports',
      component: SuperuserReportView,
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

export default router