# Koristi ovo ako pokreces iz konzole
# import sys
# sys.path.insert(0, '../')

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studservice.settings")
import django

django.setup()

from studserviceapp.models import Predmet,Nastavnik,Nalog
import csv

FILE_NAME = "raspored.csv"

def skip(row):
	if(not row): # Ako je prazan
		return True

	if(row[0]=='Svi smerovi, odeljenje 1'): # Prvi red
		return True

	if(row[1]=='Predavanja' or row[1]=='Nastavnik(ci)'): # Nazivi kolona
		return True

	return False

def process_nastavnik(row,curr_predmet,offset):
	if(row[offset]):
		nastavnik = None
		prezime,ime = row[offset].split(" ")[:2]
		if(Nastavnik.objects.filter(ime=ime,prezime=prezime).exists()): # Ako nastavnik vec postoji u bazi
			nastavnik = Nastavnik.objects.get(ime=ime,prezime=prezime)
		else:
			username = (ime[0] + prezime).lower() if ime else prezime.lower()
			nalog = Nalog.objects.create(username=username,uloga="nastavnik")
			nastavnik = Nastavnik.objects.create(ime=ime,prezime=prezime,nalog=nalog)
		nastavnik.predmet.add(curr_predmet)

def process_row(row,curr_predmet):
	for i in [1,9,17,25]:
		process_nastavnik(row,curr_predmet,i)
	
with open(FILE_NAME,encoding='utf-8') as f:
	raspored_csv = csv.reader(f,delimiter=";")
	curr_predmet = None
	for row in raspored_csv:
		if(skip(row)):
			continue
		if(len(row)==2):
			curr_predmet = Predmet.objects.create(naziv=row[0])
		else:
			process_row(row,curr_predmet)



