<template>
  <div
    class="min-h-screen relative overflow-hidden transition-colors duration-300"
    :class="isDark
      ? 'bg-gradient-to-br from-navy-950 via-navy-900 to-navy-950'
      : 'bg-gradient-to-br from-gray-50 via-white to-gray-100'"
  >
    <!-- Theme Toggle Button -->
    <button
      @click="toggleTheme"
      class="fixed top-6 right-6 z-50 p-3 rounded-full shadow-lg transition-all hover:scale-110"
      :class="isDark
        ? 'bg-white/10 hover:bg-white/20 text-yellow-400'
        : 'bg-gray-800/90 hover:bg-gray-900 text-yellow-300'"
    >
      <Sun v-if="isDark" :size="24" />
      <Moon v-else :size="24" />
    </button>

    <!-- Animated background elements -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div
        class="absolute top-1/4 -left-48 w-96 h-96 rounded-full blur-3xl animate-pulse"
        :class="isDark ? 'bg-emerald-600/10' : 'bg-emerald-600/20'"
      ></div>
      <div
        class="absolute bottom-1/4 -right-48 w-96 h-96 rounded-full blur-3xl animate-pulse"
        :class="isDark ? 'bg-blue-600/10' : 'bg-blue-600/20'"
        style="animation-delay: 1s"
      ></div>
    </div>

    <div class="relative min-h-screen flex items-center justify-center p-4 sm:p-8">
      <div class="max-w-5xl w-full">
        <!-- Header -->
        <div class="text-center mb-12 animate-fade-in">
          <h1
            class="text-5xl font-display font-bold mb-4"
            :class="isDark ? 'text-white' : 'text-gray-900'"
          >
            Welcome to <span class="text-emerald-600">JobAlert AI</span>
          </h1>
          <p
            class="text-xl"
            :class="isDark ? 'text-gray-400' : 'text-gray-600'"
          >
            Let's build your perfect job profile in just 4 steps
          </p>
        </div>

        <!-- Progress Steps -->
        <div class="mb-12">
          <div class="flex items-center justify-between max-w-3xl mx-auto mb-6">
            <div
              v-for="(step, index) in steps"
              :key="index"
              class="flex items-center"
              :class="{ 'flex-1': index < steps.length - 1 }"
            >
              <!-- Step Circle -->
              <div class="relative">
                <div
                  class="w-14 h-14 rounded-full flex items-center justify-center font-bold text-lg transition-all duration-300 relative z-10"
                  :class="
                    currentStep > index
                      ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/50'
                      : currentStep === index
                      ? 'bg-emerald-600 text-white ring-4 ring-emerald-600/30 shadow-lg shadow-emerald-600/50 scale-110'
                      : isDark ? 'bg-white/5 text-gray-500 border-2 border-white/10' : 'bg-gray-200 text-gray-400 border-2 border-gray-300'
                  "
                >
                  <Check v-if="currentStep > index" :size="20" />
                  <span v-else>{{ index + 1 }}</span>
                </div>

                <!-- Step Icon Background -->
                <div
                  v-if="currentStep === index"
                  class="absolute inset-0 bg-emerald-600/20 rounded-full blur-xl animate-pulse"
                ></div>
              </div>

              <!-- Connector Line -->
              <div
                v-if="index < steps.length - 1"
                class="flex-1 h-1 mx-3 transition-all duration-500"
                :class="currentStep > index
                  ? 'bg-gradient-to-r from-emerald-600 to-emerald-400'
                  : isDark ? 'bg-white/10' : 'bg-gray-300'"
              ></div>
            </div>
          </div>

          <!-- Step Labels -->
          <div class="flex justify-between max-w-3xl mx-auto">
            <div
              v-for="(step, index) in steps"
              :key="index"
              class="text-center transition-all duration-300"
              :style="{ width: `${100 / steps.length}%` }"
            >
              <p
                class="text-sm font-semibold mb-1 transition-colors"
                :class="currentStep >= index
                  ? isDark ? 'text-white' : 'text-gray-900'
                  : isDark ? 'text-gray-500' : 'text-gray-400'"
              >
                {{ step.title }}
              </p>
              <p
                class="text-xs transition-colors"
                :class="currentStep >= index
                  ? isDark ? 'text-gray-400' : 'text-gray-600'
                  : isDark ? 'text-gray-600' : 'text-gray-500'"
              >
                {{ step.subtitle }}
              </p>
            </div>
          </div>
        </div>

        <!-- Main Content Card -->
        <div
          class="glass-card p-8 sm:p-12 backdrop-blur-2xl shadow-2xl transition-colors"
          :class="isDark
            ? 'bg-white/5 border border-white/10'
            : 'bg-white/90 border border-gray-200'"
        >
          <!-- Step Header -->
          <div class="mb-8">
            <div class="flex items-center gap-4 mb-4">
              <div
                class="w-12 h-12 rounded-xl flex items-center justify-center"
                :class="isDark ? 'bg-emerald-600/20' : 'bg-emerald-100'"
              >
                <component :is="steps[currentStep].icon" :size="24" :class="isDark ? 'text-emerald-400' : 'text-emerald-600'" />
              </div>
              <div>
                <h2
                  class="text-3xl font-display font-bold"
                  :class="isDark ? 'text-white' : 'text-gray-900'"
                >
                  {{ steps[currentStep].heading }}
                </h2>
                <p :class="isDark ? 'text-gray-400' : 'text-gray-600'" class="mt-1">{{ steps[currentStep].description }}</p>
              </div>
            </div>

            <!-- Progress Bar -->
            <div class="w-full h-2 bg-white/5 rounded-full overflow-hidden">
              <div
                class="h-full bg-gradient-to-r from-emerald-600 to-emerald-400 transition-all duration-500"
                :style="{ width: `${((currentStep + 1) / steps.length) * 100}%` }"
              ></div>
            </div>
          </div>

          <form @submit.prevent="handleNext">
            <!-- Step 1: Basic Info -->
            <div v-show="currentStep === 0" class="space-y-6 animate-fade-in">
              <div class="grid sm:grid-cols-2 gap-6">
                <div class="sm:col-span-2">
                  <label class="block text-sm font-semibold mb-3" :class="labelText">
                    <span class="flex items-center gap-2">
                      <Briefcase :size="16" :class="isDark ? 'text-emerald-400' : 'text-emerald-600'" />
                      Current Job Title
                      <span class="text-red-400">*</span>
                    </span>
                  </label>
                  <input
                    v-model="formData.current_title"
                    type="text"
                    :class="[inputClasses, 'text-lg']"
                    placeholder="e.g., Senior Software Engineer"
                    required
                  />
                </div>

                <div>
                  <label class="block text-sm font-semibold mb-3" :class="isDark ? 'text-gray-300' : 'text-gray-700'">
                    <span class="flex items-center gap-2">
                      <Calendar :size="16" :class="isDark ? 'text-emerald-400' : 'text-emerald-600'" />
                      Years of Experience
                      <span class="text-red-400">*</span>
                    </span>
                  </label>
                  <input
                    v-model.number="formData.years_of_experience"
                    type="number"
                    min="0"
                    max="50"
                    :class="[inputClasses, 'text-lg']"
                    placeholder="e.g., 5"
                    required
                  />
                </div>

                <div>
                  <label class="block text-sm font-semibold mb-3" :class="isDark ? 'text-gray-300' : 'text-gray-700'">
                    <span class="flex items-center gap-2">
                      <Link :size="16" :class="isDark ? 'text-emerald-400' : 'text-emerald-600'" />
                      LinkedIn Profile
                    </span>
                  </label>
                  <input
                    v-model="formData.linkedin_url"
                    type="url"
                    :class="[inputClasses, 'text-lg']"
                    placeholder="https://linkedin.com/in/yourname"
                  />
                </div>

                <div class="sm:col-span-2">
                  <label class="block text-sm font-semibold mb-3" :class="isDark ? 'text-gray-300' : 'text-gray-700'">
                    <span class="flex items-center gap-2">
                      <Sparkles :size="16" :class="isDark ? 'text-emerald-400' : 'text-emerald-600'" />
                      Professional Summary
                      <span class="text-red-400">*</span>
                    </span>
                  </label>
                  <textarea
                    v-model="formData.summary"
                    :class="[inputClasses, 'h-40', 'text-lg']"
                    placeholder="Tell us about your professional experience, achievements, and career goals..."
                    required
                  ></textarea>
                  <p class="text-xs mt-2" :class="isDark ? 'text-gray-500' : 'text-gray-600'">
                    {{ formData.summary.length }} / 500 characters
                  </p>
                </div>
              </div>
            </div>

            <!-- Step 2: Skills -->
            <div v-show="currentStep === 1" class="space-y-6 animate-fade-in">
              <div>
                <label class="block text-sm font-semibold mb-3" :class="isDark ? 'text-gray-300' : 'text-gray-700'">
                  <span class="flex items-center gap-2">
                    <Target :size="16" :class="isDark ? 'text-emerald-400' : 'text-emerald-600'" />
                    Your Skills
                    <span class="text-red-400">*</span>
                  </span>
                </label>
                <div class="relative">
                  <input
                    v-model="skillInput"
                    @keydown.enter.prevent="addSkill"
                    type="text"
                    :class="[inputClasses, 'text-lg', 'pr-24']"
                    placeholder="Type a skill and press Enter..."
                  />
                  <button
                    type="button"
                    @click="addSkill"
                    class="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-lg transition-colors"
                  >
                    Add
                  </button>
                </div>
                <p class="text-xs mt-2" :class="isDark ? 'text-gray-500' : 'text-gray-600'">
                  Add technical skills, programming languages, frameworks, tools, etc.
                </p>
              </div>

              <!-- Skills Display -->
              <div v-if="formData.skills.length > 0" class="glass-card p-6" :class="isDark ? 'bg-white/5' : 'bg-white/80'">
                <div class="flex items-center justify-between mb-4">
                  <h3 class="text-sm font-semibold" :class="isDark ? 'text-gray-300' : 'text-gray-700'">
                    Added Skills ({{ formData.skills.length }})
                  </h3>
                  <button
                    type="button"
                    @click="formData.skills = []"
                    class="text-xs text-red-400 hover:text-red-300"
                  >
                    Clear all
                  </button>
                </div>
                <div class="flex flex-wrap gap-3">
                  <div
                    v-for="(skill, index) in formData.skills"
                    :key="index"
                    class="group relative inline-flex items-center gap-2 px-4 py-2.5 rounded-xl transition-all"
                    :class="isDark
                      ? 'bg-gradient-to-r from-emerald-600/20 to-emerald-500/20 border border-emerald-500/30 hover:from-emerald-600/30 hover:to-emerald-500/30'
                      : 'bg-gradient-to-r from-emerald-100 to-emerald-50 border border-emerald-300 hover:from-emerald-200 hover:to-emerald-100'"
                  >
                    <span class="font-medium" :class="isDark ? 'text-emerald-400' : 'text-emerald-700'">{{ skill }}</span>
                    <button
                      type="button"
                      @click="removeSkill(index)"
                      class="transition-colors"
                      :class="isDark ? 'text-emerald-400/60 hover:text-red-400' : 'text-emerald-600/60 hover:text-red-500'"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>

              <div v-else class="text-center py-12 glass-card border-dashed" :class="isDark ? 'bg-white/5' : 'bg-white/60'">
                <div class="flex justify-center mb-4">
                  <Palette :size="48" :class="isDark ? 'text-gray-600' : 'text-gray-400'" />
                </div>
                <p :class="isDark ? 'text-gray-400' : 'text-gray-600'">No skills added yet. Start typing above!</p>
              </div>

              <!-- Popular Skills Suggestions -->
              <div class="glass-card p-6 border" :class="isDark ? 'bg-emerald-600/5 border-emerald-600/20' : 'bg-emerald-50 border-emerald-200'">
                <p class="text-sm font-semibold mb-3 flex items-center gap-2" :class="isDark ? 'text-gray-300' : 'text-gray-700'">
                  <Lightbulb :size="16" :class="isDark ? 'text-emerald-400' : 'text-emerald-600'" />
                  Popular Skills:
                </p>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="suggestion in skillSuggestions"
                    :key="suggestion"
                    type="button"
                    @click="addSuggestion(suggestion)"
                    class="text-xs px-3 py-1.5 rounded-lg transition-colors border"
                    :class="isDark
                      ? 'bg-white/5 hover:bg-emerald-600/20 text-gray-400 hover:text-emerald-400 border-white/10 hover:border-emerald-600/30'
                      : 'bg-white hover:bg-emerald-100 text-gray-700 hover:text-emerald-700 border-gray-200 hover:border-emerald-400'"
                  >
                    + {{ suggestion }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Step 3: Job Preferences -->
            <div v-show="currentStep === 2" class="space-y-6 animate-fade-in">
              <div>
                <label class="block text-sm font-semibold mb-3" :class="isDark ? 'text-gray-300' : 'text-gray-700'">
                  <span class="flex items-center gap-2">
                    <Target :size="16" :class="isDark ? 'text-emerald-400' : 'text-emerald-600'" />
                    Desired Job Titles
                    <span class="text-red-400">*</span>
                  </span>
                </label>
                <div class="relative">
                  <input
                    v-model="roleInput"
                    @keydown.enter.prevent="addRole"
                    type="text"
                    :class="[inputClasses, 'text-lg', 'pr-24']"
                    placeholder="Type a role and press Enter..."
                  />
                  <button
                    type="button"
                    @click="addRole"
                    class="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-lg transition-colors"
                  >
                    Add
                  </button>
                </div>
              </div>

              <!-- Roles Display -->
              <div v-if="formData.desired_roles.length > 0" class="flex flex-wrap gap-3">
                <div
                  v-for="(role, index) in formData.desired_roles"
                  :key="index"
                  class="group inline-flex items-center gap-2 px-4 py-2.5 rounded-xl transition-all"
                  :class="isDark
                    ? 'bg-gradient-to-r from-blue-600/20 to-blue-500/20 border border-blue-500/30 hover:from-blue-600/30 hover:to-blue-500/30'
                    : 'bg-gradient-to-r from-blue-100 to-blue-50 border border-blue-300 hover:from-blue-200 hover:to-blue-100'"
                >
                  <span class="font-medium" :class="isDark ? 'text-blue-400' : 'text-blue-700'">{{ role }}</span>
                  <button
                    type="button"
                    @click="removeRole(index)"
                    class="transition-colors"
                    :class="isDark ? 'text-blue-400/60 hover:text-red-400' : 'text-blue-600/60 hover:text-red-500'"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              <div class="grid sm:grid-cols-2 gap-6">
                <div class="sm:col-span-2">
                  <label class="block text-sm font-semibold mb-3" :class="isDark ? 'text-gray-300' : 'text-gray-700'">
                    <span class="flex items-center gap-2">
                      <Home :size="16" :class="isDark ? 'text-emerald-400' : 'text-emerald-600'" />
                      Remote Work Preference
                    </span>
                  </label>
                  <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <button
                      v-for="option in remoteOptions"
                      :key="option.value"
                      type="button"
                      @click="formData.remote_preference = option.value"
                      class="p-4 rounded-xl border-2 transition-all"
                      :class="isDark
                        ? (formData.remote_preference === option.value
                          ? 'border-emerald-600 bg-emerald-600/20'
                          : 'border-white/10 bg-white/5 hover:bg-white/10')
                        : (formData.remote_preference === option.value
                          ? 'border-emerald-600 bg-emerald-100'
                          : 'border-gray-200 bg-white hover:bg-gray-50')"
                    >
                      <div class="flex justify-center mb-2">
                        <component :is="option.icon" :size="28" :class="isDark ? 'text-emerald-400' : 'text-emerald-600'" />
                      </div>
                      <div class="text-sm font-semibold" :class="isDark ? 'text-white' : 'text-gray-900'">{{ option.label }}</div>
                    </button>
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-semibold mb-3" :class="isDark ? 'text-gray-300' : 'text-gray-700'">
                    <span class="flex items-center gap-2">
                      <DollarSign :size="16" :class="isDark ? 'text-emerald-400' : 'text-emerald-600'" />
                      Minimum Salary
                    </span>
                  </label>
                  <div class="relative">
                    <span class="absolute left-4 top-1/2 -translate-y-1/2 text-lg" :class="isDark ? 'text-gray-400' : 'text-gray-600'">$</span>
                    <input
                      v-model.number="formData.min_salary"
                      type="number"
                      min="0"
                      step="5000"
                      :class="[inputClasses, 'text-lg', 'pl-8']"
                      placeholder="100,000"
                    />
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-semibold mb-3" :class="isDark ? 'text-gray-300' : 'text-gray-700'">
                    <span class="flex items-center gap-2">
                      <Gem :size="16" :class="isDark ? 'text-emerald-400' : 'text-emerald-600'" />
                      Maximum Salary
                    </span>
                  </label>
                  <div class="relative">
                    <span class="absolute left-4 top-1/2 -translate-y-1/2 text-lg" :class="isDark ? 'text-gray-400' : 'text-gray-600'">$</span>
                    <input
                      v-model.number="formData.max_salary"
                      type="number"
                      min="0"
                      step="5000"
                      :class="[inputClasses, 'text-lg', 'pl-8']"
                      placeholder="150,000"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Step 4: Confirmation -->
            <div v-show="currentStep === 3" class="space-y-6 animate-fade-in">
              <!-- Success Message -->
              <div class="text-center py-8">
                <div class="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6" :class="isDark ? 'bg-emerald-600/20' : 'bg-emerald-100'">
                  <PartyPopper :size="40" :class="isDark ? 'text-emerald-400' : 'text-emerald-600'" />
                </div>
                <h3 class="text-2xl font-bold mb-3" :class="isDark ? 'text-white' : 'text-gray-900'">
                  You're All Set!
                </h3>
                <p class="max-w-lg mx-auto" :class="isDark ? 'text-gray-400' : 'text-gray-700'">
                  We'll start finding perfect job matches for you. Here's what happens next:
                </p>
              </div>

              <!-- Features Grid -->
              <div class="grid sm:grid-cols-3 gap-4">
                <div class="glass-card p-6 bg-gradient-to-br from-emerald-600/10 to-emerald-600/5 border border-emerald-600/20 text-center">
                  <div class="flex justify-center mb-3">
                    <Target :size="32" :class="isDark ? 'text-emerald-400' : 'text-emerald-600'" />
                  </div>
                  <h4 class="font-semibold mb-2" :class="isDark ? 'text-white' : 'text-gray-900'">Smart Matching</h4>
                  <p class="text-sm" :class="isDark ? 'text-gray-400' : 'text-gray-700'">
                    AI scores every job against your profile
                  </p>
                </div>

                <div class="glass-card p-6 bg-gradient-to-br from-blue-600/10 to-blue-600/5 border border-blue-600/20 text-center">
                  <div class="flex justify-center mb-3">
                    <Mail :size="32" :class="isDark ? 'text-blue-400' : 'text-blue-600'" />
                  </div>
                  <h4 class="font-semibold mb-2" :class="isDark ? 'text-white' : 'text-gray-900'">Daily Digests</h4>
                  <p class="text-sm" :class="isDark ? 'text-gray-400' : 'text-gray-700'">
                    Top matches delivered every evening
                  </p>
                </div>

                <div class="glass-card p-6 bg-gradient-to-br from-purple-600/10 to-purple-600/5 border border-purple-600/20 text-center">
                  <div class="flex justify-center mb-3">
                    <Sparkles :size="32" :class="isDark ? 'text-purple-400' : 'text-purple-600'" />
                  </div>
                  <h4 class="font-semibold mb-2" :class="isDark ? 'text-white' : 'text-gray-900'">3 Free Resumes</h4>
                  <p class="text-sm" :class="isDark ? 'text-gray-400' : 'text-gray-700'">
                    AI-tailored resumes ready in seconds
                  </p>
                </div>
              </div>

              <!-- Profile Summary -->
              <div class="glass-card p-6" :class="isDark ? 'bg-white/5' : 'bg-white/80'">
                <h4 class="font-semibold mb-4 flex items-center gap-2" :class="isDark ? 'text-white' : 'text-gray-900'">
                  <ClipboardList :size="20" :class="isDark ? 'text-emerald-400' : 'text-emerald-600'" />
                  Your Profile Summary
                </h4>
                <div class="grid sm:grid-cols-2 gap-4 text-sm">
                  <div>
                    <p class="mb-1" :class="isDark ? 'text-gray-400' : 'text-gray-600'">Job Title</p>
                    <p class="font-medium" :class="isDark ? 'text-white' : 'text-gray-900'">{{ formData.current_title }}</p>
                  </div>
                  <div>
                    <p class="mb-1" :class="isDark ? 'text-gray-400' : 'text-gray-600'">Experience</p>
                    <p class="font-medium" :class="isDark ? 'text-white' : 'text-gray-900'">{{ formData.years_of_experience }} years</p>
                  </div>
                  <div class="sm:col-span-2">
                    <p class="mb-2" :class="isDark ? 'text-gray-400' : 'text-gray-600'">Skills ({{ formData.skills.length }})</p>
                    <div class="flex flex-wrap gap-2">
                      <span
                        v-for="skill in formData.skills.slice(0, 10)"
                        :key="skill"
                        class="px-2 py-1 rounded text-xs"
                        :class="isDark ? 'bg-emerald-600/20 text-emerald-400' : 'bg-emerald-100 text-emerald-700'"
                      >
                        {{ skill }}
                      </span>
                      <span v-if="formData.skills.length > 10" class="px-2 py-1 rounded text-xs" :class="isDark ? 'bg-white/5 text-gray-400' : 'bg-gray-100 text-gray-600'">
                        +{{ formData.skills.length - 10 }} more
                      </span>
                    </div>
                  </div>
                  <div class="sm:col-span-2">
                    <p class="mb-2" :class="isDark ? 'text-gray-400' : 'text-gray-600'">Looking For</p>
                    <p :class="isDark ? 'text-white' : 'text-gray-900'">{{ formData.desired_roles.join(', ') }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Navigation Buttons -->
            <div class="flex items-center justify-between mt-10 pt-6 border-t border-white/10">
              <button
                v-if="currentStep > 0"
                type="button"
                @click="handleBack"
                class="px-8 py-3 bg-white/5 hover:bg-white/10 text-white font-medium rounded-xl transition-all border border-white/10"
              >
                ← Back
              </button>
              <div v-else></div>

              <button
                type="submit"
                class="px-8 py-3 bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-700 hover:to-emerald-600 text-white font-bold rounded-xl transition-all shadow-lg shadow-emerald-600/30 hover:shadow-emerald-600/50 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center gap-2"
                :disabled="loading || !canProceed"
              >
                <template v-if="currentStep === 3">
                  <Rocket v-if="!loading" :size="20" />
                  {{ loading ? 'Completing...' : 'Complete Setup' }}
                </template>
                <template v-else>
                  Next →
                </template>
              </button>
            </div>
          </form>
        </div>

        <!-- Help Text -->
        <p
          class="text-center text-sm mt-6"
          :class="isDark ? 'text-gray-500' : 'text-gray-600'"
        >
          Questions? We're here to help at support@jobalert.ai
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { api } from '~/utils/api'
import { User, Target, Settings, PartyPopper, Globe, Home, Repeat, Building, Check, Briefcase, Calendar, GraduationCap, DollarSign, Mail, Sparkles, Link, Palette, Lightbulb, ClipboardList, Gem, Rocket, Sun, Moon } from 'lucide-vue-next'

definePageMeta({
  layout: false
})

const authStore = useAuthStore()
const router = useRouter()
const config = useRuntimeConfig()

// Theme state
const isDark = ref(true)

const toggleTheme = () => {
  isDark.value = !isDark.value
  // Persist to localStorage
  if (process.client) {
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
  }
}

// Theme-aware class helpers
const textPrimary = computed(() => isDark.value ? 'text-white' : 'text-gray-900')
const textSecondary = computed(() => isDark.value ? 'text-gray-400' : 'text-gray-600')
const textTertiary = computed(() => isDark.value ? 'text-gray-500' : 'text-gray-500')
const bgCard = computed(() => isDark.value ? 'bg-white/5' : 'bg-white/90')
const borderCard = computed(() => isDark.value ? 'border-white/10' : 'border-gray-200')
const inputClasses = computed(() =>
  isDark.value
    ? 'w-full px-4 py-3 rounded-xl border-2 bg-white/5 border-white/10 text-white placeholder-gray-500 focus:border-emerald-600 focus:bg-white/10 transition-all'
    : 'w-full px-4 py-3 rounded-xl border-2 bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:border-emerald-600 focus:ring-2 focus:ring-emerald-600/20 transition-all'
)
const labelText = computed(() => isDark.value ? 'text-gray-300' : 'text-gray-700')

// Initialize theme from localStorage
onMounted(() => {
  if (process.client) {
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      isDark.value = savedTheme === 'dark'
    }
  }
  authStore.init()
  if (!authStore.isAuthenticated) {
    router.push('/login')
  }
})

const steps = [
  {
    title: 'About You',
    subtitle: 'Basic info',
    icon: User,
    heading: 'Tell us about yourself',
    description: 'Share your professional background and experience'
  },
  {
    title: 'Your Skills',
    subtitle: 'Expertise',
    icon: Target,
    heading: 'What are your superpowers?',
    description: 'Add the skills that make you stand out'
  },
  {
    title: 'Preferences',
    subtitle: 'Dream job',
    icon: Settings,
    heading: 'What are you looking for?',
    description: 'Define your ideal job criteria'
  },
  {
    title: 'All Set',
    subtitle: 'Review',
    icon: PartyPopper,
    heading: 'Ready to find your dream job!',
    description: 'Review your profile and start matching'
  }
]

const remoteOptions = [
  { value: 'any', label: 'Any', icon: Globe },
  { value: 'remote_only', label: 'Remote', icon: Home },
  { value: 'hybrid', label: 'Hybrid', icon: Repeat },
  { value: 'onsite', label: 'Onsite', icon: Building }
]

const skillSuggestions = [
  'JavaScript', 'Python', 'React', 'Node.js', 'TypeScript',
  'AWS', 'Docker', 'SQL', 'Git', 'API Design'
]

const currentStep = ref(0)
const loading = ref(false)
const skillInput = ref('')
const roleInput = ref('')

const formData = reactive({
  current_title: '',
  years_of_experience: null as number | null,
  linkedin_url: '',
  summary: '',
  skills: [] as string[],
  desired_roles: [] as string[],
  remote_preference: 'any',
  min_salary: null as number | null,
  max_salary: null as number | null
})

const canProceed = computed(() => {
  switch (currentStep.value) {
    case 0:
      return formData.current_title && formData.years_of_experience !== null && formData.summary
    case 1:
      return formData.skills.length > 0
    case 2:
      return formData.desired_roles.length > 0
    case 3:
      return true
    default:
      return false
  }
})

const addSkill = () => {
  const skill = skillInput.value.trim()
  if (skill && !formData.skills.includes(skill)) {
    formData.skills.push(skill)
    skillInput.value = ''
  }
}

const addSuggestion = (skill: string) => {
  if (!formData.skills.includes(skill)) {
    formData.skills.push(skill)
  }
}

const removeSkill = (index: number) => {
  formData.skills.splice(index, 1)
}

const addRole = () => {
  const role = roleInput.value.trim()
  if (role && !formData.desired_roles.includes(role)) {
    formData.desired_roles.push(role)
    roleInput.value = ''
  }
}

const removeRole = (index: number) => {
  formData.desired_roles.splice(index, 1)
}

const handleBack = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const handleNext = async () => {
  if (!canProceed.value) return

  if (currentStep.value < 3) {
    currentStep.value++
  } else {
    await completeOnboarding()
  }
}

const completeOnboarding = async () => {
  try {
    loading.value = true

    // Check authentication
    if (!authStore.token) {
      console.error('No auth token found')
      alert('Session expired. Please log in again.')
      router.push('/login')
      return
    }

    console.log('Submitting onboarding data:', {
      profile: {
        current_title: formData.current_title,
        years_of_experience: formData.years_of_experience,
        linkedin_url: formData.linkedin_url || undefined,
        summary: formData.summary,
        skills: formData.skills
      },
      preferences: {
        desired_roles: formData.desired_roles,
        remote_preference: formData.remote_preference,
        min_salary: formData.min_salary || undefined,
        max_salary: formData.max_salary || undefined
      }
    })

    // Update profile using the new API format
    await api.put('/profile', {
      current_title: formData.current_title,
      years_of_experience: formData.years_of_experience,
      linkedin_url: formData.linkedin_url || undefined,
      summary: formData.summary,
      skills: formData.skills
    })

    // Update preferences using the new API format
    await api.put('/profile/preferences', {
      desired_roles: formData.desired_roles,
      remote_preference: formData.remote_preference,
      min_salary: formData.min_salary || undefined,
      max_salary: formData.max_salary || undefined
    })

    // Mark onboarding complete using the new API format
    const response = await api.post('/profile/onboarding/complete')

    authStore.updateUser(response)
    router.push('/dashboard')
  } catch (error: any) {
    console.error('Onboarding error:', error)

    alert(error.message || 'Failed to complete onboarding. Please try again.')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // Initialize theme from localStorage
  if (process.client) {
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      isDark.value = savedTheme === 'dark'
    }
  }

  authStore.init()

  // Debug: Log auth state
  console.log('Auth state:', {
    isAuthenticated: authStore.isAuthenticated,
    hasToken: !!authStore.token,
    tokenPreview: authStore.token ? authStore.token.substring(0, 20) + '...' : 'none',
    user: authStore.user
  })

  if (!authStore.isAuthenticated) {
    console.warn('User not authenticated, redirecting to login')
    router.push('/login')
  }
})
</script>

<style scoped>
.input-field {
  @apply w-full px-4 py-3 rounded-xl border-2 transition-all;
}

/* Dark mode - using data attribute approach */
html.dark .input-field,
.dark .input-field {
  @apply bg-white/5 border-white/10 text-white placeholder-gray-500;
  @apply focus:border-emerald-600 focus:bg-white/10;
}

/* Light mode - default */
html:not(.dark) .input-field,
:not(.dark) .input-field {
  @apply bg-white border-gray-300 text-gray-900 placeholder-gray-400;
  @apply focus:border-emerald-600 focus:bg-white focus:ring-2 focus:ring-emerald-600/20;
}

.glass-card {
  @apply rounded-2xl;
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.5s ease-out;
}
</style>
