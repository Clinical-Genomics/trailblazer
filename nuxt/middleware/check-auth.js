import { getUserFromCookie, getUserFromLocalStorage } from '~/utils/auth'

export default function ({ isServer, store, req, app }) {
   // If nuxt generate, pass this middleware
  if (isServer && !req) return
  const data = isServer ? getUserFromCookie(req) : getUserFromLocalStorage()
  if (!data) return
  store.commit('SET_USER', data.loggedUser, data.token)
  // set token for all axios requests
  app.$axios.setToken(data.token, 'Bearer')
}
