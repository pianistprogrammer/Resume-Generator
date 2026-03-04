<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h2 class="text-2xl font-display font-bold text-gray-900 dark:text-white">
        Feed Sources
      </h2>
      <button @click="showCreateModal = true" class="btn-primary">
        + Add Feed Source
      </button>
    </div>

    <!-- Feeds List -->
    <div v-if="adminStore.loading" class="space-y-4">
      <div v-for="i in 3" :key="i" class="skeleton h-24"></div>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="feed in adminStore.feeds"
        :key="feed.id"
        class="glass-card p-6"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-3 mb-2">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ feed.name }}
              </h3>
              <span
                :class="[
                  'badge text-xs',
                  feed.is_active
                    ? 'bg-emerald-600/20 text-emerald-400'
                    : 'bg-gray-600/20 text-gray-400'
                ]"
              >
                {{ feed.is_active ? 'Active' : 'Inactive' }}
              </span>
              <span class="badge bg-blue-600/20 text-blue-400 text-xs">
                {{ feed.feed_type.toUpperCase() }}
              </span>
            </div>

            <p class="text-sm text-gray-600 dark:text-gray-400 mb-3 font-mono break-all">
              {{ feed.url }}
            </p>

            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-gray-600 dark:text-gray-500">Total Jobs:</span>
                <span class="ml-2 font-semibold text-gray-900 dark:text-white">
                  {{ feed.total_jobs_scraped }}
                </span>
              </div>
              <div>
                <span class="text-gray-600 dark:text-gray-500">Last Scrape:</span>
                <span class="ml-2 font-semibold text-gray-900 dark:text-white">
                  {{ feed.last_scrape_job_count }} jobs
                </span>
              </div>
              <div>
                <span class="text-gray-600 dark:text-gray-500">Last Scraped:</span>
                <span class="ml-2 text-gray-900 dark:text-white">
                  {{ feed.last_scraped_at ? timeAgo(feed.last_scraped_at) : 'Never' }}
                </span>
              </div>
              <div>
                <span class="text-gray-600 dark:text-gray-500">Status:</span>
                <span
                  :class="[
                    'ml-2',
                    feed.last_scrape_success
                      ? 'text-emerald-400'
                      : 'text-red-400'
                  ]"
                >
                  {{ feed.last_scrape_success ? 'Success' : 'Failed' }}
                </span>
              </div>
            </div>

            <div v-if="!feed.last_scrape_success && feed.last_scrape_error" class="mt-3 p-3 bg-red-600/10 border border-red-600/20 rounded-lg">
              <p class="text-sm text-red-400">
                {{ feed.last_scrape_error }}
              </p>
            </div>
          </div>

          <div class="flex items-center space-x-2 ml-4">
            <button
              @click="editFeed(feed)"
              class="p-2 text-gray-600 dark:text-gray-400 hover:text-emerald-400 transition-colors"
              title="Edit"
            >
              <Pencil :size="18" />
            </button>
            <button
              @click="toggleFeedActive(feed)"
              class="p-2 transition-colors"
              :class="feed.is_active ? 'text-amber-400 hover:text-amber-300' : 'text-emerald-400 hover:text-emerald-300'"
              :title="feed.is_active ? 'Deactivate' : 'Activate'"
            >
              <Power :size="18" />
            </button>
            <button
              @click="confirmDelete(feed)"
              class="p-2 text-red-400 hover:text-red-300 transition-colors"
              title="Delete"
            >
              <Trash2 :size="18" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div
      v-if="showCreateModal || showEditModal"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
      @click.self="closeModal"
    >
      <div class="glass-card p-8 max-w-2xl w-full mx-4 animate-fade-in">
        <h2 class="text-2xl font-display font-bold text-gray-900 dark:text-white mb-6">
          {{ showEditModal ? 'Edit Feed Source' : 'Add Feed Source' }}
        </h2>

        <form @submit.prevent="saveFeed" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Feed Name
            </label>
            <input
              v-model="feedForm.name"
              type="text"
              required
              placeholder="RemoteOK, Greenhouse Stripe, etc."
              class="input-field"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Feed Type
            </label>
            <select v-model="feedForm.feed_type" required class="input-field">
              <option value="rss">RSS Feed</option>
              <option value="greenhouse">Greenhouse API</option>
              <option value="lever">Lever API</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              URL
            </label>
            <input
              v-model="feedForm.url"
              type="url"
              required
              placeholder="https://example.com/jobs.rss"
              class="input-field"
            />
            <p class="text-xs text-gray-600 dark:text-gray-500 mt-1">
              For RSS: Full RSS feed URL. For Greenhouse/Lever: Company careers page URL
            </p>
          </div>

          <div v-if="feedForm.feed_type !== 'rss'">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Company Token
            </label>
            <input
              v-model="feedForm.company_token"
              type="text"
              placeholder="company-name or token"
              class="input-field"
            />
            <p class="text-xs text-gray-600 dark:text-gray-500 mt-1">
              For Greenhouse: company token from boards.greenhouse.io/<strong>TOKEN</strong><br>
              For Lever: company name from jobs.lever.co/<strong>company-name</strong>
            </p>
          </div>

          <div class="flex space-x-3 pt-4">
            <button type="submit" class="btn-primary flex-1">
              {{ showEditModal ? 'Update Feed' : 'Create Feed' }}
            </button>
            <button type="button" @click="closeModal" class="btn-secondary">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="showDeleteModal"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
      @click.self="showDeleteModal = false"
    >
      <div class="glass-card p-8 max-w-md w-full mx-4 animate-fade-in">
        <h2 class="text-2xl font-display font-bold text-gray-900 dark:text-white mb-4">
          Delete Feed Source?
        </h2>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          Are you sure you want to delete <strong>{{ selectedFeed?.name }}</strong>?
          This action cannot be undone.
        </p>

        <div class="flex space-x-3">
          <button @click="deleteFeedConfirmed" class="btn-primary bg-red-600 hover:bg-red-700 flex-1">
            Delete
          </button>
          <button @click="showDeleteModal = false" class="btn-secondary">
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Pencil, Power, Trash2 } from 'lucide-vue-next'
import { useAdminStore } from '~/stores/admin'

