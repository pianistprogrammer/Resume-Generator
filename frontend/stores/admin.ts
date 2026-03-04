import { defineStore } from 'pinia'
import { api } from '~/utils/api'

interface AdminStats {
  total_users: number
  total_jobs: number
  total_matches: number
  total_resumes: number
  active_feeds: number
  new_users_week: number
  new_jobs_today: number
  new_resumes_week: number
}

interface User {
  id: string
  email: string
  full_name: string
  is_admin: boolean
  is_active: boolean
  credits: number
  onboarding_completed: boolean
  created_at: string
  last_login: string | null
}

interface FeedSource {
  id: string
  name: string
  url: string
  feed_type: string
  company_token: string | null
  is_active: boolean
  last_scraped_at: string | null
  last_scrape_success: boolean
  last_scrape_error: string | null
  total_jobs_scraped: number
  last_scrape_job_count: number
  created_at: string
}

interface Job {
  id: string
  title: string
  company: string
  location: string
  remote: boolean
  source: string
  ats_platform: string
  apply_url: string
  ingested_at: string
}

interface Resume {
  id: string
  user_email: string
  job_title: string
  job_company: string
  pdf_url: string
  ats_score: number
  created_at: string
}

export const useAdminStore = defineStore('admin', () => {
  const stats = ref<AdminStats | null>(null)
  const users = ref<User[]>([])
  const feeds = ref<FeedSource[]>([])
  const jobs = ref<Job[]>([])
  const resumes = ref<Resume[]>([])
  const loading = ref(false)

  // Dashboard
  const fetchDashboardStats = async () => {
    try {
      loading.value = true
      const response = await api.get<AdminStats>('/admin/dashboard')
      stats.value = response
    } catch (error) {
      console.error('Failed to fetch admin stats:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // Users
  const fetchUsers = async (params: { skip?: number; limit?: number; search?: string; is_admin?: boolean } = {}) => {
    try {
      loading.value = true
      const queryParams = new URLSearchParams()
      if (params.skip !== undefined) queryParams.append('skip', params.skip.toString())
      if (params.limit !== undefined) queryParams.append('limit', params.limit.toString())
      if (params.search) queryParams.append('search', params.search)
      if (params.is_admin !== undefined) queryParams.append('is_admin', params.is_admin.toString())

      const response = await api.get<{ users: User[] }>(`/admin/users?${queryParams.toString()}`)
      users.value = response.users
    } catch (error) {
      console.error('Failed to fetch users:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateUserCredits = async (userId: string, credits: number) => {
    try {
      await api.patch(`/admin/users/${userId}/credits`, { credits })
      await fetchUsers()
    } catch (error) {
      console.error('Failed to update user credits:', error)
      throw error
    }
  }

  const toggleUserAdmin = async (userId: string) => {
    try {
      await api.patch(`/admin/users/${userId}/toggle-admin`, {})
      await fetchUsers()
    } catch (error) {
      console.error('Failed to toggle user admin:', error)
      throw error
    }
  }

  const toggleUserActive = async (userId: string) => {
    try {
      await api.patch(`/admin/users/${userId}/toggle-active`, {})
      await fetchUsers()
    } catch (error) {
      console.error('Failed to toggle user active:', error)
      throw error
    }
  }

  // Feed Sources
  const fetchFeeds = async (includeInactive = false) => {
    try {
      loading.value = true
      const response = await api.get<{ feeds: FeedSource[] }>(`/admin/feeds?include_inactive=${includeInactive}`)
      feeds.value = response.feeds
    } catch (error) {
      console.error('Failed to fetch feeds:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createFeed = async (data: { name: string; url: string; feed_type: string; company_token?: string }) => {
    try {
      await api.post('/admin/feeds', data)
      await fetchFeeds()
    } catch (error) {
      console.error('Failed to create feed:', error)
      throw error
    }
  }

  const updateFeed = async (feedId: string, data: { name?: string; url?: string; feed_type?: string; company_token?: string }) => {
    try {
      await api.patch(`/admin/feeds/${feedId}`, data)
      await fetchFeeds()
    } catch (error) {
      console.error('Failed to update feed:', error)
      throw error
    }
  }

  const toggleFeed = async (feedId: string) => {
    try {
      await api.patch(`/admin/feeds/${feedId}/toggle`, {})
      await fetchFeeds()
    } catch (error) {
      console.error('Failed to toggle feed:', error)
      throw error
    }
  }

  const deleteFeed = async (feedId: string) => {
    try {
      await api.delete(`/admin/feeds/${feedId}`)
      await fetchFeeds()
    } catch (error) {
      console.error('Failed to delete feed:', error)
      throw error
    }
  }

  // Jobs
  const fetchJobs = async (params: { skip?: number; limit?: number; search?: string; source?: string } = {}) => {
    try {
      loading.value = true
      const queryParams = new URLSearchParams()
      if (params.skip !== undefined) queryParams.append('skip', params.skip.toString())
      if (params.limit !== undefined) queryParams.append('limit', params.limit.toString())
      if (params.search) queryParams.append('search', params.search)
      if (params.source) queryParams.append('source', params.source)

      const response = await api.get<{ jobs: Job[] }>(`/admin/jobs?${queryParams.toString()}`)
      jobs.value = response.jobs
    } catch (error) {
      console.error('Failed to fetch jobs:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const deleteJob = async (jobId: string) => {
    try {
      await api.delete(`/admin/jobs/${jobId}`)
      await fetchJobs()
    } catch (error) {
      console.error('Failed to delete job:', error)
      throw error
    }
  }

  // Resumes
  const fetchResumes = async (params: { skip?: number; limit?: number; user_id?: string } = {}) => {
    try {
      loading.value = true
      const queryParams = new URLSearchParams()
      if (params.skip !== undefined) queryParams.append('skip', params.skip.toString())
      if (params.limit !== undefined) queryParams.append('limit', params.limit.toString())
      if (params.user_id) queryParams.append('user_id', params.user_id)

      const response = await api.get<{ resumes: Resume[] }>(`/admin/resumes?${queryParams.toString()}`)
      resumes.value = response.resumes
    } catch (error) {
      console.error('Failed to fetch resumes:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    stats,
    users,
    feeds,
    jobs,
    resumes,
    loading,
    fetchDashboardStats,
    fetchUsers,
    updateUserCredits,
    toggleUserAdmin,
    toggleUserActive,
    fetchFeeds,
    createFeed,
    updateFeed,
    toggleFeed,
    deleteFeed,
    fetchJobs,
    deleteJob,
    fetchResumes,
  }
})
