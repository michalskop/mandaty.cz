<template>
    <div class="mt-2">
        <h2>{{ t['election_models'] }} <small>{{ t['moving_averages'] }}</small></h2>
        <div id="ma-plot" :style="style"></div>
        <div class="alert alert-info">
            <i class="fa fa-info-circle"></i> {{ t['info'] }}
        </div>
        <hr />
    </div>
</template>
<script>

import Plotly from 'plotly.js/lib/core'
import t from "../texts/components/HistoryChart.json"
import ltma from '../static/data/last_term_moving_averages.json'

export default {
    name: 'HistoryChart',
    data: function () {
        return {
            t,
            electionData: ltma['election_data'],
            electionDate: ltma['dates'][0],
            dates: ltma['dates'],
            choices: ltma['choices'],
            moving_averages: ltma['moving_averages'],
            style: {
                width: 1100,
                height: 920
            }
        }
    },
    methods: {
        setSize: function () {
            this.style.width = Math.min(this.style['width'], screen.width)
            this.style.height = Math.min(this.style['height'], screen.height)
        },
        hex2rgba: function (str, a) {
            return str.replace('#','').split('').reduce((r,c,i,{length: l},j,n)=>(j=parseInt(i*3/l),n=parseInt(c,16),r[j]=(l==3?n:r[j])*16+n,r),[0,0,0,a||1])
        },
        drawChart: function () {
            var $this = this
            var elections = this.electionData.map( obj => {
                var d = {
                    type: 'scatter',
                    mode: 'markers',
                    x: [$this.electionDate],
                    y: [obj.value * 100],
                    name: "Volby: " + obj.name,
                    legendgroup: obj.name,
                    showlegend: false,
                    marker: {
                        size: 30,
                        color: "rgba(" + $this.hex2rgba(obj.color, 1).join(',') + ")",
                        // border: {
                        //     color: //"rgba(" + hex2rgba(obj.color).join(',') + ")",
                        //     arearatio: 1
                        // }
                    }
                }
                return d
            })

            var data = this.choices.map(obj => {
                var d = {
                    mode: 'markers',
                    type: 'scatter',
                    line: {
                        color: "rgba(" + $this.hex2rgba(obj.color).join(',') + ")",
                        shape: "spline"
                    },
                    marker: {
                        size: 15,
                        opacity: 0.5,
                        // color: $this.hex2rgba(obj.color,.5).join(',') + ")",
                        // line: {
                        //     color: "rgba(" + $this.hex2rgba(obj.color,1).join(',') + ")",
                        //     width: 5
                        // }
                    },
                    showlegend: false
                };
                d['legendgroup'] = obj.name;
                d['name'] = obj.name;
                d['x'] = $this.dates.slice(1, $this.dates.length)
                d['y'] = obj.data.slice(1, obj.data.length).map(v => v * 100);
                return d;
            });

            var mas = this.moving_averages.map(obj => {
                var d = {
                    mode: 'lines',
                    type: 'scatter',
                    line: {
                        color: "rgba(" + $this.hex2rgba(obj.color).join(',') + ")",
                        shape: "spline"
                    },
                    hoverinfo: 'skip'
                };
                d['legendgroup'] = obj.name;
                d['name'] = obj.name;
                d['x'] = $this.dates;
                d['y'] = obj.data.map(v => v * 100);
                return d;
            });

            var upper = this.choices.map(function (obj, i) {
                var d = {
                    mode: 'lines',
                    type: 'scatter',
                    line: {
                        color: "rgba(" + $this.hex2rgba(obj.color).join(',') + ")",
                        shape: "spline",
                        width: 0.01
                    },
                    showlegend: false,
                    hoverinfo: 'skip',
                    fill: 'tonexty'
                };
                d['legendgroup'] = obj.name;
                d['name'] = obj.name;
                d['x'] = $this.dates;
                d['y'] = $this.moving_averages[i].data.map(
                    (v, index) => (index > 0) * ((v * 750 + Math.sqrt(v * 750 * (1 - v)) * 1.95 * 1.5) / 750 * 100) + (index == 0) * v * 100
                )
                d['fillcolor'] = "rgba(" + $this.hex2rgba(obj.color, 0.05).join(',') + ")";
                return d;
            });

            var lower = this.choices.map(function (obj, i) {
                var d = {
                    mode: 'lines',
                    type: 'scatter',
                    line: {
                        color: "rgba(" + $this.hex2rgba(obj.color).join(',') + ")",
                        shape: "spline",
                        width: 0.01
                    },
                    showlegend: false,
                    hoverinfo: 'skip'
                };
                d['legendgroup'] = obj.name;
                d['name'] = obj.name;
                d['x'] = $this.dates;
                d['y'] = $this.moving_averages[i].data.map(
                    (v, index) => (index > 0) * (Math.max((v * 750 - Math.sqrt(v * 750 * (1 - v)) * 1.95 * 1.5) / 750 * 100, 0)) + (index == 0) * v * 100
                );
                return d;
            });

            var limit = [{
                x: [this.electionDate, data[0]['x'][data[0]['x'].length - 1]],
                y: [5, 5],
                name: '5% hranice',
                mode: 'lines',
                // showlegend: false,
                hoverinfo: 'skip',
                fill: 'tozeroy',
                line: {
                    color: "red",
                    dash: 'dot',
                    width: 3
                }
            }]

            var bounds = [];
            for (var i = 0; i < upper.length; i++) {
                bounds.push(lower[i]);
                bounds.push(upper[i]);
            }

            data = mas.concat(data)
            data = bounds.concat(data);
            data = elections.concat(data);
            data = limit.concat(data);

            var layout = {
                xaxis: {
                    type: 'date',
                    title: this.t['date_of_poll']
                },
                yaxis: {
                    title: this.t['election_model'],
                    ticksuffix: '%',
                    showticksuffix: 'all' // or 'first' or 'all' (the default)
                },
                title:this.t['election_models'],
                showlegend: true,
                legend: {
                    traceorder: 'reversed'
                },
                width: this.style['width'],
                height: this.style['height']
            };

            var config = {
                displaylogo: false,
                staticPlot: false,
                locale: 'cs'
            }
            // TESTER = document.getElementById('ma-plot');
            Plotly.plot('ma-plot', data, layout, config);
        }
    },
    mounted() {
        this.drawChart()
        this.setSize()
        // window.addEventListener('resize', this.setSize)
    }
    // ,
    // beforeDestroy() {
    //     window.removeEventListener('resize', this.setSize)
    // }
    // var



}
</script>
