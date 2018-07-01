<template>
    <div class="container">
        <h2>{{ t['election_models'] }}</h2>
        <div class="table-responsive">
            <table class="table table-striped table-hover table-condensed">
                <thead>
                    <tr>
                        <th></th>
                        <th>{{ t['published_date'] }}</th>
                        <th v-for="(choice, index) in choices" :key="index">
                            <span v-if="!choice.choice_abbreviation" style="color:#888;">{{ t['others'] }}</span>
                            <span v-else :style="color(choice.color_color)">{{choice.choice_abbreviation}}</span>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(poll, i) in polls" :key="i">
                        <th>{{poll['pollster_abbreviation']}}</th>
                        <td>{{poll['poll_formatted_date']}}</td>
                        <td v-for="(value, index) in table[i]" :key="index">
                            <DecNumber :decNumber="value"></DecNumber>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div class="alert alert-info">
            <i class="fa fa-info-circle"></i> {{ t['info'] }}
        </div>
        <hr />
    </div>
</template>
<script>
    import config from '../config.js'
    import DecNumber from './DecNumber.vue'
    import t from "../texts/components/Table.json"
    import lastTermData from '../static/data/last_term_data.json'
    import lastTermPolls from '../static/data/last_term_polls.json'

    export default {
        data: function (){
            return {
                t,
                polls: [],
                table: [],
                choice2column: {},
                poll2row: {},
                choices: []
            }
        },
        methods: {
            prepareTable: function (polls, rows) {
                var j = 0
                for (var i = 0; i < rows.length; i++) {
                    var row = rows[i]
                    if (!(row['choice_id'] in this.$data.choice2column) && (!(row['pollster_id'] == EXCLUDE_ELECTIONS))) {
                        this.$data.choice2column[row['choice_id']] = j
                        this.$data.choices.push(row)
                        j++
                    }
                }
                var k = 0
                for (var i = 0; i < polls.length; i++) {
                    this.$data.polls[i]['poll_formatted_date'] = new Date(polls[i]['poll_published_date']).toLocaleDateString(LOCALE)
                    this.$data.table.push([])
                    if(!(polls[i]['pollster_id'] in this.$data.poll2row)) {
                        this.$data.poll2row[polls[i]['pollster_id']] = {}
                    }
                    if(!(polls[i]['poll_identifier'] in this.$data.poll2row[polls[i]['pollster_id']])) {
                        this.$data.poll2row[polls[i]['pollster_id']][polls[i]['poll_identifier']] = k
                        k++
                    }
                    for (var j = 0; j < this.choices.length; j++) {
                        this.$data.table[i].push('')
                    }
                }
                // console.log(this.$data)
                for (var i = 0; i < rows.length; i++) {
                    var row = rows[i]
                    // console.log("row:", row)
                    var r = this.$data.poll2row[row['pollster_id']][row['poll_identifier']]
                    var c = this.$data.choice2column[row['choice_id']]
                    // console.log(r,c, row)
                    this.$data.table[r][c] = Math.round(parseFloat(row['value']) * 1000) / 10
                }
                // console.log(this.$data.choices)
                return rows
            },
            getData: function () {
                this.$data.rows = this.prepareTable(this.$data.polls, lastTermData.rows)
            },
            getPolls: function () {
                this.$data.polls = lastTermPolls['rows']
                this.getData()
            },
            color: function (c) {
                if (!c) {
                    return "color:#000000;"
                } else {
                    return "color:" + c + ";"
                }
            }
        },
        mounted () {
            this.getPolls()
        },
        components: {
            DecNumber
        }
    }
</script>
