<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12">
          <v-toolbar color="secondary" dark flat>
            <v-toolbar-title>Register</v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <v-form ref="form" v-model="valid" @submit.prevent="handleRegister">
              <v-text-field
                v-model="name"
                label="Name"
                prepend-icon="mdi-account"
                :rules="[rules.required]"
                required
              ></v-text-field>
              <v-text-field
                v-model="email"
                label="Email"
                type="email"
                prepend-icon="mdi-email"
                :rules="[rules.required, rules.email]"
                required
              ></v-text-field>
              <v-text-field
                v-model="password"
                label="Password"
                :type="showPassword ? 'text' : 'password'"
                prepend-icon="mdi-lock"
                :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append="showPassword = !showPassword"
                :rules="[rules.required, rules.minLength]"
                required
              ></v-text-field>
              <v-text-field
                v-model="confirmPassword"
                label="Confirm Password"
                :type="showPassword ? 'text' : 'password'"
                prepend-icon="mdi-lock-check"
                :rules="[rules.required, rules.match]"
                required
              ></v-text-field>
            </v-form>
            <v-alert v-if="authStore.error" type="error" class="mt-4">
              {{ authStore.error }}
            </v-alert>
          </v-card-text>
          <v-card-actions>
            <v-btn to="/login" variant="text" color="secondary">
              Already have an account? Login
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn
              color="secondary"
              @click="handleRegister"
              :loading="authStore.loading"
              :disabled="!valid"
            >
              Register
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
const name = ref('')
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
    name: name.value,
    email: email.value,
    password: password.value,
  })
  
  if (success) {
    showSnackbar?.('Registration successful!', 'success')
    router.push('/')
  }
}
</script>