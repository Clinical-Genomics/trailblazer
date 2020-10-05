<template>
  <div class="app-container">
    <Navbar>
      <slot>
        <b-navbar-nav class="ml-auto">
          <b-nav-item v-for="tab in analysisTabs"
                      :key="tab.category"
                      :active="tab.category === selectedCategory"
                      @click="setCategory(tab.category)">
            {{ tab.title }}
          </b-nav-item>
        </b-navbar-nav>
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
  import Navbar from '~/components/Navbar'
  import AnalysisTable from '~/components/AnalysisTable'

  export default {
    middleware: ['authenticated'],
    data () {
      return {
        currentTabIndex: 0,
        analysisTabs: [{
          category: 'runningAnalyses',
          title: 'Running'
        }, {
          category: 'failedAnalyses',
          title: 'Failed'
        }, {
          category: 'completedAnalyses',
          title: 'Completed'
        }],
        selectedCategory: 'runningAnalyses'
      }
    },
    async fetch ({ store, app }) {
      await Promise.all([
        store.dispatch('fetchAnalyses', { isVisible: true }),
        store.dispatch('setLastUpdate')
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
  .app-container {
    padding-bottom: 45px;
  }
</style>
