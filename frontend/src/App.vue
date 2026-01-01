<template>
  <v-app>
    <v-app-bar color="primary" density="compact" v-if="authStore.isAuthenticated">
      <v-app-bar-title>My App</v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn to="/conversations" variant="text">
        <v-icon left>mdi-message-text</v-icon>
        Conversations
      </v-btn>
      <v-btn to="/reports" variant="text">
        <v-icon left>mdi-clipboard-text</v-icon>
        My Reports
      </v-btn>
      <v-btn v-if="authStore.isSuperuser" to="/admin/reports" variant="text">
        <v-icon left>mdi-shield-crown</v-icon>
        Manage Reports
      </v-btn>
      <v-btn v-if="authStore.isSuperuser" to="/users" variant="text">
        <v-icon left>mdi-account-group</v-icon>
        Users
      </v-btn>
      <v-btn to="/" variant="text">Home</v-btn>
      <v-btn @click="logout" variant="text">Logout</v-btn>
    </v-app-bar>
    
    <v-main>
      <router-view />
    </v-main>
    
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false">Close</v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script setup lang="ts">
import { ref, provide } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const snackbar = ref({
  show: false,
  message: '',
  color: 'success'
})

function showSnackbar(message: string, color: string = 'success') {
  snackbar.value = { show: true, message, color }
}

provide('showSnackbar', showSnackbar)

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>