<template>
    <div class="">
        <div class="container alert alert-success">
            <h1 class="p-4"><i class="fa fa-heart text-danger"></i> <small> {{ t['supported'] }}</small>
            </h1>
            <div class="d-flex flex-row flex-wrap justify-content-around">
                <div v-for="(supporter, index) in supporters" :key="index" class="card p-2 m-2 bg-warning">
                    <h4 class="text-dark">{{ supporter['given_name'] }} {{ supporter['family_name'] }}</h4>
                </div>
            </div>
            <div class="mt-5">
                <a :href="url_darujme" target="_blank"><h4>{{ t['support'] }}</h4></a>
            </div>
        </div>
    </div>
</template>
<script>
import config from '../config.js'
import t from "../texts/components/Darujme.json"

export default {
    data: function () {
        return {
            t,
            supporters: []
        }
    },
    mounted () {
        var $this = this
        this.url_darujme = URL_DARUJME
        fetch (API_DARUJME)
        .then(function (response) {
            return response.json()
        })
        .then(function (response) {
            $this.$data.supporters = response
        })
    }
}
</script>
