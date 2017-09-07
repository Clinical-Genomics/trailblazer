import { timeSince } from '~/utils/misc'

export const state = () => ({
  user: null,
  token: null,
  analyses: [],
  lastUpdate: null,
  analysis: null,
  jobStats: []
})

export const mutations = {
  SET_USER (state, user, token) {
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
  }
}

export const actions = {
  async setLastUpdate ({ commit }, { $axios }) {
    try {
      let { data } = await $axios('/info')
      commit('SET_LAST_UPDATE', data.updated_at)
    } catch (error) {
      // statements
      console.log(error)
    }
  },
  async updateComment ({ commit }, { $axios, analysisId, text }) {
    try {
      let { data } = await $axios.put(`/analyses/${analysisId}`, { comment: text })
      commit('UPDATE_COMMENT', {
        analysisId: data.id,
        text: data.comment
      })
    } catch (error) {
      console.log(error)
    }
  },
  async fetchAnalyses ({ commit }, { $axios, query }) {
    let url = (query) ? `/analyses?query=${query}` : '/analyses'
    try {
      let { data } = await $axios(url)
      commit('UPDATE_ANALYSES', data.analyses)
    } catch (error) {
      console.log(error)
    }
  },
  async fetchAnalysis ({ commit }, { $axios, analysisId }) {
    try {
      let { data } = await $axios(`/analyses/${analysisId}`)
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
  }
}

export const getters = {
  lastUpdate (state) {
    if (!state.lastUpdate) return null
    const lastUpdate = new Date(Date.parse(state.lastUpdate))
    return timeSince(lastUpdate)
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
