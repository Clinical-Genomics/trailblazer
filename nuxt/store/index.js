import { timeSince } from '~/utils/misc'
import jwtDecode from 'jwt-decode'
import { setToken, unsetToken, getTokenFromCookie } from '~/utils/auth'

export const state = () => ({
  user: null,
  token: null,
  analyses: [],
  lastUpdate: null,
  analysis: null,
  jobStats: []
})

export const mutations = {
  SET_USER (state, { user, token }) {
    state.user = user || null
    state.token = token || null
  },
  UPDATE_ANALYSES (state, analyses) {
    state.analyses = analyses
  },
  UPDATE_COMMENT (state, { analysisId, text }) {
    state.analyses = state.analyses.map(analysis => {
      if (analysis.id === analysisId) {
        return {
          ...analysis,
          comment: text
        }
      } else {
        return analysis
      }
    })
  },
  SET_LAST_UPDATE (state, date) {
    state.lastUpdate = date
  },
  SET_ANALYSIS (state, analysis) {
    state.analysis = analysis
  },
  SET_JOB_STATS (state, jobStats) {
    state.jobStats = jobStats
  },
  DELETE_ANALYSIS (state, analysisId) {
    state.analyses = state.analyses.filter(analysis => analysis.id !== analysisId)
  },
  SHOW_ANALYSIS (state, analysisId) {
    state.analyses = state.analyses.map(analysis => {
      if (analysis.id === analysisId) {
        return { ...analysis, is_visible: true }
      } else {
        return analysis
      }
    })
  }
}

export const actions = {
  nuxtServerInit ({ dispatch }, { req }) {
    // If nuxt generate, pass this middleware
    if (!req) return
    const token = getTokenFromCookie(req)
    if (!token) return
    dispatch('login', { token })
  },
  login ({ commit }, { token }) {
    this.$axios.setToken(token, 'Bearer')
    setToken(token)
    try {
      const user = jwtDecode(token)
      commit('SET_USER', { user, token })
    } catch (error) {
      console.log(error)
    }
  },
  logout ({ commit }) {
    this.$axios.setToken(false)
    unsetToken()
    commit('SET_USER', {})
  },
  async setLastUpdate ({ commit }) {
    try {
      let data = await this.$axios.$get('/info')
      commit('SET_LAST_UPDATE', data.updated_at)
    } catch (error) {
      // statements
      console.log(error)
    }
  },
  async updateComment ({ commit }, { analysisId, text }) {
    try {
      let data = await this.$axios.$put(`/analyses/${analysisId}`, { comment: text })
      commit('UPDATE_COMMENT', {
        analysisId: data.id,
        text: data.comment
      })
    } catch (error) {
      console.log(error)
    }
  },
  async fetchAnalyses ({ commit }, { query, isVisible, perPage }) {
    const params = { is_visible: isVisible, query, per_page: perPage || 200 }
    try {
      let data = await this.$axios.$get('/analyses', { params })
      commit('UPDATE_ANALYSES', data.analyses)
    } catch (error) {
      console.log(error)
    }
  },
  async fetchAnalysis ({ commit }, { analysisId }) {
    try {
      let data = await this.$axios.$get(`/analyses/${analysisId}`)
      commit('SET_ANALYSIS', data)
    } catch (error) {
      console.log(error)
    }
  },
  async fetchJobStats ({ commit }) {
    try {
      let data = await this.$axios.$get('/aggregate/jobs')
      commit('SET_JOB_STATS', data.jobs)
    } catch (error) {
      // statements
      console.log(error)
    }
  },
  async hideAnalysis ({ commit }, { analysisId }) {
    await this.$axios.$put(`/analyses/${analysisId}`, { is_visible: false })
    commit('DELETE_ANALYSIS', analysisId)
  },
  async unHideAnalysis ({ commit }, { analysisId }) {
    await this.$axios.$put(`/analyses/${analysisId}`, { is_visible: true })
    commit('SHOW_ANALYSIS', analysisId)
  }
}

export const getters = {
  lastUpdate (state) {
    if (!state.lastUpdate) return null
    const date = new Date(Date.parse(state.lastUpdate))
    return timeSince(date)
  },
  allAnalyses (state) {
    return state.analyses
  },
  failedAnalyses (state) {
    return state.analyses.filter(analysis => analysis.status === 'failed')
  },
  runningAnalyses (state) {
    return state.analyses.filter(analysis => analysis.status === 'running')
  },
  completedAnalyses (state) {
    return state.analyses.filter(analysis => analysis.status === 'completed')
  },
  isAuthenticated (state) {
    return !!state.user
  },
  loggedUser (state) {
    return state.user
  },
  selectedAnalysis (state) {
    return state.analysis
  },
  failedJobs (state) {
    return state.jobStats.concat().sort((jobA, jobB) => jobB.count - jobA.count)
  },
  loggedToken (state) {
    return state.token
  }
}
