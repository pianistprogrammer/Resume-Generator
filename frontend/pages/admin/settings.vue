<template>
    <div class="space-y-8">
        <!-- Header -->
        <div>
            <h1 class="text-3xl font-display font-bold text-gray-900 dark:text-white mb-2">
                System Settings
            </h1>
            <p class="text-gray-600 dark:text-gray-400">
                Configure application settings and parameters
            </p>
        </div>

        <!-- Settings Sections -->
        <div class="space-y-6">
            <!-- General Settings -->
            <div class="glass-card p-6">
                <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white mb-6">
                    General Settings
                </h2>

                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Free Credits per User
                        </label>
                        <input type="number" value="3" class="input-field max-w-xs" disabled />
                        <p class="text-xs text-gray-500 mt-1">Number of free credits given to new users</p>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Minimum Match Score
                        </label>
                        <input type="number" value="60" class="input-field max-w-xs" disabled />
                        <p class="text-xs text-gray-500 mt-1">Minimum score required to show a job match (0-100)</p>
                    </div>
                </div>
            </div>

            <!-- Job Scraping Settings -->
            <div class="glass-card p-6">
                <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white mb-6">
                    Job Scraping Settings
                </h2>

                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Feed Refresh Interval (minutes)
                        </label>
                        <input type="number" value="60" class="input-field max-w-xs" disabled />
                        <p class="text-xs text-gray-500 mt-1">How often to check RSS feeds for new jobs</p>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Max Jobs per Feed
                        </label>
                        <input type="number" value="100" class="input-field max-w-xs" disabled />
                        <p class="text-xs text-gray-500 mt-1">Maximum number of jobs to scrape from each feed</p>
                    </div>
                </div>
            </div>

            <!-- Email Settings -->
            <div class="glass-card p-6">
                <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white mb-6">
                    Email Settings
                </h2>

                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Digest Time (24-hour format)
                        </label>
                        <input type="number" value="18" min="0" max="23" class="input-field max-w-xs" disabled />
                        <p class="text-xs text-gray-500 mt-1">Hour of the day to send daily digest emails (18 = 6 PM)
                        </p>
                    </div>
                </div>
            </div>

            <!-- Info Card -->
            <div class="bg-blue-500/10 border border-blue-500/20 rounded-xl p-6">
                <div class="flex items-start space-x-3">
                    <Info :size="24" class="text-blue-400 flex-shrink-0 mt-0.5" />
                    <div>
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                            Settings Configuration
                        </h3>
                        <p class="text-gray-600 dark:text-gray-400 text-sm">
                            System settings are currently configured via environment variables in the <code
                                class="bg-gray-800 px-2 py-1 rounded text-xs">.env</code> file.
                            To modify these settings, update the corresponding environment variables and restart the
                            application.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { Info } from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'

definePageMeta({
    layout: 'admin',
    middleware: 'admin'
})

const authStore = useAuthStore()
const router = useRouter()

onMounted(() => {
    // Check if user is admin
    if (authStore.user?.role !== 'admin') {
        router.push('/login')
    }
})
</script>
