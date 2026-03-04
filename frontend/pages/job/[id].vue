<template>
  <div class="space-y-8">
    <!-- Loading State -->
    <div v-if="loading" class="space-y-4">
      <div class="skeleton h-12"></div>
      <div class="skeleton h-64"></div>
      <div class="skeleton h-32"></div>
    </div>

    <!-- Job Not Found -->
    <div v-else-if="!match" class="text-center py-16">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
        Job Not Found
      </h2>
      <p class="text-gray-600 dark:text-gray-400 mb-6">
        This job match could not be found.
      </p>
      <NuxtLink to="/matches" class="btn-primary">
        Back to Matches
      </NuxtLink>
    </div>

    <!-- Job Content -->
    <div v-else>
      <!-- Header -->
      <div class="flex items-start justify-between mb-8">
        <div class="flex-1">
          <NuxtLink to="/matches" class="text-emerald-400 hover:text-emerald-300 text-sm mb-4 inline-flex items-center">
            <ChevronLeft :size="16" class="mr-1" />
            Back to Matches
          </NuxtLink>

          <div class="flex items-start space-x-4 mt-4">
            <div class="w-16 h-16 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center text-white font-bold text-2xl flex-shrink-0 shadow-lg">
              {{ match.job.company[0].toUpperCase() }}
            </div>

            <div class="flex-1">
              <h1 class="text-3xl font-display font-bold text-gray-900 dark:text-white mb-2">
                {{ match.job.title }}
              </h1>
              <p class="text-xl text-gray-600 dark:text-gray-400 mb-4">
                {{ match.job.company }}
              </p>

              <div class="flex flex-wrap items-center gap-3">
                <span v-if="match.job.location" class="flex items-center text-gray-600 dark:text-gray-400">
                  <MapPin :size="16" class="mr-1" />
                  {{ match.job.location }}
                </span>
                <span v-if="match.job.remote" class="badge badge-remote">
                  Remote
                </span>
                <span v-if="match.job.experience_level" class="badge badge-info">
                  {{ match.job.experience_level }}
                </span>
                <span v-if="match.job.salary_min || match.job.salary_max" class="badge badge-warning">
                  {{ formatSalary(match.job.salary_min, match.job.salary_max) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="text-right ml-6">
          <div :class="['text-4xl font-bold mb-2', scoreColor(match.overall_score)]">
            {{ Math.round(match.overall_score) }}%
          </div>
          <div class="text-sm text-gray-600 dark:text-gray-400">
            Match Score
          </div>
        </div>
      </div>

      <!-- Score Breakdown -->
      <div class="glass-card p-6 mb-8">
        <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white mb-6">
          Score Breakdown
        </h2>

        <div class="space-y-4">
          <div>
            <div class="flex justify-between text-sm mb-2">
              <span class="text-gray-600 dark:text-gray-400">Title Match</span>
              <span class="font-semibold text-gray-900 dark:text-white">
                {{ Math.round(match.score_breakdown.title_score) }}%
              </span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-white/10 rounded-full h-2">
              <div
                class="bg-emerald-400 h-2 rounded-full transition-all"
                :style="{ width: match.score_breakdown.title_score + '%' }"
              ></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-sm mb-2">
              <span class="text-gray-600 dark:text-gray-400">Skills Match</span>
              <span class="font-semibold text-gray-900 dark:text-white">
                {{ Math.round(match.score_breakdown.skills_score) }}%
              </span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-white/10 rounded-full h-2">
              <div
                class="bg-blue-400 h-2 rounded-full transition-all"
                :style="{ width: match.score_breakdown.skills_score + '%' }"
              ></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-sm mb-2">
              <span class="text-gray-600 dark:text-gray-400">Location Match</span>
              <span class="font-semibold text-gray-900 dark:text-white">
                {{ Math.round(match.score_breakdown.location_score) }}%
              </span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-white/10 rounded-full h-2">
              <div
                class="bg-purple-400 h-2 rounded-full transition-all"
                :style="{ width: match.score_breakdown.location_score + '%' }"
              ></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-sm mb-2">
              <span class="text-gray-600 dark:text-gray-400">Experience Match</span>
              <span class="font-semibold text-gray-900 dark:text-white">
                {{ Math.round(match.score_breakdown.experience_score) }}%
              </span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-white/10 rounded-full h-2">
              <div
                class="bg-amber-400 h-2 rounded-full transition-all"
                :style="{ width: match.score_breakdown.experience_score + '%' }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Matched Skills -->
        <div v-if="match.score_breakdown.matched_skills && match.score_breakdown.matched_skills.length > 0" class="mt-6">
          <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">
            Matched Skills
          </h3>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="skill in match.score_breakdown.matched_skills"
              :key="skill"
class="badge badge-success"
            >
              {{ skill }}
            </span>
          </div>
        </div>
      </div>

      <!-- Job Description -->
      <div class="glass-card p-6 mb-8">
        <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white mb-6">
          Job Description
        </h2>
        <div
          class="prose prose-gray dark:prose-invert max-w-none"
          v-html="match.job.description"
        ></div>
      </div>

      <!-- Actions -->
      <div class="glass-card p-6">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white mb-2">
              Ready to Apply?
            </h2>
            <p class="text-gray-600 dark:text-gray-400">
              Generate a tailored resume or apply directly to this position.
            </p>
          </div>

          <div class="flex items-center space-x-3">
            <button
              v-if="!hasResume"
              @click="handleGenerateResume"
              :disabled="generatingResume"
              class="btn-primary flex items-center space-x-2"
            >
              <FileText :size="18" />
              <span>{{ generatingResume ? 'Generating...' : 'Generate Resume' }}</span>
            </button>

            <NuxtLink
              v-else
              :to="`/resume/${resumeId}`"
              class="btn-secondary flex items-center space-x-2"
            >
              <FileText :size="18" />
              <span>View Resume</span>
            </NuxtLink>

            <a
              :href="match.job.apply_url"
              target="_blank"
              rel="noopener noreferrer"
              @click="markAsApplied"
              class="btn-primary flex items-center space-x-2"
            >
              <ExternalLink :size="18" />
              <span>Apply Now</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ChevronLeft, MapPin, FileText, ExternalLink } from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'user']
})

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()
const { getMatch, updateMatchStatus, generateResume, getResumeByMatch, scoreColor, formatSalary, fetchMatches } = useJobs()

