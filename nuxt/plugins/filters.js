import Vue from 'vue'

Vue.filter('formatDate', (string) => {
  if (!string) return ''
  const dateObj = new Date(Date.parse(string))
  return dateObj.toLocaleDateString()
})

Vue.filter('dateDiff', (item) => {
  const diffSeconds = Date.parse(item.completed_at) - Date.parse(item.started_at)
  return `${Math.floor(diffSeconds / 1000 / 60 / 60)}h`
})