const adminStore = useAdminStore()

const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const selectedFeed = ref<any>(null)

const feedForm = ref({
  name: '',
  url: '',
  feed_type: 'rss',
  company_token: ''
})

const timeAgo = (date: string) => {
  const now = new Date()
  const then = new Date(date)
  const diff = now.getTime() - then.getTime()

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (days > 0) return `${days}d ago`
  if (hours > 0) return `${hours}h ago`
  if (minutes > 0) return `${minutes}m ago`
  return 'Just now'
}

const editFeed = (feed: any) => {
  selectedFeed.value = feed
  feedForm.value = {
    name: feed.name,
    url: feed.url,
    feed_type: feed.feed_type,
    company_token: feed.company_token || ''
  }
  showEditModal.value = true
}

const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  selectedFeed.value = null
  feedForm.value = {
    name: '',
    url: '',
    feed_type: 'rss',
    company_token: ''
  }
}

const saveFeed = async () => {
  try {
    if (showEditModal.value && selectedFeed.value) {
      await adminStore.updateFeed(selectedFeed.value.id, {
        name: feedForm.value.name,
        url: feedForm.value.url,
        feed_type: feedForm.value.feed_type,
        company_token: feedForm.value.company_token || undefined
      })
    } else {
      await adminStore.createFeed({
        name: feedForm.value.name,
        url: feedForm.value.url,
        feed_type: feedForm.value.feed_type,
        company_token: feedForm.value.company_token || undefined
      })
    }
    closeModal()
  } catch (error) {
    console.error('Failed to save feed:', error)
    alert('Failed to save feed. Please try again.')
  }
}

const toggleFeedActive = async (feed: any) => {
  try {
    await adminStore.toggleFeed(feed.id)
  } catch (error) {
    console.error('Failed to toggle feed:', error)
    alert('Failed to toggle feed. Please try again.')
  }
}

const confirmDelete = (feed: any) => {
  selectedFeed.value = feed
  showDeleteModal.value = true
}

const deleteFeedConfirmed = async () => {
  try {
    if (selectedFeed.value) {
      await adminStore.deleteFeed(selectedFeed.value.id)
      showDeleteModal.value = false
      selectedFeed.value = null
    }
  } catch (error) {
    console.error('Failed to delete feed:', error)
    alert('Failed to delete feed. Please try again.')
  }
}

onMounted(async () => {
  await adminStore.fetchFeeds(true)
})
</script>
