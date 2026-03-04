export default defineNuxtPlugin(() => {
  if (process.client) {
    const authStore = useAuthStore()
    authStore.init()
  }
})
