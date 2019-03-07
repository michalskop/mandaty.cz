<template>
    <span>
        {{ floor }}<small v-if="hasDecimal">.{{ decimal }}</small>
    </span>
</template>
<script>
    export default {
        props: ['decNumber'],
        data: function () {
            return {
                floor: '',
                decimal: 0,
                hasDecimal: false
            }
        },
        mounted () {
            if (this.decNumber != '' && this.decNumber != null) {
                this.floor = Math.floor(this.decNumber)
            }
            this.decimal = Math.round(10 * (this.decNumber - this.floor))

            if (this.decimal > 0) {
                this.hasDecimal = true
            }
        }
    }

</script>
