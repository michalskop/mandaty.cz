<template>
    <div class="container">
        <h2>{{ t['election_models'] }}</h2>
        <div class="m-2">
            <i class="fa fa-filter"></i> {{ t.filter }}: <span v-for="pollster in pollsters" :key="pollster.id"><button type="button" class="btn btn-sm m-1" @click="filterPolls(pollster)" :class="[{ 'btn-info': pollster.active }, {'btn-outline-info': !pollster.active}]">{{ pollster.abbreviation }}</button></span>
        </div>
        <div class="table-responsive">
            <table class="table table-striped table-hover table-condensed">
                <thead>
                    <tr>
                        <th></th>
                        <th>{{ t['end_date'] }}</th>
                        <th v-for="(choice, index) in choices" :key="index">
                            <span v-if="!choice.choice_abbreviation" style="color:#888;">{{ t['others'] }}</span>
                            <span v-else :style="color(choice.color_color)">{{choice.choice_abbreviation}}</span>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(poll, i) in polls" :key="i" v-if="pollsters_active[poll['pollster_id']]">
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
                choices: [],
                pollsters: [],
                pollsters_active: {}
            }
        },
        methods: {
            prepareTable: function (polls, rows) {
                let j = 0
                this.$data.table = []
                this.$data.poll2row = {}
                this.$data.choice2column = {}
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
                    polls[i]['poll_formatted_date'] = new Date(polls[i]['poll_end_date']).toLocaleDateString(LOCALE)
                    this.$data.table.push([])
                    if(!(polls[i]['pollster_id'] in this.$data.poll2row)) {
                        this.$data.poll2row[polls[i]['pollster_id']] = {}
                    }
                    if(!(polls[i]['poll_identifier'] in this.$data.poll2row[polls[i]['pollster_id']])) {
                        this.$data.poll2row[polls[i]['pollster_id']][polls[i]['poll_identifier']] = k
                        k++
                    }
                    for (var jj = 0; jj < this.$data.choices.length; jj++) {
                        this.$data.table[i].push('')
                    }
                }
                // console.log(this.$data.table)
                for (var i = 0; i < rows.length; i++) {
                    var row = rows[i]
                    // console.log("row:", row)
                    // console.log(this.$data.choice2column)
                    var r = this.$data.poll2row[row['pollster_id']][row['poll_identifier']]
                    var c = this.$data.choice2column[row['choice_id']]
                    // console.log(r,c, row)
                    this.$data.table[r][c] = Math.round(parseFloat(row['value']) * 1000) / 10
                }
                console.log(this.$data.table)
                console.log(rows)
                return rows
            },
            getData: function () {
                this.$data.rows = this.prepareTable(this.$data.polls, lastTermData.rows)
            },
            getPolls: function () {
                this.$data.polls = lastTermPolls['rows']
                this.getPollsters()
                this.getData()
            },
            color: function (c) {
                if (!c) {
                    return "color:#000000;"
                } else {
                    return "color:" + c + ";"
                }
            },
            getPollsters: function () {
                // get pollsters (to enable filtering)
                let pollster_ids = []
                const $this = this
                this.$data.polls.forEach(function (poll) {
                    if (!pollster_ids.includes(poll.pollster_id)) {
                        $this.pollsters.push({
                            "id": poll.pollster_id,
                            "abbreviation": poll.pollster_abbreviation,
                            "name": poll.pollster_name,
                            "active": true
                        })
                        $this.pollsters_active[poll.pollster_id] = true
                        pollster_ids.push(poll.pollster_id)
                    }
                    $this.pollsters.sort((a, b) => a.abbreviation.localeCompare(b.abbreviation))
                })
            },
            filterPolls: function (pollster) {
                // switch active in pollsters (for filtering)
                pollster.active = !pollster.active
                this.pollsters_active[pollster.id] = !this.pollsters_active[pollster.id]
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
<style scoped>
.filter {

}
</style>
