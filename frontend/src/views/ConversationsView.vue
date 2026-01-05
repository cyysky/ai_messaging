<template>
  <v-container class="py-6">
    <v-row>
      <v-col cols="12" md="8">
        <v-card rounded="lg">
          <v-card-title class="d-flex align-center pa-4">
            <v-icon color="primary" class="mr-2">mdi-message-text</v-icon>
            <span class="text-h6 font-weight-bold">Messages</span>
            <v-spacer></v-spacer>
            <v-btn icon variant="text" @click="loadMessages" class="mr-1">
              <v-icon>mdi-refresh</v-icon>
            </v-btn>
            <v-btn icon variant="text" color="primary" @click="showNewMessageDialog = true">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </v-card-title>
          
          <v-divider></v-divider>
          
          <v-card-text class="pa-4">
            <v-tabs v-model="activeTab" color="primary" class="mb-4">
              <v-tab value="all" rounded="lg">All Messages</v-tab>
              <v-tab value="sent" rounded="lg">Sent</v-tab>
              <v-tab value="received" rounded="lg">Received</v-tab>
              <v-tab value="unread" v-if="unreadCount > 0" rounded="lg">
                Unread
                <v-badge :content="unreadCount" color="error" inline></v-badge>
              </v-tab>
            </v-tabs>

            <v-text-field
              v-model="search"
              prepend-inner-icon="mdi-magnify"
              label="Search messages"
              variant="outlined"
              density="comfortable"
              hide-details
              class="mb-4"
              rounded="lg"
            ></v-text-field>

            <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-4"></v-progress-linear>

            <v-list v-if="loading" lines="three" class="message-list">
              <v-list-item v-for="n in 5" :key="n">
                <template v-slot:prepend>
                  <v-skeleton-loader type="avatar"></v-skeleton-loader>
                </template>
                <v-skeleton-loader type="list-item-three-line"></v-skeleton-loader>
              </v-list-item>
            </v-list>

            <v-list v-else-if="filteredMessages.length > 0" lines="three" class="message-list rounded-lg">
              <v-list-item
                v-for="message in filteredMessages"
                :key="message.id"
                :class="{ 'unread-message': !message.is_read && message.recipient_id === currentUserId }"
                class="mb-2 rounded-lg"
              >
                <template v-slot:prepend>
                  <v-avatar :color="message.sender_id === currentUserId ? 'primary' : 'secondary'" size="44">
                    <span class="text-subtitle-1">{{ getUserInitials(message) }}</span>
                  </v-avatar>
                </template>

                <v-list-item-title class="font-weight-medium">
                  {{ message.sender_id === currentUserId ? 'You' : getOtherUserName(message) }}
                  <v-chip size="x-small" class="ml-2" :color="message.is_read ? 'success' : 'warning'" variant="flat">
                    {{ message.is_read ? 'Read' : 'Unread' }}
                  </v-chip>
                </v-list-item-title>
                <v-list-item-subtitle class="text-truncate" style="max-width: 300px">
                  {{ message.content }}
                </v-list-item-subtitle>
                <v-list-item-subtitle class="text-caption mt-1 text-medium-emphasis">
                  {{ formatDate(message.created_at) }}
                </v-list-item-subtitle>

                <template v-slot:append>
                  <div class="d-flex flex-column align-end">
                    <v-btn icon variant="text" size="small" @click.stop="openReplyDialog(message)" v-if="message.sender_id !== currentUserId" class="mb-1">
                      <v-icon size="small" color="primary">mdi-reply</v-icon>
                    </v-btn>
                    <v-menu>
                      <template v-slot:activator="{ props }">
                        <v-btn icon variant="text" size="small" v-bind="props">
                          <v-icon size="small">mdi-dots-vertical</v-icon>
                        </v-btn>
                      </template>
                      <v-list density="compact" rounded="lg">
                        <v-list-item @click="openEditDialog(message)" v-if="message.sender_id === currentUserId">
                          <template v-slot:prepend>
                            <v-icon size="small">mdi-pencil</v-icon>
                          </template>
                          <v-list-item-title>Edit</v-list-item-title>
                        </v-list-item>
                        <v-list-item @click="deleteMessage(message.id)" v-if="message.sender_id === currentUserId || message.recipient_id === currentUserId">
                          <template v-slot:prepend>
                            <v-icon size="small" color="error">mdi-delete</v-icon>
                          </template>
                          <v-list-item-title class="text-error">Delete</v-list-item-title>
                        </v-list-item>
                        <v-list-item @click="markAsRead(message.id)" v-if="!message.is_read && message.recipient_id === currentUserId">
                          <template v-slot:prepend>
                            <v-icon size="small">mdi-check</v-icon>
                          </template>
                          <v-list-item-title>Mark as read</v-list-item-title>
                        </v-list-item>
                      </v-list>
                    </v-menu>
                  </div>
                </template>
              </v-list-item>
            </v-list>

            <div v-else class="text-center py-12">
              <v-icon size="80" color="grey-lighten-2" class="mb-4">mdi-message-text-outline</v-icon>
              <p class="text-h6 text-grey">No messages found</p>
              <p class="text-body-2 text-grey">Send a message to start a conversation</p>
              <v-btn color="primary" class="mt-4" @click="showNewMessageDialog = true">
                <v-icon left>mdi-plus</v-icon>
                New Message
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card rounded="lg" class="mb-4">
          <v-card-title class="pa-4">
            <v-icon color="accent" class="mr-2">mdi-lightning-bolt</v-icon>
            Quick Actions
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text class="pa-4">
            <v-btn block color="primary" class="mb-3" @click="showNewMessageDialog = true" rounded="lg">
              <v-icon left>mdi-plus</v-icon>
              New Message
            </v-btn>
            <v-btn block variant="outlined" class="mb-3" @click="markAllAsRead" :disabled="unreadCount === 0" rounded="lg">
              <v-icon left>mdi-check-all</v-icon>
              Mark All as Read
            </v-btn>
            <v-divider class="my-4"></v-divider>
            <v-alert type="info" variant="tonal" density="compact" rounded="lg">
              <div class="d-flex align-center">
                <v-icon class="mr-2">mdi-email-outline</v-icon>
                <span>Unread Messages: <strong>{{ unreadCount }}</strong></span>
              </div>
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- New Message Dialog -->
    <v-dialog v-model="showNewMessageDialog" max-width="500" rounded="xl">
      <v-card>
        <v-card-title class="pa-4">
          <v-icon color="primary" class="mr-2">mdi-message-plus</v-icon>
          New Message
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pa-4">
          <v-select
            v-model="newMessage.recipient_id"
            :items="users"
            item-title="username"
            item-value="id"
            label="Recipient"
            required
          ></v-select>
          <v-textarea
            v-model="newMessage.content"
            label="Message"
            rows="4"
            required
          ></v-textarea>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showNewMessageDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="sendMessage" :loading="sending" rounded="lg">Send</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Edit Message Dialog -->
    <v-dialog v-model="showEditDialog" max-width="500" rounded="xl">
      <v-card>
        <v-card-title class="pa-4">
          <v-icon color="secondary" class="mr-2">mdi-pencil</v-icon>
          Edit Message
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pa-4">
          <v-textarea
            v-model="editMessage.content"
            label="Message"
            rows="4"
            required
          ></v-textarea>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showEditDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="updateMessage" :loading="saving" rounded="lg">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Reply Dialog -->
    <v-dialog v-model="showReplyDialog" max-width="500" rounded="xl">
      <v-card>
        <v-card-title class="pa-4">
          <v-icon color="primary" class="mr-2">mdi-reply</v-icon>
          Reply to Message
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pa-4">
          <v-textarea
            v-model="replyMessage.content"
            label="Reply"
            rows="4"
            required
          ></v-textarea>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showReplyDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="sendReply" :loading="sending" rounded="lg">Send</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { messageService, authService, type MessageResponse, type MessageCreate, type MessageUpdate } from '@/services/api'

