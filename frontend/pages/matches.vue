<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-display font-bold text-gray-900 dark:text-white mb-2">
          Job Matches
        </h1>
        <p class="text-gray-600 dark:text-gray-400">
          {{ stats.total }} total matches • {{ stats.new }} new
        </p>
      </div>

      <button @click="refreshMatches" class="btn-secondary flex items-center space-x-2">
        <RefreshCw :size="18" :class="{ 'animate-spin': refreshing }" />
        <span>Refresh</span>
      </button>
    </div>

    <!-- Filter Tabs -->
    <div class="glass-card p-2 flex space-x-2 overflow-x-auto">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        @click="activeTab = tab.value"
        :class="[
          'px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap',
          activeTab === tab.value
            ? 'bg-emerald-600 text-white hover:bg-emerald-700'
            : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-white/10 hover:text-gray-900 dark:hover:text-white'
        ]"
      >
        {{ tab.label }}
        <span v-if="tab.count > 0" class="ml-2 text-xs">{{ tab.count }}</span>
      </button>
    </div>

    <!-- Matches List -->
    <div v-if="loading" class="space-y-4">
      <div v-for="i in 5" :key="i" class="skeleton h-32"></div>
    </div>

    <div v-else-if="filteredMatches.length === 0" class="text-center py-16">
      <Search :size="64" class="text-gray-600 dark:text-gray-600 text-gray-400 mx-auto mb-4" />
      <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
        No matches found
      </h3>
      <p class="text-gray-600 dark:text-gray-400 mb-6">
        {{ getEmptyMessage() }}
      </p>
      <button @click="refreshMatches" class="btn-primary flex items-center space-x-2 mx-auto">
        <RefreshCw :size="18" :class="{ 'animate-spin': refreshing }" />
        <span>Check for Matches</span>
      </button>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="match in filteredMatches"
        :key="match.id"
        class="glass-card p-6 hover:border-emerald-300 hover:shadow-md transition-all cursor-pointer"
        @click="navigateTo(`/job/${match.job.id}`)"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-start space-x-4 flex-1">
            <!-- Company Logo -->
            <div class="w-16 h-16 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center text-white font-bold text-2xl flex-shrink-0 shadow-lg">
              {{ match.job.company[0].toUpperCase() }}
            </div>

            <!-- Job Info -->
            <div class="flex-1">
              <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-1">
                {{ match.job.title }}
              </h3>
              <p class="text-gray-600 dark:text-gray-400 mb-3">
                {{ match.job.company }}
              </p>

              <div class="flex flex-wrap items-center gap-3 text-sm text-gray-600 dark:text-gray-400">
                <span v-if="match.job.location" class="flex items-center">
                  <MapPin :size="16" class="mr-1" />
                  {{ match.job.location }}
                </span>
                <span v-if="match.job.remote" class="badge bg-emerald-100 dark:bg-emerald-600/20 text-emerald-700 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-500/30">
                  Remote
                </span>
                <span class="flex items-center">
                  <Clock :size="16" class="mr-1" />
                  {{ timeAgo(match.created_at) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Score -->
          <div class="text-right ml-4">
            <div :class="['text-3xl font-bold mb-1', scoreColor(match.overall_score)]">
              {{ Math.round(match.overall_score) }}%
            </div>
            <div class="text-xs text-gray-600 dark:text-gray-500">
              Match Score
            </div>
          </div>
        </div>

        <!-- Skills -->
        <div v-if="match.matched_skills && match.matched_skills.length > 0" class="flex flex-wrap gap-2 mb-4">
          <span
            v-for="skill in match.matched_skills.slice(0, 6)"
            :key="skill"
            class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-100 dark:bg-blue-600/20 text-blue-700 dark:text-blue-400 border border-blue-300 dark:border-blue-500/30"
          >
            {{ skill }}
          </span>
          <span v-if="match.matched_skills.length > 6" class="text-xs text-gray-600 dark:text-gray-500">
            +{{ match.matched_skills.length - 6 }} more
          </span>
        </div>

        <!-- Actions -->
        <div class="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-white/10">
          <div class="flex items-center space-x-2">
            <span
              :class="[
                'inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium',
                getStatusBadgeClass(match.status)
              ]"
            >
              {{ getStatusLabel(match.status) }}
            </span>
          </div>

          <button
            @click.stop="viewJob(match)"
            class="text-emerald-400 hover:text-emerald-300 text-sm font-medium flex items-center"
          >
            View Details
            <ChevronRight :size="16" class="ml-1" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Search, MapPin, Clock, ChevronRight, RefreshCw } from 'lucide-vue-next'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'user']
})

