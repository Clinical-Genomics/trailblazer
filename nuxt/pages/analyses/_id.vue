<template>
  <div>
    <Navbar />
    <main class="container">
      <div class="card mt-3">
        <div class="card-block">
          <div class="row">
            <div class="col-6">
              <small class="text-muted">Family</small>
              <h4 class="card-title">
                {{ selectedAnalysis.family }}
                <span v-if="selectedAnalysis.priority === 'high'" class="badge badge-danger">prio</span>
              </h4>
            </div>
            <div class="col-6">
              <small class="text-muted">Comment</small>
              <CommentBox @saved="saveComment" :message="selectedAnalysis.comment" :parentId="selectedAnalysis.id" />
            </div>
          </div>
        </div>
        <div class="card-block">
          <div class="row stats">
            <div class="col-4 col-sm-3 col-md-2 stat">
              <small class="text-muted">Version</small>
              <h5>{{ selectedAnalysis.version }}</h5>
            </div>
            <div class="col-4 col-sm-3 col-md-2 stat">
              <small class="text-muted">Started</small>
              <h5>{{ selectedAnalysis.started_at|formatDate }}</h5>
            </div>
            <div class="col-4 col-sm-3 col-md-2 stat">
              <small class="text-muted">Analysis type</small>
              <h5>{{ selectedAnalysis.type }}</h5>
            </div>
            <div v-if="selectedAnalysis.completed_at" class="col-4 col-sm-3 col-md-2 stat">
              <small class="text-muted">Runtime</small>
              <h5>{{ selectedAnalysis|dateDiff }}</h5>
            </div>
            <div class="col-4 col-sm-3 col-md-2 stat">
              <small class="text-muted">Status</small>
              <h5>{{ selectedAnalysis.status }}</h5>
            </div>
            <div v-if="selectedAnalysis.user" class="col-4 col-sm-3 col-md-2 stat">
              <small class="text-muted">User</small>
              <h5>{{ selectedAnalysis.user.name }}</h5>
            </div>
          </div>
        </div>
        <ul v-if="selectedAnalysis.status == 'failed'" class="list-group list-group-flush">
          <li v-for="job in selectedAnalysis.failed_jobs" class="list-group-item justify-content-between">
            {{ job.name }} ({{ job.context }}) - {{ job.elapsed }}s
            <span class="badge badge-default badge-pill">{{ job.status }}</span>
          </li>
        </ul>
        <div v-if="selectedAnalysis.status == 'running'" class="card-block">
          <small class="text-muted">Progress</small>
          <b-progress :value="selectedAnalysis.progress" :max="1" show-progress></b-progress>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex'
  import Navbar from '~/components/Navbar'
  import AnalysisTable from '~/components/AnalysisTable'
  import CommentBox from '~/components/CommentBox'

  export default {
    async fetch ({ store, params, app }) {
      await store.dispatch('fetchAnalysis', { $axios: app.$axios, analysisId: params.id })
    },
    computed: {
      ...mapGetters(['selectedAnalysis'])
    },
    methods: {
      saveComment ({ parentId, text }) {
        this.$store.dispatch('updateComment', {
          analysisId: parentId,
          text: text
        })
      }
    },
    components: {
      AnalysisTable,
      Navbar,
      CommentBox
    }
  }
</script>

<style scoped>

</style>
