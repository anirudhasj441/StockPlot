const app = Vue.createApp({
    el: "#app",
    delimiters: ['[[', ']]'],
    data(){
        return {
            tmp: "Temp",
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
                        text: "Date"
                    },
                    autorange: true,
                    rangeselector: {buttons: [
                        {
                        count: 1,
                        label: '1m',
                        step: 'month',
                        stepmode: 'backward'
                        },
                        {
                        count: 3,
                        label: '3m',
                        step: 'month',
                        stepmode: 'backward'
                        },
                        {step: 'all'},
                    ]},
                    rangeslider: {},
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
            var url = "https://alpha-vantage.p.rapidapi.com/query?keywords=" + String(value) +"&function=SYMBOL_SEARCH&datatype=json";
            const xhr = new XMLHttpRequest();
            xhr.withCredentials = true;
            xhr.open("get", url);
            xhr.onload = function(){
                var response = JSON.parse(xhr.response);
                for(var item of response.bestMatches){
                    console.log(item);
                    data = {
                        name: item["2. name"],
                        symbol: item["1. symbol"],
                        currency: item["8. currency"]
                    }
                    this.search_results.push(data);
                }
                this.filter_loading = false;
                this.show_results = true;
                console.log(response.bestMatches);
                console.log(this.search_results);
            }.bind(this)
            xhr.setRequestHeader("X-RapidAPI-Key", "7517de7ee2mshc50158a550fd525p1ee8c2jsnabb54b407710")
            xhr.setRequestHeader("X-RapidAPI-Host", "alpha-vantage.p.rapidapi.com");
            xhr.send();
        },
        updateSearch: function(value){
            if(value == ""){
                this.show_results = false;
                this.search_results = [];
            }
        },
        buttonClicked: function(symbol, name, currency){
            this.show_results = false;
            var url = "https://alpha-vantage.p.rapidapi.com/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=" + symbol + "&outputsize=compact&interval=5min&datatype=json";
            console.log(url);
            const xhr = new XMLHttpRequest();
            xhr.withCredentials = true;
            xhr.open("get", url);
            xhr.setRequestHeader("X-RapidAPI-Key", "7517de7ee2mshc50158a550fd525p1ee8c2jsnabb54b407710");
            xhr.setRequestHeader("X-RapidAPI-Host", "alpha-vantage.p.rapidapi.com");
            xhr.onload = function(){
                var response = JSON.parse(xhr.response);
                console.log(response);
                var ts = response["Time Series (Daily)"];
                var x = [];
                var y = [];
                var plot_data = [{
                    x: [],
                    y: [],
                    type: "scatter"
                }];
                for(var data in ts){
                    x.push(data);
                    y.push(ts[data]["4. close"])
                }
                plot_data[0]["x"] = x;
                plot_data[0]["y"] = y;
                plot_data[0]["type"] = 'scatter';
                this.layout.title = name;
                this.layout.yaxis.title.text = "Price " + currency;
                this.latest_price = parseFloat(y[0]).toFixed(2);
                this.latest_time = x[0];
                this.currency = currency;
                this.plotly(this.plot_container, plot_data, this.layout, this.config);
            }.bind(this)
            xhr.send();
            this.search_value = name;
            this.search_results = [];
        },
    },
    mounted(){
        this.plot_container = document.getElementById("plot");
    },
})

// app.use(Quasar);
app.mount("#app");

//New Line