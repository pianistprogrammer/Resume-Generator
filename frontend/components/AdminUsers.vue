<template>
  <div class="space-y-6">
    <!-- Header with Search -->
    <div class="flex items-center justify-between">
      <input
        v-model="searchQuery"
        @input="debouncedSearch"
        type="text"
        placeholder="Search users by email or name..."
        class="input-field max-w-md"
      />
    </div>

    <!-- Users List -->
    <div v-if="adminStore.loading" class="space-y-4">
      <div v-for="i in 5" :key="i" class="skeleton h-24"></div>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="user in adminStore.users"
        :key="user.id"
        class="glass-card p-6"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-3 mb-2">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ user.full_name || 'No Name' }}
              </h3>
              <span
v-if="user.role === 'admin'"
                class="badge bg-purple-600/20 text-purple-400 text-xs"
              >
                ADMIN
              </span>
              <span
                :class="[
                  'badge text-xs',
                  user.is_active
                    ? 'bg-emerald-600/20 text-emerald-400'
                    : 'bg-gray-600/20 text-gray-400'
                ]"
              >
                {{ user.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>

            <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
              {{ user.email }}
            </p>

            <div class="grid grid-cols-3 gap-4 text-sm">
              <div>
                <span class="text-gray-600 dark:text-gray-500">Credits:</span>
                <span class="ml-2 font-semibold text-emerald-400">
                  {{ user.credits }}
                </span>
              </div>
              <div>
                <span class="text-gray-600 dark:text-gray-500">Joined:</span>
                <span class="ml-2 text-gray-900 dark:text-white">
                  {{ formatDate(user.created_at) }}
                </span>
              </div>
              <div>
                <span class="text-gray-600 dark:text-gray-500">Onboarded:</span>
                <span class="ml-2 text-gray-900 dark:text-white">
                  {{ user.onboarding_completed ? 'Yes' : 'No' }}
                </span>
              </div>
            </div>
          </div>

          <div class="flex items-center space-x-2 ml-4">
            <button
              @click="updateCredits(user)"
              class="p-2 text-emerald-400 hover:text-emerald-300 transition-colors"
              title="Update Credits"
            >
              <Coins :size="18" />
            </button>
            <button
              @click="toggleAdmin(user)"
              class="p-2 text-purple-400 hover:text-purple-300 transition-colors"
              title="Toggle Admin"
            >
              <Shield :size="18" />
            </button>
            <button
              @click="toggleActive(user)"
              class="p-2 transition-colors"
              :class="user.is_active ? 'text-amber-400 hover:text-amber-300' : 'text-emerald-400 hover:text-emerald-300'"
              :title="user.is_active ? 'Deactivate' : 'Activate'"
            >
              <Power :size="18" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Update Credits Modal -->
    <div
      v-if="showCreditsModal"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
      @click.self="showCreditsModal = false"
    >
      <div class="glass-card p-8 max-w-md w-full mx-4 animate-fade-in">
        <h2 class="text-2xl font-display font-bold text-gray-900 dark:text-white mb-4">
          Update Credits
        </h2>
        <p class="text-gray-600 dark:text-gray-400 mb-4">
          Update credits for <strong>{{ selectedUser?.email }}</strong>
        </p>

        <input
          v-model.number="newCredits"
          type="number"
          min="0"
          class="input-field mb-6"
          placeholder="Enter new credit amount"
        />

        <div class="flex space-x-3">
          <button @click="saveCredits" class="btn-primary flex-1">
            Update
          </button>
          <button @click="showCreditsModal = false" class="btn-secondary">
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Coins, Shield, Power } from 'lucide-vue-next'
import { useAdminStore } from '~/stores/admin'

const adminStore = useAdminStore()

const searchQuery = ref('')
const showCreditsModal = ref(false)
const selectedUser = ref<any>(null)
const newCredits = ref(0)

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

let searchTimeout: NodeJS.Timeout
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(async () => {
    await adminStore.fetchUsers({ search: searchQuery.value || undefined })
  }, 300)
}

const updateCredits = (user: any) => {
  selectedUser.value = user
  newCredits.value = user.credits
  showCreditsModal.value = true
}

const saveCredits = async () => {
  try {
    if (selectedUser.value) {
      await adminStore.updateUserCredits(selectedUser.value.id, newCredits.value)
      showCreditsModal.value = false
    }
  } catch (error) {
    console.error('Failed to update credits:', error)
    alert('Failed to update credits. Please try again.')
  }
}

const toggleAdmin = async (user: any) => {
  if (confirm(`${user.role === 'admin' ? 'Remove' : 'Grant'} admin access for ${user.email}?`)) {
    try {
      await adminStore.toggleUserAdmin(user.id)
    } catch (error) {
      console.error('Failed to toggle admin:', error)
      alert('Failed to update admin status. Please try again.')
    }
  }
}

const toggleActive = async (user: any) => {
  if (confirm(`${user.is_active ? 'Deactivate' : 'Activate'} ${user.email}?`)) {
    try {
      await adminStore.toggleUserActive(user.id)
    } catch (error) {
      console.error('Failed to toggle active:', error)
      alert('Failed to update active status. Please try again.')
    }
  }
}

onMounted(async () => {
  await adminStore.fetchUsers()
})
</script>
