<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-display font-bold text-gray-900 dark:text-white mb-2">
          Admin Dashboard
        </h1>
        <p class="text-gray-600 dark:text-gray-400">
          Overview of system metrics and activity
        </p>
      </div>
    </div>

    <!-- Stats Grid -->
    <div v-if="adminStore.stats" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <NuxtLink to="/admin/users" class="stat-card hover:scale-105 transition-transform cursor-pointer">
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
      </NuxtLink>

      <NuxtLink to="/admin/jobs" class="stat-card hover:scale-105 transition-transform cursor-pointer">
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
      </NuxtLink>

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

      <NuxtLink to="/admin/resumes" class="stat-card hover:scale-105 transition-transform cursor-pointer">
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
      </NuxtLink>
    </div>

    <!-- Quick Links -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <NuxtLink to="/admin/feeds" class="glass-card p-6 hover:scale-105 transition-transform">
        <div class="flex items-center space-x-4">
          <div class="w-12 h-12 bg-emerald-600/20 rounded-xl flex items-center justify-center">
            <Rss :size="24" class="text-emerald-400" />
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              Feed Sources
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              {{ adminStore.stats?.active_feeds || 0 }} active feeds
            </p>
          </div>
          <ChevronRight :size="20" class="text-gray-400" />
        </div>
      </NuxtLink>

      <NuxtLink to="/admin/payments" class="glass-card p-6 hover:scale-105 transition-transform">
        <div class="flex items-center space-x-4">
          <div class="w-12 h-12 bg-blue-600/20 rounded-xl flex items-center justify-center">
            <CreditCard :size="24" class="text-blue-400" />
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              Payments
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              View transactions
            </p>
          </div>
          <ChevronRight :size="20" class="text-gray-400" />
        </div>
      </NuxtLink>

      <NuxtLink to="/admin/settings" class="glass-card p-6 hover:scale-105 transition-transform">
        <div class="flex items-center space-x-4">
          <div class="w-12 h-12 bg-purple-600/20 rounded-xl flex items-center justify-center">
            <Settings :size="24" class="text-purple-400" />
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              Settings
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              System configuration
            </p>
          </div>
          <ChevronRight :size="20" class="text-gray-400" />
        </div>
      </NuxtLink>
    </div>

    <!-- Recent Activity -->
    <div class="glass-card p-6">
      <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white mb-6">
        System Activity
      </h2>

      <div class="space-y-4">
        <div class="flex items-center space-x-4 p-4 bg-emerald-500/10 rounded-xl">
          <div class="w-10 h-10 bg-emerald-600/20 rounded-full flex items-center justify-center">
            <Briefcase :size="20" class="text-emerald-400" />
          </div>
          <div class="flex-1">
            <p class="text-sm font-medium text-gray-900 dark:text-white">
              New jobs scraped
            </p>
            <p class="text-xs text-gray-600 dark:text-gray-400">
              {{ adminStore.stats?.new_jobs_today || 0 }} jobs added today
            </p>
          </div>
        </div>

        <div class="flex items-center space-x-4 p-4 bg-blue-500/10 rounded-xl">
          <div class="w-10 h-10 bg-blue-600/20 rounded-full flex items-center justify-center">
            <Users :size="20" class="text-blue-400" />
          </div>
          <div class="flex-1">
            <p class="text-sm font-medium text-gray-900 dark:text-white">
              New user registrations
            </p>
            <p class="text-xs text-gray-600 dark:text-gray-400">
              {{ adminStore.stats?.new_users_week || 0 }} users this week
            </p>
          </div>
        </div>

        <div class="flex items-center space-x-4 p-4 bg-amber-500/10 rounded-xl">
          <div class="w-10 h-10 bg-amber-600/20 rounded-full flex items-center justify-center">
            <FileText :size="20" class="text-amber-400" />
          </div>
          <div class="flex-1">
            <p class="text-sm font-medium text-gray-900 dark:text-white">
              Resumes generated
            </p>
            <p class="text-xs text-gray-600 dark:text-gray-400">
              {{ adminStore.stats?.new_resumes_week || 0 }} resumes this week
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Users, Briefcase, Target, FileText, Rss, Settings, CreditCard, ChevronRight } from 'lucide-vue-next'
import { useAdminStore } from '~/stores/admin'
import { useAuthStore } from '~/stores/auth'

definePageMeta({
  layout: 'admin',
  middleware: 'admin'
})

const adminStore = useAdminStore()
const authStore = useAuthStore()
const router = useRouter()

onMounted(async () => {
  // Check if user is admin
  if (authStore.user?.role !== 'admin') {
    router.push('/login')
    return
  }

  // Fetch dashboard stats
  await adminStore.fetchDashboardStats()
})
</script>
