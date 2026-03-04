<template>
  <div class="space-y-6">
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
                <span class="ml-2 font-semibold text-emerald-400">
                  {{ Math.round(resume.ats_score || 0) }}%
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
  </div>
</template>

<script setup lang="ts">
import { FileText } from 'lucide-vue-next'
import { useAdminStore } from '~/stores/admin'

const adminStore = useAdminStore()

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(async () => {
  await adminStore.fetchResumes({ limit: 50 })
})
</script>
