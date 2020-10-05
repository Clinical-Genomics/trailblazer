import Vue from 'vue'
import GoogleAuth from 'vue-google-auth'

Vue.use(GoogleAuth, { client_id: process.env.GOOGLE_OAUTH_CLIENT_ID })
Vue.googleAuth().load()
