<template>
  <v-app>
    <!-- Navigation Drawer for mobile -->
    <v-navigation-drawer v-model="drawer" app temporary v-if="authStore.isAuthenticated">
      <v-list-item class="pa-4">
        <template v-slot:prepend>
          <v-avatar color="primary" size="40">
            <span class="text-h6">{{ userInitials }}</span>
          </v-avatar>
        </template>
        <v-list-item-title class="text-h6">{{ authStore.user?.full_name || authStore.user?.username || 'User' }}</v-list-item-title>
        <v-list-item-subtitle>{{ authStore.user?.email }}</v-list-item-subtitle>
      </v-list-item>
      <v-divider></v-divider>
      <v-list nav density="comfortable">
        <v-list-item to="/" prepend-icon="mdi-home" title="Home"></v-list-item>
        <v-list-item to="/conversations" prepend-icon="mdi-message-text" title="Conversations"></v-list-item>
        <v-list-item to="/reports" prepend-icon="mdi-clipboard-text" title="My Reports"></v-list-item>
        <v-list-item v-if="authStore.isSuperuser" to="/admin/reports" prepend-icon="mdi-shield-crown" title="Manage Reports"></v-list-item>
        <v-list-item v-if="authStore.isSuperuser" to="/users" prepend-icon="mdi-account-group" title="Users"></v-list-item>
      </v-list>
      <template v-slot:append>
        <div class="pa-4">
          <v-btn block color="error" variant="tonal" @click="logout">
            <v-icon left>mdi-logout</v-icon>
            Logout
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <!-- App Bar -->
    <v-app-bar color="surface" elevation="1" v-if="authStore.isAuthenticated">
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-app-bar-title class="text-h6 font-weight-bold">
        <v-icon color="primary" class="mr-2">mdi-message-text</v-icon>
        AI Messaging
      </v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn icon @click="toggleTheme" class="mr-2">
        <v-icon>{{ isDark ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
      </v-btn>
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn icon v-bind="props">
            <v-avatar color="primary" size="32">
              <span class="text-body-2">{{ userInitials }}</span>
            </v-avatar>
          </v-btn>
        </template>
        <v-list density="compact" min-width="150">
          <v-list-item>
            <v-list-item-title class="font-weight-medium">{{ authStore.user?.full_name || authStore.user?.username || 'User' }}</v-list-item-title>
            <v-list-item-subtitle>{{ authStore.user?.email }}</v-list-item-subtitle>
          </v-list-item>
          <v-divider class="my-2"></v-divider>
          <v-list-item @click="logout">
            <template v-slot:prepend>
              <v-icon color="error">mdi-logout</v-icon>
            </template>
            <v-list-item-title class="text-error">Logout</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <v-main class="bg-background">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </v-main>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000" location="bottom right">
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false">Close</v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script setup lang="ts">
import { ref, provide, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTheme } from 'vuetify'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const theme = useTheme()

const drawer = ref(false)
const snackbar = ref({
  show: false,
  message: '',
  color: 'success'
})

const userInitials = computed(() => {
  const name = authStore.user?.full_name || authStore.user?.username || 'U'
  return name.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2)
})

const isDark = computed(() => theme.global.current.value.dark)

function toggleTheme() {
  theme.global.name.value = isDark.value ? 'light' : 'dark'
}

function showSnackbar(message: string, color: string = 'success') {
  snackbar.value = { show: true, message, color }
}

provide('showSnackbar', showSnackbar)

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>