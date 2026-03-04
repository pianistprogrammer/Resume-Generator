<template>
  <div class="space-y-8">
    <!-- Header -->
    <div>
      <h1 class="text-3xl font-display font-bold text-gray-900 dark:text-white mb-2">
        Job Preferences
      </h1>
      <p class="text-gray-600 dark:text-gray-400">
        Configure your job search preferences to get better matches
      </p>
    </div>

    <!-- Job Preferences -->
    <div class="glass-card p-6">
      <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white mb-6">
        Desired Roles
      </h2>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
            Job Titles (press Enter to add)
          </label>
          <input
            v-model="newRole"
            @keydown.enter.prevent="addRole"
            type="text"
            class="input-field"
            placeholder="e.g., Software Engineer, Product Manager"
          />
        </div>

        <div class="flex flex-wrap gap-2">
          <span
            v-for="(role, index) in preferences.desired_roles"
            :key="index"
            class="badge bg-emerald-600/20 text-emerald-400 flex items-center space-x-2"
          >
            <span>{{ role }}</span>
            <button @click="removeRole(index)" class="hover:text-emerald-200">
              <X :size="14" />
            </button>
          </span>
        </div>
      </div>
    </div>

    <!-- Location Preferences -->
    <div class="glass-card p-6">
      <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white mb-6">
        Location Preferences
      </h2>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
            Desired Locations (press Enter to add)
          </label>
          <input
            v-model="newLocation"
            @keydown.enter.prevent="addLocation"
            type="text"
            class="input-field"
            placeholder="e.g., San Francisco, CA"
          />
        </div>

        <div class="flex flex-wrap gap-2">
          <span
            v-for="(location, index) in preferences.desired_locations"
            :key="index"
            class="badge bg-blue-600/20 text-blue-400 flex items-center space-x-2"
          >
            <span>{{ location }}</span>
            <button @click="removeLocation(index)" class="hover:text-blue-200">
              <X :size="14" />
            </button>
          </span>
        </div>

        <div class="mt-4">
          <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
            Remote Preference
          </label>
          <select v-model="preferences.remote_preference" class="input-field">
            <option value="no_preference">No Preference</option>
            <option value="remote_only">Remote Only</option>
            <option value="hybrid">Hybrid</option>
            <option value="onsite">On-site Only</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Salary Range -->
    <div class="glass-card p-6">
      <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white mb-6">
        Salary Expectations
      </h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
            Minimum Salary ($)
          </label>
          <input
            v-model.number="preferences.min_salary"
            type="number"
            step="1000"
            class="input-field"
            placeholder="e.g., 80000"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
            Maximum Salary ($)
          </label>
          <input
            v-model.number="preferences.max_salary"
            type="number"
            step="1000"
            class="input-field"
            placeholder="e.g., 150000"
          />
        </div>
      </div>
    </div>

    <!-- Experience Level -->
    <div class="glass-card p-6">
      <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white mb-6">
        Experience Level
      </h2>

      <div class="space-y-3">
        <label
          v-for="level in experienceLevels"
          :key="level.value"
          class="flex items-center space-x-3 cursor-pointer"
        >
          <input
            type="checkbox"
            :value="level.value"
            v-model="preferences.experience_levels"
            class="w-5 h-5 bg-white/10 border-2 border-gray-600 rounded focus:ring-emerald-500 text-emerald-600"
          />
          <span class="text-gray-900 dark:text-white">{{ level.label }}</span>
        </label>
      </div>
    </div>

    <!-- Keywords -->
    <div class="glass-card p-6">
      <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white mb-6">
        Keywords
      </h2>

      <div class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
            Required Keywords (press Enter to add)
          </label>
          <input
            v-model="newRequiredKeyword"
            @keydown.enter.prevent="addRequiredKeyword"
            type="text"
            class="input-field"
            placeholder="e.g., React, Cloud, AI"
          />
          <p class="text-xs text-gray-600 dark:text-gray-500 mt-1">
            Jobs must contain these keywords
          </p>

          <div class="flex flex-wrap gap-2 mt-3">
            <span
              v-for="(keyword, index) in preferences.required_keywords"
              :key="index"
              class="badge bg-emerald-600/20 text-emerald-400 flex items-center space-x-2"
            >
              <span>{{ keyword }}</span>
              <button @click="removeRequiredKeyword(index)" class="hover:text-emerald-200">
                <X :size="14" />
              </button>
            </span>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
            Exclude Keywords (press Enter to add)
          </label>
          <input
            v-model="newExcludeKeyword"
            @keydown.enter.prevent="addExcludeKeyword"
            type="text"
            class="input-field"
            placeholder="e.g., Manager, Sales, Intern"
          />
          <p class="text-xs text-gray-600 dark:text-gray-500 mt-1">
            Jobs with these keywords will be filtered out
          </p>

          <div class="flex flex-wrap gap-2 mt-3">
            <span
              v-for="(keyword, index) in preferences.exclude_keywords"
              :key="index"
              class="badge bg-red-600/20 text-red-400 flex items-center space-x-2"
            >
              <span>{{ keyword }}</span>
              <button @click="removeExcludeKeyword(index)" class="hover:text-red-200">
                <X :size="14" />
              </button>
            </span>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
            Exclude Companies (press Enter to add)
          </label>
          <input
            v-model="newExcludeCompany"
            @keydown.enter.prevent="addExcludeCompany"
            type="text"
            class="input-field"
            placeholder="e.g., Company Name"
          />
          <p class="text-xs text-gray-600 dark:text-gray-500 mt-1">
            Jobs from these companies will be filtered out
          </p>

          <div class="flex flex-wrap gap-2 mt-3">
            <span
              v-for="(company, index) in preferences.exclude_companies"
              :key="index"
              class="badge bg-red-600/20 text-red-400 flex items-center space-x-2"
            >
              <span>{{ company }}</span>
              <button @click="removeExcludeCompany(index)" class="hover:text-red-200">
                <X :size="14" />
              </button>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Save Button -->
    <div class="flex justify-end">
      <button @click="savePreferences" class="btn-primary">
        Save Preferences
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { X } from 'lucide-vue-next'
import { api } from '~/utils/api'

