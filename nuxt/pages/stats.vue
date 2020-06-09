<template>
  <div>
    <Navbar />

    <b-container class="mt-4">
      <h4 class="mb-3">Top failed job categories last 31 days</h4>

      <b-list-group>
        <b-list-group-item
          v-for="job in failedJobs"
          :key="job.id"
          class="d-flex justify-content-between align-items-center">
          <nuxt-link :to="{ name: '/analyses', params: { failedJob: job.name }}">
            {{ job.name }}
          </nuxt-link>
          <b-badge>{{ job.count }}</b-badge>
        </b-list-group-item>
      </b-list-group>
    </b-container>
  </div>
</template>

<script>
  import Navbar from '~/components/Navbar'
  import { mapGetters } from 'vuex'

  export default {
    middleware: ['authenticated'],
    async fetch ({ store, app }) {
      await store.dispatch('fetchJobStats')
    },
    computed: {
      ...mapGetters([
        'failedJobs'
      ])
    },
    components: {
      Navbar
    }
  }
</script>
