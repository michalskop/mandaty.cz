<template>
  <div>
      <Header></Header>
    <div class="container">
        <!-- <h1>{{ t['title'] }} <small><small>{{ t['subtitle'] }}</small></small></h1> -->
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
import Table from '@/components/Table.vue'
import Darujme from '@/components/Darujme.vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import t from "../texts/index.json"

export default {
  name: 'about',
  data:  function () {
      return {
          t
      }
  },
  components: {
      'history-chart': () => import('@/components/HistoryChart.vue'),
      Table,
      Darujme,
      Header,
      Footer
  }
}
</script>
