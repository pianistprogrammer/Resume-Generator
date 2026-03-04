export default defineNuxtRouteMiddleware((to, from) => {
  const authStore = useAuthStore()

  // On client side, check localStorage before redirecting
  if (process.client) {
    // Initialize from localStorage if not already initialized
    if (!authStore.token) {
      authStore.init()
    }

    // After init, check if user is authenticated
    if (!authStore.isAuthenticated) {
      return navigateTo('/login')
    }
  } else {
    // On server side, check store state
    if (!authStore.isAuthenticated) {
      return navigateTo('/login')
    }
  }
})
