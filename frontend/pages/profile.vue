<template>
  <div class="space-y-8">
    <!-- Header -->
    <div>
      <h1 class="text-3xl font-display font-bold text-gray-900 dark:text-white mb-2">
        Profile
      </h1>
      <p class="text-gray-600 dark:text-gray-400">
        Manage your professional information
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="space-y-6">
      <div class="glass-card p-6">
        <div class="skeleton h-8 w-48 mb-4"></div>
        <div class="space-y-4">
          <div class="skeleton h-12 w-full"></div>
          <div class="skeleton h-12 w-full"></div>
          <div class="skeleton h-12 w-full"></div>
        </div>
      </div>
    </div>

    <!-- Profile Content -->
    <div v-else class="space-y-8">
      <!-- Personal Information -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white">
          Personal Information
        </h2>
        <button
          v-if="!editingPersonal"
          @click="editingPersonal = true"
          class="text-emerald-400 hover:text-emerald-300 text-sm font-medium flex items-center"
        >
          <Edit :size="16" class="mr-1" />
          Edit
        </button>
      </div>

      <form v-if="editingPersonal" @submit.prevent="savePersonal" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
              Full Name
            </label>
            <input
              v-model="personalForm.full_name"
              type="text"
              class="input-field"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
              Email
            </label>
            <input
              v-model="personalForm.email"
              type="email"
              disabled
              class="input-field opacity-50 cursor-not-allowed"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
              Phone
            </label>
            <input
              v-model="personalForm.phone"
              type="tel"
              class="input-field"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
              Location
            </label>
            <input
              v-model="personalForm.location"
              type="text"
              class="input-field"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
              LinkedIn URL
            </label>
            <input
              v-model="personalForm.linkedin_url"
              type="url"
              class="input-field"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
              GitHub URL
            </label>
            <input
              v-model="personalForm.github_url"
              type="url"
              class="input-field"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
              Portfolio URL
            </label>
            <input
              v-model="personalForm.portfolio_url"
              type="url"
              class="input-field"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
              Current Title
            </label>
            <input
              v-model="personalForm.current_title"
              type="text"
              class="input-field"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
              Years of Experience
            </label>
            <input
              v-model.number="personalForm.years_of_experience"
              type="number"
              min="0"
              class="input-field"
            />
          </div>
        </div>

        <div class="flex space-x-3 pt-4">
          <button type="submit" class="btn-primary">
            Save Changes
          </button>
          <button type="button" @click="cancelPersonal" class="btn-secondary">
            Cancel
          </button>
        </div>
      </form>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <p class="text-sm text-gray-600 dark:text-gray-500 mb-1">Full Name</p>
          <p class="text-gray-900 dark:text-white">{{ profile.full_name || 'Not set' }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-600 dark:text-gray-500 mb-1">Email</p>
          <p class="text-gray-900 dark:text-white">{{ profile.email }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-600 dark:text-gray-500 mb-1">Phone</p>
          <p class="text-gray-900 dark:text-white">{{ profile.phone || 'Not set' }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-600 dark:text-gray-500 mb-1">Location</p>
          <p class="text-gray-900 dark:text-white">{{ profile.location || 'Not set' }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-600 dark:text-gray-500 mb-1">LinkedIn</p>
          <a v-if="profile.linkedin_url" :href="profile.linkedin_url" target="_blank" class="text-emerald-400 hover:text-emerald-300">
            {{ profile.linkedin_url }}
          </a>
          <p v-else class="text-gray-600 dark:text-gray-500">Not set</p>
        </div>

        <div>
          <p class="text-sm text-gray-600 dark:text-gray-500 mb-1">GitHub</p>
          <a v-if="profile.github_url" :href="profile.github_url" target="_blank" class="text-emerald-400 hover:text-emerald-300">
            {{ profile.github_url }}
          </a>
          <p v-else class="text-gray-600 dark:text-gray-500">Not set</p>
        </div>

        <div>
          <p class="text-sm text-gray-600 dark:text-gray-500 mb-1">Portfolio</p>
          <a v-if="profile.portfolio_url" :href="profile.portfolio_url" target="_blank" class="text-emerald-400 hover:text-emerald-300">
            {{ profile.portfolio_url }}
          </a>
          <p v-else class="text-gray-600 dark:text-gray-500">Not set</p>
        </div>

        <div>
          <p class="text-sm text-gray-600 dark:text-gray-500 mb-1">Current Title</p>
          <p class="text-gray-900 dark:text-white">{{ profile.current_title || 'Not set' }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-600 dark:text-gray-500 mb-1">Years of Experience</p>
          <p class="text-gray-900 dark:text-white">{{ profile.years_of_experience || 'Not set' }}</p>
        </div>
      </div>
    </div>

    <!-- Skills -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white">
          Skills
        </h2>
        <button
          v-if="!editingSkills"
          @click="editingSkills = true"
          class="text-emerald-400 hover:text-emerald-300 text-sm font-medium flex items-center"
        >
          <Edit :size="16" class="mr-1" />
          Edit
        </button>
      </div>

      <div v-if="editingSkills" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 dark:text-gray-300 text-gray-700 mb-2">
            Add skills (press Enter to add)
          </label>
          <input
            v-model="newSkill"
            @keydown.enter.prevent="addSkill"
            type="text"
            class="input-field"
            placeholder="e.g., React, Python, AWS"
          />
        </div>

        <div class="flex flex-wrap gap-3">
          <span
            v-for="(skill, index) in skillsForm"
            :key="index"
            class="inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all bg-emerald-100 dark:bg-gradient-to-r dark:from-emerald-500/20 dark:to-emerald-600/20 text-emerald-700 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-500/30 hover:border-emerald-400 dark:hover:border-emerald-400/50 hover:shadow-lg hover:shadow-emerald-500/20"
          >
            <span>{{ skill }}</span>
            <button @click="removeSkill(index)" class="ml-2 hover:text-emerald-600 dark:hover:text-emerald-200 transition-colors">
              <X :size="16" />
            </button>
          </span>
        </div>

        <div class="flex space-x-3 pt-4">
          <button @click="saveSkills" class="btn-primary">
            Save Changes
          </button>
          <button @click="cancelSkills" class="btn-secondary">
            Cancel
          </button>
        </div>
      </div>

      <div v-else>
        <div v-if="profile.skills && profile.skills.length > 0" class="flex flex-wrap gap-3">
          <span
            v-for="skill in profile.skills"
            :key="skill"
            class="inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium bg-emerald-100 dark:bg-gradient-to-r dark:from-emerald-500/20 dark:to-emerald-600/20 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-500/30 shadow-sm"
          >
            {{ skill }}
          </span>
        </div>
        <p v-else class="text-gray-600 dark:text-gray-500">No skills added yet</p>
      </div>
    </div>

    <!-- Work Experience -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white">
          Work Experience
        </h2>
        <button
          @click="addExperience"
          class="text-emerald-400 hover:text-emerald-300 text-sm font-medium flex items-center"
        >
          <Plus :size="16" class="mr-1" />
          Add Experience
        </button>
      </div>

      <div v-if="profile.work_experience && profile.work_experience.length > 0" class="space-y-4">
        <div
          v-for="(exp, index) in profile.work_experience"
          :key="index"
          class="glass-card p-4 border border-gray-200 dark:border-white/10"
        >
          <!-- View Mode -->
          <div v-if="editingExpIndex !== index">
            <div class="flex items-start justify-between mb-2">
              <div class="flex-1">
                <h3 class="font-semibold text-gray-900 dark:text-white">{{ exp.title }}</h3>
                <p class="text-emerald-400">{{ exp.company }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-500">
                  {{ exp.start_date }} - {{ exp.end_date || 'Present' }}
                  <span v-if="exp.location"> • {{ exp.location }}</span>
                </p>
              </div>
              <div class="flex space-x-2">
                <button
                  @click="editExperience(index)"
                  class="text-emerald-400 hover:text-emerald-300"
                >
                  <Edit :size="16" />
                </button>
                <button
                  @click="deleteExperience(index)"
                  class="text-red-400 hover:text-red-300"
                >
                  <Trash2 :size="16" />
                </button>
              </div>
            </div>
            <ul v-if="exp.bullets && exp.bullets.length > 0" class="list-disc list-inside space-y-1 text-sm text-gray-700 dark:text-gray-300 mt-3">
              <li v-for="(bullet, bIndex) in exp.bullets" :key="bIndex">{{ bullet }}</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Add/Edit Experience Form -->
      <div v-if="editingExpIndex !== null" class="glass-card p-4 border border-gray-200 dark:border-white/10 space-y-4">
        <h3 class="font-semibold text-gray-900 dark:text-white mb-4">
          {{ editingExpIndex === -1 ? 'Add New Experience' : 'Edit Experience' }}
        </h3>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Job Title *
            </label>
            <input
              v-model="experienceForm.title"
              type="text"
              class="input-field"
              placeholder="e.g., Senior Software Engineer"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Company *
            </label>
            <input
              v-model="experienceForm.company"
              type="text"
              class="input-field"
              placeholder="e.g., Google"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Start Date *
            </label>
            <input
              v-model="experienceForm.start_date"
              type="text"
              class="input-field"
              placeholder="e.g., Jan 2020"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              End Date
            </label>
            <input
              v-model="experienceForm.end_date"
              type="text"
              class="input-field"
              placeholder="Leave empty if current"
            />
          </div>

          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Location
            </label>
            <input
              v-model="experienceForm.location"
              type="text"
              class="input-field"
              placeholder="e.g., San Francisco, CA"
            />
          </div>

          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Achievements & Responsibilities
            </label>
            <div class="space-y-2">
              <div
                v-for="(bullet, bIndex) in experienceForm.bullets"
                :key="bIndex"
                class="flex space-x-2"
              >
                <input
                  v-model="experienceForm.bullets[bIndex]"
                  type="text"
                  class="input-field flex-1"
                  placeholder="Describe your achievement or responsibility..."
                />
                <button
                  v-if="experienceForm.bullets.length > 1"
                  @click="removeBullet(bIndex)"
                  class="text-red-400 hover:text-red-300 p-2"
                >
                  <X :size="20" />
                </button>
              </div>
              <button
                @click="addBullet"
                class="text-emerald-400 hover:text-emerald-300 text-sm font-medium flex items-center"
              >
                <Plus :size="16" class="mr-1" />
                Add bullet point
              </button>
            </div>
          </div>
        </div>

        <div class="flex space-x-3 pt-4">
          <button @click="saveExperience" class="btn-primary">
            Save
          </button>
          <button @click="cancelEditExperience" class="btn-secondary">
            Cancel
          </button>
        </div>
      </div>

      <p v-else-if="!profile.work_experience || profile.work_experience.length === 0" class="text-gray-600 dark:text-gray-500">No work experience added yet</p>
    </div>

    <!-- Education -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white">
          Education
        </h2>
        <button
          @click="addEducation"
          class="text-emerald-400 hover:text-emerald-300 text-sm font-medium flex items-center"
        >
          <Plus :size="16" class="mr-1" />
          Add Education
        </button>
      </div>

      <div v-if="profile.education && profile.education.length > 0" class="space-y-4">
        <div
          v-for="(edu, index) in profile.education"
          :key="index"
          class="glass-card p-4 border border-gray-200 dark:border-white/10"
        >
          <!-- View Mode -->
          <div v-if="editingEduIndex !== index">
            <div class="flex items-start justify-between mb-2">
              <div class="flex-1">
                <h3 class="font-semibold text-gray-900 dark:text-white">{{ edu.degree }} <span v-if="edu.field">in {{ edu.field }}</span></h3>
                <p class="text-emerald-400">{{ edu.institution }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-500">
                  <span v-if="edu.graduation_year">{{ edu.graduation_year }}</span>
                  <span v-if="edu.gpa"> • GPA: {{ edu.gpa }}/5.0</span>
                </p>
              </div>
              <div class="flex space-x-2">
                <button
                  @click="editEducation(index)"
                  class="text-emerald-400 hover:text-emerald-300"
                >
                  <Edit :size="16" />
                </button>
                <button
                  @click="deleteEducation(index)"
                  class="text-red-400 hover:text-red-300"
                >
                  <Trash2 :size="16" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Add/Edit Education Form -->
      <div v-if="editingEduIndex !== null" class="glass-card p-4 border border-gray-200 dark:border-white/10 space-y-4">
        <h3 class="font-semibold text-gray-900 dark:text-white mb-4">
          {{ editingEduIndex === -1 ? 'Add New Education' : 'Edit Education' }}
        </h3>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Degree *
            </label>
            <input
              v-model="educationForm.degree"
              type="text"
              class="input-field"
              placeholder="e.g., Bachelor of Science"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Field of Study
            </label>
            <input
              v-model="educationForm.field"
              type="text"
              class="input-field"
              placeholder="e.g., Computer Science"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Institution *
            </label>
            <input
              v-model="educationForm.institution"
              type="text"
              class="input-field"
              placeholder="e.g., Stanford University"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Graduation Year
            </label>
            <input
              v-model="educationForm.graduation_year"
              type="text"
              class="input-field"
              placeholder="e.g., 2020"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              GPA (out of 5.0)
            </label>
            <input
              v-model.number="educationForm.gpa"
              type="number"
              step="0.01"
              min="0"
              max="5"
              class="input-field"
              placeholder="e.g., 4.0"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Enter your GPA on a 5.0 scale
            </p>
          </div>
        </div>

        <div class="flex space-x-3 pt-4">
          <button @click="saveEducation" class="btn-primary">
            Save
          </button>
          <button @click="cancelEditEducation" class="btn-secondary">
            Cancel
          </button>
        </div>
      </div>

      <p v-else-if="!profile.education || profile.education.length === 0" class="text-gray-600 dark:text-gray-500">No education added yet</p>
    </div>

    <!-- Certifications -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white">
          Certifications
        </h2>
        <button
          @click="addCertification"
          class="text-emerald-400 hover:text-emerald-300 text-sm font-medium flex items-center"
        >
          <Plus :size="16" class="mr-1" />
          Add Certification
        </button>
      </div>

      <div v-if="profile.certifications && profile.certifications.length > 0" class="space-y-4">
        <div
          v-for="(cert, index) in profile.certifications"
          :key="index"
          class="glass-card p-4 border border-gray-200 dark:border-white/10"
        >
          <!-- View Mode -->
          <div v-if="editingCertIndex !== index">
            <div class="flex items-start justify-between mb-2">
              <div class="flex-1">
                <h3 class="font-semibold text-gray-900 dark:text-white">{{ cert.name }}</h3>
                <p class="text-emerald-400">{{ cert.issuer }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-500">
                  <span v-if="cert.issue_date">{{ cert.issue_date }}</span>
                  <span v-if="cert.expiry_date"> • Expires: {{ cert.expiry_date }}</span>
                  <span v-if="cert.credential_id"> • ID: {{ cert.credential_id }}</span>
                </p>
              </div>
              <div class="flex space-x-2">
                <button
                  @click="editCertification(index)"
                  class="text-emerald-400 hover:text-emerald-300"
                >
                  <Edit :size="16" />
                </button>
                <button
                  @click="deleteCertification(index)"
                  class="text-red-400 hover:text-red-300"
                >
                  <Trash2 :size="16" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Add/Edit Certification Form -->
      <div v-if="editingCertIndex !== null" class="glass-card p-4 border border-gray-200 dark:border-white/10 space-y-4">
        <h3 class="font-semibold text-gray-900 dark:text-white mb-4">
          {{ editingCertIndex === -1 ? 'Add New Certification' : 'Edit Certification' }}
        </h3>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Certification Name *
            </label>
            <input
              v-model="certificationForm.name"
              type="text"
              class="input-field"
              placeholder="e.g., AWS Certified Solutions Architect"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Issuing Organization *
            </label>
            <input
              v-model="certificationForm.issuer"
              type="text"
              class="input-field"
              placeholder="e.g., Amazon Web Services"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Issue Date
            </label>
            <input
              v-model="certificationForm.issue_date"
              type="text"
              class="input-field"
              placeholder="e.g., Jan 2023"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Expiry Date
            </label>
            <input
              v-model="certificationForm.expiry_date"
              type="text"
              class="input-field"
              placeholder="e.g., Jan 2026 or leave empty"
            />
          </div>

          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Credential ID
            </label>
            <input
              v-model="certificationForm.credential_id"
              type="text"
              class="input-field"
              placeholder="e.g., ABC123XYZ"
            />
          </div>
        </div>

        <div class="flex space-x-3 pt-4">
          <button @click="saveCertification" class="btn-primary">
            Save
          </button>
          <button @click="cancelEditCertification" class="btn-secondary">
            Cancel
          </button>
        </div>
      </div>

      <p v-else-if="!profile.certifications || profile.certifications.length === 0" class="text-gray-600 dark:text-gray-500">No certifications added yet</p>
    </div>

    <!-- Professional Summary -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-display font-bold text-gray-900 dark:text-white">
          Professional Summary
        </h2>
        <button
          v-if="!editingSummary"
          @click="editingSummary = true"
          class="text-emerald-400 hover:text-emerald-300 text-sm font-medium flex items-center"
        >
          <Edit :size="16" class="mr-1" />
          Edit
        </button>
      </div>

      <div v-if="editingSummary" class="space-y-4">
        <textarea
          v-model="summaryForm"
          rows="6"
          class="input-field"
          placeholder="Write a brief professional summary about yourself..."
        ></textarea>

        <div class="flex space-x-3">
          <button @click="saveSummary" class="btn-primary">
            Save Changes
          </button>
          <button @click="cancelSummary" class="btn-secondary">
            Cancel
          </button>
        </div>
      </div>

      <div v-else>
        <p v-if="profile.summary" class="text-gray-900 dark:text-white whitespace-pre-wrap">
          {{ profile.summary }}
        </p>
        <p v-else class="text-gray-600 dark:text-gray-500">No summary added yet</p>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Edit, X, Plus, Trash2 } from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'
import { api } from '~/utils/api'

definePageMeta({
  layout: 'app'
})

const authStore = useAuthStore()

const editingPersonal = ref(false)
const editingSkills = ref(false)
const editingSummary = ref(false)
const editingExpIndex = ref<number | null>(null)
const editingEduIndex = ref<number | null>(null)
const editingCertIndex = ref<number | null>(null)
const loading = ref(true)

const profile = ref({
  email: authStore.user?.email || '',
  full_name: '',
  phone: '',
  location: '',
  linkedin_url: '',
  github_url: '',
  portfolio_url: '',
  current_title: '',
  skills: [] as string[],
  summary: '',
  years_of_experience: 0,
  work_experience: [] as any[],
  education: [] as any[],
  certifications: [] as any[]
})

const personalForm = ref({ ...profile.value })
const skillsForm = ref<string[]>([])
const summaryForm = ref('')
const newSkill = ref('')
const experienceForm = ref({
  title: '',
  company: '',
  start_date: '',
  end_date: '',
  location: '',
  bullets: ['']
})
const educationForm = ref({
  degree: '',
  field: '',
  institution: '',
  graduation_year: '',
  gpa: null as number | null
})
const certificationForm = ref({
  name: '',
  issuer: '',
  issue_date: '',
  expiry_date: '',
  credential_id: ''
})

// Fetch profile data
const fetchProfile = async () => {
  try {
    loading.value = true
    const response = await api.get<any>('/profile')

    // Update profile from response
    if (response.profile) {
      profile.value = {
        email: response.email,
        full_name: response.profile.full_name || '',
        phone: response.profile.phone || '',
        location: response.profile.location || '',
        linkedin_url: response.profile.linkedin_url || '',
        github_url: response.profile.github_url || '',
        portfolio_url: response.profile.portfolio_url || '',
        current_title: response.profile.current_title || '',
        skills: response.profile.skills || [],
        summary: response.profile.summary || '',
        years_of_experience: response.profile.years_of_experience || 0,
        work_experience: response.profile.work_experience || [],
        education: response.profile.education || [],
        certifications: response.profile.certifications || []
      }

      // Initialize forms
      personalForm.value = { ...profile.value }
      skillsForm.value = [...profile.value.skills]
      summaryForm.value = profile.value.summary
    }
  } catch (error) {
    console.error('Failed to fetch profile:', error)
  } finally {
    loading.value = false
  }
}

const savePersonal = async () => {
  try {
    await api.put('/profile', {
      full_name: personalForm.value.full_name,
      phone: personalForm.value.phone,
      location: personalForm.value.location,
      linkedin_url: personalForm.value.linkedin_url,
      github_url: personalForm.value.github_url,
      portfolio_url: personalForm.value.portfolio_url,
      current_title: personalForm.value.current_title,
      years_of_experience: personalForm.value.years_of_experience
    })

    profile.value = { ...personalForm.value }
    editingPersonal.value = false
  } catch (error: any) {
    console.error('Failed to save personal info:', error)
    alert(error.message || 'Failed to save personal information')
  }
}

const cancelPersonal = () => {
  personalForm.value = { ...profile.value }
  editingPersonal.value = false
}

const addSkill = () => {
  if (newSkill.value.trim() && !skillsForm.value.includes(newSkill.value.trim())) {
    skillsForm.value.push(newSkill.value.trim())
    newSkill.value = ''
  }
}

const removeSkill = (index: number) => {
  skillsForm.value.splice(index, 1)
}

const saveSkills = async () => {
  try {
    await api.put('/profile', {
      skills: skillsForm.value
    })

    profile.value.skills = [...skillsForm.value]
    editingSkills.value = false
  } catch (error: any) {
    console.error('Failed to save skills:', error)
    alert(error.message || 'Failed to save skills')
  }
}

const cancelSkills = () => {
  skillsForm.value = [...profile.value.skills]
  editingSkills.value = false
}

const saveSummary = async () => {
  try {
    await api.put('/profile', {
      summary: summaryForm.value
    })

    profile.value.summary = summaryForm.value
    editingSummary.value = false
  } catch (error: any) {
    console.error('Failed to save summary:', error)
    alert(error.message || 'Failed to save summary')
  }
}

const cancelSummary = () => {
  summaryForm.value = profile.value.summary
  editingSummary.value = false
}

// Work Experience Functions
const addExperience = () => {
  experienceForm.value = {
    title: '',
    company: '',
    start_date: '',
    end_date: '',
    location: '',
    bullets: ['']
  }
  editingExpIndex.value = -1 // -1 means adding new
}

const editExperience = (index: number) => {
  const exp = profile.value.work_experience[index]
  experienceForm.value = {
    title: exp.title,
    company: exp.company,
    start_date: exp.start_date,
    end_date: exp.end_date || '',
    location: exp.location || '',
    bullets: exp.bullets && exp.bullets.length > 0 ? [...exp.bullets] : ['']
  }
  editingExpIndex.value = index
}

const addBullet = () => {
  experienceForm.value.bullets.push('')
}

const removeBullet = (index: number) => {
  experienceForm.value.bullets.splice(index, 1)
}

const saveExperience = async () => {
  try {
    // Filter out empty bullets
    const cleanedBullets = experienceForm.value.bullets.filter(b => b.trim() !== '')

    const expData = {
      title: experienceForm.value.title,
      company: experienceForm.value.company,
      start_date: experienceForm.value.start_date,
      end_date: experienceForm.value.end_date || null,
      location: experienceForm.value.location || null,
      bullets: cleanedBullets
    }

    let updatedExperiences = [...profile.value.work_experience]

    if (editingExpIndex.value === -1) {
      // Adding new
      updatedExperiences.push(expData)
    } else if (editingExpIndex.value !== null) {
      // Editing existing
      updatedExperiences[editingExpIndex.value] = expData
    }

    // Save to backend
    await api.put('/profile', {
      work_experience: updatedExperiences
    })

    profile.value.work_experience = updatedExperiences
    editingExpIndex.value = null
  } catch (error: any) {
    console.error('Failed to save experience:', error)
    alert(error.message || 'Failed to save experience')
  }
}

const cancelEditExperience = () => {
  editingExpIndex.value = null
}

const deleteExperience = async (index: number) => {
  if (!confirm('Are you sure you want to delete this experience?')) return

  try {
    const updatedExperiences = profile.value.work_experience.filter((_, i) => i !== index)

    await api.put('/profile', {
      work_experience: updatedExperiences
    })

    profile.value.work_experience = updatedExperiences
  } catch (error: any) {
    console.error('Failed to delete experience:', error)
    alert(error.message || 'Failed to delete experience')
  }
}

// Education Functions
const addEducation = () => {
  educationForm.value = {
    degree: '',
    field: '',
    institution: '',
    graduation_year: '',
    gpa: null
  }
  editingEduIndex.value = -1 // -1 means adding new
}

const editEducation = (index: number) => {
  const edu = profile.value.education[index]
  educationForm.value = {
    degree: edu.degree,
    field: edu.field || '',
    institution: edu.institution,
    graduation_year: edu.graduation_year || '',
    gpa: edu.gpa ? parseFloat(edu.gpa) : null
  }
  editingEduIndex.value = index
}

const saveEducation = async () => {
  try {
    const eduData = {
      degree: educationForm.value.degree,
      field: educationForm.value.field || null,
      institution: educationForm.value.institution,
      graduation_year: educationForm.value.graduation_year || null,
      gpa: educationForm.value.gpa ? parseFloat(educationForm.value.gpa) : null
    }

    let updatedEducation = [...profile.value.education]

    if (editingEduIndex.value === -1) {
      // Adding new
      updatedEducation.push(eduData)
    } else if (editingEduIndex.value !== null) {
      // Editing existing
      updatedEducation[editingEduIndex.value] = eduData
    }

    // Save to backend
    await api.put('/profile', {
      education: updatedEducation
    })

    profile.value.education = updatedEducation
    editingEduIndex.value = null
  } catch (error: any) {
    console.error('Failed to save education:', error)
    alert(error.message || 'Failed to save education')
  }
}

const cancelEditEducation = () => {
  editingEduIndex.value = null
}

const deleteEducation = async (index: number) => {
  if (!confirm('Are you sure you want to delete this education?')) return

  try {
    const updatedEducation = profile.value.education.filter((_, i) => i !== index)

    await api.put('/profile', {
      education: updatedEducation
    })

    profile.value.education = updatedEducation
  } catch (error: any) {
    console.error('Failed to delete education:', error)
    alert(error.message || 'Failed to delete education')
  }
}

// Certification Functions
const addCertification = () => {
  certificationForm.value = {
    name: '',
    issuer: '',
    issue_date: '',
    expiry_date: '',
    credential_id: ''
  }
  editingCertIndex.value = -1 // -1 means adding new
}

const editCertification = (index: number) => {
  const cert = profile.value.certifications[index]
  certificationForm.value = {
    name: cert.name,
    issuer: cert.issuer,
    issue_date: cert.issue_date || '',
    expiry_date: cert.expiry_date || '',
    credential_id: cert.credential_id || ''
  }
  editingCertIndex.value = index
}

const saveCertification = async () => {
  try {
    const certData = {
      name: certificationForm.value.name,
      issuer: certificationForm.value.issuer,
      issue_date: certificationForm.value.issue_date || null,
      expiry_date: certificationForm.value.expiry_date || null,
      credential_id: certificationForm.value.credential_id || null
    }

    let updatedCertifications = [...profile.value.certifications]

    if (editingCertIndex.value === -1) {
      // Adding new
      updatedCertifications.push(certData)
    } else if (editingCertIndex.value !== null) {
      // Editing existing
      updatedCertifications[editingCertIndex.value] = certData
    }

    // Save to backend
    await api.put('/profile', {
      certifications: updatedCertifications
    })

    profile.value.certifications = updatedCertifications
    editingCertIndex.value = null
  } catch (error: any) {
    console.error('Failed to save certification:', error)
    alert(error.message || 'Failed to save certification')
  }
}

const cancelEditCertification = () => {
  editingCertIndex.value = null
}

const deleteCertification = async (index: number) => {
  if (!confirm('Are you sure you want to delete this certification?')) return

  try {
    const updatedCertifications = profile.value.certifications.filter((_, i) => i !== index)

    await api.put('/profile', {
      certifications: updatedCertifications
    })

    profile.value.certifications = updatedCertifications
  } catch (error: any) {
    console.error('Failed to delete certification:', error)
    alert(error.message || 'Failed to delete certification')
  }
}

// Fetch profile on mount
onMounted(async () => {
  await fetchProfile()
})
</script>
