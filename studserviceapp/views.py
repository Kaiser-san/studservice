from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import *

def index(request):
    return HttpResponse("Dobrodošli na studentski servis")

def timetableforuser(request, username):
    raspored=" "
    termini = Termin.objects.all()
    nalog = Nalog.objects.get(username = username)
    if(nalog.uloga == "student"):
        profil = Student.objects.get(nalog=nalog)
        grupaID = Student.grupa.through.objects.get(student_id=profil.id).grupa_id
        grupa = Grupa.objects.get(id = grupaID)
        for j in range(len(termini)):
            if grupa in termini[j].grupe.all():
               string = "%s %s %s %s %s %s %s %s<br/>" % (termini[j].oznaka_ucionice,termini[j].predmet.naziv,termini[j].tip_nastave,termini[j].nastavnik.ime,termini[j].nastavnik.prezime,termini[j].pocetak,termini[j].zavrsetak,termini[j].dan)
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

def newGroup(request):
    context = { 'predmeti' : Predmet.objects.all()}
    return render(request, 'studserviceapp/newGroup.html', context)

def addGroup(request):
    izbornaGrupa = IzbornaGrupa(oznaka_grupe=request.POST['oznaka_grupe'], oznaka_semestra=request.POST['oznaka_semestra'], kapacitet=request.POST['kapacitet'], smer=request.POST['smer'], aktivna=True if request.POST['aktivna'] == 'on' else False, za_semestar=Semestar.objects.get(id = request.POST['za_semestar']))
    izbornaGrupa.save()
    for predmet_id in request.POST['predmeti']:
        izbornaGrupa.predmeti.add(Predmet.objects.get(id=predmet_id))
    return HttpResponse("Uspesno dodata grupa")

def izaberiGrupu(request):
    izabrana_grupa = IzbornaGrupa.objects.get(id=request.POST['izbor_grupe'])
    student = Student.objects.get(smer=request.POST['oznaka_semestra'],
        broj_indeksa=request.POST['broj_indeksa'],
        godina_upisa=int(request.POST['godina_upisa']))
    izbor_grupe = IzborGrupe.objects.create(
        ostvarenoESPB=int(request.POST['broj_ostvarenih_ESPB']),
        upisujeESPB=int(request.POST['broj_ESPB_upisanih']),
        broj_polozenih_ispita=int(request.POST['broj_polozenih_ispita']),
        upisuje_semestar=int(request.POST['semestar']),
        prvi_put_upisuje_semestar=(request.POST['prvi_put_upisuje']=='Da'),
        nacin_placanja = request.POST['nacin_placanja'],
        student = student ,
        izabrana_grupa = izabrana_grupa ,
        upisan = False)
    for predmet_id in request.POST['predmeti']:
        predmet = Predmet.objects.get(id=predmet_id)
        izbor_grupe.nepolozeni_predmeti.add(predmet)
    return HttpResponse("Uspesno izabrana grupa")

def izborgrupe(request,username):
    context = {'username' : username ,
                'predmeti' : Predmet.objects.all() ,
                'neparni_semsetar' : True  ,
                'grupe' : IzbornaGrupa.objects.all()}
    return render(request,'studserviceapp/izborGrupe.html',context)