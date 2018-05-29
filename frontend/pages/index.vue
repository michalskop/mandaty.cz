<template>
  <div class="about container">
    <h1>{{ t['title'] }}</h1>
    <no-ssr>
        <!-- <test-chart></test-chart> -->
        <history-chart></history-chart>
    </no-ssr>
    <Table></Table>
  </div>
</template>
<script>
import Table from '@/components/Table.vue'
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
      Table
  }
}
</script>
