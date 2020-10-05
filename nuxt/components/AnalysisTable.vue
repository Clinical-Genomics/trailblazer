<template>
  <div>
    <div class="table-reponsive">
        <b-table hover :items="analyses" :fields="fields">
        <template #cell(family)="data">
          <nuxt-link :to="{ name: 'analyses-id', params: { id: data.item.id }}">
            {{ data.value }}
          </nuxt-link>
          <span v-if="data.item.priority === 'high'" class="badge badge-info">prio</span>
        </template>
        <template #cell(started_at)="data">
          {{ data.value | formatDate }}
        </template>
        <template #cell(user)="data">
          <span v-if="data.value">{{ data.value.name }}</span>
        </template>
        <template #cell(status)="data">
          <b-progress v-if="data.value === 'running'"
                      :value="data.item.progress"
                      :max="1"
                      show-progress />
          <b-button-group v-else>
            <b-button
              v-if="data.value === 'failed'"
              :id="`failed-button-${data.item.id}`"
              variant="danger"
              size="sm">
              {{ data.value }}
            </b-button>
            <b-popover
              v-if="data.value === 'failed'"
              :target="`failed-button-${data.item.id}`"
              triggers="hover"
              placement="left">
              <div
                v-for="job in data.item.failed_jobs"
                :key="job.id"
                v-if="job.status === 'failed'">
                {{ job.name }}
              </div>
            </b-popover>
            <b-button-group v-else-if="data.value === 'completed'">
              <b-button variant="success" size="sm">{{ data.value }}</b-button>
              <b-button size="sm">{{ data.item|dateDiff }}</b-button>
            </b-button-group>
            <b-btn variant="info" size="sm" v-else>{{ data.value }}</b-btn>
            <b-btn
              v-if="data.item.is_visible"
              variant="warning"
              size="sm"
              @click="hideAnalysis({ analysisId: data.item.id })">
              Hide
            </b-btn>
            <b-btn
              v-else
              variant="info"
              size="sm"
              @click="unHideAnalysis({ analysisId: data.item.id })">
              Unhide
            </b-btn>
          </b-button-group>
        </template>
        <template #cell(comment)="data">
          <div class="comment-box">
            <CommentBox @saved="saveComment" :message="data.value" :parentId="data.item.id" />
          </div>
        </template>
      </b-table>
    </div>

    <div v-if="analyses.length === 0" class="text-center mt-5">No matching analyses!</div>
  </div>
</template>

<script>
  import { mapActions } from 'vuex'
  import CommentBox from '~/components/CommentBox'

  export default {
    props: ['analyses'],
    data () {
      return {
        fields:
          [
          { key: 'family', label: 'Family', sortable: true },
          { key: 'started_at', label: 'Started' },
          { key: 'version', label: 'Version' },
          { key: 'type', label: 'Type' },
          { key: 'user', label: 'User' },
          { key: 'status', label: 'Status', sortable: true },
          { key: 'comment', label: 'Comment' }
        ]
      }
    },
    methods: {
      ...mapActions([ 'hideAnalysis', 'unHideAnalysis' ]),
      async saveComment ({ parentId, text }) {
        await this.$store.dispatch('updateComment', {
          analysisId: parentId,
          text: text
        })
      }
    },
    components: {
      CommentBox
    }
  }
</script>

<style>
  .comment-box {
    max-width: 350px;
  }
</style>

