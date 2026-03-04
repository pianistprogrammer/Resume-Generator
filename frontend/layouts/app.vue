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
        </div>

        <!-- Navigation -->
        <nav class="flex-1 p-4 space-y-2">
          <NuxtLink
            to="/dashboard"
            class="flex items-center space-x-3 px-4 py-3 rounded-xl transition-all"
            :class="isActive('/dashboard')
              ? 'bg-emerald-600 text-white hover:bg-emerald-700'
              : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-white/10'"
          >
            <LayoutDashboard :size="20" />
            <span class="font-medium">Dashboard</span>
          </NuxtLink>

          <NuxtLink
            to="/matches"
            class="flex items-center space-x-3 px-4 py-3 rounded-xl transition-all relative"
            :class="isActive('/matches')
              ? 'bg-emerald-600 text-white hover:bg-emerald-700'
              : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-white/10'"
          >
            <Target :size="20" />
            <span class="font-medium">Matches</span>
            <span v-if="newMatchesCount > 0" class="ml-auto bg-emerald-600 text-white text-xs font-bold px-2 py-1 rounded-full">
              {{ newMatchesCount }}
            </span>
          </NuxtLink>

          <NuxtLink
            to="/profile"
            class="flex items-center space-x-3 px-4 py-3 rounded-xl transition-all"
            :class="isActive('/profile')
              ? 'bg-emerald-600 text-white hover:bg-emerald-700'
              : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-white/10'"
          >
            <User :size="20" />
            <span class="font-medium">Profile</span>
          </NuxtLink>

          <NuxtLink
            to="/preferences"
            class="flex items-center space-x-3 px-4 py-3 rounded-xl transition-all"
            :class="isActive('/preferences')
              ? 'bg-emerald-600 text-white hover:bg-emerald-700'
              : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-white/10'"
          >
            <Sliders :size="20" />
            <span class="font-medium">Preferences</span>
          </NuxtLink>

          <NuxtLink
            to="/settings"
            class="flex items-center space-x-3 px-4 py-3 rounded-xl transition-all"
            :class="isActive('/settings')
              ? 'bg-emerald-600 text-white hover:bg-emerald-700'
              : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-white/10'"
          >
            <Settings :size="20" />
            <span class="font-medium">Settings</span>
          </NuxtLink>
        </nav>

        <!-- User menu -->
        <div class="p-4 border-t border-gray-200 dark:border-white/10">
          <!-- Theme toggle -->
          <button
            @click="toggleTheme"
            class="w-full mb-3 bg-gray-100 dark:glass-card p-3 rounded-xl flex items-center justify-center space-x-2 hover:bg-gray-200 dark:hover:bg-white/20 transition-all"
          >
            <Sun v-if="isDark" :size="18" class="text-gray-400" />
            <Moon v-else :size="18" class="text-gray-700" />
            <span class="text-sm text-gray-700 dark:text-gray-400">
              {{ isDark ? 'Light Mode' : 'Dark Mode' }}
            </span>
          </button>

          <div class="bg-gray-100 dark:glass-card p-4 rounded-xl">
            <div class="flex items-center justify-between mb-3">
              <span class="text-sm text-gray-600 dark:text-gray-400">Credits</span>
              <span class="text-lg font-bold text-emerald-400">{{ user?.credits || 0 }}</span>
            </div>
            <div class="text-xs text-gray-600 dark:text-gray-500 mb-3">
              {{ user?.email }}
            </div>
            <button
              @click="handleLogout"
              class="w-full btn-secondary text-sm py-2"
            >
              Logout
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
import { LayoutDashboard, Target, User, Sliders, Settings, Sun, Moon } from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const { isDark, toggleTheme, initTheme } = useTheme()

const user = computed(() => authStore.user)
const newMatchesCount = ref(0)

const isActive = (path: string) => {
  return route.path === path
}

const handleLogout = () => {
  authStore.logout()
}

// Watch theme changes for debugging
watch(isDark, (newVal) => {
  console.log('Theme changed to:', newVal ? 'dark' : 'light')
  console.log('HTML classes:', document.documentElement.className)
})

// Fetch new matches count (placeholder)
onMounted(async () => {
  initTheme()
  console.log('Initial theme:', isDark.value ? 'dark' : 'light')
  authStore.init()

  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }

  if (authStore.needsOnboarding) {
    router.push('/onboarding')
    return
  }

  // Fetch latest user data (including credits)
  try {
    await authStore.fetchMe()
  } catch (error) {
    console.error('Failed to fetch user data:', error)
  }

  // TODO: Fetch actual new matches count
  // const { getDashboardStats } = useJobs()
  // const stats = await getDashboardStats()
  // newMatchesCount.value = stats.new_matches
})
</script>
