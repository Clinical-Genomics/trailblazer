const https = require('https')
const fs = require('fs')
const { Nuxt } = require('nuxt')

if (process.env.NODE_ENV !== 'production') {
  console.log("You need to set 'NODE_ENV=production' to start the server")
  process.exit(1)
}

const port = process.env.PORT || 3000
const host = process.env.HOST || 'localhost'
const sslKeyPath = process.env.SSL_KEY || '/tmp/myserver.key'
const sslCertPath = process.env.SSL_CERT || '/tmp/server.crt'

// Based on: https://github.com/nuxt/nuxt.js/issues/146

// Nuxt.js setup
let config = require('./nuxt.config.js')
const nuxt = new Nuxt(config)

// HTTPS Server
const options = {
  key: fs.readFileSync(sslKeyPath),
  cert: fs.readFileSync(sslCertPath)
}

// Create the server
https
  .createServer(options, nuxt.render)
  .listen(port, host)

console.log(`Server listening on https://${host}:${port}`)
