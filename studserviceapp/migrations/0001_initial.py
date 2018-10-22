# Generated by Django 2.1.2 on 2018-10-20 11:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Grupa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oznaka_grupe', models.CharField(max_length=10)),
                ('smer', models.CharField(max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='IzborGrupe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ostvarenoESPB', models.IntegerField()),
                ('upisujeESPB', models.IntegerField()),
                ('broj_polozenih_ispita', models.IntegerField()),
                ('upisuje_semestar', models.IntegerField()),
                ('prvi_put_upisuje_semestar', models.BooleanField()),
                ('nacin_placanja', models.CharField(max_length=30)),
                ('upisan', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='IzbornaGrupa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oznaka_grupe', models.CharField(max_length=20)),
                ('oznaka_semestra', models.IntegerField()),
                ('kapacitet', models.IntegerField()),
                ('smer', models.CharField(max_length=20)),
                ('aktivna', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Konsultacije',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mesto', models.CharField(max_length=50)),
                ('vreme_od', models.TimeField()),
                ('vreme_do', models.TimeField()),
                ('dan', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Nalog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=200)),
                ('lozinka', models.CharField(max_length=100, null=True)),
                ('uloga', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Nastavnik',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ime', models.CharField(max_length=200)),
                ('prezime', models.CharField(max_length=200)),
                ('titula', models.CharField(max_length=20, null=True)),
                ('zvanje', models.CharField(max_length=40, null=True)),
                ('nalog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studserviceapp.Nalog')),
            ],
        ),
        migrations.CreateModel(
            name='Obavestenje',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datum_postavljanja', models.DateTimeField()),
                ('tekst', models.CharField(max_length=1000)),
                ('fajl', models.FileField(upload_to='')),
                ('postavio', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='studserviceapp.Nalog')),
            ],
        ),
        migrations.CreateModel(
            name='Predmet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('naziv', models.CharField(max_length=200)),
                ('espb', models.IntegerField(null=True)),
                ('semestar_po_programu', models.IntegerField(null=True)),
                ('fond_predavanja', models.IntegerField(null=True)),
                ('fond_vezbe', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RasporedNastave',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datum_unosa', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='RasporedPolaganja',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ispitni_rok', models.CharField(max_length=50, null=True)),
                ('kolokvijumska_nedelja', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Semestar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vrsta', models.CharField(max_length=20)),
                ('skolska_godina_pocetak', models.IntegerField()),
                ('skolska_godina_kraj', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ime', models.CharField(max_length=200)),
                ('prezime', models.CharField(max_length=200)),
                ('broj_indeksa', models.IntegerField()),
                ('godina_upisa', models.IntegerField()),
                ('smer', models.CharField(max_length=20)),
                ('grupa', models.ManyToManyField(to='studserviceapp.Grupa')),
                ('nalog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studserviceapp.Nalog')),
            ],
        ),
        migrations.CreateModel(
            name='Termin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oznaka_ucionice', models.CharField(max_length=50)),
                ('pocetak', models.TimeField()),
                ('zavrsetak', models.TimeField()),
                ('dan', models.CharField(max_length=15)),
                ('tip_nastave', models.CharField(max_length=15)),
                ('grupe', models.ManyToManyField(to='studserviceapp.Grupa')),
                ('nastavnik', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='studserviceapp.Nastavnik')),
                ('predmet', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='studserviceapp.Predmet')),
                ('raspored', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studserviceapp.RasporedNastave')),
            ],
        ),
        migrations.CreateModel(
            name='TerminPolaganja',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ucionice', models.CharField(max_length=100)),
                ('pocetak', models.TimeField()),
                ('zavrsetak', models.TimeField()),
                ('datum', models.DateField()),
                ('nastavnik', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='studserviceapp.Nastavnik')),
                ('predmet', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='studserviceapp.Predmet')),
                ('raspored_polaganja', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studserviceapp.RasporedPolaganja')),
            ],
        ),
        migrations.CreateModel(
            name='VazniDatumi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kategorija', models.CharField(max_length=200)),
                ('oznaka', models.CharField(max_length=200)),
                ('datum_od', models.DateField(null=True)),
                ('datum_do', models.DateField(null=True)),
                ('okvirno', models.CharField(max_length=200, null=True)),
                ('skolska_godina', models.CharField(max_length=15)),
            ],
        ),
        migrations.AddField(
            model_name='rasporednastave',
            name='semestar',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='studserviceapp.Semestar'),
        ),
        migrations.AddField(
            model_name='nastavnik',
            name='predmet',
            field=models.ManyToManyField(to='studserviceapp.Predmet'),
        ),
        migrations.AddField(
            model_name='konsultacije',
            name='nastavnik',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studserviceapp.Nastavnik'),
        ),
        migrations.AddField(
            model_name='konsultacije',
            name='predmet',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='studserviceapp.Predmet'),
        ),
        migrations.AddField(
            model_name='izbornagrupa',
            name='predmeti',
            field=models.ManyToManyField(to='studserviceapp.Predmet'),
        ),
        migrations.AddField(
            model_name='izbornagrupa',
            name='za_semestar',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='studserviceapp.Semestar'),
        ),
        migrations.AddField(
            model_name='izborgrupe',
            name='nepolozeni_predmeti',
            field=models.ManyToManyField(to='studserviceapp.Predmet'),
        ),
        migrations.AddField(
            model_name='izborgrupe',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='studserviceapp.Student'),
        ),
        migrations.AddField(
            model_name='grupa',
            name='semestar',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='studserviceapp.Semestar'),
        ),
    ]