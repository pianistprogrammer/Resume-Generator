<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-display font-bold text-gray-900 dark:text-white mb-2">
          Dashboard
        </h1>
        <p class="text-gray-600 dark:text-gray-400">
          Welcome back, {{ user?.full_name || 'there' }}!
        </p>
      </div>

      <div class="flex items-center space-x-3">
        <button @click="refreshMatches" class="btn-secondary flex items-center space-x-2">
          <RefreshCw :size="18" :class="{ 'animate-spin': refreshing }" />
          <span>Refresh</span>
        </button>
        <NuxtLink to="/matches" class="btn-primary">
          View All Matches
        </NuxtLink>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div class="stat-card">
        <div class="flex items-center justify-between mb-4">
          <Target :size="32" class="text-emerald-400" />
          <span class="text-emerald-400 text-xs font-medium">TOTAL</span>
        </div>
        <div class="text-3xl font-bold text-gray-900 dark:text-white mb-1">
          {{ stats.total_matches || 0 }}
        </div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Total Matches</div>
      </div>

      <div class="stat-card">
        <div class="flex items-center justify-between mb-4">
          <Sparkles :size="32" class="text-amber-400" />
          <span class="text-amber-400 text-xs font-medium">NEW</span>
        </div>
        <div class="text-3xl font-bold text-gray-900 dark:text-white mb-1">
          {{ stats.new_matches || 0 }}
        </div>
        <div class="text-sm text-gray-600 dark:text-gray-400">New (24h)</div>
      </div>

      <div class="stat-card">
        <div class="flex items-center justify-between mb-4">
          <CheckCircle :size="32" class="text-blue-400" />
          <span class="text-blue-400 text-xs font-medium">APPLIED</span>
        </div>
        <div class="text-3xl font-bold text-gray-900 dark:text-white mb-1">
          {{ stats.applied_count || 0 }}
        </div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Applications</div>
      </div>

      <div class="stat-card">
        <div class="flex items-center justify-between mb-4">
          <TrendingUp :size="32" class="text-purple-400" />
          <span class="text-purple-400 text-xs font-medium">AVG</span>
        </div>
        <div class="text-3xl font-bold text-gray-900 dark:text-white mb-1">
          {{ stats.average_score || 0 }}%
        </div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Avg Score</div>
      </div>
    </div>

    <!-- Recent Matches -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white">
          Recent Matches
        </h2>
        <NuxtLink to="/matches" class="text-emerald-400 hover:text-emerald-300 text-sm font-medium">
          View all →
        </NuxtLink>
      </div>

      <div v-if="loading" class="space-y-4">
        <div v-for="i in 3" :key="i" class="skeleton h-24"></div>
      </div>

      <div v-else-if="matches.length === 0" class="text-center py-12">
        <Search :size="64" class="text-gray-600 mx-auto mb-4" />
        <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">No matches yet</h3>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          We're analyzing jobs from multiple sources. New matches will appear here automatically based on your profile and preferences.
        </p>
        <button @click="refreshMatches" class="btn-primary flex items-center space-x-2 mx-auto">
          <RefreshCw :size="18" :class="{ 'animate-spin': refreshing }" />
          <span>Check for Matches</span>
        </button>
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="match in matches.slice(0, 5)"
          :key="match.id"
          class="glass-card p-4 hover:border-emerald-300 hover:shadow-md transition-all cursor-pointer"
          @click="navigateTo(`/job/${match.job.id}`)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-3 mb-2">
                <div class="w-12 h-12 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-lg">
                  {{ match.job.company[0].toUpperCase() }}
                </div>
                <div>
                  <h3 class="font-semibold text-gray-900 dark:text-white">{{ match.job.title }}</h3>
                  <p class="text-sm text-gray-600 dark:text-gray-400">{{ match.job.company }}</p>
                </div>
              </div>

              <div class="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
                <span v-if="match.job.location">📍 {{ match.job.location }}</span>
                <span v-if="match.job.remote" class="badge bg-emerald-100 dark:bg-emerald-600/20 text-emerald-700 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-500/30">
                  Remote
                </span>
              </div>
            </div>

            <div class="text-right">
              <div :class="['text-2xl font-bold mb-1', scoreColor(match.overall_score)]">
                {{ Math.round(match.overall_score) }}%
              </div>
              <div class="text-xs text-gray-600 dark:text-gray-500">
                {{ timeAgo(match.created_at) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Target, Sparkles, CheckCircle, TrendingUp, Search, RefreshCw } from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'user']
})

const authStore = useAuthStore()
const { getDashboardStats, fetchMatches, ingestUrl, scoreColor, timeAgo } = useJobs()

const user = computed(() => authStore.user)
const stats = ref({
  total_matches: 0,
  new_matches: 0,
  applied_count: 0,
  average_score: 0
})

const matches = ref([])
const loading = ref(true)
const refreshing = ref(false)

onMounted(async () => {
  try {
    // Fetch stats
    const dashboardStats = await getDashboardStats()
    stats.value = dashboardStats

    // Fetch recent matches
    const recentMatches = await fetchMatches({ limit: 5 })
    matches.value = recentMatches

  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  } finally {
    loading.value = false
  }
})

const refreshMatches = async () => {
  if (refreshing.value) return

  try {
    refreshing.value = true

    // Fetch latest stats
    const dashboardStats = await getDashboardStats()
    stats.value = dashboardStats

    // Fetch latest matches
    const recentMatches = await fetchMatches({ limit: 5 })
    matches.value = recentMatches
  } catch (error) {
    console.error('Failed to refresh matches:', error)
  } finally {
    refreshing.value = false
  }
}
</script>
