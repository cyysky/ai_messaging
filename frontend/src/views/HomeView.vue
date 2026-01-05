<template>
  <v-container class="py-8">
    <!-- Welcome Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="d-flex align-center">
          <v-avatar color="primary" size="56" class="mr-4">
            <span class="text-h5">{{ userInitials }}</span>
          </v-avatar>
          <div>
            <h1 class="text-h4 font-weight-bold">Welcome back, {{ authStore.user?.full_name || authStore.user?.username || 'User' }}!</h1>
            <p class="text-body-1 text-medium-emphasis">Here's what's happening with your account today.</p>
          </div>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="tonal" @click="showProfileDialog = true" rounded="lg">
            <v-icon left>mdi-account-edit</v-icon>
            Edit Profile
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Quick Stats -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card color="primary" variant="tonal" class="pa-4" rounded="lg">
          <div class="d-flex align-center">
            <v-avatar color="primary" size="48" class="mr-3">
              <v-icon color="white">mdi-message-text</v-icon>
            </v-avatar>
            <div>
              <div class="text-h4 font-weight-bold">{{ stats.messages }}</div>
              <div class="text-caption text-medium-emphasis">Messages</div>
            </div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card color="success" variant="tonal" class="pa-4" rounded="lg">
          <div class="d-flex align-center">
            <v-avatar color="success" size="48" class="mr-3">
              <v-icon color="white">mdi-clipboard-check</v-icon>
            </v-avatar>
            <div>
              <div class="text-h4 font-weight-bold">{{ stats.reports }}</div>
              <div class="text-caption text-medium-emphasis">Reports</div>
            </div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card color="warning" variant="tonal" class="pa-4" rounded="lg">
          <div class="d-flex align-center">
            <v-avatar color="warning" size="48" class="mr-3">
              <v-icon color="white">mdi-clock-outline</v-icon>
            </v-avatar>
            <div>
              <div class="text-h4 font-weight-bold">{{ stats.pending }}</div>
              <div class="text-caption text-medium-emphasis">Pending</div>
            </div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card color="info" variant="tonal" class="pa-4" rounded="lg">
          <div class="d-flex align-center">
            <v-avatar color="info" size="48" class="mr-3">
              <v-icon color="white">mdi-account-group</v-icon>
            </v-avatar>
            <div>
              <div class="text-h4 font-weight-bold">{{ stats.active }}</div>
              <div class="text-caption text-medium-emphasis">Active</div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Quick Actions -->
    <v-row>
      <v-col cols="12" md="8">
        <v-card rounded="lg">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-lightning-bolt</v-icon>
            Quick Actions
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" sm="6">
                <v-card color="primary" variant="tonal" to="/conversations" hover class="pa-4">
                  <div class="d-flex align-center">
                    <v-icon size="32" class="mr-3">mdi-message-text</v-icon>
                    <div>
                      <div class="text-subtitle-1 font-weight-medium">Send Message</div>
                      <div class="text-caption text-medium-emphasis">Start a new conversation</div>
                    </div>
                  </div>
                </v-card>
              </v-col>
              <v-col cols="12" sm="6">
                <v-card color="secondary" variant="tonal" to="/reports" hover class="pa-4">
                  <div class="d-flex align-center">
                    <v-icon size="32" class="mr-3">mdi-plus-circle</v-icon>
                    <div>
                      <div class="text-subtitle-1 font-weight-medium">Create Report</div>
                      <div class="text-caption text-medium-emphasis">Submit a new report</div>
                    </div>
                  </div>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="4">
        <v-card rounded="lg">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-information</v-icon>
            Account Info
          </v-card-title>
          <v-card-text>
            <v-list density="compact">
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon color="primary">mdi-account</v-icon>
                </template>
                <v-list-item-title>{{ authStore.user?.full_name || authStore.user?.username || 'User' }}</v-list-item-title>
                <v-list-item-subtitle>Name</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon color="secondary">mdi-email</v-icon>
                </template>
                <v-list-item-title>{{ authStore.user?.email || 'N/A' }}</v-list-item-title>
                <v-list-item-subtitle>Email</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon color="accent">mdi-shield-account</v-icon>
                </template>
                <v-list-item-title>{{ authStore.isSuperuser ? 'Administrator' : 'User' }}</v-list-item-title>
                <v-list-item-subtitle>Role</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon color="success">mdi-phone</v-icon>
                </template>
                <v-list-item-title>{{ authStore.user?.phone_number || 'Not set' }}</v-list-item-title>
                <v-list-item-subtitle>Phone</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Profile Edit Dialog -->
    <v-dialog v-model="showProfileDialog" max-width="500" rounded="xl">
      <v-card>
        <v-card-title class="pa-4">
          <v-icon color="primary" class="mr-2">mdi-account-edit</v-icon>
          Edit Profile
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pa-4">
          <v-form ref="profileForm" v-model="formValid">
            <v-text-field
              v-model="profileData.username"
              label="Username"
              prepend-inner-icon="mdi-account-outline"
              disabled
              hint="Username cannot be changed"
              persistent-hint
            ></v-text-field>
            <v-text-field
              v-model="profileData.email"
              label="Email"
              type="email"
              prepend-inner-icon="mdi-email-outline"
              disabled
              hint="Email cannot be changed"
              persistent-hint
              class="mt-4"
            ></v-text-field>
            <v-text-field
              v-model="profileData.full_name"
              label="Full Name"
              prepend-inner-icon="mdi-account-details-outline"
            ></v-text-field>
            <v-text-field
              v-model="profileData.phone_number"
              label="Phone Number"
              prepend-inner-icon="mdi-phone-outline"
              :rules="[v => !v || /^[+]?[0-9\s\-().]{7,20}$/.test(v) || 'Invalid phone number format']"
              placeholder="+60127939038"
            ></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showProfileDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="updateProfile" :loading="saving" :disabled="!formValid" rounded="lg">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, inject, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authService } from '@/services/api'

const authStore = useAuthStore()
const showSnackbar = inject('showSnackbar') as (message: string, color?: string) => void

const showProfileDialog = ref(false)
const formValid = ref(false)
const saving = ref(false)

const profileData = ref({
  username: '',
  email: '',
  full_name: '',
  phone_number: ''
})

watch(showProfileDialog, (val) => {
  if (val && authStore.user) {
    profileData.value = {
      username: authStore.user.username,
      email: authStore.user.email,
      full_name: authStore.user.full_name || '',
      phone_number: authStore.user.phone_number || ''
    }
  }
})

const userInitials = computed(() => {
  const name = authStore.user?.full_name || authStore.user?.username || 'U'
  return name.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2)
})

const stats = ref({
  messages: 0,
  reports: 0,
  pending: 0,
  active: 0,
})

async function updateProfile() {
  saving.value = true
  try {
    const updatedUser = await authService.updateCurrentUser({
      full_name: profileData.value.full_name || undefined,
      phone_number: profileData.value.phone_number || undefined
    })
    authStore.updateUser(updatedUser)
    showSnackbar?.('Profile updated successfully', 'success')
    showProfileDialog.value = false
  } catch (error) {
    console.error('Failed to update profile:', error)
    showSnackbar?.('Failed to update profile', 'error')
  } finally {
    saving.value = false
  }
}

function refreshStats() {
  stats.value = {
    messages: Math.floor(Math.random() * 50) + 1,
    reports: Math.floor(Math.random() * 20) + 1,
    pending: Math.floor(Math.random() * 10) + 1,
    active: Math.floor(Math.random() * 30) + 1,
  }
}

onMounted(() => {
  refreshStats()
})
</script>