const jobId = route.params.id as string

const match = ref<any>(null)
const loading = ref(true)
const generatingResume = ref(false)
const hasResume = ref(false)
const resumeId = ref<string | null>(null)

const fetchMatchByJobId = async () => {
  try {
    loading.value = true

    // Fetch all matches and find the one with this job_id
    const matches = await fetchMatches({ limit: 100 })

    const foundMatch = matches.find((m: any) => m.job.id === jobId)

    if (foundMatch) {
      match.value = foundMatch

      // Check if resume exists
      try {
        const resume = await getResumeByMatch(foundMatch.id)
        if (resume) {
          hasResume.value = true
          resumeId.value = resume.id
        }
      } catch (error) {
        // No resume yet
        hasResume.value = false
      }
    }
  } catch (error) {
    console.error('Failed to fetch match:', error)
  } finally {
    loading.value = false
  }
}

const handleGenerateResume = async () => {
  if (!match.value || generatingResume.value) return

  try {
    generatingResume.value = true
    const result = await generateResume(match.value.id)

    // Refresh user credits in auth store
    await authStore.fetchMe()

    // Refresh match to get resume info
    await fetchMatchByJobId()
  } catch (error) {
    console.error('Failed to generate resume:', error)
    alert('Failed to generate resume. Please try again.')
  } finally {
    generatingResume.value = false
  }
}

const markAsApplied = async () => {
  if (!match.value) return

  try {
    await updateMatchStatus(match.value.id, 'applied')
    // Optionally refresh match
    await fetchMatchByJobId()
  } catch (error) {
    console.error('Failed to update match status:', error)
  }
}

onMounted(async () => {
  await fetchMatchByJobId()
})
</script>

<style scoped>
.prose {
  @apply text-gray-700 dark:text-gray-300;
}

.prose :deep(h1),
.prose :deep(h2),
.prose :deep(h3),
.prose :deep(h4) {
  @apply text-gray-900 dark:text-white font-bold mt-6 mb-4;
}

.prose :deep(p) {
  @apply mb-4;
}

.prose :deep(ul),
.prose :deep(ol) {
  @apply mb-4 pl-6;
}

.prose :deep(li) {
  @apply mb-2;
}

.prose :deep(a) {
  @apply text-emerald-400 hover:text-emerald-300;
}

.prose :deep(strong) {
  @apply font-semibold text-gray-900 dark:text-white;
}
</style>
