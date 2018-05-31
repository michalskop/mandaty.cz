<template>
    <header class="navbar navbar-dark bd-navbar bg-primary">
        <a class="navbar-brand" href="/">{{ t['title'] }}<small class="d-none d-sm-inline"> {{ t['subtitle'] }}</small></a>

            <ul class="navbar-nav flex-row ml-auto d-flex">
                <li class="nav-item">
                    <a :href="api_url" class="nav-link"><i class="fa fa-database"></i> {{ t['api'] }}</a>
                </li>
            </ul>
    </header>
</template>
<script>
import config from '../config.js'
import t from "../texts/components/Header.json"

export default {
    data: function () {
        return {
            t,
            api_url: ''
        }
    },
    mounted () {
        this.api_url = API_URL
    }
}
</script>
<style scoped>

</style>
