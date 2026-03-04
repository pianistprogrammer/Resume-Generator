<template>
  <div>
    <!-- This will redirect to login or dashboard -->
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

definePageMeta({
  layout: false
})

const authStore = useAuthStore()

onMounted(() => {
  authStore.init()

  if (authStore.isAuthenticated) {
    if (authStore.user?.role === 'admin') {
      navigateTo('/admin')
    } else if (authStore.needsOnboarding) {
      navigateTo('/onboarding')
    } else {
      navigateTo('/dashboard')
    }
  } else {
    navigateTo('/login')
  }
})
</script>
