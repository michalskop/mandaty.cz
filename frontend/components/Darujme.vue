<template>
    <div class="">
        <div class="container alert alert-success">
            <h1 class="p-4"><i class="fa fa-heart text-danger"></i> <small> {{ t['supported'] }}</small>
            </h1>
            <div class="d-flex flex-row flex-wrap justify-content-around">
                <div v-for="(supporter, index) in supporters" :key="index" class="card p-2 m-2" :class="bgClass(supporter.date)">
                    <h4 :class="textClass(supporter.date)">{{ supporter['given_name'] }} {{ supporter['family_name'] }}</h4>
                </div>
            </div>
            <div class="mt-5">
                <a :href="url_darujme" target="_blank"><h4  class="outlink">{{ t['support'] }}</h4></a>
            </div>
        </div>
        <div data-darujme-widget-token="e2esjcadvq7fynj6">&nbsp;</div>
    </div>
</template>
<script>
import config from '../config.js'
import t from "../texts/components/Darujme.json"

export default {
    data: function () {
        return {
            t,
            supporters: [],
            url_darujme: ''
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
            $this.$data.supporters = response.reverse().filter( function (item) {
                return item.last
            })
        })

        +function(w, d, s, u, a, b) {
            w['DarujmeObject'] = u;
            w[u] = w[u] || function () { (w[u].q = w[u].q || []).push(arguments) };
            a = d.createElement(s); b = d.getElementsByTagName(s)[0];
            a.async = 1; a.src = "https:\/\/www.darujme.cz\/assets\/scripts\/widget.js";
            b.parentNode.insertBefore(a, b);
        }(window, document, 'script', 'Darujme');
        Darujme(1, "e2esjcadvq7fynj6", 'render', "https:\/\/www.darujme.cz\/widget?token=e2esjcadvq7fynj6", "100%");
    },
    methods: {
        diffDays: function (a, b) {
            return Math.ceil(Math.abs(a - b) / (1000 * 3600 * 24))
        },
        bgClass: function(isoDate) {
            var aa = Date.parse(isoDate)
            var b = new Date()
            var bb = b.getTime()
            if (this.diffDays(aa, bb) > 540) {
                return "bg-light"
            } else {
                if (this.diffDays(aa, bb) > 270) {
                    return "bg-secondary"
                } else {
                    return "bg-warning"
                }
            }
        }
        ,
        textClass: function(isoDate) {
            var aa = Date.parse(isoDate)
            var b = new Date()
            var bb = b.getTime()
            if (this.diffDays(aa, bb) > 540) {
                return "text-secondary"
            } else {
                if (this.diffDays(aa, bb) > 270) {
                    return "text-light"
                } else {
                    return "text-dark"
                }
            }
        }
    }
}
</script>

<style scoped>
    .outlink {
        text-decoration: underline;
    }
</style>
