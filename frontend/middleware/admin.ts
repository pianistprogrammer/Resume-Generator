export default defineNuxtRouteMiddleware((to, from) => {
  const authStore = useAuthStore()

  // Check if user is authenticated and is admin
  if (!authStore.isAuthenticated || !authStore.user?.is_admin) {
    return navigateTo('/dashboard')
  }
})
