import { getTokenFromLocalStorage } from '~/utils/auth'

function checkAuth ({ store, app }) {
  if (process.server) return
  const token = getTokenFromLocalStorage()
  if (!token) return
  store.dispatch('login', { token })
}

export default checkAuth
