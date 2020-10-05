export default ({ store, app: { $axios }, isClient }) => {
  $axios.setToken(store.getters.userToken)

  if (isClient) {
    setInterval(() => {
      window.gapi.auth2.getAuthInstance().currentUser.get().reloadAuthResponse().then((authRes) => {
        store.dispatch('login', { token: authRes.id_token })
      })
    }, 3600000)
  }
}
