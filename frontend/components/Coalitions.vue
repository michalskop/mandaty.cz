<template>
    <div>
        <h3>{{ t['header'] }} <span class="badge">{{ date }}</span> <small><span class="badge badge-pill badge-info small-badge">Experimentální</span></small></h3>
        <h6>{{ t['description'] }}</h6>
        <div class="container">
            <div class="row justify-content-center text-center">
                <div v-for="(coalition, i) in coalitions" :key="i" class="block">
                    <span class="parties">
                        <span v-for="(party, j) in coalition['party_codes']" :key="j" class="">
                            <span v-bind:style="{ color: meta[party]['color']}">{{ meta[party]['name'] }}</span>
                            <span v-if="j < coalition['party_codes'].length - 1">+</span>
                        </span>
                        ~ {{ coalition['seats'] }}
                        <span v-if="i == 0">{{ t['seats'] }}</span>
                    </span>
                    <br />
                    <span v-if="i == 0">{{ t['chance_to_majority'] }}</span><span v-else>{{ t['chance'] }}</span> {{ coalition['majority_probability'] | nicePercentage }}
                </div>
            </div>
        </div>
        <div class="alert alert-info">
            <i class="fa fa-info-circle"></i>&nbsp;<span v-html="t['info']"></span>
        </div>
        <hr />
    </div>
</template>

<script>
    import config from "../config.js"
    import t from "../texts/components/Coalitions.json"
    import currentCoalitions from '../static/data/current_coalitions.json'

    export default {
        data: function (){
            return {
                t,
                config,
                coalitions: currentCoalitions['coalitions'],
                meta: currentCoalitions['meta'],
                date: new Date(currentCoalitions['date']).toLocaleDateString(LOCALE)
            }
        },
        filters: {
            abs(value) {
                return Math.abs(value);
            },
            nicePercentage(value) {
                if (value > 0.99) return "> 99%"
                if (value < 0.03) return "< " + Math.round(Math.ceil(value * 100)) + "%"
                return "~ " + Math.round(value * 100) + "%"
            }
        }

    }

</script>

<style scoped>
    .small-badge {
        font-size: 0.5em;
        position: relative;
        bottom: 1em;
    }
    .block {
        padding: 1.25em .75em;
        border: solid gray 1px;
        border-radius: 2em;
        margin: 0.25em;
    }
    .parties {
        font-size: 1.25em;
        font-weight: bold;
    }
</style>
