import { getTokenFromLocalStorage } from '~/utils/auth'

function checkAuth ({ isServer, store, app }) {
  if (isServer) return
  const token = getTokenFromLocalStorage()
  if (!token) return
  store.dispatch('login', { token })
}

export default checkAuth
