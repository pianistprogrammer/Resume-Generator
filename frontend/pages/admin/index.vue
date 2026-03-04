<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-display font-bold text-gray-900 dark:text-white mb-2">
          Admin Dashboard
        </h1>
        <p class="text-gray-600 dark:text-gray-400">
          Manage users, jobs, feeds, and system settings
        </p>
      </div>
    </div>

    <!-- Stats Grid -->
    <div v-if="adminStore.stats" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div class="stat-card">
        <div class="flex items-center justify-between mb-4">
          <Users :size="32" class="text-blue-400" />
          <span class="text-blue-400 text-xs font-medium">USERS</span>
        </div>
        <div class="text-3xl font-bold text-gray-900 dark:text-white mb-1">
          {{ adminStore.stats.total_users }}
        </div>
        <div class="text-sm text-gray-600 dark:text-gray-400">
          +{{ adminStore.stats.new_users_week }} this week
        </div>
      </div>

      <div class="stat-card">
        <div class="flex items-center justify-between mb-4">
          <Briefcase :size="32" class="text-emerald-400" />
          <span class="text-emerald-400 text-xs font-medium">JOBS</span>
        </div>
        <div class="text-3xl font-bold text-gray-900 dark:text-white mb-1">
          {{ adminStore.stats.total_jobs }}
        </div>
        <div class="text-sm text-gray-600 dark:text-gray-400">
          +{{ adminStore.stats.new_jobs_today }} today
        </div>
      </div>

      <div class="stat-card">
        <div class="flex items-center justify-between mb-4">
          <Target :size="32" class="text-purple-400" />
          <span class="text-purple-400 text-xs font-medium">MATCHES</span>
        </div>
        <div class="text-3xl font-bold text-gray-900 dark:text-white mb-1">
          {{ adminStore.stats.total_matches }}
        </div>
        <div class="text-sm text-gray-600 dark:text-gray-400">
          Total Matches
        </div>
      </div>

      <div class="stat-card">
        <div class="flex items-center justify-between mb-4">
          <FileText :size="32" class="text-amber-400" />
          <span class="text-amber-400 text-xs font-medium">RESUMES</span>
        </div>
        <div class="text-3xl font-bold text-gray-900 dark:text-white mb-1">
          {{ adminStore.stats.total_resumes }}
        </div>
        <div class="text-sm text-gray-600 dark:text-gray-400">
          +{{ adminStore.stats.new_resumes_week }} this week
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="glass-card p-2 flex space-x-2 overflow-x-auto">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        @click="activeTab = tab.value"
        :class="[
          'px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap flex items-center space-x-2',
          activeTab === tab.value
            ? 'bg-emerald-600 text-white'
            : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-white/10'
        ]"
      >
        <component :is="tab.icon" :size="18" />
        <span>{{ tab.label }}</span>
      </button>
    </div>

    <!-- Content Sections -->
    <div v-if="activeTab === 'users'">
      <AdminUsers />
    </div>

    <div v-if="activeTab === 'feeds'">
      <AdminFeeds />
    </div>

    <div v-if="activeTab === 'jobs'">
      <AdminJobs />
    </div>

    <div v-if="activeTab === 'resumes'">
      <AdminResumes />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Users, Briefcase, Target, FileText, Rss, Settings } from 'lucide-vue-next'
import { useAdminStore } from '~/stores/admin'
import { useAuthStore } from '~/stores/auth'

definePageMeta({
  layout: 'app',
  middleware: 'admin'
})

const adminStore = useAdminStore()
const authStore = useAuthStore()
const router = useRouter()

const activeTab = ref('users')

const tabs = [
  { label: 'Users', value: 'users', icon: Users },
  { label: 'Feed Sources', value: 'feeds', icon: Rss },
  { label: 'Jobs', value: 'jobs', icon: Briefcase },
  { label: 'Resumes', value: 'resumes', icon: FileText },
]

onMounted(async () => {
  // Check if user is admin
  if (!authStore.user?.is_admin) {
    router.push('/dashboard')
    return
  }

  // Fetch dashboard stats
  await adminStore.fetchDashboardStats()
})
</script>
