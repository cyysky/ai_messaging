<template>
  <v-container class="py-6">
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="d-flex align-center">
          <v-icon color="accent" size="40" class="mr-3">mdi-account-group</v-icon>
          <div>
            <h1 class="text-h4 font-weight-bold">User Management</h1>
            <p class="text-body-2 text-medium-emphasis">Manage system users and permissions</p>
          </div>
        </div>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card rounded="lg">
          <v-card-title class="d-flex align-center pa-4">
            <v-icon color="primary" class="mr-2">mdi-account-multiple</v-icon>
            Users
            <v-spacer></v-spacer>
            <v-btn color="primary" @click="showCreateDialog = true" rounded="lg">
              <v-icon left>mdi-plus</v-icon>
              Add User
            </v-btn>
          </v-card-title>
          
          <v-divider></v-divider>
          
          <v-card-text class="pa-4">
            <v-text-field
              v-model="search"
              prepend-inner-icon="mdi-magnify"
              label="Search users"
              single-line
              hide-details
              class="mb-4"
              rounded="lg"
            ></v-text-field>
            
            <v-data-table
              :headers="headers"
              :items="users"
              :loading="loading"
              :search="search"
              :items-per-page="10"
              class="elevation-0"
            >
              <template v-slot:item.is_active="{ item }">
                <v-chip :color="item.is_active ? 'success' : 'error'" size="small" rounded="lg">
                  {{ item.is_active ? 'Active' : 'Disabled' }}
                </v-chip>
              </template>
              
              <template v-slot:item.is_superuser="{ item }">
                <v-chip :color="item.is_superuser ? 'warning' : 'default'" size="small" variant="tonal" rounded="lg">
                  {{ item.is_superuser ? 'Superuser' : 'User' }}
                </v-chip>
              </template>
              
              <template v-slot:item.created_at="{ item }">
                {{ new Date(item.created_at).toLocaleDateString() }}
              </template>
              
              <template v-slot:item.actions="{ item }">
                <v-btn-group density="compact" variant="text" rounded="lg">
                  <v-btn
                    v-if="item.is_active"
                    color="warning"
                    size="small"
                    @click="disableUser(item)"
                    :disabled="item.id === currentUserId"
                  >
                    <v-icon>mdi-account-off</v-icon>
                    <v-tooltip activator="parent">Disable</v-tooltip>
                  </v-btn>
                  <v-btn
                    v-else
                    color="success"
                    size="small"
                    @click="enableUser(item)"
                  >
                    <v-icon>mdi-account-check</v-icon>
                    <v-tooltip activator="parent">Enable</v-tooltip>
                  </v-btn>
                  
                  <v-btn
                    color="info"
                    size="small"
                    @click="toggleSuperuser(item)"
                    :disabled="item.id === currentUserId"
                  >
                    <v-icon>mdi-shield-account</v-icon>
                    <v-tooltip activator="parent">Toggle Superuser</v-tooltip>
                  </v-btn>
                  
                  <v-btn
                    color="error"
                    size="small"
                    @click="confirmDelete(item)"
                    :disabled="item.id === currentUserId"
                  >
                    <v-icon>mdi-delete</v-icon>
                    <v-tooltip activator="parent">Delete</v-tooltip>
                  </v-btn>
                </v-btn-group>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Create User Dialog -->
    <v-dialog v-model="showCreateDialog" max-width="500" rounded="xl">
      <v-card>
        <v-card-title class="pa-4">
          <v-icon color="primary" class="mr-2">mdi-account-plus</v-icon>
          Create New User
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pa-4">
          <v-form ref="createForm" v-model="formValid">
            <v-text-field
              v-model="newUser.username"
              label="Username"
              :rules="[v => !!v || 'Username is required']"
              required
              prepend-inner-icon="mdi-account-outline"
            ></v-text-field>
            <v-text-field
              v-model="newUser.email"
              label="Email"
              type="email"
              :rules="[v => !!v || 'Email is required', v => /.+@.+\..+/.test(v) || 'Email must be valid']"
              required
              prepend-inner-icon="mdi-email-outline"
            ></v-text-field>
            <v-text-field
              v-model="newUser.password"
              label="Password"
              type="password"
              :rules="[v => !!v || 'Password is required', v => v.length >= 6 || 'Password must be at least 6 characters']"
              required
              prepend-inner-icon="mdi-lock-outline"
            ></v-text-field>
            <v-text-field
              v-model="newUser.full_name"
              label="Full Name"
              prepend-inner-icon="mdi-account-details-outline"
            ></v-text-field>
            <v-text-field
              v-model="newUser.phone_number"
              label="Phone Number"
              prepend-inner-icon="mdi-phone-outline"
            ></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showCreateDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="createUser" :disabled="!formValid" rounded="lg">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="400" rounded="xl">
      <v-card>
        <v-card-title class="pa-4">
          <v-icon color="error" class="mr-2">mdi-alert</v-icon>
          Confirm Delete
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pa-4">
          Are you sure you want to delete user <strong>{{ userToDelete?.username }}</strong>?
          This action cannot be undone.
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showDeleteDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="deleteUser" rounded="lg">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, inject } from 'vue'
import { userService, type UserResponse } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const showSnackbar = inject('showSnackbar') as (message: string, color?: string) => void

