<template>
    <div class="space-y-8">
        <!-- Loading State -->
        <div v-if="loading" class="space-y-4">
            <div class="skeleton h-12"></div>
            <div class="skeleton h-64"></div>
            <div class="skeleton h-32"></div>
        </div>

        <!-- Job Not Found -->
        <div v-else-if="!job" class="text-center py-16">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                Job Not Found
            </h2>
            <p class="text-gray-600 dark:text-gray-400 mb-6">
                This job could not be found.
            </p>
            <NuxtLink to="/admin/jobs" class="btn-primary">
                Back to Jobs
            </NuxtLink>
        </div>

        <!-- Job Content -->
        <div v-else>
            <!-- Header -->
            <div class="flex items-start justify-between mb-8">
                <div class="flex-1">
                    <NuxtLink to="/admin/jobs"
                        class="text-purple-400 hover:text-purple-300 text-sm mb-4 inline-flex items-center">
                        <ChevronLeft :size="16" class="mr-1" />
                        Back to Jobs
                    </NuxtLink>

                    <div class="flex items-start space-x-4 mt-4">
                        <div
                            class="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold text-2xl flex-shrink-0 shadow-lg">
                            {{ job.company[0].toUpperCase() }}
                        </div>

                        <div class="flex-1">
                            <h1 class="text-3xl font-display font-bold text-gray-900 dark:text-white mb-2">
                                {{ job.title }}
                            </h1>
                            <p class="text-xl text-gray-600 dark:text-gray-400 mb-4">
                                {{ job.company }}
                            </p>

                            <div class="flex flex-wrap items-center gap-3">
                                <span v-if="job.location" class="badge badge-location">
                                    <MapPin :size="14" class="mr-1" />
                                    {{ job.location }}
                                </span>
                                <span v-if="job.remote" class="badge badge-remote">
                                    Remote
                                </span>
                                <span v-if="job.experience_level" class="badge badge-info">
                                    {{ job.experience_level }}
                                </span>
                                <span v-if="job.salary_min || job.salary_max" class="badge badge-warning">
                                    {{ formatSalary(job.salary_min, job.salary_max) }}
                                </span>
                                <span class="badge badge-source">
                                    {{ job.source }}
                                </span>
                                <span v-if="job.ats_platform" class="badge badge-platform">
                                    {{ job.ats_platform }}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="text-right ml-6">
                    <a :href="job.apply_url" target="_blank" rel="noopener noreferrer"
                        class="btn-primary flex items-center space-x-2">
                        <ExternalLink :size="18" />
                        <span>View Application</span>
                    </a>
                </div>
            </div>

            <!-- Metadata Card -->
            <div class="glass-card p-6 mb-8">
                <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white mb-6">
                    Job Metadata
                </h2>

                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <div>
                        <div class="text-sm text-gray-600 dark:text-gray-400 mb-1">Source</div>
                        <div class="font-semibold text-gray-900 dark:text-white">{{ job.source }}</div>
                    </div>

                    <div>
                        <div class="text-sm text-gray-600 dark:text-gray-400 mb-1">ATS Platform</div>
                        <div class="font-semibold text-gray-900 dark:text-white">
                            {{ job.ats_platform || 'N/A' }}
                        </div>
                    </div>

                    <div>
                        <div class="text-sm text-gray-600 dark:text-gray-400 mb-1">Posted At</div>
                        <div class="font-semibold text-gray-900 dark:text-white">
                            {{ job.posted_at ? formatDate(job.posted_at) : 'N/A' }}
                        </div>
                    </div>

                    <div>
                        <div class="text-sm text-gray-600 dark:text-gray-400 mb-1">Ingested At</div>
                        <div class="font-semibold text-gray-900 dark:text-white">
                            {{ formatDate(job.ingested_at) }}
                        </div>
                    </div>

                    <div>
                        <div class="text-sm text-gray-600 dark:text-gray-400 mb-1">Fingerprint</div>
                        <div class="font-mono text-xs text-gray-900 dark:text-white truncate">
                            {{ job.fingerprint }}
                        </div>
                    </div>

                    <div>
                        <div class="text-sm text-gray-600 dark:text-gray-400 mb-1">Source URL</div>
                        <div class="text-sm text-gray-900 dark:text-white truncate">
                            <a :href="job.source_url" target="_blank" class="text-purple-400 hover:text-purple-300">
                                {{ job.source_url }}
                            </a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Extracted Skills -->
            <div v-if="job.extracted_skills && job.extracted_skills.length > 0" class="glass-card p-6 mb-8">
                <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white mb-6">
                    Extracted Skills
                </h2>
                <div class="flex flex-wrap gap-2">
                    <span v-for="skill in job.extracted_skills" :key="skill" class="badge badge-success">
                        {{ skill }}
                    </span>
                </div>
            </div>

            <!-- Job Description -->
            <div class="glass-card p-6 mb-8">
                <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white mb-6">
                    Job Description
                </h2>
                <div class="prose prose-gray dark:prose-invert max-w-none" v-html="job.description"></div>
            </div>

            <!-- Actions -->
            <div class="glass-card p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white mb-2">
                            Job Actions
                        </h2>
                        <p class="text-gray-600 dark:text-gray-400">
                            Manage this job posting
                        </p>
                    </div>

                    <div class="flex items-center space-x-3">
                        <NuxtLink to="/admin/jobs" class="btn-secondary">
                            Back to Jobs
                        </NuxtLink>

                        <button @click="handleDelete"
                            class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors flex items-center space-x-2">
                            <Trash2 :size="18" />
                            <span>Delete Job</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ChevronLeft, MapPin, ExternalLink, Trash2 } from 'lucide-vue-next'
import { useAdminStore } from '~/stores/admin'
import { api } from '~/utils/api'

definePageMeta({
    layout: 'admin',
    middleware: ['auth', 'admin']
})

const adminStore = useAdminStore()
const route = useRoute()
const router = useRouter()

const jobId = route.params.id as string

const job = ref<any>(null)
const loading = ref(true)

const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return 'Not specified'
    if (min && max) return `$${(min / 1000).toFixed(0)}k - $${(max / 1000).toFixed(0)}k`
    if (min) return `$${(min / 1000).toFixed(0)}k+`
    if (max) return `Up to $${(max / 1000).toFixed(0)}k`
    return 'Not specified'
}

const fetchJobDetails = async () => {
    try {
        loading.value = true
        const response = await api.get<any>(`/admin/jobs/${jobId}`)
        job.value = response
    } catch (error) {
        console.error('Failed to fetch job details:', error)
    } finally {
        loading.value = false
    }
}

const handleDelete = async () => {
    if (!job.value) return

    if (confirm(`Delete job "${job.value.title}" at ${job.value.company}?`)) {
        try {
            await adminStore.deleteJob(job.value.id)
            router.push('/admin/jobs')
        } catch (error) {
            console.error('Failed to delete job:', error)
            alert('Failed to delete job. Please try again.')
        }
    }
}

onMounted(async () => {
    await fetchJobDetails()
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
    @apply text-purple-400 hover:text-purple-300;
}

.prose :deep(strong) {
    @apply font-semibold text-gray-900 dark:text-white;
}
</style>
