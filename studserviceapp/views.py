from django.shortcuts import render

import csv
import io

import json

# Create your views here.
from django.http import HttpResponse
from .models import *

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from .parse_raspored_polaganja import import_data
from .send_gmail import create_and_send_message

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

def podaciStudenta(request, username):
    studentNalog = Nalog.objects.get(username = username)
    student = Student.objects.get(nalog=studentNalog)
    slikaUrl = ''
    if student.slika.name:
        slikaUrl = student.slika.url
    context = { 'student' : student, 'slikaURL' : slikaUrl }
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
        context = {'errors':errors,'to_correct':to_correct,'tip_rasporeda':tip_rasporeda,
        'naziv_rasporeda':naziv_rasporeda}
        return render(request,'studserviceapp/submitRasporedPolaganja_failed.html',context)
    

def sendMail(request, username):
    nalog = Nalog.objects.get(username=username)
    uloga = nalog.uloga
    opcije_predmeti = []
    opcije_grupe = []
    opcije_smer = []

    if username=='jmarkovic16': uloga = 'administrator'

    if (uloga == "student"):
        return HttpResponse("Student ne moze da salje email-ove!")

    elif(uloga == "nastavnik"):
        person = Nastavnik.objects.get(nalog=nalog)

        predmetiID = []
        for predmet in person.predmet.through.objects.all():
            if(predmet.nastavnik_id == person.nalog_id):
                predmetiID.append(predmet.predmet_id)
        for predmet in Predmet.objects.all():
            if predmet.id in predmetiID:
                opcije_predmeti.append(predmet)

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
                opcije_grupe.append(grupa)

    else:
        person = nalog;
        for grupa in Grupa.objects.all():
            if not(grupa in opcije_grupe):
                opcije_grupe.append(grupa)
            if  (not grupa.smer in opcije_smer and grupa.smer!=None):
                opcije_smer.append(grupa.smer)
        for predmet in Predmet.objects.all():
            if not(predmet in opcije_predmeti):
                opcije_predmeti.append(predmet)

    opcije_smer.sort()
    opcije_grupe.sort(key = lambda x : x.oznaka_grupe)
    opcije_predmeti.sort(key = lambda x : x.naziv)
    context = {'person' : person,
                'uloga' : uloga,
                'opcije_predmeti' : opcije_predmeti,
                'opcije_grupe' : opcije_grupe,
                'opcije_smer' : opcije_smer}

    return render(request,'studserviceapp/mailForm.html',context)

def mailSent(request):
    to_list = []
    sender = " "
    body = " "
    subject = " "
    file = None

    if 'body' in request.POST:
         body = request.POST['body']
    if 'subject' in request.POST:
        subject = request.POST['subject']
    if 'uloga' in request.POST:
        if request.POST['uloga']=='nastavnik':
            sender = request.POST['sender-prof'] + "@raf.rs"
        else:
            sender = request.POST['sender'] + "@raf.rs"
    if 'file' in request.POST:
        file = request.POST['file']
    nalog_id = []
    student_id = []
    if 'to' in request.POST:
        primalac = request.POST['to']
        if primalac == 'svi':
            for student in Student.objects.all():
                nalog_id.append(student.nalog_id)
        elif primalac in request.POST['to_smer']:
            for student in Student.objects.all():
                if student.smer == primalac:
                    nalog_id.append(student.nalog_id)
        elif primalac in request.POST['to_grupe']:
            for student in Student.grupa.through.objects.all():
                if student.grupa_id == int(primalac):
                    nalog_id.append(Student.objects.get(id=student.student_id).nalog_id)
        else:
            for predmet in Predmet.objects.all():
                if primalac in predmet.naziv:
                    terminiID = []
                    for termin in Termin.objects.all():
                        if (termin.predmet_id==predmet.id):
                            ter = termin
                            terminiID.append(termin.id)
                    terminGrupe = ter.grupe.through.objects.all()
                    grupeID = []
                    for grupa in terminGrupe:
                        if(grupa.termin_id in terminiID):
                            grupeID.append(grupa.grupa_id)
                    for grupa in Grupa.objects.all():
                        if grupa.id in grupeID:
                            for student in Student.grupa.through.objects.all():
                                if student.grupa_id == grupa.id:
                                    nalog_id.append(Student.objects.get(id=student.student_id).nalog_id)
                    break

    for nalog in Nalog.objects.all():
        if nalog.id in nalog_id:
            create_and_send_message("Test",sender,nalog.username+"@raf.rs",subject,body,file)
    return HttpResponse("Uspesno poslat email!")

