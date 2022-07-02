from django.shortcuts import render

# Create your views here.

def home(request):
    params = {
        "tmp": "temp"
    }
    return render(request, 'plots/index.html', params)