definePageMeta({
  layout: 'app'
})

const loading = ref(true)

const preferences = ref({
  desired_roles: [] as string[],
  desired_locations: [] as string[],
  remote_preference: 'no_preference',
  min_salary: null as number | null,
  max_salary: null as number | null,
  experience_levels: [] as string[],
  required_keywords: [] as string[],
  exclude_keywords: [] as string[],
  exclude_companies: [] as string[]
})

const experienceLevels = [
  { label: 'Entry Level', value: 'entry' },
  { label: 'Mid Level', value: 'mid' },
  { label: 'Senior Level', value: 'senior' },
  { label: 'Lead / Principal', value: 'lead' },
  { label: 'Executive', value: 'executive' }
]

const newRole = ref('')
const newLocation = ref('')
const newRequiredKeyword = ref('')
const newExcludeKeyword = ref('')
const newExcludeCompany = ref('')

// Fetch preferences
const fetchPreferences = async () => {
  try {
    loading.value = true
    const response = await api.get<any>('/profile')

    if (response.preferences) {
      preferences.value = {
        desired_roles: response.preferences.desired_roles || [],
        desired_locations: response.preferences.desired_locations || [],
        remote_preference: response.preferences.remote_preference || 'no_preference',
        min_salary: response.preferences.min_salary || null,
        max_salary: response.preferences.max_salary || null,
        experience_levels: response.preferences.experience_levels || [],
        required_keywords: response.preferences.required_keywords || [],
        exclude_keywords: response.preferences.exclude_keywords || [],
        exclude_companies: response.preferences.exclude_companies || []
      }
    }
  } catch (error) {
    console.error('Failed to fetch preferences:', error)
  } finally {
    loading.value = false
  }
}

const addRole = () => {
  if (newRole.value.trim() && !preferences.value.desired_roles.includes(newRole.value.trim())) {
    preferences.value.desired_roles.push(newRole.value.trim())
    newRole.value = ''
  }
}

const removeRole = (index: number) => {
  preferences.value.desired_roles.splice(index, 1)
}

const addLocation = () => {
  if (newLocation.value.trim() && !preferences.value.desired_locations.includes(newLocation.value.trim())) {
    preferences.value.desired_locations.push(newLocation.value.trim())
    newLocation.value = ''
  }
}

const removeLocation = (index: number) => {
  preferences.value.desired_locations.splice(index, 1)
}

const addRequiredKeyword = () => {
  if (newRequiredKeyword.value.trim() && !preferences.value.required_keywords.includes(newRequiredKeyword.value.trim())) {
    preferences.value.required_keywords.push(newRequiredKeyword.value.trim())
    newRequiredKeyword.value = ''
  }
}

const removeRequiredKeyword = (index: number) => {
  preferences.value.required_keywords.splice(index, 1)
}

const addExcludeKeyword = () => {
  if (newExcludeKeyword.value.trim() && !preferences.value.exclude_keywords.includes(newExcludeKeyword.value.trim())) {
    preferences.value.exclude_keywords.push(newExcludeKeyword.value.trim())
    newExcludeKeyword.value = ''
  }
}

const removeExcludeKeyword = (index: number) => {
  preferences.value.exclude_keywords.splice(index, 1)
}

const addExcludeCompany = () => {
  if (newExcludeCompany.value.trim() && !preferences.value.exclude_companies.includes(newExcludeCompany.value.trim())) {
    preferences.value.exclude_companies.push(newExcludeCompany.value.trim())
    newExcludeCompany.value = ''
  }
}

const removeExcludeCompany = (index: number) => {
  preferences.value.exclude_companies.splice(index, 1)
}

const savePreferences = async () => {
  try {
    await api.put('/profile/preferences', preferences.value)
    alert('Preferences saved successfully!')
  } catch (error: any) {
    console.error('Failed to save preferences:', error)
    alert(error.message || 'Failed to save preferences')
  }
}

onMounted(async () => {
  await fetchPreferences()
})
</script>