const loading = ref(true)
const messages = ref<MessageResponse[]>([])
const search = ref('')
const activeTab = ref('all')
const unreadCount = ref(0)
const currentUserId = ref<number | null>(null)
const users = ref<{ id: number; username: string }[]>([])

// Dialogs
const showNewMessageDialog = ref(false)
const showEditDialog = ref(false)
const showReplyDialog = ref(false)
const sending = ref(false)
const saving = ref(false)

// Form data
const newMessage = ref<MessageCreate>({ recipient_id: 0, content: '' })
const editMessage = ref<MessageUpdate>({})
const replyMessage = ref<MessageCreate>({ recipient_id: 0, content: '' })
const selectedMessage = ref<MessageResponse | null>(null)

const filteredMessages = computed(() => {
  let filtered = messages.value

  // Filter by tab
  if (activeTab.value === 'sent') {
    filtered = filtered.filter(m => m.sender_id === currentUserId.value)
  } else if (activeTab.value === 'received') {
    filtered = filtered.filter(m => m.recipient_id === currentUserId.value)
  } else if (activeTab.value === 'unread') {
    filtered = filtered.filter(m => !m.is_read && m.recipient_id === currentUserId.value)
  }

  // Filter by search
  if (search.value) {
    const query = search.value.toLowerCase()
    filtered = filtered.filter(m => m.content.toLowerCase().includes(query))
  }

  return filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
})

