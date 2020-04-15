<template>
  <b-navbar sticky toggleable>
    <b-nav-toggle target="nav_collapse"></b-nav-toggle>

    <nuxt-link class="navbar-brand" to="/">Trailblazer</nuxt-link>
    <b-collapse is-nav id="nav_collapse">
      <b-navbar-nav>
        <b-nav-item v-if="isAuthenticated" to="/dashboard">Dashboard</b-nav-item>
        <b-nav-item v-if="isAuthenticated" to="/analyses">Analyses</b-nav-item>
        <b-nav-item v-if="isAuthenticated" to="/stats">Stats</b-nav-item>
        <b-button v-if="showSignin" @click="onSignIn" variant="info">
          Sign in with Google
        </b-button>
        <b-button v-else variant="link" @click="onSignOut">Sign out</b-button>
      </b-navbar-nav>

      <slot></slot>
    </b-collapse>
  </b-navbar>
</template>

<script>
  import { mapGetters } from 'vuex'

  export default {
    computed: {
      ...mapGetters(['isAuthenticated']),
      showSignin () {
        return !this.isAuthenticated
      }
    },
    methods: {
      onSignIn () {
        this.$googleAuth().directAccess()
        this.$googleAuth().signIn(googleUser => {
          const idToken = googleUser.tc.id_token
          this.$store.dispatch('login', { token: idToken })
          this.$router.push('dashboard')
        }, error => {
          console.log(error.error)
        })
      },
      onSignOut () {
        this.$store.dispatch('logout')
        this.$router.push('/')
      }
    }
  }
</script>

<style>
  nav {
    background-color: #fff;
    border-bottom: 1px solid #eee;
    box-shadow: 0 2px 2px -2px rgba(0, 0, 0, .2);
  }
  .navbar-light .navbar-brand,
  .navbar-light .navbar-brand:hover {
    font-weight: 500;
    color: hsla(339, 75%, 55%, 1);
  }
</style>
