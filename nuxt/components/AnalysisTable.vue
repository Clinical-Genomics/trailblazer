<template>
  <div>
    <b-table hover responsive :items="analyses" :fields="fields">
      <template slot="family" scope="field">
        <nuxt-link :to="{ name: 'analyses-id', params: { id: field.item.id }}">
          {{ field.value }}
        </nuxt-link>
        <span v-if="field.item.priority === 'high'" class="badge badge-danger">prio</span>
      </template>
      <template slot="started_at" scope="field">
        {{ field.value | formatDate }}
      </template>
      <template slot="user" scope="field">
        <span v-if="field.value">{{ field.value.name }}</span>
      </template>
      <template slot="status" scope="field">
        <b-progress v-if="field.value === 'running'" :value="field.item.progress" :max="1" show-progress></b-progress>
        <b-popover v-else-if="field.value === 'failed'" triggers="hover" placement="right">
          <b-btn variant="danger" size="sm">{{ field.value }}</b-btn>
          <span slot="content">
            <div v-for="job in field.item.failed_jobs" v-if="job.status === 'failed'">
              {{ job.name }}
            </div>
          </span>
        </b-popover>
        <b-button-group v-else-if="field.value === 'completed'" >
          <b-button variant="success" size="sm">{{ field.value }}</b-button>
          <b-button size="sm">{{ field.item|dateDiff }}</b-button>
        </b-button-group>
        <b-btn variant="info" size="sm" v-else>{{ field.value }}</b-btn>
      </template>
      <template slot="comment" scope="field">
        <CommentBox @saved="saveComment" :message="field.value" :parentId="field.item.id" />
      </template>
    </b-table>

    <div v-if="analyses.length === 0" class="text-center mt-5">No matching analyses!</div>
  </div>
</template>

<script>
  import CommentBox from '~components/CommentBox'

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
      saveComment ({ parentId, text }) {
        this.$store.dispatch('updateComment', {
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
