<template>
  <div>
    <Navbar />

    <section class="section">
      <h4>Top failed job categories</h4>

      <div class="list-horizontal">
        <div v-for="job in failedJobs" :key="job.id" class="card mr-3">
          <div class="card-block text-center">
            <small class="text-muted">{{ job.name }}</small>
            <h1>{{ job.count }}</h1>
          </div>
        </div>
      </div>
    </section>
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

<style scoped>
  .section {
    padding: 2rem;
  }

  .list-horizontal {
    display: flex;
    flex-wrap: nowrap;
    overflow-x: auto;
    padding: 1rem 0;
  }
</style>
