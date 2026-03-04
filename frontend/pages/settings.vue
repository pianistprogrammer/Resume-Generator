<template>
  <div class="space-y-8">
    <!-- Header -->
    <div>
      <h1 class="text-3xl font-display font-bold text-gray-900 dark:text-white mb-2">
        Settings
      </h1>
      <p class="text-gray-600 dark:text-gray-400">
        Manage your account and notification settings
      </p>
    </div>

    <!-- Credits -->
    <div class="glass-card p-6">
      <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white mb-6">
        Credits
      </h2>

      <div class="flex items-center justify-between mb-6">
        <div>
          <p class="text-gray-600 dark:text-gray-400 text-sm mb-1">Current Balance</p>
          <p class="text-4xl font-bold text-emerald-400">{{ credits }}</p>
        </div>
        <Coins :size="48" class="text-emerald-400 opacity-50" />
      </div>

      <div class="space-y-3 mb-6">
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-600 dark:text-gray-400">Total Purchased</span>
          <span class="text-gray-900 dark:text-white font-medium">{{ totalCreditsPurchased }}</span>
        </div>
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-600 dark:text-gray-400">Resumes Generated</span>
          <span class="text-gray-900 dark:text-white font-medium">{{ totalCreditsPurchased - credits }}</span>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          v-for="pack in creditPacks"
          :key="pack.credits"
          @click="purchaseCredits(pack)"
          class="glass-card dark:glass-card bg-gray-50 p-4 hover:bg-white/20 dark:hover:bg-white/20 hover:bg-gray-100 transition-all"
        >
          <p class="text-2xl font-bold text-gray-900 dark:text-white mb-1">
            {{ pack.credits }} {{ pack.credits === 1 ? 'Credit' : 'Credits' }}
          </p>
          <p class="text-emerald-400 font-semibold mb-2">${{ pack.price }}</p>
          <p class="text-xs text-gray-600 dark:text-gray-500">
            ${{ (pack.price / pack.credits).toFixed(2) }} per resume
          </p>
        </button>
      </div>
    </div>

    <!-- Notification Settings -->
    <div class="glass-card p-6">
      <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white mb-6">
        Notifications
      </h2>

      <div class="space-y-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-900 dark:text-white font-medium mb-1">
              Email Notifications
            </p>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Receive job match alerts via email
            </p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              v-model="notifications.email_enabled"
              class="sr-only peer"
            />
            <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
          </label>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
            Email Frequency
          </label>
          <select
            v-model="notifications.frequency"
            :disabled="!notifications.email_enabled"
            class="input-field"
            :class="{ 'opacity-50 cursor-not-allowed': !notifications.email_enabled }"
          >
            <option value="instant">Instant (as matches arrive)</option>
            <option value="daily">Daily Digest</option>
            <option value="weekly">Weekly Summary</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
            Minimum Match Score
          </label>
          <div class="flex items-center space-x-4">
            <input
              type="range"
              v-model.number="notifications.min_score_threshold"
              min="0"
              max="100"
              step="5"
              :disabled="!notifications.email_enabled"
              class="flex-1"
              :class="{ 'opacity-50 cursor-not-allowed': !notifications.email_enabled }"
            />
            <span class="text-emerald-400 font-bold text-lg w-12">
              {{ notifications.min_score_threshold }}%
            </span>
          </div>
          <p class="text-xs text-gray-600 dark:text-gray-500 mt-2">
            Only notify me about jobs with a match score of {{ notifications.min_score_threshold }}% or higher
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
            Daily Digest Time (24-hour format)
          </label>
          <input
            type="number"
            v-model.number="notifications.digest_time_hour"
            min="0"
            max="23"
            :disabled="!notifications.email_enabled || notifications.frequency !== 'daily'"
            class="input-field"
            :class="{ 'opacity-50 cursor-not-allowed': !notifications.email_enabled || notifications.frequency !== 'daily' }"
            placeholder="18"
          />
          <p class="text-xs text-gray-600 dark:text-gray-500 mt-1">
            {{ notifications.digest_time_hour }}:00 in your local timezone
          </p>
        </div>

        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-900 dark:text-white font-medium mb-1">
              Resume Ready Alerts
            </p>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Get notified when your tailored resume is ready
            </p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              v-model="notifications.notify_resume_ready"
              :disabled="!notifications.email_enabled"
              class="sr-only peer"
            />
            <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600" :class="{ 'opacity-50': !notifications.email_enabled }"></div>
          </label>
        </div>
      </div>

      <div class="flex justify-end mt-6">
        <button @click="saveNotifications" class="btn-primary">
          Save Notification Settings
        </button>
      </div>
    </div>

    <!-- Account Settings -->
    <div class="glass-card p-6">
      <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white mb-6">
        Account
      </h2>

      <div class="space-y-4">
        <div>
          <button
            @click="showPasswordModal = true"
            class="text-emerald-400 hover:text-emerald-300 text-sm font-medium flex items-center"
          >
            <Key :size="16" class="mr-2" />
            Change Password
          </button>
        </div>

        <div class="pt-4 border-t border-white/10 dark:border-white/10 border-gray-200">
          <button
            @click="showDeleteModal = true"
            class="text-red-400 hover:text-red-300 text-sm font-medium flex items-center"
          >
            <Trash2 :size="16" class="mr-2" />
            Delete Account
          </button>
        </div>
      </div>
    </div>

    <!-- Change Password Modal -->
    <div
      v-if="showPasswordModal"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
      @click.self="showPasswordModal = false"
    >
      <div class="glass-card p-8 max-w-md w-full mx-4">
        <h2 class="text-2xl font-display font-bold text-gray-900 dark:text-white mb-6">
          Change Password
        </h2>

        <form @submit.prevent="changePassword" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
              Current Password
            </label>
            <input
              v-model="passwordForm.current"
              type="password"
              required
              class="input-field"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
              New Password
            </label>
            <input
              v-model="passwordForm.new"
              type="password"
              required
              minlength="6"
              class="input-field"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
              Confirm New Password
            </label>
            <input
              v-model="passwordForm.confirm"
              type="password"
              required
              minlength="6"
              class="input-field"
            />
          </div>

          <div class="flex space-x-3 pt-4">
            <button type="submit" class="btn-primary flex-1">
              Update Password
            </button>
            <button type="button" @click="showPasswordModal = false" class="btn-secondary">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Account Modal -->
    <div
      v-if="showDeleteModal"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
      @click.self="showDeleteModal = false"
    >
      <div class="glass-card p-8 max-w-md w-full mx-4">
        <h2 class="text-2xl font-display font-bold text-red-400 mb-4">
          Delete Account
        </h2>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          This action cannot be undone. All your data, including matches and resumes, will be permanently deleted.
        </p>

        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
            Type "DELETE" to confirm
          </label>
          <input
            v-model="deleteConfirm"
            type="text"
            class="input-field"
            placeholder="DELETE"
          />
        </div>

        <div class="flex space-x-3">
          <button
            @click="deleteAccount"
            :disabled="deleteConfirm !== 'DELETE'"
            class="flex-1 px-4 py-3 bg-red-600 hover:bg-red-700 disabled:bg-red-600/50 disabled:cursor-not-allowed text-white rounded-xl font-medium transition-all"
          >
            Delete My Account
          </button>
          <button @click="showDeleteModal = false" class="btn-secondary">
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Coins, Key, Trash2 } from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'
import { api } from '~/utils/api'

