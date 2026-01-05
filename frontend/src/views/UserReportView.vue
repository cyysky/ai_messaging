<template>
  <v-container class="py-6">
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="d-flex align-center">
          <v-icon color="secondary" size="40" class="mr-3">mdi-clipboard-text</v-icon>
          <div>
            <h1 class="text-h4 font-weight-bold">My Reports</h1>
            <p class="text-body-2 text-medium-emphasis">Manage and track your submitted reports</p>
          </div>
        </div>
      </v-col>
    </v-row>

    <v-row>
      <!-- Create Report Form -->
      <v-col cols="12" md="5">
        <v-card rounded="lg">
          <v-card-title class="pa-4">
            <v-icon color="primary" class="mr-2">mdi-plus-circle</v-icon>
            Create New Report
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text class="pa-4">
            <v-form @submit.prevent="createReport">
              <v-text-field
                v-model="form.title"
                label="Title"
                required
                :error-messages="errors.title"
                prepend-inner-icon="mdi-format-title"
              ></v-text-field>
              <v-textarea
                v-model="form.content"
                label="Content"
                required
                rows="4"
                :error-messages="errors.content"
                prepend-inner-icon="mdi-text"
              ></v-textarea>
              <v-btn type="submit" color="primary" :loading="loading" block rounded="lg" class="mt-2">
                <v-icon left>mdi-send</v-icon>
                Submit Report
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Reports List -->
      <v-col cols="12" md="7">
        <!-- Filter -->
        <v-chip-group v-model="statusFilter" mandatory class="mb-4">
          <v-chip filter value="" rounded="lg">All</v-chip>
          <v-chip filter value="open" color="error" variant="tonal" rounded="lg">Open</v-chip>
          <v-chip filter value="in_progress" color="warning" variant="tonal" rounded="lg">In Progress</v-chip>
          <v-chip filter value="resolved" color="success" variant="tonal" rounded="lg">Resolved</v-chip>
        </v-chip-group>

        <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-4"></v-progress-linear>

        <v-row v-if="reports.length > 0">
          <v-col cols="12" v-for="report in reports" :key="report.id">
            <v-card rounded="lg" class="mb-3">
              <v-card-title class="d-flex align-center pa-4">
                <v-icon color="secondary" class="mr-2">mdi-file-document</v-icon>
                {{ report.title }}
                <v-spacer></v-spacer>
                <v-chip :color="getStatusColor(report.status)" size="small" rounded="lg">
                  {{ report.status.replace('_', ' ') }}
                </v-chip>
              </v-card-title>
              <v-divider></v-divider>
              <v-card-text class="pa-4">
                <p class="text-body-2 mb-3">{{ report.content }}</p>
                <v-divider class="my-3"></v-divider>
                <div class="d-flex flex-wrap align-center gap-3">
                  <div class="text-caption text-medium-emphasis">
                    <v-icon size="small" class="mr-1">mdi-clock-outline</v-icon>
                    Created: {{ formatDate(report.created_at) }}
                  </div>
                  <div v-if="report.resolved_at" class="text-caption text-medium-emphasis">
                    <v-icon size="small" color="success" class="mr-1">mdi-check-circle</v-icon>
                    Resolved: {{ formatDate(report.resolved_at) }}
                    <span v-if="report.resolver_username"> by {{ report.resolver_username }}</span>
                  </div>
                </div>
                <div v-if="report.comment" class="mt-3">
                  <v-alert type="info" variant="tonal" density="compact" rounded="lg">
                    <template v-slot:prepend>
                      <v-icon color="info">mdi-account-tie</v-icon>
                    </template>
                    <strong>Admin Response:</strong> {{ report.comment }}
                  </v-alert>
                </div>
              </v-card-text>
              <v-card-actions v-if="report.status === 'open'" class="pa-4 pt-0">
                <v-spacer></v-spacer>
                <v-btn color="warning" variant="tonal" @click="openEditDialog(report)" rounded="lg">
                  <v-icon left>mdi-pencil</v-icon>
                  Edit
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>

        <v-card v-else-if="!loading" rounded="lg" class="text-center pa-8">
          <v-icon size="64" color="grey-lighten-2" class="mb-4">mdi-clipboard-text-outline</v-icon>
          <p class="text-h6 text-grey">No reports found</p>
          <p class="text-body-2 text-grey">Create a new report to get started</p>
        </v-card>
      </v-col>
    </v-row>

    <!-- Edit Dialog -->
    <v-dialog v-model="editDialog" max-width="500" rounded="xl">
      <v-card>
        <v-card-title class="pa-4">
          <v-icon color="warning" class="mr-2">mdi-pencil</v-icon>
          Edit Report
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pa-4">
          <v-form @submit.prevent="updateReport">
            <v-text-field
              v-model="editForm.title"
              label="Title"
              required
            ></v-text-field>
            <v-textarea
              v-model="editForm.content"
              label="Content"
              required
              rows="4"
            ></v-textarea>
            <v-btn type="submit" color="primary" :loading="loading" block rounded="lg" class="mt-2">
              Save Changes
            </v-btn>
          </v-form>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="editDialog = false">Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, inject } from 'vue'
import { reportService, type ReportResponse, type ReportCreate, type ReportUpdate } from '@/services/api'

const showSnackbar = inject<(message: string, color: string) => void>('showSnackbar')

const reports = ref<ReportResponse[]>([])
const loading = ref(false)
const statusFilter = ref('')
const editDialog = ref(false)

const form = ref<ReportCreate>({
  title: '',
  content: ''
})

const editForm = ref<ReportUpdate>({
  title: '',
  content: ''
})

const editingReportId = ref<number | null>(null)
const errors = ref<{ title?: string; content?: string }>({})

async function fetchReports() {
  loading.value = true
  try {
    reports.value = await reportService.getMyReports(statusFilter.value || undefined)
  } catch (e) {
    const axiosError = e as { response?: { data?: { detail?: string } } }
    showSnackbar?.(axiosError.response?.data?.detail || 'Failed to fetch reports', 'error')
  } finally {
    loading.value = false
  }
}

async function createReport() {
  errors.value = {}
  loading.value = true
  try {
    await reportService.createReport(form.value)
    showSnackbar?.('Report created successfully', 'success')
    form.value = { title: '', content: '' }
    await fetchReports()
  } catch (e) {
    const axiosError = e as { response?: { data?: { detail?: string | Record<string, string[]> } } }
    const detail = axiosError.response?.data?.detail
    if (typeof detail === 'object' && detail !== null) {
      errors.value = detail as { title?: string; content?: string }
    } else {
      showSnackbar?.(typeof detail === 'string' ? detail : 'Failed to create report', 'error')
    }
  } finally {
    loading.value = false
  }
}

function openEditDialog(report: ReportResponse) {
  editingReportId.value = report.id
  editForm.value = { title: report.title, content: report.content }
  editDialog.value = true
}

async function updateReport() {
  if (editingReportId.value === null) return
  
  loading.value = true
  try {
    await reportService.updateReport(editingReportId.value, editForm.value)
    showSnackbar?.('Report updated successfully', 'success')
    editDialog.value = false
    await fetchReports()
  } catch (e) {
    const axiosError = e as { response?: { data?: { detail?: string } } }
    showSnackbar?.(axiosError.response?.data?.detail || 'Failed to update report', 'error')
  } finally {
    loading.value = false
  }
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'open': return 'error'
    case 'in_progress': return 'warning'
    case 'resolved': return 'success'
    default: return 'grey'
  }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString()
}

watch(statusFilter, () => {
  fetchReports()
})

onMounted(() => {
  fetchReports()
})
</script>