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
    context = { 'predmeti' : Predmet.objects.all() }
    return render(request, 'studserviceapp/newGroup.html', context)

def addGroup(request):
    aktivna = False
    if 'aktivna' in request.POST and request.POST['aktivna']:
        aktivna = True
    izbornaGrupa = IzbornaGrupa(oznaka_grupe=request.POST['oznaka_grupe'], oznaka_semestra=request.POST['oznaka_semestra'], kapacitet=request.POST['kapacitet'], smer=request.POST['smer'], aktivna=aktivna, za_semestar=Semestar.objects.get(id = request.POST['za_semestar']))
    izbornaGrupa.save()
    for predmet_id in request.POST.getlist('predmeti'):
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
    for predmet_id in request.POST.getlist('predmeti'):
        predmet = Predmet.objects.get(id=predmet_id)
        izbor_grupe.nepolozeni_predmeti.add(predmet)
    return HttpResponse("Uspesno izabrana grupa")

def izborgrupe(request,username):
    if(not Nalog.objects.filter(username=username).exists()):
        return HttpResponse("Nalog {} ne postoji".format(username))

    nalog = Nalog.objects.get(username=username)
    student = Student.objects.get(nalog=nalog)

    if(IzborGrupe.objects.filter(student=student).exists()):
        return HttpResponse("Vec ste izabrali grupu.")

    curr_semestar = Semestar.objects.order_by('-pk')[0]
    neparni_semsetar = (curr_semestar.vrsta == 'neparni')

    skolska_godina_pocetak = curr_semestar.skolska_godina_pocetak
    skolska_godina_kraj = curr_semestar.skolska_godina_kraj

    semestri = [1,3,5,7] if neparni_semsetar else [2,4,6,8]
    predmeti = Predmet.objects.all()
    izborne_grupe = IzbornaGrupa.objects.all()

    smerovi = ['RN','RM','RD','RI','S','M','D']
    smerovi.remove(student.smer)
    smerovi = [student.smer] + smerovi

    godine_upisa = [2013,2014,2015,2016,2017,2018]
    godine_upisa.remove(student.godina_upisa)
    godine_upisa = [student.godina_upisa] + godine_upisa

    context = { 'student' : student ,
                'predmeti' : predmeti ,
                'smerovi' : smerovi ,
                'godine_upisa' : godine_upisa ,
                'skolska_godina_pocetak' : skolska_godina_pocetak ,
                'skolska_godina_kraj' : skolska_godina_kraj ,
                'semestri' : semestri ,
                'grupe' : izborne_grupe}
    return render(request,'studserviceapp/izborGrupe.html',context)

def changeGroup(request,grupa):
    context = {'grupa' : IzbornaGrupa.objects.get(oznaka_grupe=grupa),
                'predmeti' : Predmet.objects.all()}
    return render(request,'studserviceapp/changeGroup.html',context)

def changedGroup(request):
    izbornaGrupa = IzbornaGrupa.objects.get(oznaka_grupe=request.POST['oznaka_grupe'])
    izbornaGrupa.oznaka_semestra = oznaka_semestra=request.POST['oznaka_semestra']
    izbornaGrupa.kapacitet = request.POST['kapacitet']
    izbornaGrupa.smer = request.POST['smer']
    izbornaGrupa.aktivna = False
    if 'aktivna' in request.POST and request.POST['aktivna']:
        izbornaGrupa.aktivna = True
    izbornaGrupa.za_semestar = Semestar.objects.get(id = request.POST['za_semestar'])
    izbornaGrupa.save()
    if 'reset' in request.POST:
        predmeti = izbornaGrupa.predmeti.through.objects.all()
        for predmet in predmeti:
            if(predmet.izbornagrupa_id==izbornaGrupa.id):
                predmet.delete()
    if 'predmeti' in request.POST:
        for predmet_id in request.POST.getlist('predmeti'):
            izbornaGrupa.predmeti.add(Predmet.objects.get(id=predmet_id))
    return HttpResponse("Uspesna izmena grupe")

def groupList(request):
    context = {'grupe' : Grupa.objects.all(),
               'studenti' : Student.objects.all()}
    return render(request,'studserviceapp/groupList.html',context)

def groupStudents(request,group):
    studenti = " "
    grupa = Grupa.objects.get(oznaka_grupe=group)

    for student in Student.objects.all():
        grupa = Grupa.objects.get(id = Student.grupa.through.objects.get(student_id=(Student.objects.get(nalog=student.nalog)).id).grupa_id)
        if(grupa.oznaka_grupe==group):
            studenti += "%s %s %s <br/>" % (student.ime, student.prezime, student.broj_indeksa)
    return HttpResponse("Spisak studenata za grupu %s : <br/> %s" % (group, studenti))
