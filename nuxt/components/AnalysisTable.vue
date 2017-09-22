<template>
  <div>
    <b-table hover responsive :items="analyses" :fields="fields" class="w-100">
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
        <span v-else-if="field.value === 'failed'">
          <b-button :id="`failed-button-${field.item.id}`" variant="danger" size="sm">
            {{ field.value }}
          </b-button>
          <b-popover :target="`failed-button-${field.item.id}`" triggers="hover" placement="right">
            <div v-for="job in field.item.failed_jobs" :key="job.id" v-if="job.status === 'failed'">
              {{ job.name }}
            </div>
          </b-popover>
        </span>
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
