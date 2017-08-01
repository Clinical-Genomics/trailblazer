<template>
  <div>
    <Navbar>
      <slot>
        <b-nav is-nav-bar class="ml-auto">
          <b-nav-item v-for="tab in analysisTabs" key="tab.category" :active="tab.category === selectedCategory" @click="setCategory(tab.category)">
            {{ tab.title }}
          </b-nav-item>
        </b-nav>

        <form class="form-inline ml-3" @submit.prevent="queryAnalyses">
          <input v-model="query" type="text" class="form-control" placeholder="search family, status">
        </form>
      </slot>
    </Navbar>

    <AnalysisTable :analyses="selectedAnalyses" />

    <footer class="sticky-footer w-100 d-flex justify-content-between">
      <span v-if="loggedUser">Welcome <strong>{{ loggedUser.name }}</strong></span>
      <span v-if="lastUpdate">Updated {{ lastUpdate }} ago</span>
    </footer>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex'
  import Navbar from '~components/Navbar'
  import AnalysisTable from '~components/AnalysisTable'

  export default {
    middleware: ['authenticated'],
    data () {
      return {
        query: '',
        currentTabIndex: 0,
        analysisTabs: [{
          category: 'allAnalyses',
          title: 'All'
        }, {
          category: 'failedAnalyses',
          title: 'Failed'
        }, {
          category: 'runningAnalyses',
          title: 'Running'
        }, {
          category: 'completedAnalyses',
          title: 'Completed'
        }],
        selectedCategory: 'allAnalyses'
      }
    },
    async fetch ({ store, app }) {
      await Promise.all([
        store.dispatch('fetchAnalyses', { $axios: app.$axios }),
        store.dispatch('setLastUpdate', { $axios: app.$axios })
      ])
    },
    computed: {
      currentTabId () {
        for (let tab of this.analysisTabs) {
          if (tab.index === this.currentTabIndex) {
            return tab.id
          }
        }
      },
      ...mapGetters([
        'allAnalyses',
        'failedAnalyses',
        'runningAnalyses',
        'completedAnalyses',
        'lastUpdate',
        'isAuthenticated',
        'loggedUser'
      ]),
      selectedAnalyses () {
        return this[this.selectedCategory]
      }
    },
    methods: {
      queryAnalyses () {
        this.$store.dispatch('fetchAnalyses', { $axios: this.$axios, query: this.query })
      },
      setCategory (analysisCategory) {
        this.selectedCategory = analysisCategory
      }
    },
    components: {
      AnalysisTable,
      Navbar
    }
  }
</script>

<style>
  .index-tabs ul {
    display: none;
  }

  .sticky-footer {
    position: fixed;
    bottom: 0;
    display: flex;
    justify-content: center;
    padding: 1rem;

    background-color: #fff;
    border-bottom: 1px solid #eee;
    box-shadow: 0 -2px 2px -1px rgba(0, 0, 0, .2);
  }
</style>
