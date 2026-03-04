<template>
  <div class="min-h-screen flex">
    <!-- Left side - Marketing -->
    <div class="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-emerald-600 to-emerald-800 p-12 flex-col justify-between">
      <div>
        <h1 class="text-5xl font-display font-bold text-white mb-4">
          JobAlert AI
        </h1>
        <p class="text-emerald-100 text-xl">
          Your AI-powered job hunting assistant
        </p>
      </div>

      <div class="space-y-8">
        <div class="flex items-start space-x-4">
          <div class="flex-shrink-0 w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
            <Target :size="24" class="text-white" />
          </div>
          <div>
            <h3 class="text-white font-semibold text-lg">Smart Matching</h3>
            <p class="text-emerald-100">
              AI-powered algorithm scores jobs against your profile
            </p>
          </div>
        </div>

        <div class="flex items-start space-x-4">
          <div class="flex-shrink-0 w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
            <Sparkles :size="24" class="text-white" />
          </div>
          <div>
            <h3 class="text-white font-semibold text-lg">Tailored Resumes</h3>
            <p class="text-emerald-100">
              Claude AI generates ATS-optimized resumes in seconds
            </p>
          </div>
        </div>

        <div class="flex items-start space-x-4">
          <div class="flex-shrink-0 w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
            <Mail :size="24" class="text-white" />
          </div>
          <div>
            <h3 class="text-white font-semibold text-lg">Daily Digests</h3>
            <p class="text-emerald-100">
              Get your top job matches delivered every evening
            </p>
          </div>
        </div>
      </div>

      <p class="text-emerald-200 text-sm">
        Join thousands of job seekers landing their dream roles
      </p>
    </div>

    <!-- Right side - Form -->
    <div class="w-full lg:w-1/2 flex items-center justify-center p-8 bg-navy-950">
      <div class="w-full max-w-lg space-y-8">
        <!-- Logo for mobile -->
        <div class="lg:hidden text-center">
          <h1 class="text-3xl font-display font-bold text-white">
            JobAlert AI
          </h1>
        </div>

        <!-- Toggle between Login/Register -->
        <div class="glass-card p-2 flex space-x-2">
          <button
            @click="isLogin = true"
            :class="[
              'flex-1 py-3 rounded-lg font-medium transition-all',
              isLogin
                ? 'bg-emerald-600 text-white'
                : 'text-gray-400 hover:text-white'
            ]"
          >
            Login
          </button>
          <button
            @click="isLogin = false"
            :class="[
              'flex-1 py-3 rounded-lg font-medium transition-all',
              !isLogin
                ? 'bg-emerald-600 text-white'
                : 'text-gray-400 hover:text-white'
            ]"
          >
            Register
          </button>
        </div>

        <!-- Login Form -->
        <div v-if="isLogin" class="glass-card p-8 space-y-6">
          <div>
            <h2 class="text-2xl font-display font-bold text-white mb-2">
              Welcome back
            </h2>
            <p class="text-gray-400">Sign in to continue your job search</p>
          </div>

          <form @submit.prevent="handleLogin" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">
                Email
              </label>
              <input
                v-model="loginForm.email"
                type="email"
                required
                class="input-field"
                placeholder="your@email.com"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <input
                v-model="loginForm.password"
                type="password"
                required
                class="input-field"
                placeholder="••••••••"
              />
            </div>

            <div v-if="error" class="bg-red-500/10 border border-red-500 text-red-500 px-4 py-3 rounded-xl text-sm">
              {{ error }}
            </div>

            <button
              type="submit"
              :disabled="loading"
              class="btn-primary w-full"
            >
              {{ loading ? 'Signing in...' : 'Sign in' }}
            </button>
          </form>
        </div>

        <!-- Register Form -->
        <div v-else class="glass-card p-8 space-y-6">
          <div>
            <h2 class="text-2xl font-display font-bold text-white mb-2">
              Create account
            </h2>
            <p class="text-gray-400">Start finding your perfect job today</p>
          </div>

          <form @submit.prevent="handleRegister" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">
                Full Name
              </label>
              <input
                v-model="registerForm.full_name"
                type="text"
                required
                class="input-field"
                placeholder="John Doe"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">
                Email
              </label>
              <input
                v-model="registerForm.email"
                type="email"
                required
                class="input-field"
                placeholder="your@email.com"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">
                Location
              </label>
              <input
                v-model="registerForm.location"
                type="text"
                required
                class="input-field"
                placeholder="San Francisco, CA"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <input
                v-model="registerForm.password"
                type="password"
                required
                minlength="6"
                class="input-field"
                placeholder="••••••••"
              />
            </div>

            <div v-if="error" class="bg-red-500/10 border border-red-500 text-red-500 px-4 py-3 rounded-xl text-sm">
              {{ error }}
            </div>

            <button
              type="submit"
              :disabled="loading"
              class="btn-primary w-full"
            >
              {{ loading ? 'Creating account...' : 'Create account' }}
            </button>
          </form>

          <p class="text-sm text-gray-400 text-center">
            By signing up, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Target, Sparkles, Mail } from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'

definePageMeta({
  layout: false
})

const authStore = useAuthStore()
const router = useRouter()

const isLogin = ref(true)
const loading = ref(false)
const error = ref('')

const loginForm = reactive({
  email: '',
  password: ''
})

const registerForm = reactive({
  email: '',
  password: '',
  full_name: '',
  location: ''
})

const handleLogin = async () => {
  try {
    error.value = ''
    loading.value = true

    await authStore.login(loginForm.email, loginForm.password)

    // Redirect based on role and onboarding status
    if (authStore.user?.role === 'admin') {
      router.push('/admin')
    } else if (authStore.needsOnboarding) {
      router.push('/onboarding')
    } else {
      router.push('/dashboard')
    }
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  try {
    error.value = ''
    loading.value = true

    await authStore.register(
      registerForm.email,
      registerForm.password,
      registerForm.full_name,
      registerForm.location
    )

    // New users always need onboarding
    router.push('/onboarding')
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// Check if already logged in
onMounted(() => {
  authStore.init()

  if (authStore.isAuthenticated) {
    if (authStore.user?.role === 'admin') {
      router.push('/admin')
    } else if (authStore.needsOnboarding) {
      router.push('/onboarding')
    } else {
      router.push('/dashboard')
    }
  }
})
</script>
