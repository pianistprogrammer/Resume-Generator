<template>
  <div class="space-y-8">
    <!-- Loading State -->
    <div v-if="loading" class="space-y-4">
      <div class="skeleton h-12"></div>
      <div class="skeleton h-64"></div>
      <div class="skeleton h-32"></div>
    </div>

    <!-- Resume Not Found -->
    <div v-else-if="!resume" class="text-center py-16">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
        Resume Not Found
      </h2>
      <p class="text-gray-600 dark:text-gray-400 mb-6">
        This resume could not be found.
      </p>
      <NuxtLink to="/matches" class="btn-primary">
        Back to Matches
      </NuxtLink>
    </div>

    <!-- Resume Content -->
    <div v-else>
      <!-- Header -->
      <div class="flex items-start justify-between mb-8">
        <div>
          <NuxtLink to="/matches" class="text-emerald-400 hover:text-emerald-300 text-sm mb-4 inline-flex items-center">
            <ChevronLeft :size="16" class="mr-1" />
            Back to Matches
          </NuxtLink>

          <h1 class="text-3xl font-display font-bold text-gray-900 dark:text-white mt-4 mb-2">
            Tailored Resume
          </h1>
          <p class="text-gray-600 dark:text-gray-400">
            Generated {{ timeAgo(resume.created_at) }}
          </p>
        </div>

        <div class="flex items-center space-x-3">
          <a
            v-if="resume.pdf_url"
            :href="resume.pdf_url"
            target="_blank"
            rel="noopener noreferrer"
            class="btn-secondary flex items-center space-x-2"
          >
            <Download :size="18" />
            <span>Download PDF</span>
          </a>

          <button
            v-else
            @click="handleGeneratePdf"
            :disabled="generatingPdf"
            class="btn-secondary flex items-center space-x-2"
          >
            <Download :size="18" :class="{ 'animate-spin': generatingPdf }" />
            <span>{{ generatingPdf ? 'Generating PDF...' : 'Generate PDF' }}</span>
          </button>

          <div class="flex items-center space-x-2 px-4 py-2 rounded-lg bg-emerald-100 dark:bg-emerald-600/20 border border-emerald-300 dark:border-emerald-500/30">
            <span class="text-sm font-medium text-emerald-700 dark:text-emerald-400">
              ATS Score:
            </span>
            <span class="text-lg font-bold text-emerald-700 dark:text-emerald-400">
              {{ Math.round(resume.content.ats_score) }}%
            </span>
          </div>
        </div>
      </div>

      <!-- Resume Preview -->
      <div class="glass-card p-8">
        <!-- Contact Information -->
        <div class="mb-8 pb-8 border-b border-gray-200 dark:border-white/10">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-1">
            {{ resume.content.full_name }}
          </h2>
          <div class="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400">
            <span v-if="resume.content.email">{{ resume.content.email }}</span>
            <span v-if="resume.content.phone">{{ resume.content.phone }}</span>
            <span v-if="resume.content.location">{{ resume.content.location }}</span>
            <a
              v-if="resume.content.linkedin_url"
              :href="resume.content.linkedin_url"
              target="_blank"
              class="text-emerald-400 hover:text-emerald-300"
            >
              LinkedIn
            </a>
            <a
              v-if="resume.content.portfolio_url"
              :href="resume.content.portfolio_url"
              target="_blank"
              class="text-emerald-400 hover:text-emerald-300"
            >
              Portfolio
            </a>
          </div>
        </div>

        <!-- Summary -->
        <div v-if="resume.content.summary" class="mb-8">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-3">
            Professional Summary
          </h3>
          <p class="text-gray-700 dark:text-gray-300 leading-relaxed">
            {{ resume.content.summary }}
          </p>
        </div>

        <!-- Skills -->
        <div v-if="resume.content.skills && resume.content.skills.length > 0" class="mb-8">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-3">
            Skills
          </h3>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="skill in resume.content.skills"
              :key="skill"
              class="badge bg-blue-100 dark:bg-blue-600/20 text-blue-700 dark:text-blue-400 border border-blue-300 dark:border-blue-500/30"
            >
              {{ skill }}
            </span>
          </div>
        </div>

        <!-- Work Experience -->
        <div v-if="resume.content.experience && resume.content.experience.length > 0" class="mb-8">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">
            Work Experience
          </h3>
          <div class="space-y-6">
            <div
              v-for="(exp, index) in resume.content.experience"
              :key="index"
              class="border-l-2 border-emerald-400 pl-4"
            >
              <h4 class="font-semibold text-gray-900 dark:text-white">
                {{ exp.title }}
              </h4>
              <p class="text-gray-600 dark:text-gray-400 text-sm mb-2">
                {{ exp.company }} • {{ exp.start_date }} - {{ exp.end_date || 'Present' }}
                <span v-if="exp.location"> • {{ exp.location }}</span>
              </p>
              <ul v-if="exp.bullets && exp.bullets.length > 0" class="list-disc list-inside space-y-1 text-gray-700 dark:text-gray-300">
                <li v-for="(bullet, bIndex) in exp.bullets" :key="bIndex">
                  {{ bullet }}
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Education -->
        <div v-if="resume.content.education && resume.content.education.length > 0" class="mb-8">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">
            Education
          </h3>
          <div class="space-y-4">
            <div v-for="(edu, index) in resume.content.education" :key="index">
              <h4 class="font-semibold text-gray-900 dark:text-white">
                {{ edu.degree }} <span v-if="edu.field">in {{ edu.field }}</span>
              </h4>
              <p class="text-gray-600 dark:text-gray-400 text-sm">
                {{ edu.institution }}
                <span v-if="edu.graduation_year"> • {{ edu.graduation_year }}</span>
                <span v-if="edu.gpa"> • GPA: {{ edu.gpa }}/5.0</span>
              </p>
            </div>
          </div>
        </div>

        <!-- Certifications -->
        <div v-if="resume.content.certifications && resume.content.certifications.length > 0" class="mb-8">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">
            Certifications
          </h3>
          <ul class="space-y-2">
            <li
              v-for="(cert, index) in resume.content.certifications"
              :key="index"
              class="text-gray-700 dark:text-gray-300"
            >
              <strong>{{ cert.name }}</strong>
              <span v-if="cert.issuer"> - {{ cert.issuer }}</span>
              <span v-if="cert.issue_date" class="text-gray-600 dark:text-gray-400"> ({{ cert.issue_date }})</span>
            </li>
          </ul>
        </div>

        <!-- Keywords Analysis -->
        <div class="pt-8 border-t border-gray-200 dark:border-white/10">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">
            Keyword Analysis
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Keywords Injected -->
            <div>
              <h4 class="font-semibold text-emerald-600 dark:text-emerald-400 mb-2 flex items-center">
                <CheckCircle :size="18" class="mr-2" />
                Keywords Injected ({{ resume.content.keywords_injected?.length || 0 }})
              </h4>
              <div v-if="resume.content.keywords_injected && resume.content.keywords_injected.length > 0" class="flex flex-wrap gap-2">
                <span
                  v-for="keyword in resume.content.keywords_injected"
                  :key="keyword"
                  class="badge bg-emerald-100 dark:bg-emerald-600/20 text-emerald-700 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-500/30 text-xs"
                >
                  {{ keyword }}
                </span>
              </div>
              <p v-else class="text-sm text-gray-500 dark:text-gray-400">No keywords injected</p>
            </div>

            <!-- Keywords Missing -->
            <div>
              <h4 class="font-semibold text-amber-600 dark:text-amber-400 mb-2 flex items-center">
                <AlertCircle :size="18" class="mr-2" />
                Keywords Missing ({{ resume.content.keywords_missing?.length || 0 }})
              </h4>
              <div v-if="resume.content.keywords_missing && resume.content.keywords_missing.length > 0" class="flex flex-wrap gap-2">
                <span
                  v-for="keyword in resume.content.keywords_missing"
                  :key="keyword"
                  class="badge bg-amber-100 dark:bg-amber-600/20 text-amber-700 dark:text-amber-400 border border-amber-300 dark:border-amber-500/30 text-xs"
                >
                  {{ keyword }}
                </span>
              </div>
              <p v-else class="text-sm text-gray-500 dark:text-gray-400">No missing keywords</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Generation Stats -->
      <div class="glass-card p-6">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">
          Generation Stats
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Generation Time</p>
            <p class="text-xl font-semibold text-gray-900 dark:text-white">
              {{ resume.generation_time_seconds?.toFixed(2) || 'N/A' }}s
            </p>
          </div>
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Created</p>
            <p class="text-xl font-semibold text-gray-900 dark:text-white">
              {{ new Date(resume.created_at).toLocaleDateString() }}
            </p>
          </div>
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Resume ID</p>
            <p class="text-sm font-mono text-gray-900 dark:text-white break-all">
              {{ resume.id }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ChevronLeft, Download, CheckCircle, AlertCircle } from 'lucide-vue-next'

definePageMeta({
  layout: 'app',
  middleware: 'auth'
})

const route = useRoute()
const { getResumeById } = useJobs()

const resumeId = route.params.id as string

const resume = ref<any>(null)
const loading = ref(true)
const generatingPdf = ref(false)

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

const fetchResume = async () => {
  try {
    loading.value = true
    resume.value = await getResumeById(resumeId)
  } catch (error) {
    console.error('Failed to fetch resume:', error)
  } finally {
    loading.value = false
  }
}

const handleGeneratePdf = async () => {
  try {
    generatingPdf.value = true

    const config = useRuntimeConfig()
    const authStore = useAuthStore()

    const response = await fetch(`${config.public.apiBase}/resumes/${resumeId}/regenerate-pdf`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (!response.ok) {
      throw new Error('Failed to generate PDF')
    }

    const result = await response.json()

    // Refresh resume data to get the new PDF URL
    await fetchResume()

    console.log('PDF generated successfully:', result.data.pdf_url)
  } catch (error) {
    console.error('Failed to generate PDF:', error)
    alert('Failed to generate PDF. Please try again.')
  } finally {
    generatingPdf.value = false
  }
}

onMounted(async () => {
  await fetchResume()
})
</script>
