<template>
  <div>
    <Navbar />
    <main class="container">
      <b-card class="mt-3" no-body>
        <b-card-body>
          <b-row>
            <b-col>
              <small class="text-muted">Family</small>
              <h5 class="card-title">
                {{ selectedAnalysis.family }}
                <b-badge v-if="selectedAnalysis.priority === 'high'"
                        variant="danger">
                  prio
                </b-badge>
              </h5>
            </b-col>
            <b-col>
              <small class="text-muted">Comment</small>
              <CommentBox @saved="saveComment"
                          :message="selectedAnalysis.comment"
                          :parentId="selectedAnalysis.id" />
            </b-col>
          </b-row>
        </b-card-body>
        <b-card-body>
          <b-row class="stats">
            <b-col cols="6" sm="4" class="stat">
              <small class="text-muted">Version</small>
              <h5>{{ selectedAnalysis.version }}</h5>
            </b-col>
            <b-col cols="6" sm="4" class="stat">
              <small class="text-muted">Started</small>
              <h5>{{ selectedAnalysis.started_at|formatDate }}</h5>
            </b-col>
            <b-col cols="6" sm="4" class="stat">
              <small class="text-muted">Analysis type</small>
              <h5>{{ selectedAnalysis.type }}</h5>
            </b-col>
            <b-col v-if="selectedAnalysis.completed_at" cols="6" sm="4" class="stat">
              <small class="text-muted">Runtime</small>
              <h5>{{ selectedAnalysis|dateDiff }}</h5>
            </b-col>
            <b-col cols="6" sm="4" class="stat">
              <small class="text-muted">Status</small>
              <h5>{{ selectedAnalysis.status }}</h5>
            </b-col>
            <b-col v-if="selectedAnalysis.user" cols="6" sm="4" class="stat">
              <small class="text-muted">User</small>
              <h5>{{ selectedAnalysis.user.name }}</h5>
            </b-col>
          </b-row>
        </b-card-body>
        <b-list-group v-if="selectedAnalysis.status == 'failed'" flush>
          <b-list-group-item v-for="job in selectedAnalysis.failed_jobs"
                             :key="job.id"
                             class="justify-content-between">
            {{ job.name }} ({{ job.context }}) - {{ job.elapsed / 60 }} min
            <b-badge pill>{{ job.status }}</b-badge>
          </b-list-group-item>
        </b-list-group>
        <b-card-body v-if="selectedAnalysis.status == 'running'">
          <small class="text-muted">Progress</small>
          <b-progress :value="selectedAnalysis.progress" :max="1" show-progress></b-progress>
        </b-card-body>
      </b-card>
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
      await store.dispatch('fetchAnalysis', { analysisId: params.id })
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
