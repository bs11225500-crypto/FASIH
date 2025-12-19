from django.shortcuts import render

def specialist_dashboard(request):
    return render(request, "specialist/specialist_dashboard.html")