definePageMeta({
  layout: 'app'
})

const authStore = useAuthStore()
const loading = ref(true)

const credits = ref(authStore.user?.credits || 0)
const totalCreditsPurchased = ref(0)

const creditPacks = [
  { credits: 1, price: 2.99 },
  { credits: 5, price: 9.99 },
  { credits: 20, price: 19.99 }
]

const notifications = ref({
  email_enabled: true,
  frequency: 'daily',
  min_score_threshold: 70,
  digest_time_hour: 18,
  notify_resume_ready: true
})

const showPasswordModal = ref(false)
const showDeleteModal = ref(false)

const passwordForm = ref({
  current: '',
  new: '',
  confirm: ''
})

const deleteConfirm = ref('')

// Fetch settings
const fetchSettings = async () => {
  try {
    loading.value = true
    const response = await api.get<any>('/profile')

    if (response.notification_settings) {
      notifications.value = {
        email_enabled: response.notification_settings.email_enabled ?? true,
        frequency: response.notification_settings.frequency || 'daily',
        min_score_threshold: response.notification_settings.min_score_threshold || 70,
        digest_time_hour: response.notification_settings.digest_time_hour || 18,
        notify_resume_ready: response.notification_settings.notify_resume_ready ?? true
      }
    }

    credits.value = response.credits || 0
    totalCreditsPurchased.value = 0 // TODO: Add this to API response
  } catch (error) {
    console.error('Failed to fetch settings:', error)
  } finally {
    loading.value = false
  }
}

const purchaseCredits = async (pack: any) => {
  try {
    // TODO: Integrate with Stripe
    console.log('Purchasing credits:', pack)
    alert('Payment integration coming soon!')
  } catch (error) {
    console.error('Failed to purchase credits:', error)
  }
}

const saveNotifications = async () => {
  try {
    await api.put('/profile/notifications', notifications.value)
    alert('Notification settings saved successfully!')
  } catch (error: any) {
    console.error('Failed to save notifications:', error)
    alert(error.message || 'Failed to save notification settings')
  }
}

const changePassword = async () => {
  if (passwordForm.value.new !== passwordForm.value.confirm) {
    alert('New passwords do not match')
    return
  }

  try {
    // TODO: Implement change password API endpoint
    console.log('Changing password')
    alert('Password change feature coming soon!')
    showPasswordModal.value = false
    passwordForm.value = { current: '', new: '', confirm: '' }
  } catch (error) {
    console.error('Failed to change password:', error)
  }
}

const deleteAccount = async () => {
  try {
    // TODO: Implement delete account API endpoint
    console.log('Deleting account')
    alert('Account deletion feature coming soon!')
    // authStore.logout()
  } catch (error) {
    console.error('Failed to delete account:', error)
  }
}

onMounted(async () => {
  await fetchSettings()
})
</script>
