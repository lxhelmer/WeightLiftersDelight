# Voimaharjoittelu tietokantasovellus
Sovelluksessa voidaan tallentaa ja seurata voimaharjottelutuloksia ja niiden kehitystä.
Tuloksia voi tallentaa liikkeen ja ajankohdan mukaan.
Muita tallennettavia tietoja ovat käyttäjän kilpailuluokka (painoluokka ja sukupuoli)
Tietoja voidaan hakea käyttäjäkohtaisten tulosten mukaan sekä kilpailuluokan mukaan.
Lähtökohtaisesti tietokannat sisältävät perinteiset voimanosto ja painonnostoliikkeet.
Lisäksi voidaan toteuttaa ominaisuus lisätä seurattavia liikkeitä.
Tuloksia voi seurata taulukkoina sekä kaavioina.

# Käyttäjät
Sovelluksessa on kaikille näkyvä näkymä julkisista tiedoista.
Sovellukseen voi kirjautua sisään ja käyttäjätyyppejä on kaksi, peruskäyttäjä sekä hallinnointi käyttäjä. Peruskäyttäjän voi luoda sovelluksessa.
Peruskäyttäjä voi hallinnoida omia tietojaan rajattomasti. Luoda, katsella, poistaa.
Peruskäyttäjä voi valita näkyvätkö hänen tuloksensa kaikille avoimissa julkisissa tilastoissa. Valinta voidaan tehdä tuloskohtaisesti.
Peruskäyttäjä voi myös tarkastella muita peruskäyttäjäprofiileita joissa näkyvät näiden profiilien julkiset tulokset.
Peruskäyttäjä voi poistaa oman tilinsä ja tietonsa profiilistaan.

Hallinnointikäyttäjällä on rajattomat oikeudet.

# Näkymät
Päänäkymät ovat: Julkiset tulokset, profiilikohtaiset tulokset, tuloksen lisäys.

## Ohjelman käyttö

Luo virtuaaliympäristö komennolla 
```bash 
python3 -m venv venv
```
käynnistä virtuaaliympäristö komennolla 
```bash 
source venv/bin/activate
```

Asenna riippuvuuder komennolla
```bash
pip install -r ./requirements.txt
```

Lataa tietokantarakenne tietokantaan komennolla ohjelma käyttää oletusarvona wld nimistä tietokantaa.
```bash
psql <tietokannan nimi> < schema.sql
```

Voit luoda urheilulajit sekä kilpailuluokat seuraavilla komennoilla:
```bash
psql <tietokannan nimi> <  create_classes.sql
psql <tietokannan nimi> <  create_movements.sql
```

Käynnistä ohjelma komennolla
```bash
flask run
```
Ohjelma tarvitsee lisäksi tiedoston .env jossa asetetaan kurssimateriaalin mukaisesti ympäristömuuttujat 'DATABASE_URL' ja 'SECRET_KEY'

## Ohjelman tila 06.08.

Toiminnallisuus on alullaan. Tietokantaan voi lisätä tuloksia ja käyttöliittymä sisältää perusnäkymän jossa lisäys tehdään sekä profile välilehden
jolla voidaan tarkastella tuloksia. Sovellus toimii tällä hetkellä one-user tilassa sillä toteutan käyttäjäkohtaisen toiminnallisuuden samalla kun teen käyttäjänhallinnan kuntoon.
Sovellus on vähän jäljessä siitä tilasta missä sen haluaisin olevan, mutta korjaan tilanteen tällä viikolla. Tietokannan rakenne on tällä hetkellä suppea sillä en ole vielä päättänyt
millä tavalla jaan tiedon. Tietokanta kuitenkin sisältää jo nyt suurimman osan tallennettavasta tiedosta. Sen käyttö on vain tällä hetkellä epäkäytännöllistä.

## Ohjelman tila 07.08 Palautusta 2 täydentävät korjaukset

Ohjelmassa voi nyt tehdä ne asiat mitkä olisin halunnut saada valmiiksi ennen palautusta kaksi. Käyttäjä voi kirjautua sisään sekä luoda uuden perus tason käyttäjän. Käyttäjä voi lisätä sekä tarkastella omia tuloksiaa.
Käyttäjä voi myös filtteröidä tuloksia eri nostotyyppien mukaan. Käyttäjälle näytetään vain käyttäjäkohtaiset tulokset. Käyttäjänhallinta on toteutettu hashattyjä salasanoja säilyttäen sekä flaskin sessionia käyttäen.
Käyttäjä profiili on kaikille käyttäjille saman url '/profile' takana mutta tiedon filtteröinti tapahtuu tietokanta tasolla eikä muitten käyttäjien tietoon kosketa. Jos käyttäjä ei ole kirjautunut sisään ohjataan hänet '/landing'
sivulle mikä on kirjautumis/registeröitymis sivu.

## Ohjelman tila 20.8.
Ohjelma on hyvällä mallilla, puutteet ovat lähinnä käyttöliittymään liittyviä bugeja ja pieniä ominaisuuksia.
Käyttäjä voi:
    Luoda käyttäjän ja valita sille normaalin tai admin tilan.
    Luonnin yhteydessä valita lajinsa sekä painoluokkansa, ohjelma valitsee oikeat luokat ilmoitetun painon mukaan.
    Lisätä tuloksia ja valita minkä lajin tulos.
    Tulokselle voi lisätä tiedon jos se on suoritettu kilpailussa.
    Admin käyttäjä voi lisätä kilpailuja.
    Admin käyttäjällä on oma näkymä joka on tällä hetkellä /users polun takana nappi etusivulla.
    Users välilehdeltä admin voi hallita käyttäjiä sekä heidän tuloksiaan.