const activeTab = ref('all')
const loading = ref(true)
const refreshing = ref(false)

const tabs = ref([
  { label: 'All', value: 'all', count: 0 },
  { label: 'New', value: 'new', count: 0 },
  { label: 'Resume Ready', value: 'resume_ready', count: 0 },
  { label: 'Applied', value: 'applied', count: 0 },
  { label: 'Saved', value: 'saved', count: 0 }
])

const stats = ref({
  total: 0,
  new: 0
})

const matches = ref([])

const filteredMatches = computed(() => {
  if (activeTab.value === 'all') {
    return matches.value
  }
  return matches.value.filter((match: any) => match.status === activeTab.value)
})

const scoreColor = (score: number) => {
  if (score >= 80) return 'text-emerald-400'
  if (score >= 60) return 'text-amber-400'
  return 'text-red-400'
}

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

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    new: 'New',
    resume_ready: 'Resume Ready',
    applied: 'Applied',
    saved: 'Saved',
    rejected: 'Not Interested'
  }
  return labels[status] || status
}

const getStatusBadgeClass = (status: string) => {
  const classes: Record<string, string> = {
    new: 'bg-blue-100 dark:bg-blue-600/20 text-blue-700 dark:text-blue-400 border border-blue-300 dark:border-blue-500/30',
    resume_ready: 'bg-emerald-100 dark:bg-emerald-600/20 text-emerald-700 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-500/30',
    applied: 'bg-purple-100 dark:bg-purple-600/20 text-purple-700 dark:text-purple-400 border border-purple-300 dark:border-purple-500/30',
    saved: 'bg-amber-100 dark:bg-amber-600/20 text-amber-700 dark:text-amber-400 border border-amber-300 dark:border-amber-500/30',
    rejected: 'bg-red-100 dark:bg-red-600/20 text-red-700 dark:text-red-400 border border-red-300 dark:border-red-500/30'
  }
  return classes[status] || 'bg-gray-100 dark:bg-gray-600/20 text-gray-700 dark:text-gray-400 border border-gray-300 dark:border-gray-500/30'
}

const getEmptyMessage = () => {
  const messages: Record<string, string> = {
    all: "No job matches yet. We're analyzing jobs from multiple sources and will notify you when we find matches based on your profile and preferences.",
    new: "No new matches at the moment. Check back soon!",
    resume_ready: "No resumes ready yet. Generate resumes for your top matches!",
    applied: "You haven't applied to any jobs yet. Start applying!",
    saved: "No saved jobs. Save jobs you're interested in!"
  }
  return messages[activeTab.value] || messages.all
}

const viewJob = (match: any) => {
  navigateTo(`/job/${match.job.id}`)
}

const refreshMatches = async () => {
  if (refreshing.value) return
  await fetchMatches()
}

const fetchMatches = async () => {
  try {
    loading.value = true
    refreshing.value = true

    // Fetch from API
    const { fetchMatches: fetchMatchesAPI } = useJobs()
    matches.value = await fetchMatchesAPI()

    // Update tab counts
    tabs.value[0].count = matches.value.length
    tabs.value[1].count = matches.value.filter((m: any) => m.status === 'new').length
    tabs.value[2].count = matches.value.filter((m: any) => m.status === 'resume_ready').length
    tabs.value[3].count = matches.value.filter((m: any) => m.status === 'applied').length
    tabs.value[4].count = matches.value.filter((m: any) => m.status === 'saved').length

    stats.value.total = matches.value.length
    stats.value.new = tabs.value[1].count
  } catch (error) {
    console.error('Failed to fetch matches:', error)
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

onMounted(() => {
  fetchMatches()
})
</script>
