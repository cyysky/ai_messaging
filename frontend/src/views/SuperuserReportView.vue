<template>
  <v-container class="py-6">
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="d-flex align-center">
          <v-icon color="warning" size="40" class="mr-3">mdi-shield-crown</v-icon>
          <div>
            <h1 class="text-h4 font-weight-bold">Report Management</h1>
            <p class="text-body-2 text-medium-emphasis">Review and manage user reports</p>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Filter -->
    <v-row class="mb-4">
      <v-col cols="12">
        <v-chip-group v-model="statusFilter" mandatory>
          <v-chip filter value="" rounded="lg">All</v-chip>
          <v-chip filter value="open" color="error" variant="tonal" rounded="lg">Open</v-chip>
          <v-chip filter value="in_progress" color="warning" variant="tonal" rounded="lg">In Progress</v-chip>
          <v-chip filter value="resolved" color="success" variant="tonal" rounded="lg">Resolved</v-chip>
        </v-chip-group>
      </v-col>
    </v-row>

    <!-- Reports Table -->
    <v-row>
      <v-col cols="12">
        <v-card rounded="lg">
          <v-card-text class="pa-0">
            <v-data-table
              :headers="headers"
              :items="reports"
              :loading="loading"
              :items-per-page="10"
              class="elevation-0"
            >
              <template v-slot:item.title="{ item }">
                <div class="font-weight-medium">{{ item.title }}</div>
                <div class="text-caption text-medium-emphasis">{{ item.reporter_username }}</div>
              </template>
              
              <template v-slot:item.status="{ item }">
                <v-chip :color="getStatusColor(item.status)" size="small" rounded="lg">
                  {{ item.status.replace('_', ' ') }}
                </v-chip>
              </template>
              
              <template v-slot:item.created_at="{ item }">
                {{ formatDate(item.created_at) }}
              </template>
              
              <template v-slot:item.resolved_at="{ item }">
                <span v-if="item.resolved_at" class="text-success">
                  <v-icon size="small" class="mr-1">mdi-check-circle</v-icon>
                  {{ formatDate(item.resolved_at) }}
                </span>
                <span v-else class="text-medium-emphasis">-</span>
              </template>
              
              <template v-slot:item.actions="{ item }">
                <v-btn
                  color="primary"
                  size="small"
                  variant="tonal"
                  @click="openManageDialog(item)"
                  rounded="lg"
                >
                  <v-icon left size="small">mdi-pencil</v-icon>
                  Manage
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-if="reports.length === 0 && !loading">
      <v-col cols="12">
        <v-card rounded="lg" class="text-center pa-8">
          <v-icon size="64" color="grey-lighten-2" class="mb-4">mdi-clipboard-text-off-outline</v-icon>
          <p class="text-h6 text-grey">No reports found</p>
        </v-card>
      </v-col>
    </v-row>

    <!-- Manage Dialog -->
    <v-dialog v-model="manageDialog" max-width="600" rounded="xl">
      <v-card v-if="selectedReport">
        <v-card-title class="pa-4">
          <v-icon color="primary" class="mr-2">mdi-clipboard-check</v-icon>
          Manage Report
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pa-4">
          <v-alert type="info" variant="tonal" class="mb-4" rounded="lg">
            <div class="d-flex align-center mb-2">
              <v-icon size="small" class="mr-2">mdi-account</v-icon>
              <strong>Reporter:</strong>&nbsp;{{ selectedReport.reporter_username }}
            </div>
            <div class="d-flex align-center">
              <v-icon size="small" class="mr-2">mdi-clock-outline</v-icon>
              <strong>Created:</strong>&nbsp;{{ formatDate(selectedReport.created_at) }}
            </div>
          </v-alert>
          
          <v-text-field
            :model-value="selectedReport.title"
            label="Title"
            readonly
            density="comfortable"
            class="mb-3"
          ></v-text-field>
          
          <v-textarea
            :model-value="selectedReport.content"
            label="Content"
            readonly
            rows="3"
            class="mb-4"
          ></v-textarea>
          
          <v-divider class="my-4"></v-divider>
          
          <v-select
            v-model="manageForm.status"
            :items="statusOptions"
            label="Status"
            density="comfortable"
            class="mb-3"
          ></v-select>
          
          <v-textarea
            v-model="manageForm.comment"
            label="Comment (Response to user)"
            rows="3"
            hint="Add a comment to respond to the user"
            persistent-hint
          ></v-textarea>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-btn
            color="success"
            variant="tonal"
            :loading="loading"
            @click="resolveReport"
            :disabled="selectedReport.status === 'resolved'"
            rounded="lg"
          >
            <v-icon left>mdi-check</v-icon>
            Mark Resolved
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="manageDialog = false">Cancel</v-btn>
          <v-btn
            color="primary"
            :loading="loading"
            @click="saveComment"
            rounded="lg"
          >
            Save Comment
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, inject } from 'vue'
import { reportService, type ReportResponse, type ReportCommentRequest } from '@/services/api'

const showSnackbar = inject<(message: string, color: string) => void>('showSnackbar')

const reports = ref<ReportResponse[]>([])
const loading = ref(false)
const statusFilter = ref('')
const manageDialog = ref(false)
const selectedReport = ref<ReportResponse | null>(null)

const headers = [
  { title: 'Title', key: 'title', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Created', key: 'created_at', sortable: true },
  { title: 'Resolved', key: 'resolved_at', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false },
]

const statusOptions = [
  { title: 'Open', value: 'open' },
  { title: 'In Progress', value: 'in_progress' },
  { title: 'Resolved', value: 'resolved' },
]

const manageForm = ref<ReportCommentRequest>({
  comment: '',
  status: 'open'
})

async function fetchReports() {
  loading.value = true
  try {
    reports.value = await reportService.getAllReports(statusFilter.value || undefined)
  } catch (e) {
    const axiosError = e as { response?: { data?: { detail?: string } } }
    showSnackbar?.(axiosError.response?.data?.detail || 'Failed to fetch reports', 'error')
  } finally {
    loading.value = false
  }
}

function openManageDialog(report: ReportResponse) {
  selectedReport.value = report
  manageForm.value = {
    comment: report.comment || '',
    status: report.status
  }
  manageDialog.value = true
}

async function saveComment() {
  if (!selectedReport.value) return
  
  loading.value = true
  try {
    await reportService.addReportComment(selectedReport.value.id, manageForm.value)
    showSnackbar?.('Comment saved successfully', 'success')
    manageDialog.value = false
    await fetchReports()
  } catch (e) {
    const axiosError = e as { response?: { data?: { detail?: string } } }
    showSnackbar?.(axiosError.response?.data?.detail || 'Failed to save comment', 'error')
  } finally {
    loading.value = false
  }
}

async function resolveReport() {
  if (!selectedReport.value) return
  
  loading.value = true
  try {
    await reportService.resolveReport(selectedReport.value.id, manageForm.value.comment)
    showSnackbar?.('Report resolved successfully', 'success')
    manageDialog.value = false
    await fetchReports()
  } catch (e) {
    const axiosError = e as { response?: { data?: { detail?: string } } }
    showSnackbar?.(axiosError.response?.data?.detail || 'Failed to resolve report', 'error')
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