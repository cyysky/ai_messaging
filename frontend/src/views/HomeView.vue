<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h5">
            Welcome, {{ authStore.user?.name || 'User' }}!
          </v-card-title>
          <v-card-text>
            <p class="text-body-1">
              This is your dashboard. You are now logged in to the application.
            </p>
            <v-divider class="my-4"></v-divider>
            <v-row>
              <v-col cols="12" md="4">
                <v-card color="primary" variant="tonal">
                  <v-card-text>
                    <div class="text-h4">{{ stats.users }}</div>
                    <div class="text-subtitle-2">Total Users</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="4">
                <v-card color="success" variant="tonal">
                  <v-card-text>
                    <div class="text-h4">{{ stats.active }}</div>
                    <div class="text-subtitle-2">Active Sessions</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="4">
                <v-card color="warning" variant="tonal">
                  <v-card-text>
                    <div class="text-h4">{{ stats.pending }}</div>
                    <div class="text-subtitle-2">Pending Tasks</div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary" variant="elevated" @click="refreshStats">
              <v-icon left>mdi-refresh</v-icon>
              Refresh
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const stats = ref({
  users: 0,
  active: 0,
  pending: 0,
})

function refreshStats() {
  // Simulate fetching stats
  stats.value = {
    users: Math.floor(Math.random() * 100) + 1,
    active: Math.floor(Math.random() * 50) + 1,
    pending: Math.floor(Math.random() * 20) + 1,
  }
}

onMounted(() => {
  refreshStats()
})
</script>