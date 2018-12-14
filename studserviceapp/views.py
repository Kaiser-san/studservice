from django.shortcuts import render

import csv
import io

# Create your views here.
from django.http import HttpResponse
from .models import *

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from .parse_raspored_polaganja import import_data

def index(request):
    return HttpResponse("Dobrodošli na studentski servis<br/>Za dodavanje grupe idite na http://127.0.0.1:8000/studserviceapp/newGroup<br/>Za menjanje grupe idite na http://127.0.0.1:8000/studserviceapp/changeGroup/[OZNAKA GRUPE]<br/>Za upis idite na http://127.0.0.1:8000/studserviceapp/izborgrupe/[NALOG]<br/>Za liste grupa idite na http://127.0.0.1:8000/studserviceapp/groupList<br/>Za raspored http://127.0.0.1:8000/studserviceapp/timetable/[NALOG]")

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

    popunjenost_grupa = {x.id: 0 for x in IzbornaGrupa.objects.all()}
    for izbor_grupe in IzborGrupe.objects.all():
        popunjenost_grupa[izbor_grupe.izabrana_grupa.id] += 1
    izborne_grupe = list(filter(lambda grupa: popunjenost_grupa[grupa.id] < grupa.kapacitet and grupa.aktivna, IzbornaGrupa.objects.all()))

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
            studenti += "%s %s %s %s\\%s <br/>" % (student.ime, student.prezime, student.smer, student.broj_indeksa,(student.godina_upisa%100))
    return HttpResponse("Spisak studenata za grupu %s : <br/> %s" % (group, studenti))

def sendMail(request, username):
    nalog = Nalog.objects.get(username=username)
    uloga = nalog.uloga
    opcijePredmeti = []
    opcijeGrupe = []
    opcijeSmer = []

    if (uloga == "student"):
        return HttpResponse("Student ne moze da salje mail-ove!")

    elif(uloga == "nastavnik"):
        person = Nastavnik.objects.get(nalog=nalog)

        predmetiID = []
        for predmet in person.predmet.through.objects.all():
            if(predmet.nastavnik_id == person.nalog_id):
                predmetiID.append(predmet.predmet_id)
        for predmet in Predmet.objects.all():
            if predmet.id in predmetiID:
                opcijePredmeti.append(predmet)

        terminiID = []
        for termin in Termin.objects.all():
            if (termin.predmet_id in predmetiID and person.id==termin.nastavnik_id):
                ter = termin
                terminiID.append(termin.id)
        terminGrupe = ter.grupe.through.objects.all()
        grupeID = []
        for grupa in terminGrupe:
            if(grupa.termin_id in terminiID):
                grupeID.append(grupa.grupa_id)
        for grupa in Grupa.objects.all():
            if grupa.id in grupeID:
                opcijeGrupe.append(grupa)

    else:
        person = nalog;
        for grupa in Grupa.objects.all():
            if not(grupa in opcijeGrupe):
                opcijeGrupe.append(grupa)
        for predmet in Predmet.objects.all():
            if not(predmet in opcijePredmeti):
                opcijePredmeti.append(predmet)
    opcijeGrupe.sort(key = lambda x : x.oznaka_grupe)
    opcijePredmeti.sort(key = lambda x : x.naziv)
    context = {'person' : person,
                'uloga' : uloga,
                'opcijePredmeti' : opcijePredmeti,
                'opcijeGrupe' : opcijeGrupe}
    return render(request,'studserviceapp/mailForm.html',context)

def mailSent(request):
    body = ""
    subject = ""

    if 'body' in request.POST:
        body = request.POST['body']
    if 'subject' in request.POST:
        subject = request.POST['subject']

    return HttpResponse("Uspesno poslat mail!")
def podaciStudenta(request, username):
    studentNalog = Nalog.objects.get(username = username)
    context = { 'student' : Student.objects.get(nalog=studentNalog) }
    return render(request, 'studserviceapp/podaciStudenta.html', context)

def uploadSliku(request):
    nalog = Nalog.objects.get(username = request.POST['nalog'])
    student = Student.objects.get(nalog = nalog)
    pic = request.FILES['pic']
    fs = FileSystemStorage()
    filename = fs.save(pic.name, pic)
    student.slika = fs.url(filename)
    student.save()
    return HttpResponse("Uspesno dodata slika")



def predajeStudentima(request, username):
    profesorNalog = Nalog.objects.get(username = username)
    profesor = Nastavnik.objects.get(nalog=profesorNalog)
    context = { 'predmeti' : {} }
    for predmet in profesor.predmet.all():
        context['predmeti'][predmet.naziv] = []
        for izbornaGrupa in IzbornaGrupa.objects.all():
            if predmet in izbornaGrupa.predmeti.all():
                context['predmeti'][predmet.naziv].append(izbornaGrupa)
    return render(request, 'studserviceapp/predajeStudentima.html', context)

def izbornaGrupaList(request, group):
    studenti = " "
    for student in Student.objects.all():
        try:
            izborGrupe = IzborGrupe.objects.get(student=student)
        except IzborGrupe.DoesNotExist:
            continue
        izbornaGrupa = IzbornaGrupa.objects.get(oznaka_grupe=izborGrupe.izabrana_grupa.oznaka_grupe)
        if(izbornaGrupa.oznaka_grupe==group):
            if student.slika and hasattr(student.slika, 'url'):
                studenti += "<a href=" + student.slika.url + ">" + student.ime + "</a><br/>"
            else:
                studenti += student.ime + "<br/>"
    return HttpResponse("Spisak studenata za grupu %s : <br/> %s" % (group, studenti))

def submitRasporedPolaganja(request):
    return render(request,'studserviceapp/submitRasporedPolaganja.html')

def do_submitRasporedPolaganja(request):
    if 'dokument' in request.FILES:
        tip_rasporeda = request.POST['tip_rasporeda']
        naziv_rasporeda = request.POST['naziv_rasporeda']
        file = request.FILES['dokument']
        file = file.read().decode('UTF-8')
        file = io.StringIO(file)
        dokument = csv.reader(file)

    else:
        tip_rasporeda = request.POST['tip_rasporeda']
        naziv_rasporeda = request.POST['naziv_rasporeda']
        predmeti = request.POST.getlist('predmet[]')
        profesori = request.POST.getlist('profesor[]')
        ucionice = request.POST.getlist('ucionice[]')
        vreme = request.POST.getlist('vreme[]')
        dan = request.POST.getlist('dan[]')
        datum = request.POST.getlist('datum[]')

        dokument = []

        for i in range(len(predmeti)):
            dokument.append([predmeti[i],"","",profesori[i],ucionice[i],vreme[i],dan[i],datum[i]])


    if(tip_rasporeda=='klk_nedelja'):
        errors,to_correct = import_data(dokument,klk_nedelja=naziv_rasporeda)
    else:
        errors,to_correct = import_data(dokument,ispitni_rok=naziv_rasporeda)
    if not errors:
        return HttpResponse("Uspesno ste izvrsili ubacivanje rasporeda")
    else:
        context = {'errors':errors,'to_correct':to_correct,'tip_rasporeda':tip_rasporeda,'naziv_rasporeda':naziv_rasporeda}
        return render(request,'studserviceapp/submitRasporedPolaganja_failed.html',context)
    

        
