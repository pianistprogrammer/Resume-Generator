export default defineNuxtRouteMiddleware((to, from) => {
  const authStore = useAuthStore()

  // Check if user is authenticated and is admin
  if (!authStore.isAuthenticated) {
    return navigateTo('/login')
  }
  
  if (authStore.user?.role !== 'admin') {
    return navigateTo('/login')
  }
})
