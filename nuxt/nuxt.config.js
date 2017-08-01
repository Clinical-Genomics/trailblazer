module.exports = {
  /*
  ** Router config
  */
  router: {
    middleware: 'check-auth'
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
    ],
    script: [
      { type: 'text/javascript', src: 'https://apis.google.com/js/api:client.js' }
    ]
  },
  /*
  ** Customize the progress-bar color
  */
  loading: { color: '#3B8070' },
  css: [ '~static/main.css' ],
  modules: [
    '@nuxtjs/proxy',
    '@nuxtjs/axios'
  ],
  proxy: [
    ['/api', { target: process.env.BASE_URL, pathRewrite: { '^/api': '/api/v1' } }]
  ],
  env: {
    GOOGLE_OAUTH_CLIENT_ID: process.env.GOOGLE_OAUTH_CLIENT_ID
  },
  /*
  ** Build configuration
  */
  build: {
    /*
    ** Run ESLINT on save
    */
    extend (config, ctx) {
      if (ctx.isClient) {
        config.module.rules.push({
          enforce: 'pre',
          test: /\.(js|vue)$/,
          loader: 'eslint-loader',
          exclude: /(node_modules)/
        })
      }
    },
    vendor: ['bootstrap-vue', 'vue-google-signin-button']
  },
  plugins: [
    '~plugins/bootstrap-vue.js',
    '~plugins/vue-click-outside.js',
    '~plugins/vue-google-signin-button.js',
    '~plugins/filters.js'
  ]
}