const loading = ref(false)
const users = ref<UserResponse[]>([])
const search = ref('')
const currentUserId = ref(authStore.user?.id ?? 0)

const showCreateDialog = ref(false)
const showDeleteDialog = ref(false)
const userToDelete = ref<UserResponse | null>(null)
const formValid = ref(false)

const newUser = ref({
  username: '',
  email: '',
  password: '',
  full_name: '',
  phone_number: ''
})

const snackbar = ref({
  show: false,
  message: '',
  color: 'success'
})

const headers = [
  { title: 'Username', key: 'username' },
  { title: 'Email', key: 'email' },
  { title: 'Full Name', key: 'full_name' },
  { title: 'Status', key: 'is_active' },
  { title: 'Role', key: 'is_superuser' },
  { title: 'Created', key: 'created_at' },
  { title: 'Actions', key: 'actions', sortable: false }
]

async function loadUsers() {
  loading.value = true
  try {
    users.value = await userService.listUsers()
  } catch (error) {
    console.error('Failed to load users:', error)
    showSnackbar?.('Failed to load users', 'error')
  } finally {
    loading.value = false
  }
}

async function createUser() {
  try {
    await userService.createUser(newUser.value)
    showSnackbar?.('User created successfully', 'success')
    showCreateDialog.value = false
    newUser.value = { username: '', email: '', password: '', full_name: '', phone_number: '' }
    await loadUsers()
  } catch (error) {
    console.error('Failed to create user:', error)
    showSnackbar?.('Failed to create user', 'error')
  }
}

async function disableUser(user: UserResponse) {
  try {
    await userService.disableUser(user.id)
    showSnackbar?.('User disabled successfully', 'success')
    await loadUsers()
  } catch (error) {
    console.error('Failed to disable user:', error)
    showSnackbar?.('Failed to disable user', 'error')
  }
}

async function enableUser(user: UserResponse) {
  try {
    await userService.enableUser(user.id)
    showSnackbar?.('User enabled successfully', 'success')
    await loadUsers()
  } catch (error) {
    console.error('Failed to enable user:', error)
    showSnackbar?.('Failed to enable user', 'error')
  }
}

async function toggleSuperuser(user: UserResponse) {
  try {
    await userService.toggleSuperuser(user.id, !user.is_superuser)
    showSnackbar?.(`User ${user.is_superuser ? 'removed from' : 'added to'} superusers`, 'success')
    await loadUsers()
  } catch (error) {
    console.error('Failed to toggle superuser status:', error)
    showSnackbar?.('Failed to update superuser status', 'error')
  }
}

function confirmDelete(user: UserResponse) {
  userToDelete.value = user
  showDeleteDialog.value = true
}

async function deleteUser() {
  if (!userToDelete.value) return
  
  try {
    await userService.deleteUser(userToDelete.value.id)
    showSnackbar?.('User deleted successfully', 'success')
    showDeleteDialog.value = false
    userToDelete.value = null
    await loadUsers()
  } catch (error) {
    console.error('Failed to delete user:', error)
    showSnackbar?.('Failed to delete user', 'error')
  }
}

onMounted(() => {
  loadUsers()
})
</script>