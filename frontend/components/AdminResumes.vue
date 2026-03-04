<template>
  <div class="space-y-6">
    <!-- Header with Page Size -->
    <div class="flex items-center justify-between">
      <div class="text-sm text-gray-600 dark:text-gray-400">
        {{ adminStore.resumesTotal }} total resumes
      </div>
      <select
        v-model="pageSize"
        @change="changePageSize"
        class="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
      >
        <option :value="10">10 per page</option>
        <option :value="20">20 per page</option>
        <option :value="50">50 per page</option>
      </select>
    </div>

    <!-- Resumes List -->
    <div v-if="adminStore.loading" class="space-y-4">
      <div v-for="i in 5" :key="i" class="skeleton h-24"></div>
    </div>

    <div v-else-if="adminStore.resumes.length === 0" class="text-center py-12">
      <p class="text-gray-600 dark:text-gray-400">No resumes found</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="resume in adminStore.resumes"
        :key="resume.id"
        class="glass-card p-6"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {{ resume.job_title }}
            </h3>
            <p class="text-gray-600 dark:text-gray-400 mb-3">
              {{ resume.job_company }}
            </p>

            <div class="grid grid-cols-3 gap-4 text-sm mb-3">
              <div>
                <span class="text-gray-600 dark:text-gray-500">User:</span>
                <span class="ml-2 text-gray-900 dark:text-white">
                  {{ resume.user_email }}
                </span>
              </div>
              <div>
                <span class="text-gray-600 dark:text-gray-500">ATS Score:</span>
                <span class="ml-2 font-semibold"
                  :class="resume.ats_score ? 'text-emerald-600 dark:text-emerald-400' : 'text-gray-600 dark:text-gray-400'">
                  {{ resume.ats_score ? Math.round(resume.ats_score) + '%' : 'N/A' }}
                </span>
              </div>
              <div>
                <span class="text-gray-600 dark:text-gray-500">Generated:</span>
                <span class="ml-2 text-gray-900 dark:text-white">
                  {{ formatDate(resume.created_at) }}
                </span>
              </div>
            </div>
          </div>

          <div class="flex items-center space-x-2 ml-4">
            <a
              v-if="resume.pdf_url"
              :href="resume.pdf_url"
              target="_blank"
              class="p-2 text-emerald-400 hover:text-emerald-300 transition-colors"
              title="View PDF"
            >
              <FileText :size="18" />
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="adminStore.resumesTotal > adminStore.resumesLimit" class="flex items-center justify-between glass-card p-4">
      <div class="text-sm text-gray-600 dark:text-gray-400">
        Showing {{ adminStore.resumesSkip + 1 }} - {{ Math.min(adminStore.resumesSkip + adminStore.resumesLimit,
          adminStore.resumesTotal) }} of {{ adminStore.resumesTotal }}
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
          <button v-for="page in visiblePages" :key="page" @click="page !== '...' ? goToPage(page) : null"
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
import { FileText, ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { useAdminStore } from '~/stores/admin'

const adminStore = useAdminStore()
const pageSize = ref(10)

const currentPage = computed(() => Math.floor(adminStore.resumesSkip / adminStore.resumesLimit) + 1)
const totalPages = computed(() => Math.ceil(adminStore.resumesTotal / adminStore.resumesLimit))

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

const goToPage = async (page: number | string) => {
  if (typeof page !== 'number' || page < 1 || page > totalPages.value) return
  const skip = (page - 1) * adminStore.resumesLimit
  await adminStore.fetchResumes({ skip })
}

const changePageSize = async () => {
  await adminStore.fetchResumes({
    skip: 0,
    limit: pageSize.value
  })
}

onMounted(async () => {
  pageSize.value = 10
  await adminStore.fetchResumes({ skip: 0, limit: pageSize.value })
})
</script>
