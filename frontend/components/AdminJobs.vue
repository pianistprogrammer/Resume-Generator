<template>
  <div class="space-y-6">
    <!-- Header with Search -->
    <div class="flex items-center space-x-4">
      <input
        v-model="searchQuery"
        @input="debouncedSearch"
        type="text"
        placeholder="Search jobs by title or company..."
        class="input-field flex-1"
      />
      <select
        v-model="pageSize"
        @change="changePageSize"
        class="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
      >
        <option :value="20">20 per page</option>
        <option :value="30">30 per page</option>
        <option :value="50">50 per page</option>
      </select>
      <div class="text-sm text-gray-600 dark:text-gray-400 whitespace-nowrap">
        {{ adminStore.jobsTotal }} total
      </div>
    </div>

    <!-- Jobs List -->
    <div v-if="adminStore.loading" class="space-y-4">
      <div v-for="i in 5" :key="i" class="skeleton h-32"></div>
    </div>

    <div v-else-if="adminStore.jobs.length === 0" class="text-center py-12">
      <p class="text-gray-600 dark:text-gray-400">No jobs found</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="job in adminStore.jobs"
        :key="job.id"
        class="glass-card p-6"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {{ job.title }}
            </h3>
            <p class="text-gray-600 dark:text-gray-400 mb-3">
              {{ job.company }}
            </p>

            <div class="flex flex-wrap gap-2 mb-3">
              <span v-if="job.location" class="badge badge-location">
                {{ job.location }}
              </span>
              <span v-if="job.remote" class="badge badge-remote">
                Remote
              </span>
              <span class="badge badge-source">
                {{ job.source }}
              </span>
              <span v-if="job.ats_platform" class="badge badge-platform">
                {{ job.ats_platform }}
              </span>
            </div>

            <p class="text-sm text-gray-600 dark:text-gray-500">
              Ingested: {{ formatDate(job.ingested_at) }}
            </p>
          </div>

          <div class="flex items-center space-x-2 ml-4">
            <a
              :href="job.apply_url"
              target="_blank"
              class="p-2 text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300 transition-colors"
              title="View Job"
            >
              <ExternalLink :size="18" />
            </a>
            <button
              @click="deleteJob(job)"
              class="p-2 text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 transition-colors"
              title="Delete"
            >
              <Trash2 :size="18" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="adminStore.jobsTotal > adminStore.jobsLimit" class="flex items-center justify-between glass-card p-4">
      <div class="text-sm text-gray-600 dark:text-gray-400">
        Showing {{ adminStore.jobsSkip + 1 }} - {{ Math.min(adminStore.jobsSkip + adminStore.jobsLimit,
          adminStore.jobsTotal) }} of {{ adminStore.jobsTotal }}
      </div>

      <div class="flex items-center space-x-2">
        <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1"
          class="px-3 py-2 rounded-lg transition-colors"
          :class="currentPage === 1
            ? 'bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-600 cursor-not-allowed'
            : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'">
          <ChevronLeft :size="18" />
        </button>

        <div class="flex items-center space-x-1">
          <button v-for="page in visiblePages" :key="page" @click="page !== '...' && goToPage(page as number)"
            class="px-3 py-2 rounded-lg transition-colors text-sm font-medium"
            :class="page === currentPage
              ? 'bg-purple-600 text-white'
              : page === '...'
                ? 'bg-transparent text-gray-600 dark:text-gray-400 cursor-default'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'">
            {{ page }}
          </button>
        </div>

        <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages"
          class="px-3 py-2 rounded-lg transition-colors"
          :class="currentPage === totalPages
            ? 'bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-600 cursor-not-allowed'
            : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'">
          <ChevronRight :size="18" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ExternalLink, Trash2, ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { useAdminStore } from '~/stores/admin'

const adminStore = useAdminStore()
const searchQuery = ref('')
const currentSearchQuery = ref('')
const pageSize = ref(50)

const currentPage = computed(() => Math.floor(adminStore.jobsSkip / adminStore.jobsLimit) + 1)
const totalPages = computed(() => Math.ceil(adminStore.jobsTotal / adminStore.jobsLimit))

const visiblePages = computed(() => {
  const pages: (number | string)[] = []
  const total = totalPages.value
  const current = currentPage.value

  if (total <= 7) {
    // Show all pages if 7 or fewer
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    // Always show first page
    pages.push(1)

    if (current > 3) {
      pages.push('...')
    }

    // Show pages around current
    const start = Math.max(2, current - 1)
    const end = Math.min(total - 1, current + 1)

    for (let i = start; i <= end; i++) {
      pages.push(i)
    }

    if (current < total - 2) {
      pages.push('...')
    }

    // Always show last page
    pages.push(total)
  }

  return pages
})

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

let searchTimeout: NodeJS.Timeout
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(async () => {
    currentSearchQuery.value = searchQuery.value
    await adminStore.fetchJobs({ skip: 0, search: searchQuery.value || undefined })
  }, 300)
}

const goToPage = async (page: number) => {
  if (page < 1 || page > totalPages.value) return
  const skip = (page - 1) * adminStore.jobsLimit
  await adminStore.fetchJobs({
    skip,
    search: currentSearchQuery.value || undefined
  })
}

const deleteJob = async (job: any) => {
  if (confirm(`Delete job "${job.title}" at ${job.company}?`)) {
    try {
      await adminStore.deleteJob(job.id)
    } catch (error) {
      console.error('Failed to delete job:', error)
      alert('Failed to delete job. Please try again.')
    }
  }
}

const changePageSize = async () => {
  await adminStore.fetchJobs({
    skip: 0,
    limit: pageSize.value,
    search: currentSearchQuery.value || undefined
  })
}

onMounted(async () => {
  pageSize.value = adminStore.jobsLimit
  await adminStore.fetchJobs({ skip: 0, limit: pageSize.value })
})
</script>
