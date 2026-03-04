export default defineNuxtRouteMiddleware((to, from) => {
  const authStore = useAuthStore()

  // Redirect admins to admin dashboard
  if (authStore.user?.role === 'admin') {
    return navigateTo('/admin')
  }
})
