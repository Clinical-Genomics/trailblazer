<template>
  <div>
    <div class="table-reponsive">
        <b-table hover :items="analyses" :fields="fields">
        <template slot="family" scope="field">
          <nuxt-link :to="{ name: 'analyses-id', params: { id: field.item.id }}">
            {{ field.value }}
          </nuxt-link>
          <span v-if="field.item.priority === 'high'" class="badge badge-info">prio</span>
        </template>
        <template slot="started_at" scope="field">
          {{ field.value | formatDate }}
        </template>
        <template slot="user" scope="field">
          <span v-if="field.value">{{ field.value.name }}</span>
        </template>
        <template slot="status" scope="field">
          <b-progress v-if="field.value === 'running'"
                      :value="field.item.progress"
                      :max="1"
                      show-progress />
          <b-button-group v-else>
            <b-button
              v-if="field.value === 'failed'"
              :id="`failed-button-${field.item.id}`"
              variant="danger"
              size="sm">
              {{ field.value }}
            </b-button>
            <b-popover
              v-if="field.value === 'failed'"
              :target="`failed-button-${field.item.id}`"
              triggers="hover"
              placement="left">
              <div
                v-for="job in field.item.failed_jobs"
                :key="job.id"
                v-if="job.status === 'failed'">
                {{ job.name }}
              </div>
            </b-popover>
            <b-button-group v-else-if="field.value === 'completed'">
              <b-button variant="success" size="sm">{{ field.value }}</b-button>
              <b-button size="sm">{{ field.item|dateDiff }}</b-button>
            </b-button-group>
            <b-btn variant="info" size="sm" v-else>{{ field.value }}</b-btn>
            <b-btn
              v-if="field.item.is_visible"
              variant="warning"
              size="sm"
              @click="hideAnalysis({ analysisId: field.item.id })">
              Hide
            </b-btn>
            <b-btn
              v-else
              variant="info"
              size="sm"
              @click="unHideAnalysis({ analysisId: field.item.id })">
              Unhide
            </b-btn>
          </b-button-group>
        </template>
        <template slot="comment" scope="field">
          <div class="comment-box">
            <CommentBox @saved="saveComment" :message="field.value" :parentId="field.item.id" />
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
        fields: {
          family: {
            label: 'Family',
            sortable: true
          },
          started_at: {
            label: 'Started'
          },
          version: {
            label: 'Version'
          },
          type: {
            label: 'Type'
          },
          user: {
            label: 'User'
          },
          status: {
            label: 'Status',
            sortable: true
          },
          comment: {
            label: 'Comment'
          }
        }
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

