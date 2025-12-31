<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Login</v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <v-form ref="form" v-model="valid" @submit.prevent="handleLogin">
              <v-text-field
                v-model="username"
                label="Username"
                prepend-icon="mdi-account"
                :rules="[rules.required]"
                required
              ></v-text-field>
              <v-text-field
                v-model="password"
                label="Password"
                :type="showPassword ? 'text' : 'password'"
                prepend-icon="mdi-lock"
                :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append="showPassword = !showPassword"
                :rules="[rules.required]"
                required
              ></v-text-field>
            </v-form>
            <v-alert v-if="authStore.error" type="error" class="mt-4">
              {{ authStore.error }}
            </v-alert>
          </v-card-text>
          <v-card-actions>
            <v-btn to="/register" variant="text" color="secondary">
              Don't have an account? Register
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              @click="handleLogin"
              :loading="authStore.loading"
              :disabled="!valid"
            >
              Login
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