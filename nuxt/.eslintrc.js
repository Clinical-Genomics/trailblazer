module.exports = {
  root: true,
  parser: 'vue-eslint-parser',
  parserOptions: {
     parser: "babel-eslint",
      ecmaVersion: 2020,
      sourceType: "module"
  },
  env: {
    browser: true,
    node: true
  },
  extends: ['plugin:vue/recommended', 'plugin:vue/base',
  ],
  // required to lint *.vue files
  plugins: [
    'vue'
  ],
  // add your custom rules here
  rules: {
    'vue/require-valid-default-prop': 0,
    'vue/no-unused-vars': 0,
    'vue/return-in-computed-property': 0,
    'vue/no-unused-components': 0,
    'vue/no-use-v-if-with-v-for': 0
  },
  globals: {}
}
