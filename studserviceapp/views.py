from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import Termin, Student, Nastavnik, Nalog

def index(request):
    return HttpResponse("Dobrodošli na studentski servis")
def timetableforuser(request, username):
    raspored=" "
    termini = Termin.objects.all()
    nalog = Nalog.objects.get(username = username)
    if(nalog.uloga == "student"):
        profil = Student.objects.get(nalog=nalog)

        for j in range(len(termini)):
            if profil.grupa in termini[j].grupe.all():
               string = "%s %s %s %s %s %s %s %s<br/>" % (termini[j].oznaka_ucionice,termini[j].predmet,termini[j].tip_nastave,termini[j].nastavnik.ime,termini[j].nastavnik.prezime,termini[j].pocetak,termini[j].zavrsetak,termini[j].dan)
               raspored += string
    else:
        profil = Nastavnik.objects.get(nalog=nalog)
        predmeti = profil.predmet.all()
        for i in range(len(predmeti)):
        	for j in range(len(termini)):
        		if(predmeti[i]==termini[j].predmet):
        			string = "%s %s %s %s %s %s<br/>" % (termini[j].oznaka_ucionice,predmeti[i].naziv,termini[j].tip_nastave,termini[j].pocetak,termini[j].zavrsetak,termini[j].dan)
        			raspored+=string
    return HttpResponse("Dobrodošli na studentski servis, raspored za %s %s: <br/>%s" % (profil.ime,profil.prezime,raspored))