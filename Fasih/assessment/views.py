from django.shortcuts import render

def assessment_form(request):
    return render(request, 'assessment/assessment_form.html')
