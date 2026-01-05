<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="5" lg="4">
        <v-card class="pa-4" elevation="8" rounded="xl">
          <v-card-text class="text-center pb-0">
            <v-icon size="64" color="secondary" class="mb-4">mdi-account-plus</v-icon>
            <h1 class="text-h4 font-weight-bold mb-2">Create Account</h1>
            <p class="text-body-2 text-medium-emphasis mb-6">Join AI Messaging today</p>
          </v-card-text>
          
          <v-card-text>
            <v-form ref="form" v-model="valid" @submit.prevent="handleRegister">
              <v-text-field
                v-model="username"
                label="Username"
                prepend-inner-icon="mdi-account-outline"
                :rules="[rules.required]"
                autofocus
              ></v-text-field>
              <v-text-field
                v-model="email"
                label="Email"
                type="email"
                prepend-inner-icon="mdi-email-outline"
                :rules="[rules.required, rules.email]"
              ></v-text-field>
              <v-text-field
                v-model="password"
                label="Password"
                :type="showPassword ? 'text' : 'password'"
                prepend-inner-icon="mdi-lock-outline"
                :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showPassword = !showPassword"
                :rules="[rules.required, rules.minLength]"
              ></v-text-field>
              <v-text-field
                v-model="confirmPassword"
                label="Confirm Password"
                :type="showPassword ? 'text' : 'password'"
                prepend-inner-icon="mdi-lock-check-outline"
                :rules="[rules.required, rules.match]"
              ></v-text-field>
              
              <v-btn
                block
                color="secondary"
                size="large"
                class="mt-4 mb-4"
                @click="handleRegister"
                :loading="authStore.loading"
                :disabled="!valid"
              >
                Create Account
              </v-btn>
            </v-form>
            
            <v-alert v-if="authStore.error" type="error" variant="tonal" class="mb-4">
              {{ authStore.error }}
            </v-alert>
          </v-card-text>
          
          <v-divider class="mx-4"></v-divider>
          
          <v-card-actions class="justify-center py-4">
            <span class="text-body-2 text-medium-emphasis">Already have an account?</span>
            <v-btn to="/login" color="secondary" variant="text" class="px-2">
              Sign In
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
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)

const showSnackbar = inject<(message: string, color?: string) => void>('showSnackbar')

const rules = {
  required: (v: string) => !!v || 'Required',
  email: (v: string) => /.+@.+\..+/.test(v) || 'E-mail must be valid',
  minLength: (v: string) => v.length >= 6 || 'Min 6 characters',
  match: (v: string) => v === password.value || 'Passwords do not match',
}

async function handleRegister() {
  if (!valid.value) return
  
  const success = await authStore.register({
    username: username.value,
    email: email.value,
    password: password.value,
  })
  
  if (success) {
    showSnackbar?.('Registration successful!', 'success')
    router.push('/')
  }
}
</script>