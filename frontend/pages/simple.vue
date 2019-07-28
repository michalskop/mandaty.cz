<template>
  <div>
      <Header></Header>
    <div class="container">
        <!-- <h1>{{ t['title'] }} <small><small>{{ t['subtitle'] }}</small></small></h1> -->
        <Seats></Seats>
    </div>
  </div>
</template>
<script>
import Seats from '@/components/Seats.vue'
import Header from '@/components/Header.vue'
import t from "../texts/index.json"

export default {
  name: 'simple',
  data:  function () {
      return {
          t
      }
  },
  components: {
      Seats,
      Header
  }
}
</script>
