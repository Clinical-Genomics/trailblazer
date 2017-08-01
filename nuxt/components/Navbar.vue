<template>
  <b-navbar sticky="sticky-top" toggleable>
    <b-nav-toggle target="nav_collapse"></b-nav-toggle>

    <nuxt-link class="navbar-brand" to="/">Trailblazer</nuxt-link>
    <b-collapse is-nav id="nav_collapse">
      <b-nav is-nav-bar>
        <b-nav-item v-if="isAuthenticated" to="/dashboard">Dashboard</b-nav-item>
        <b-nav-item v-if="isAuthenticated" to="/stats">Stats</b-nav-item>
        <g-signin-button v-if="showSignin" class="btn btn-link" :params="googleSignInParams" @success="onSignInSuccess" @error="onSignInError">
          Sign in with Google
        </g-signin-button>
        <div v-else class="btn btn-link" @click="onSignOff">Sign out</div>
      </b-nav>

      <slot></slot>
    </b-collapse>
  </b-navbar>
</template>

<script>
  import { mapGetters } from 'vuex'
  import { setToken, unsetToken } from '~/utils/auth'

  export default {
    data () {
      return {
        googleClientId: process.env.GOOGLE_OAUTH_CLIENT_ID
      }
    },
    computed: {
      ...mapGetters(['isAuthenticated']),
      googleSignInParams () {
        return {
          client_id: this.googleClientId
        }
      },
      showSignin () {
        return (this.googleClientId && !this.isAuthenticated)
      }
    },
    methods: {
      onSignInSuccess (googleUser) {
        // `googleUser` is the GoogleUser object that represents the just-signed-in user.
        // See https://developers.google.com/identity/sign-in/web/reference#users
        const authRes = googleUser.getAuthResponse()
        // persist token to localStorage
        setToken(authRes.id_token)
        this.$router.replace({ path: 'dashboard' })
      },
      onSignInError (error) {
        // `error` contains any error occurred.
        console.log('OH NOES', error)
      },
      onSignOff () {
        this.$store.commit('SET_USER')
        unsetToken()
        this.$router.replace({ path: '/' })
      }
    }
  }
</script>

<style scoped>
  nav {
    padding: 1rem 2rem;
    background-color: #fff;
    border-bottom: 1px solid #eee;
    box-shadow: 0 2px 2px -2px rgba(0, 0, 0, .2);
  }
  .nav-item {
    color: #000;
  }
</style>
