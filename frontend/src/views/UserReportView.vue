<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">My Reports</h1>
      </v-col>
    </v-row>

    <!-- Create Report Form -->
    <v-row>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Create New Report</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="createReport">
              <v-text-field
                v-model="form.title"
                label="Title"
                required
                :error-messages="errors.title"
              ></v-text-field>
              <v-textarea
                v-model="form.content"
                label="Content"
                required
                rows="4"
                :error-messages="errors.content"
              ></v-textarea>
              <v-btn type="submit" color="primary" :loading="loading" block>
                Submit Report
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Filter -->
    <v-row class="mt-4">
      <v-col cols="12">
        <v-chip-group v-model="statusFilter" mandatory>
          <v-chip filter value="">All</v-chip>
          <v-chip filter value="open">Open</v-chip>
          <v-chip filter value="in_progress">In Progress</v-chip>
          <v-chip filter value="resolved">Resolved</v-chip>
        </v-chip-group>
      </v-col>
    </v-row>

    <!-- Reports List -->
    <v-row>
      <v-col cols="12" md="6" v-for="report in reports" :key="report.id">
        <v-card>
          <v-card-title class="d-flex align-center">
            {{ report.title }}
            <v-spacer></v-spacer>
            <v-chip :color="getStatusColor(report.status)" size="small">
              {{ report.status }}
            </v-chip>
          </v-card-title>
          <v-card-text>
            <p class="text-body-2">{{ report.content }}</p>
            <v-divider class="my-2"></v-divider>
            <div class="text-caption text-grey">
              Created: {{ formatDate(report.created_at) }}
            </div>
            <div v-if="report.comment" class="mt-2">
              <v-alert type="info" variant="tonal" density="compact">
                <strong>Admin Response:</strong> {{ report.comment }}
              </v-alert>
            </div>
            <div v-if="report.resolved_at" class="text-caption text-grey mt-1">
              Resolved: {{ formatDate(report.resolved_at) }}
              <span v-if="report.resolver_username"> by {{ report.resolver_username }}</span>
            </div>
          </v-card-text>
          <v-card-actions v-if="report.status === 'open'">
            <v-spacer></v-spacer>
            <v-btn color="warning" size="small" @click="openEditDialog(report)">
              Edit
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-if="reports.length === 0 && !loading">
      <v-col cols="12">
        <v-alert type="info">No reports found.</v-alert>
      </v-col>
    </v-row>

    <!-- Edit Dialog -->
    <v-dialog v-model="editDialog" max-width="500">
      <v-card>
        <v-card-title>Edit Report</v-card-title>
        <v-card-text>
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
            <v-btn type="submit" color="primary" :loading="loading" block>
              Save Changes
            </v-btn>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="editDialog = false">Cancel</v-btn>
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