import Cookie from 'js-cookie'

export const setToken = (token) => {
  if (process.server) return
  window.localStorage.setItem('token', token)
  Cookie.set('jwt', token)
}

export const unsetToken = () => {
  if (process.server) return
  window.localStorage.removeItem('token')
  Cookie.remove('jwt')
  window.localStorage.setItem('logout', Date.now())
}

export const getTokenFromCookie = (req) => {
  if (!req.headers.cookie) return
  const jwtCookie = req.headers.cookie.split(';').find(c => c.trim().startsWith('jwt='))
  if (!jwtCookie) return
  const jwt = jwtCookie.split('=')[1]
  return jwt
}

export const getTokenFromLocalStorage = () => {
  return window.localStorage.token
}
