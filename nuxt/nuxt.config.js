module.exports = {
  /*
  ** Router config
  */
  router: {
    middleware: 'check-auth',
    base: process.env.ROUTER_BASE || '/'
  },
  /*
  ** Headers of the page
  */
  head: {
    title: 'Trailblazer',
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: 'Nuxt.js project' }
    ],
    link: [
      { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
    ]
  },
  /*
  ** Customize the progress-bar color
  */
  loading: { color: '#3B8070' },
  css: [ '~static/main.css' ],
  modules: [
    [ '@nuxtjs/axios', { redirectError: { 403: '/' } } ],
    'bootstrap-vue/nuxt'
  ],
  env: { GOOGLE_OAUTH_CLIENT_ID: process.env.GOOGLE_OAUTH_CLIENT_ID },
  /*
  ** Build configuration
  */
  build: {
    /*
    ** Run ESLINT on save
    */
    extend (config, { isClient }) {
      if (isClient) {
        config.module.rules.push({
          enforce: 'pre',
          test: /\.(js|vue)$/,
          loader: 'eslint-loader',
          exclude: /(node_modules)/
        })
      }
    },
    vendor: [ 'vue-google-auth' ]
  },
  plugins: [
    '~/plugins/vue-click-outside.js',
    { src: '~/plugins/vue-google-auth.js', ssr: false },
    '~/plugins/filters.js',
    '~/plugins/auth.js'
  ]
}
