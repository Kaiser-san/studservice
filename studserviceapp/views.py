from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
def index(request):
    return HttpResponse("Dobrodošli na studentski servis")
def timetableforuser(request, username):
    return HttpResponse("Dobrodošli na studentski servis, raspored za username %s." % username)