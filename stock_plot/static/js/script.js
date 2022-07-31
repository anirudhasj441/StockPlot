const app = Vue.createApp({
    el: "#app",
    delimiters: ['[[', ']]'],
    data(){
        return {
            tmp: "Temp",
            search: true,
            loading: false,
            search_value: "",
            search_results: [],
            data: {}
        }
    },
    methods: {
        plotly: function(div, data){
            Plotly.newPlot(div, data);
        },
        filter: function(value){
            if(value.length < 3){
                return;
            }
            var url = "https://alpha-vantage.p.rapidapi.com/query?keywords=" + String(value) +"&function=SYMBOL_SEARCH&datatype=json";
            const xhr = new XMLHttpRequest();
            xhr.withCredentials = true;
            xhr.open("get", url);
            xhr.onload = function(){
                var response = JSON.parse(xhr.response);
                console.log(response);
                this.search_results = [];
                for(var item of response.bestMatches){
                    console.log(item);
                    data = {
                        name: item["2. name"],
                        symbol: item["1. symbol"]
                    }
                    this.search_results.push(data);
                }
                console.log(response.bestMatches);
                console.log(this.search_results);
                clearTimeout(timeout);
            }.bind(this)
            xhr.setRequestHeader("X-RapidAPI-Key", "7517de7ee2mshc50158a550fd525p1ee8c2jsnabb54b407710")
            xhr.setRequestHeader("X-RapidAPI-Host", "alpha-vantage.p.rapidapi.com");
            xhr.send();
        },
        buttonClicked: function(symbol, name){
            console.log(symbol);
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
                    y.push(ts[data]["1. open"])
                }
                plot_data[0]["x"] = x;
                plot_data[0]["y"] = y;
                plot_data[0]["type"] = 'scatter';
                Plotly.react(this.plot_container, plot_data);
                console.log(plot_data);
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

app.use(Quasar);
app.mount("#app");