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
              <span v-if="job.location" class="badge bg-blue-600/20 text-blue-400 text-xs">
                {{ job.location }}
              </span>
              <span v-if="job.remote" class="badge bg-emerald-600/20 text-emerald-400 text-xs">
                Remote
              </span>
              <span class="badge bg-purple-600/20 text-purple-400 text-xs">
                {{ job.source }}
              </span>
              <span v-if="job.ats_platform" class="badge bg-amber-600/20 text-amber-400 text-xs">
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
              class="p-2 text-emerald-400 hover:text-emerald-300 transition-colors"
              title="View Job"
            >
              <ExternalLink :size="18" />
            </a>
            <button
              @click="deleteJob(job)"
              class="p-2 text-red-400 hover:text-red-300 transition-colors"
              title="Delete"
            >
              <Trash2 :size="18" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ExternalLink, Trash2 } from 'lucide-vue-next'
import { useAdminStore } from '~/stores/admin'

const adminStore = useAdminStore()
const searchQuery = ref('')

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
    await adminStore.fetchJobs({ search: searchQuery.value || undefined })
  }, 300)
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

onMounted(async () => {
  await adminStore.fetchJobs({ limit: 50 })
})
</script>
