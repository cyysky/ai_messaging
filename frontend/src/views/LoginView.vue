<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="5" lg="4">
        <v-card class="pa-4" elevation="8" rounded="xl">
          <v-card-text class="text-center pb-0">
            <v-icon size="64" color="primary" class="mb-4">mdi-message-text</v-icon>
            <h1 class="text-h4 font-weight-bold mb-2">Welcome Back</h1>
            <p class="text-body-2 text-medium-emphasis mb-6">Sign in to continue to AI Messaging</p>
          </v-card-text>
          
          <v-card-text>
            <v-form ref="form" v-model="valid" @submit.prevent="handleLogin">
              <v-text-field
                v-model="username"
                label="Username"
                prepend-inner-icon="mdi-account-outline"
                :rules="[rules.required]"
                autofocus
              ></v-text-field>
              <v-text-field
                v-model="password"
                label="Password"
                :type="showPassword ? 'text' : 'password'"
                prepend-inner-icon="mdi-lock-outline"
                :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showPassword = !showPassword"
                :rules="[rules.required]"
              ></v-text-field>
              
              <v-btn
                block
                color="primary"
                size="large"
                class="mt-4 mb-4"
                @click="handleLogin"
                :loading="authStore.loading"
                :disabled="!valid"
              >
                Sign In
              </v-btn>
            </v-form>
            
            <v-alert v-if="authStore.error" type="error" variant="tonal" class="mb-4">
              {{ authStore.error }}
            </v-alert>
          </v-card-text>
          
          <v-divider class="mx-4"></v-divider>
          
          <v-card-actions class="justify-center py-4">
            <span class="text-body-2 text-medium-emphasis">Don't have an account?</span>
            <v-btn to="/register" color="primary" variant="text" class="px-2">
              Sign Up
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const valid = ref(false)
const username = ref('')
const password = ref('')
const showPassword = ref(false)

const showSnackbar = inject<(message: string, color?: string) => void>('showSnackbar')

const rules = {
  required: (v: string) => !!v || 'Required',
}

async function handleLogin() {
  if (!valid.value) return
  
  const success = await authStore.login({
    username: username.value,
    password: password.value,
  })
  
  if (success) {
    showSnackbar?.('Login successful!', 'success')
    router.push('/')
  }
}
</script>