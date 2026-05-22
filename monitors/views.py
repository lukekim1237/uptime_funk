from django.shortcuts import render

def index(request):
    return render(request, 'monitors/index.html')