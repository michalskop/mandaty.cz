<template>
    <div>
        <h3>{{ t['seats_number'] }} <small>{{ t['with_error_estimate'] }}</small> <span class="badge">{{ date }}</span> <span class="badge badge-info small-badge">Experimentální</span></h3>
        <div class="container">
            <div class="row">
                <div v-for="(party, i) in seats" :key="i" class="">
                    <div class="block" v-bind:style="{ color: party.color}">
                        <div class="">
                            <h4 v-bind:style="{ color: party.color}">{{ party.name }}</h4>
                        </div>
                        <div class="text-center">
                            <span class="number">{{ party.seats }}</span>
                        </div>
                        <div class="text-center lo-hi">
                            <strong>{{ party.lo }} - {{ party.hi }}</strong>
                        </div>
                        <div class="difference" >
                            <span v-if="party.difference > 0">
                                <span class="text-success">▲ {{ party.difference }}</span>
                            </span>
                            <span v-else-if="party.difference < 0">
                                <span class="text-danger">▼{{ party.difference | abs }}</span>
                            </span>
                            <span v-else>
                                <span class="text-muted">⚫ 0</span>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="alert alert-info">
            <i class="fa fa-info-circle"></i>&nbsp;<span v-html="t['info']"></span>
        </div>
    </div>
</template>

<script>
    import config from "../config.js"
    import t from "../texts/components/Seats.json"
    import currentSeats from '../static/data/current_seats.json'

    export default {
        data: function (){
            return {
                t,
                config,
                seats: currentSeats['data'],
                date: new Date(currentSeats['date']).toLocaleDateString(LOCALE)
            }
        },
        filters: {
            abs(value) {
                return Math.abs(value);
            }
        },

    }

</script>

<style scoped>
    h4 {
        padding-left: 2px;
        margin-bottom: 0px;
    }
    .small-badge {
        font-size: 0.33em;
        position: relative;
        bottom: 1em;
    }
    .number {
        font-family: "News Cycle","Arial Narrow Bold",sans-serif;
        font-weight: 700;
        line-height: 1.1;
        color: #000;
        font-size: 4em;
    }
    .block {
      border-style: solid;
      border-width: 3px;
      width: 10em;
      height: 10em;
      border-radius: 8px;
      margin: 8px;
      position: relative;
      min-width: 160px;
    }
    .difference {
        position: absolute;
        top: 3em;
        left: 7em;
    }
    .lo-hi {
        font-size: 1.75em;
    }
</style>
