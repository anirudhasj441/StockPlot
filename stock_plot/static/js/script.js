const app = Vue.createApp({
    el: "#app",
    delimiters: ['[[', ']]'],
    data(){
        return {
            tmp: "Temp",
            period: "1d",
            preloader: true,
            search: true,
            loading: false,
            show_results: false,
            filter_loading: false,
            plot_added: false,
            auto_reload: false,
            graph_loading: false,
            show_password: false,
            show_message: false,
            email_error: false,
            password_error: false,
            fname_error: false,
            lname_error: false,
            signin_loading: false,
            signup_loading: false,
            search_value: "",
            latest_price: "",
            currency: "",
            latest_time: "",
            fname: "",
            lname: "",
            email: "",
            password: "",
            message_tag: "",
            message: "",
            chart_type: "line_chart",
            current_year: "",
            email_error_message: "",
            password_error_message: "",
            fname_error_message: "",
            lname_error_message: "",
            search_results: [],
            data: [],
            layout: {
                title: "",
                dragmode: "pan",
                xaxis: {
                    title: {
                        text: "Time"
                    },
                    'rangeslider' : {
                        'visible' : false
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
            config: {
                responsive: false,
                displaylogo: false
            }
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
            var url = "/plots/search";
            var data = {
                "q": value
            }
            const xhr = new XMLHttpRequest();
            xhr.open("post", url);
            xhr.onload = function(){
                var response = JSON.parse(xhr.response);
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
        updateChartType: function(){
            this.chart_type = (this.chart_type == "line_chart") ? "candlestick_chart" : "line_chart";
            this.showPlot(this.symbol, this.name, this.currency);
        },
        showStock: function(symbol, name, currency){
            window.location.href = "/stock?symbol=" + symbol + "&name=" + name + "&currency=" + currency;
        },
        loadPlot: function(){
            if(this.stock_page){
                var symbol = document.getElementById("symbol").value;
                var name = document.getElementById("name").value;
                var currency = document.getElementById("currency").value;
                this.showPlot(symbol, name, currency);
                this.getNews(symbol);
            }
        },
        signUp: function(){
            if(!this.validate("sign_up")){
                return;
            }
            this.signup_loading = true;
            let url = "/signup";
            let data = {
                fname: this.fname,
                lname: this.lname,
                email: this.email,
                password: this.password
            }
            const xhr = new XMLHttpRequest();
            xhr.open("post", url);
            xhr.onload = function(){
                this.signup_loading = false
                var response = JSON.parse(xhr.response);
                if(response.status == "success"){
                    this.message_tag = "success";
                }
                else{
                    this.message_tag = "danger";
                }
                this.message = response.message;
                this.show_message = true;
            }.bind(this)
            xhr.send(JSON.stringify(data));
        },
        signIn: function(){
            if(!this.validate("sign_in")){
                return;
            }
            this.signin_loading = true;
            let url = "/signin";
            let data = {
                email: this.email,
                password: this.password
            }
            const xhr = new XMLHttpRequest();
            xhr.open("post", url);
            xhr.onload = function(){
                this.signin_loading = false;
                let response = JSON.parse(xhr.response);
                if(response.status == "success"){
                    var modal_el = document.getElementById("sign-form");
                    var modal = bootstrap.Modal.getInstance(modal_el);
                    modal.hide();
                    window.location.reload();
                }
                else{
                    this.message_tag = "danger";
                    this.message = response.message;
                    this.show_message = true;
                }
            }.bind(this)
            xhr.send(JSON.stringify(data));
        },
        resetValidation: function(){
            this.email_error = false;
            this.password_error = false;
            this.email_error_message = "";
            this.password_error_message = "";
        },
        validate: function(form){
            var is_pass = true;
            this.resetValidation();
            if(form == "sign_up"){
                if(this.fname.replaceAll(" ", "") == ""){
                    this.fname_error = true;
                    this.fname_error_message = "First name should not be empty"
                    is_pass = false;
                }
                if(this.lname.replaceAll(" ", "") == ""){
                    this.lname_error = true;
                    this.lname_error_message = "Last name should not be empty"
                    is_pass = false;
                }
            }
            if(this.email.replaceAll(" ", "") == ""){
                this.email_error = true;
                this.email_error_message = "email should not be empty"
                is_pass = false;
            }
            if(this.password.replaceAll(" ", "") == ""){
                this.password_error = true;
                this.password_error_message = "Password should not be empty"
                is_pass = false;
            }
            return is_pass;
        },
        showForm: function(){
            this.show_message = false;
            this.resetValidation();
            this.email = "";
            this.password = "";
        },
        getNews: function(symbol){
            let url = "/stock/news";
            let data = {
                "symbol": symbol
            }
            const xhr = new XMLHttpRequest();
            xhr.open("post", url);
            xhr.onload = function(){
                let response = JSON.parse(xhr.response);
                console.log(response);
            }.bind(this)
            xhr.send(JSON.stringify(data));
        },
        showPlot: function(symbol, name, currency, auto_reload=false){
            if(!auto_reload && this.plot_added){
                this.graph_loading = true;
            }
            this.show_results = false;
            this.symbol = symbol;
            this.name = name;
            this.currency = currency;
            // var url = "https://alpha-vantage.p.rapidapi.com/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=" + symbol + "&outputsize=compact&interval=5min&datatype=json";
            var url = "/plots/intraday";
            var data = {
                "sym": symbol,
                "period": this.period,
                "chart_type": this.chart_type
            }
            const xhr = new XMLHttpRequest();
            xhr.open("post", url);
            xhr.onload = function(){
                var response = JSON.parse(xhr.response);
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
                    this.layout.xaxis.rangebreaks = [];
                }
                this.latest_price = parseFloat(response["latest_price"]).toFixed(2);
                this.latest_time = response["latest_time"];
                this.currency = currency;
                this.data = response.data;
                // this.layout = response.layout;
                this.plotly(this.plot_container, this.data, this.layout, this.config);
                // this.auto_reload = true;
                this.graph_loading = false; 
            }.bind(this)
            xhr.send(JSON.stringify(data));
            this.search_value = name;
            this.search_results = [];
        }
    },
    mounted(){
        this.preloader = false;
        this.plot_container = document.getElementById("plot");
        this.current_year = new Date().getFullYear();
        this.stock_page = document.getElementById("stock-page").value;
        this.loadPlot();
        const interval = setInterval(function(){
            if(this.auto_reload){
                this.showPlot(this.symbol, this.name, this.currency, true);
            }
        }.bind(this), 5000);
    },
})

// app.use(Quasar);
app.mount("#app");