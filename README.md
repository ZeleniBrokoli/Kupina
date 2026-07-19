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

# Pokretanje projekta

## 1. Instalacija biblioteka

```bash
pip install -r requirements.txt
```

## 2. Pokretanje MongoDB baze

Pokrenuti lokalni MongoDB server.

## 3. Kreirati `.env` fajl

Primer sadržaja:

```env
TMDB_API_KEY=YOUR_API_KEY
SECRET_KEY=YOUR_SECRET_KEY
```

## 4. Pokrenuti Spark skripte

Izvršiti skripte za:

- učitavanje podataka,
- analitiku,
- treniranje ALS modela,
- generisanje preporuka.

## 5. Pokrenuti aplikaciju

```bash
python main.py
```

---

# Moguća unapređenja

- hibridni sistem preporuke;
- preporuke zasnovane na sadržaju filma;
- optimizacija hiperparametara ALS modela;

---

# Autor

Projekat je razvijen kao studentski projekat u okviru predmeta **Obrada velikog skupa podataka** na Prirodno-matematičkom fakultetu Univerziteta u Nišu.