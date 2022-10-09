const app = Vue.createApp({
    el: "#app",
    delimiters: ['[[', ']]'],
    data(){
        return {
            tmp: "Temp",
            period: "1d",
            search: true,
            loading: false,
            show_results: false,
            filter_loading: false,
            plot_added: false,
            search_value: "",
            latest_price: "",
            currency: "",
            latest_time: "",
            search_results: [],
            data: [],
            layout: {
                title: "",
                xaxis: {
                    title: {
                        text: "Time"
                    },
                    rangebreaks: []
                },
                yaxis: {
                    title: {
                        text: ""
                    }
                },
                margin: {
                    l: 50,
                    r: 50,
                    b: 50,
                    t: 100
                }
            },
            config: {}
        }
    },
    methods: {
        plotly: function(div, data, layout, config){
            this.plot_added = true;
            Plotly.react(div, data, layout, config);
        },
        filter: function(value){
            if(value.length < 3){
                return;
            }
            this.search_results = [];
            this.show_results = false;
            this.filter_loading = true;
            var url = "/search";
            var data = {
                "q": value
            }
            const xhr = new XMLHttpRequest();
            xhr.open("post", url);
            xhr.onload = function(){
                var response = JSON.parse(xhr.response);
                console.log(response)
                this.search_results = response;
                this.filter_loading = false;
                this.show_results = true;
            }.bind(this)
            xhr.send(JSON.stringify(data));
        },
        updateSearch: function(value){
            if(value == ""){
                this.show_results = false;
                this.search_results = [];
            }
        },
        setPeriod: function(value){
            this.period = value;
            this.showPlot(this.symbol, this.name, this.currency);
        },
        showPlot: function(symbol, name, currency){
            this.show_results = false;
            this.symbol = symbol;
            this.name = name;
            this.currency = currency;
            // var url = "https://alpha-vantage.p.rapidapi.com/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=" + symbol + "&outputsize=compact&interval=5min&datatype=json";
            var url = "/intraday";
            var data = {
                "sym": symbol,
                "period": this.period
            }
            const xhr = new XMLHttpRequest();
            xhr.open("post", url);
            xhr.onload = function(){
                var response = JSON.parse(xhr.response);
                console.log(response);
                this.layout.title = name;
                this.layout.yaxis.title.text = "Price " + currency;
                // this.layout.xaxis.rangebreaks[0].values = response.dt_breaks;
                if(["5d", "1mo"].includes(this.period)){
                    this.layout.xaxis.rangebreaks = [
                        {
                            bounds: [16,9.25],
                            pattern: "hour"
                        },
                        {
                            bounds: ['sat','mon']
                        }
                    ]
                }
                else{
                    console.log(this.period);
                    this.layout.xaxis.rangebreaks = [];
                }
                this.latest_price = parseFloat(response["latest_price"]).toFixed(2);
                this.latest_time = response["latest_time"];
                this.currency = currency;
                this.data = response.data;
                console.log(this.layout.xaxis);
                // this.layout = response.layout;
                this.plotly(this.plot_container, this.data, this.layout, this.config);
            }.bind(this)
            xhr.send(JSON.stringify(data));
            this.search_value = name;
            this.search_results = [];
        }
    },
    mounted(){
        this.plot_container = document.getElementById("plot");
    },
})

// app.use(Quasar);
app.mount("#app");