# 🎬 Kupina – Sistem za preporuku filmova

Kupina je web aplikacija razvijena u okviru projekta iz predmeta **Obrada velikog skupa podataka**. Cilj projekta je razvoj sistema za preporuku filmova korišćenjem tehnika obrade velikih podataka i algoritama mašinskog učenja.

Aplikacija omogućava korisnicima da pretražuju filmove, ocenjuju ih, prave listu omiljenih filmova i dobijaju personalizovane preporuke na osnovu prethodnih ocena.

---

# Korišćene tehnologije

### Backend
- Python
- Flask
- Flask-Login

### Obrada velikih podataka
- Apache Spark (PySpark)
- Spark SQL
- Spark MLlib (ALS)

### Baza podataka
- MongoDB

### Frontend
- HTML
- CSS
- JavaScript
- Chart.js

---

# Skup podataka

Za razvoj sistema korišćen je **MovieLens 1M** skup podataka koji sadrži približno:

- 1.000.000 ocena
- 6.040 korisnika
- 3.952 filma

Podaci su importovani u MongoDB, nakon čega se obrađuju pomoću Apache Spark-a.

---

# Pokretanje projekta

## Preduslovi

Pre pokretanja projekta potrebno je instalirati:

- Python 3.12+
- MongoDB Community Server
- Java (JDK 17 ili noviji)
- Apache Spark (ukoliko nije konfigurisan kroz PySpark)

---

## 1. Kloniranje repozitorijuma

```bash
git clone https://github.com/ZeleniBrokoli/Kupina.git
cd Kupina
```

---

## 2. Kreiranje virtuelnog okruženja

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

## 3. Instalacija potrebnih biblioteka

```bash
pip install -r requirements.txt
```

Za Spark deo projekta:

```bash
pip install -r requirements-spark.txt
```

---

## 4. Pokretanje MongoDB servera

Pokrenuti lokalni MongoDB server.

---

## 5. Kreiranje `.env` fajla

U root direktorijumu projekta potrebno je kreirati `.env` fajl.

Primer sadržaja:

```env
TMDB_API_KEY=YOUR_API_KEY
SECRET_KEY=YOUR_SECRET_KEY
```

---

## 6. Učitavanje MovieLens skupa podataka

MovieLens 1M skup podataka nalazi se u direktorijumu:

```text
dataset/ml-1m/
```

Početni `.dat` fajlovi konvertuju se u CSV format komandom:

```bash
python dataset/scripts/convert_movielens_to_csv.py
```

Nakon konverzije nastaju fajlovi:

- `users.csv`
- `movies.csv`
- `ratings.csv`

CSV fajlovi se zatim učitavaju u MongoDB bazu `kupina`:

```bash
python dataset/scripts/import_csv_to_mongodb.py
```

Skripta kreira i popunjava kolekcije:

- `users`
- `movies`
- `ratings`

Pri ponovnom pokretanju postojeće MovieLens kolekcije se brišu i podaci se učitavaju iznova.

## 7. Pokretanje Spark dela projekta (Pokretanje Jupyter Notebook-a)

Pokrenuti:

```bash
jupyter notebook
```

Otvoriti notebook **Kupina_Spark_Analysis.ipynb** i izvršiti sve ćelije redom.

Notebook:

- izvršava Spark analize;
- trenira ALS model;
- generiše preporuke;
- čuva rezultate u MongoDB kolekcije:
  - `spark_analytics`
  - `recommendations`
  - `als_model_metrics`.

---

## 8. Pokretanje web aplikacije

Pokretanje aplikacije:

```bash
python backend/app.py
```

Nakon pokretanja aplikacija je dostupna na:

```
http://localhost:5000
```

# Funkcionalnosti

Aplikacija omogućava:

- registraciju i prijavu korisnika
- pretragu filmova
- pregled detalja o filmu
- ocenjivanje filmova
- dodavanje filmova u Watchlist
- ostavljanje komentara
- prikaz personalizovanih preporuka
- prikaz analitičkih izveštaja i grafikona

---

# Sistem preporuke

Za generisanje preporuka korišćen je **ALS (Alternating Least Squares)** algoritam iz biblioteke Spark MLlib.

Proces rada:

1. učitavanje ocena iz MongoDB baze;
2. priprema i filtriranje podataka;
3. treniranje ALS modela;
4. evaluacija modela pomoću RMSE metrike;
5. generisanje preporuka za svakog korisnika;
6. čuvanje preporuka u MongoDB;
7. prikaz preporuka kroz web aplikaciju.

---

# Analitika

Spark se koristi za generisanje različitih analitičkih izveštaja, uključujući:

- najviše ocenjene filmove;
- filmove sa najboljom prosečnom ocenom;
- najaktivnije korisnike;
- raspodelu ocena;
- raspodelu aktivnosti korisnika;
- broj filmova po decenijama;
- prosečnu ocenu po žanru;
- odnos broja ocena i prosečne ocene filma.

Rezultati se čuvaju u MongoDB i prikazuju kroz interaktivne grafikone.

---

# Struktura projekta

```
Kupina
│
├── backend/        # Flask aplikacija
├── spark/          # Spark obrada podataka i sistem preporuke
├── scripts/        # Pomoćne skripte
├── database/       # Fajlovi vezani za bazu
├── main.py
├── requirements.txt
└── README.md
```

---

# Moguća unapređenja

- hibridni sistem preporuke;
- preporuke zasnovane na sadržaju filma;
- optimizacija hiperparametara ALS modela;

---

# Autor

Projekat je razvijen kao studentski projekat u okviru predmeta **Obrada velikog skupa podataka** na Prirodno-matematičkom fakultetu Univerziteta u Nišu.