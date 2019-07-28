<template>
  <div>
      <Header></Header>
    <div class="container">
        <!-- <h1>{{ t['title'] }} <small><small>{{ t['subtitle'] }}</small></small></h1> -->
        <Seats></Seats>
        <Coalitions></Coalitions>
        <no-ssr>
            <!-- <test-chart></test-chart> -->
            <history-chart></history-chart>
        </no-ssr>
        <Table></Table>
        <Darujme></Darujme>
    </div>
    <Footer></Footer>
  </div>
</template>
<script>
import Seats from '@/components/Seats.vue'
import Coalitions from '@/components/Coalitions.vue'
import Table from '@/components/Table.vue'
import Darujme from '@/components/Darujme.vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import t from "../texts/index.json"
import config from '../config.js'

export default {
  name: 'index',
  data:  function () {
      return {
          t
      }
  },
  head: function () {
      return {
          meta: [
              {property: 'og:image', content: BASE_URL + this.t['og:image']},
              {property: 'og:url', content: BASE_URL},
              {property: 'og:type', content: 'website'},
              {property: 'og:title', content: this.t['title']},
              {property: 'og:description', content: this.t['og:description']},
              {property: 'fb:app_id', content: FB_APP_ID}
          ]
      }
  },
  components: {
      'history-chart': () => import('@/components/HistoryChart.vue'),
      Seats,
      Coalitions,
      Table,
      Darujme,
      Header,
      Footer
  }
}
</script>
