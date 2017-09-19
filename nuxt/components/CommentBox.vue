<template>
  <div>
    <form v-if="isEditing" @submit.prevent="onSubmit">
      <input v-click-outside="toggleEdit" type="text" v-model="text" class="form-control">
    </form>
    <span v-else @dblclick="toggleEdit">
      <span v-if="message">{{ message }}</span>
      <i v-else class="text-muted">Double-click</i>
    </span>
  </div>
</template>

<script>
  export default {
    props: ['parentId', 'message'],
    data () {
      return {
        text: '',
        isEditing: false
      }
    },
    methods: {
      onSubmit (event) {
        this.$emit('saved', {
          parentId: this.parentId,
          text: this.text
        })
        this.isEditing = false
      },
      toggleEdit () {
        console.log('toggling edit')
        if (!this.text) {
          this.text = this.message
        }
        this.isEditing = !this.isEditing
      }
    }
  }
</script>