def home(request, username):
    nalog = Nalog.objects.get(username = username)
    linkovi = {}
    raspored =[]
    if nalog.uloga == 'student':
        student = Student.objects.get(nalog=nalog)
        for termin in Termin.objects.all():
            if student.grupa.get() in termin.grupe.all():
                terminGrupe = termin.grupe.order_by('oznaka_grupe').first().oznaka_grupe
                for grupa in termin.grupe.order_by('oznaka_grupe'):
                    terminGrupe += ', ' + grupa.oznaka_grupe
                raspored.append([termin.predmet.naziv, termin.tip_nastave, termin.nastavnik.ime + " " + termin.nastavnik.prezime, terminGrupe, termin.dan, termin.pocetak.strftime("%H:%M") + '-' + termin.zavrsetak.strftime("%H:%M"), termin.oznaka_ucionice])
        linkovi['Ceo Raspored'] = 'http://127.0.0.1:8000/studserviceapp/raspored'
        linkovi['Podaci Studenta'] = 'http://127.0.0.1:8000/studserviceapp/podaciStudenta/'+nalog.username
        if IzbornaGrupa.objects.count() > 0:
            linkovi['Izbor Grupe'] = 'http://127.0.0.1:8000/studserviceapp/izborgrupe/'+nalog.username
    elif nalog.uloga == 'nastavnik':
        nastavnik = Nastavnik.objects.get(nalog=nalog)
        for termin in Termin.objects.all():
            if nastavnik == termin.nastavnik:
                terminGrupe = termin.grupe.order_by('oznaka_grupe').first().oznaka_grupe
                for grupa in termin.grupe.order_by('oznaka_grupe'):
                    terminGrupe += ', ' + grupa.oznaka_grupe
                raspored.append(
                    [termin.predmet.naziv, termin.tip_nastave, termin.nastavnik.ime + " " + termin.nastavnik.prezime,
                     terminGrupe, termin.dan,
                     termin.pocetak.strftime("%H:%M") + '-' + termin.zavrsetak.strftime("%H:%M"),
                     termin.oznaka_ucionice])
        linkovi['Ceo Raspored'] = 'http://127.0.0.1:8000/studserviceapp/raspored'
        linkovi['Predaje Studentima'] = 'http://127.0.0.1:8000/studserviceapp/predajeStudentima/' + nalog.username
        linkovi['Slanje Mejla'] = 'http://127.0.0.1:8000/studserviceapp/mail/' + nalog.username
    elif nalog.uloga == 'sekretar':
        for termin in Termin.objects.all():
            terminGrupe = termin.grupe.order_by('oznaka_grupe').first().oznaka_grupe
            for grupa in termin.grupe.order_by('oznaka_grupe'):
                terminGrupe += ', ' + grupa.oznaka_grupe
            raspored.append(
                [termin.predmet.naziv, termin.tip_nastave, termin.nastavnik.ime + " " + termin.nastavnik.prezime,
                 terminGrupe, termin.dan,
                 termin.pocetak.strftime("%H:%M") + '-' + termin.zavrsetak.strftime("%H:%M"),
                 termin.oznaka_ucionice])
        linkovi['Unos Obavestenja'] = 'http://127.0.0.1:8000/studserviceapp/raspored'
        linkovi['Slanje Mejla'] = 'http://127.0.0.1:8000/studserviceapp/mail/' + nalog.username
        linkovi['Izborne Grupe'] = 'http://127.0.0.1:8000/studserviceapp/izborneGrupe'
        linkovi['Spisak Studenata'] = 'http://127.0.0.1:8000/studserviceapp/groupList'
    else:
        for termin in Termin.objects.all():
            terminGrupe = termin.grupe.order_by('oznaka_grupe').first().oznaka_grupe
            for grupa in termin.grupe.order_by('oznaka_grupe'):
                terminGrupe += ', ' + grupa.oznaka_grupe
            raspored.append(
                [termin.predmet.naziv, termin.tip_nastave, termin.nastavnik.ime + " " + termin.nastavnik.prezime,
                 terminGrupe, termin.dan,
                 termin.pocetak.strftime("%H:%M") + '-' + termin.zavrsetak.strftime("%H:%M"),
                 termin.oznaka_ucionice])
        linkovi['Unos Obavestenja'] = 'http://127.0.0.1:8000/studserviceapp/raspored'
        linkovi['Slanje Mejla'] = 'http://127.0.0.1:8000/studserviceapp/mail/' + nalog.username
        linkovi['Unos Grupe'] = 'http://127.0.0.1:8000/studserviceapp/newGroup'
        linkovi['Izborne Grupe'] = 'http://127.0.0.1:8000/studserviceapp/izborneGrupe'
        linkovi['Spisak Studenata'] = 'http://127.0.0.1:8000/studserviceapp/groupList'
    grupe = []
    for grupa in Grupa.objects.all():
        grupe.append(grupa.oznaka_grupe)
    grupe.sort()

    nastavnici = []
    for nastavnik in Nastavnik.objects.all():
        nastavnici.append(nastavnik.ime + ' ' + nastavnik.prezime)
    nastavnici.sort()

    ucionice = set()
    for termin in Termin.objects.all():
        ucionice.add(termin.oznaka_ucionice)
    ucionice = list(ucionice)
    ucionice.sort()

    obavestenja = []
    for obavestenje in Obavestenje.objects.order_by('datum_postavljanja')[0:5]:
        fajl = ''
        if obavestenje.fajl.name:
            fajl = obavestenje.fajl.url
        obavestenja.append([obavestenje.postavio, obavestenje.datum_postavljanja.strftime("%Y-%m-%d %H:%M:%S"), obavestenje.tekst, fajl])

    context = \
        {
            'linkovi' : json.dumps(linkovi),
            'raspored' : json.dumps(raspored),
            'grupe' : json.dumps(grupe),
            'nastavnici' : json.dumps(nastavnici),
            'ucionice' : json.dumps(ucionice),
            'obavestenja' : json.dumps(obavestenja)
        }
    return render(request, 'studserviceapp/home.html', context)