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
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

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