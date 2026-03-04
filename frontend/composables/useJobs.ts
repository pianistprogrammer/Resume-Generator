import { useAuthStore } from '~/stores/auth'
import { api } from '~/utils/api'

interface JobFilters {
  skip?: number
  limit?: number
  company?: string
  remote?: boolean
  search?: string
  status_filter?: string
  min_score?: number
}

export const useJobs = () => {
  // Fetch user matches
  const fetchMatches = async (filters: JobFilters = {}) => {
    const queryParams = new URLSearchParams()

    if (filters.skip) queryParams.append('skip', filters.skip.toString())
    if (filters.limit) queryParams.append('limit', filters.limit.toString())
    if (filters.status_filter) queryParams.append('status_filter', filters.status_filter)
    if (filters.min_score) queryParams.append('min_score', filters.min_score.toString())

    return await api.get<any>(`/jobs/my/matches?${queryParams.toString()}`)
  }

  // Get single match
  const getMatch = async (matchId: string) => {
    return await api.get<any>(`/jobs/my/matches/${matchId}`)
  }

  // Update match status
  const updateMatchStatus = async (matchId: string, status: string) => {
    return await api.patch<any>(`/jobs/my/matches/${matchId}/status`, { status })
  }

  // Get dashboard stats
  const getDashboardStats = async () => {
    return await api.get<any>(`/jobs/my/dashboard/stats`)
  }

  // Ingest URL
  const ingestUrl = async (url: string) => {
    return await api.post<any>(`/jobs/ingest-url`, { url })
  }

  // Generate resume
  const generateResume = async (matchId: string) => {
    return await api.post<any>(`/resumes/generate/${matchId}`)
  }

  // Get resume
  const getResume = async (resumeId: string) => {
    return await api.get<any>(`/resumes/${resumeId}`)
  }

  // Get resume by match
  const getResumeByMatch = async (matchId: string) => {
    return await api.get<any>(`/resumes/match/${matchId}`)
  }

  // Helpers
  const scoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-400'
    if (score >= 60) return 'text-amber-400'
    return 'text-red-400'
  }

  const scoreRingColor = (score: number) => {
    if (score >= 80) return '#10b981'
    if (score >= 60) return '#f59e0b'
    return '#ef4444'
  }

  const timeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)

    if (seconds < 60) return 'just now'
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`
    return `${Math.floor(seconds / 604800)}w ago`
  }

  const formatSalary = (min: number | null, max: number | null) => {
    if (!min && !max) return 'Not specified'

    const format = (n: number) => {
      if (n >= 1000) return `$${Math.floor(n / 1000)}k`
      return `$${n}`
    }

    if (min && max) return `${format(min)} - ${format(max)}`
    if (min) return `${format(min)}+`
    if (max) return `Up to ${format(max)}`
  }

  return {
    fetchMatches,
    getMatch,
    updateMatchStatus,
    getDashboardStats,
    ingestUrl,
    generateResume,
    getResume,
    getResumeById: getResume, // Alias
    getResumeByMatch,
    scoreColor,
    scoreRingColor,
    timeAgo,
    formatSalary
  }
}