function getUserInitials(message: MessageResponse): string {
  if (message.sender_id === currentUserId.value) {
    return 'Y'
  }
  return 'U'
}

function getOtherUserName(message: MessageResponse): string {
  return 'User' // In a real app, you'd fetch the username
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } else if (days === 1) {
    return 'Yesterday'
  } else if (days < 7) {
    return date.toLocaleDateString([], { weekday: 'short' })
  } else {
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
  }
}

async function loadMessages() {
  loading.value = true
  try {
    const [allMessages, count] = await Promise.all([
      messageService.listMessages(0, 100, activeTab.value === 'unread'),
      messageService.getUnreadCount()
    ])
    messages.value = allMessages
    unreadCount.value = count.unread_count
  } catch (error) {
    console.error('Failed to load messages:', error)
  } finally {
    loading.value = false
  }
}

async function sendMessage() {
  if (!newMessage.value.recipient_id || !newMessage.value.content) return
  
  sending.value = true
  try {
    await messageService.createMessage(newMessage.value)
    showNewMessageDialog.value = false
    newMessage.value = { recipient_id: 0, content: '' }
    await loadMessages()
  } catch (error) {
    console.error('Failed to send message:', error)
  } finally {
    sending.value = false
  }
}

function openEditDialog(message: MessageResponse) {
  selectedMessage.value = message
  editMessage.value = { content: message.content }
  showEditDialog.value = true
}

async function updateMessage() {
  if (!selectedMessage.value || !editMessage.value.content) return
  
  saving.value = true
  try {
    await messageService.updateMessage(selectedMessage.value.id, editMessage.value)
    showEditDialog.value = false
    await loadMessages()
  } catch (error) {
    console.error('Failed to update message:', error)
  } finally {
    saving.value = false
  }
}

async function deleteMessage(messageId: number) {
  if (!confirm('Are you sure you want to delete this message?')) return
  
  try {
    await messageService.deleteMessage(messageId)
    await loadMessages()
  } catch (error) {
    console.error('Failed to delete message:', error)
  }
}

async function markAsRead(messageId: number) {
  try {
    await messageService.markAsRead(messageId)
    await loadMessages()
  } catch (error) {
    console.error('Failed to mark as read:', error)
  }
}

async function markAllAsRead() {
  try {
    await messageService.markAllAsRead()
    await loadMessages()
  } catch (error) {
    console.error('Failed to mark all as read:', error)
  }
}

function openReplyDialog(message: MessageResponse) {
  selectedMessage.value = message
  replyMessage.value = {
    recipient_id: message.sender_id,
    content: ''
  }
  showReplyDialog.value = true
}

async function sendReply() {
  if (!replyMessage.value.recipient_id || !replyMessage.value.content) return
  
  sending.value = true
  try {
    await messageService.createMessage(replyMessage.value)
    showReplyDialog.value = false
    replyMessage.value = { recipient_id: 0, content: '' }
    await loadMessages()
  } catch (error) {
    console.error('Failed to send reply:', error)
  } finally {
    sending.value = false
  }
}

onMounted(async () => {
  try {
    const user = await authService.getCurrentUser()
    currentUserId.value = user.id
    await loadMessages()
  } catch (error) {
    console.error('Failed to initialize:', error)
  }
})
</script>

<style scoped>
.message-list {
  max-height: calc(100vh - 350px);
  overflow-y: auto;
}

.unread-message {
  background-color: rgba(var(--v-theme-primary), 0.04);
}
</style>