<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Report Management</h1>
      </v-col>
    </v-row>

    <!-- Filter -->
    <v-row>
      <v-col cols="12">
        <v-chip-group v-model="statusFilter" mandatory>
          <v-chip filter value="">All</v-chip>
          <v-chip filter value="open">Open</v-chip>
          <v-chip filter value="in_progress">In Progress</v-chip>
          <v-chip filter value="resolved">Resolved</v-chip>
        </v-chip-group>
      </v-col>
    </v-row>

    <!-- Reports Table -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="reports"
              :loading="loading"
              :items-per-page="10"
            >
              <template v-slot:item.title="{ item }">
                <div class="font-weight-medium">{{ item.title }}</div>
                <div class="text-caption text-grey">{{ item.reporter_username }}</div>
              </template>
              
              <template v-slot:item.status="{ item }">
                <v-chip :color="getStatusColor(item.status)" size="small">
                  {{ item.status }}
                </v-chip>
              </template>
              
              <template v-slot:item.created_at="{ item }">
                {{ formatDate(item.created_at) }}
              </template>
              
              <template v-slot:item.resolved_at="{ item }">
                {{ item.resolved_at ? formatDate(item.resolved_at) : '-' }}
              </template>
              
              <template v-slot:item.actions="{ item }">
                <v-btn
                  color="primary"
                  size="small"
                  variant="text"
                  @click="openManageDialog(item)"
                >
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
        <v-alert type="info">No reports found.</v-alert>
      </v-col>
    </v-row>

    <!-- Manage Dialog -->
    <v-dialog v-model="manageDialog" max-width="600">
      <v-card v-if="selectedReport">
        <v-card-title>Manage Report</v-card-title>
        <v-card-text>
          <v-alert type="info" variant="tonal" class="mb-4">
            <div><strong>Reporter:</strong> {{ selectedReport.reporter_username }}</div>
            <div><strong>Created:</strong> {{ formatDate(selectedReport.created_at) }}</div>
          </v-alert>
          
          <v-text-field
            :model-value="selectedReport.title"
            label="Title"
            readonly
            variant="outlined"
            density="compact"
          ></v-text-field>
          
          <v-textarea
            :model-value="selectedReport.content"
            label="Content"
            readonly
            variant="outlined"
            rows="3"
          ></v-textarea>
          
          <v-divider class="my-4"></v-divider>
          
          <v-select
            v-model="manageForm.status"
            :items="statusOptions"
            label="Status"
            variant="outlined"
          ></v-select>
          
          <v-textarea
            v-model="manageForm.comment"
            label="Comment (Response to user)"
            variant="outlined"
            rows="3"
            hint="Add a comment to respond to the user"
            persistent-hint
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-btn
            color="success"
            variant="elevated"
            :loading="loading"
            @click="resolveReport"
            :disabled="selectedReport.status === 'resolved'"
          >
            Mark Resolved
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn @click="manageDialog = false">Cancel</v-btn>
          <v-btn
            color="primary"
            :loading="loading"
            @click="saveComment"
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