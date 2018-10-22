import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studservice.settings")
import django

django.setup()
from studserviceapp.models import Student, Grupa, Semestar, Nalog

semestar = Semestar(vrsta='neparni', skolska_godina_pocetak=2018, skolska_godina_kraj=2019)
semestar.save()
g301 = Grupa(oznaka_grupe='301', smer='RN', semestar=semestar)
g301.save()
g302 = Grupa(oznaka_grupe='302', smer='RN', semestar=semestar)
g302.save()

lukaNalog = Nalog(username="ldjuric16", uloga="student")
lukaNalog.save()
jovanNalog = Nalog(username="jmarkovic16", uloga="student")
jovanNalog.save()
markoNalog = Nalog(username="msreckovic16", uloga="student")
markoNalog.save()

luka = Student(ime='Luka', prezime='Djuric', broj_indeksa='18', godina_upisa='2016', smer='RN', nalog=lukaNalog)
luka.save()
luka.grupa.add(g302)
jovan = Student(ime='Jovan', prezime='Markovic', broj_indeksa='48', godina_upisa='2016', smer='RN', nalog=jovanNalog)
jovan.save()
jovan.grupa.add(g302)
marko = Student(ime='Marko', prezime='Sreckovic', broj_indeksa='7', godina_upisa='2016', smer='RN', nalog=markoNalog)
marko.save()
marko.grupa.add(g301)

print(Student.objects.all())