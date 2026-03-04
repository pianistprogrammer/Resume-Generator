<template>
    <div class="min-h-screen bg-gray-50 dark:bg-navy-950">
        <!-- Sidebar -->
        <aside class="fixed inset-y-0 left-0 w-64 glass-card border-r border-gray-200 dark:border-white/10">
            <div class="flex flex-col h-full">
                <!-- Logo -->
                <div class="p-6 border-b border-gray-200 dark:border-white/10">
                    <h1 class="text-2xl font-display font-bold text-gray-900 dark:text-white">
                        JobAlert AI
                    </h1>
                    <p class="text-xs text-purple-600 dark:text-purple-400 font-semibold mt-1">
                        ADMIN PANEL
                    </p>
                </div>

                <!-- Navigation -->
                <nav class="flex-1 p-4 space-y-2">
                    <NuxtLink to="/admin" class="flex items-center space-x-3 px-4 py-3 rounded-xl transition-all"
                        :class="isActive('/admin')
                            ? 'bg-purple-600 text-white hover:bg-purple-700'
                            : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-white/10'">
                        <LayoutDashboard :size="20" />
                        <span class="font-medium">Dashboard</span>
                    </NuxtLink>

                    <NuxtLink to="/admin/users" class="flex items-center space-x-3 px-4 py-3 rounded-xl transition-all"
                        :class="isActive('/admin/users')
                            ? 'bg-purple-600 text-white hover:bg-purple-700'
                            : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-white/10'">
                        <Users :size="20" />
                        <span class="font-medium">Users</span>
                    </NuxtLink>

                    <NuxtLink to="/admin/feeds" class="flex items-center space-x-3 px-4 py-3 rounded-xl transition-all"
                        :class="isActive('/admin/feeds')
                            ? 'bg-purple-600 text-white hover:bg-purple-700'
                            : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-white/10'">
                        <Rss :size="20" />
                        <span class="font-medium">Feed Sources</span>
                    </NuxtLink>

                    <NuxtLink to="/admin/jobs" class="flex items-center space-x-3 px-4 py-3 rounded-xl transition-all"
                        :class="isActive('/admin/jobs')
                            ? 'bg-purple-600 text-white hover:bg-purple-700'
                            : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-white/10'">
                        <Briefcase :size="20" />
                        <span class="font-medium">Jobs</span>
                    </NuxtLink>

                    <NuxtLink to="/admin/resumes"
                        class="flex items-center space-x-3 px-4 py-3 rounded-xl transition-all" :class="isActive('/admin/resumes')
                            ? 'bg-purple-600 text-white hover:bg-purple-700'
                            : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-white/10'">
                        <FileText :size="20" />
                        <span class="font-medium">Resumes</span>
                    </NuxtLink>

                    <NuxtLink to="/admin/payments"
                        class="flex items-center space-x-3 px-4 py-3 rounded-xl transition-all" :class="isActive('/admin/payments')
                            ? 'bg-purple-600 text-white hover:bg-purple-700'
                            : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-white/10'">
                        <CreditCard :size="20" />
                        <span class="font-medium">Payments</span>
                    </NuxtLink>

                    <NuxtLink to="/admin/settings"
                        class="flex items-center space-x-3 px-4 py-3 rounded-xl transition-all" :class="isActive('/admin/settings')
                            ? 'bg-purple-600 text-white hover:bg-purple-700'
                            : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-white/10'">
                        <Settings :size="20" />
                        <span class="font-medium">Settings</span>
                    </NuxtLink>
                </nav>

                <!-- User menu -->
                <div class="p-4 border-t border-gray-200 dark:border-white/10">
                    <!-- Theme toggle -->
                    <button @click="toggleTheme"
                        class="w-full mb-3 bg-gray-100 dark:glass-card p-3 rounded-xl flex items-center justify-center space-x-2 hover:bg-gray-200 dark:hover:bg-white/20 transition-all">
                        <Sun v-if="isDark" :size="18" class="text-gray-400" />
                        <Moon v-else :size="18" class="text-gray-700" />
                        <span class="text-sm text-gray-700 dark:text-gray-400">
                            {{ isDark ? 'Light Mode' : 'Dark Mode' }}
                        </span>
                    </button>

                    <!-- User info -->
                    <div class="glass-card p-3 rounded-xl">
                        <div class="flex items-center space-x-3 mb-3">
                            <div
                                class="w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                                {{ user?.full_name?.charAt(0) || 'A' }}
                            </div>
                            <div class="flex-1 min-w-0">
                                <p class="text-sm font-medium text-gray-900 dark:text-white truncate">
                                    {{ user?.full_name || 'Admin' }}
                                </p>
                                <p class="text-xs text-gray-600 dark:text-gray-400 truncate">
                                    {{ user?.email }}
                                </p>
                            </div>
                        </div>
                        <button @click="logout"
                            class="w-full bg-red-500/10 hover:bg-red-500/20 text-red-500 px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center justify-center space-x-2">
                            <LogOut :size="16" />
                            <span>Sign out</span>
                        </button>
                    </div>
                </div>
            </div>
        </aside>

        <!-- Main content -->
        <main class="ml-64 p-8">
            <slot />
        </main>
    </div>
</template>

<script setup lang="ts">
import { LayoutDashboard, Users, Rss, Briefcase, FileText, CreditCard, Settings, Sun, Moon, LogOut } from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'
import { useTheme } from '~/composables/useTheme'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const { isDark, toggleTheme, initTheme } = useTheme()

const user = computed(() => authStore.user)

const isActive = (path: string) => {
    if (path === '/admin') {
        return route.path === '/admin'
    }
    return route.path.startsWith(path)
}

const logout = async () => {
    await authStore.logout()
    router.push('/login')
}

onMounted(() => {
    initTheme()
})
</script>
