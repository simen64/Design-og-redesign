
# En moderne vinyl / musikk spiller

## Ideen

Idden er å ha en boks hvor man kan scanne en eller annen form for fysisk ting for å spille av musikk. Denne fysiske tingen skal ha album coveret på seg så man kan se hvilke album man spiller av. Litt som en vinylspiller.

Funksjoner jeg vil ha med:
- Spille av musikk gjennom Home Assistant og Spotify
- Lett måte å legge til ny musikk
- fint utseende
- lys ellerno
- pause musikken når man tar av platen

## Planen

### Hjernen

Hjernen til prosjektet skal være en SBC (single board computer) eller en mikroprosesor. Dette kan være en Arduino, Raspberry Pi, eller en form for ESP development board. Jeg har en god del variasjoner av disse  som ligger å støver, ettersom at jeg har kjøpt en god del av dem til enten prosjekter som ikke ble noe av eller bare for å eksperimentere. Denne "Hjernen" skal styre alt, som å spille av musikken, finne ut hvilke album som er scannet, og holde koden til prosjektet. Hvis hjernen er en SBC, kan jeg også bruke det som en server i tilegg til å være en musikkspiller.

### Scanneren

For å scanne albumet skal jeg feste NFC-klistremerker på det som skal være den fysiske tingen. Et NFC-klistremerke / NFC-tag er et lite klistremerke med en veldig liten databrikke som kan holde små mengder med data, som en ID til et album. Disse NFC-klistremerkene har jeg hatt en bunke av liggende å støve, ettersom jeg kjøpte masse av dem for å bruke rundt i huset til automasjoner.
NFC-klistremerkene oppererer med teknologien NfcA, Mifare Ultralight, og Ndef.
Scanneren jeg har tenkt til å bruke er en RC5200 RFID scanner. Selvom denen scanneren egentlig er laget for en annen teknologi (RFID istedenfor NFC) støtter den mifare ultralight, som skal gjøre det mulig å scanne mine NFC klistremerker. Når NFC-klistremerket har blitt scannet finner den IDen til albumet, og sender det til hjernen.

### Å spille av musikk

For å spill av musikk har jeg tenkt til å gå gjennom Home assistant. Home assistant er et self hosted smarthus kontrollsenter, her har jeg tilkoblet høytalerne jeg tenker å bruke. Home assistant støøter webhooks som er en måte for enheter å sende data en vei til en server ved hjelp av http (web linker) Når et album er scannet skal SBCen finne ut hvilke album det er, sende dette med en webhook over til homeassistant, som gjennom Spotify sin API spiller det av på høytaleren jeg har bestemt.

## Flowchart
![Musikkspiller_flowchart](https://github.com/simen64/Design-og-redesign/blob/b5c3e3b5bfac3fbb8e957e4738b0917208530f8e/NFC-musikkspiller%20/Bilder/Musikkspiller_flowchart.jpg)

## Arduino

Planen først var å bruke en Arduino som hjernen. Arduinoer er et elektronikk-brett med en mikroprosessor. De er veldig kjent for å brukes i elektronikk prosjekter som det her. Arduinoen har strøm, og data utganger som gjør den bra til å koble til komponenter. Jeg har hatt noen Arduinoer av forrige generajon liggende siden 2019, og har ikke egentlig brukt dem sins. Jeg fikk de til julegave sammen med masse andre elektroniske komponenter, som endte opp med å komme til nytte nå 4 år senere.

For at prosjektet skal fungere trenger den å ha tilgang til Wifi, noe min arduino ikke har. Heldigvis har jeg også en ESP8266 modul som jeg også fikk sammen med Arduinoen. En esp8266 er også en mikroprosessor, bare at den har innebygd wifi. Det som er med den modulen jeg har er at den ikke har en USB til å programmere den, heller ikke nok GPIO porter (Porter for å koble til komponenter) Fordi den mangler dette koblet jeg den opp til Arduinoen min gjennom serie kommunikasjon (en måte å sende data på gjennom ledninger)

## Oppkobling
![Arduino oppkobling](https://github.com/simen64/Design-og-redesign/blob/86e651944495e410128a51a4ffa52c13428fa7e2/NFC-musikkspiller%20/Bilder/Arduino%20oppkobling.png)

### Serie kommunikasjon

For å kommunisere med ESP8266 modulen kan jeg bruke en serie monitor for å sende kommandoer til prosessoren, en sånn serie monitor er bygd inn i programvaren Arduino IDE, som er programmet jeg bruker til å kode til arduinoen.
Et problem jeg endte opp med å ha var at siden jeg hadde koblet ESP8266 modulen til Arduinoen sine serie porter, ble det konflikt med USBen som lastet koden over. Derfor måtte jeg plugge ut modulen vær gang jeg lastet opp ny kode, for å så plugge den inn igjen. Koden jeg lastet opp til Arduinoen inneholdte ikke noe, fordi jeg for nå bare trengte å bruke serie kommandoer for å kommunisere med ESP8266 modulen.

Jeg startet med å sjekke at jeg hadde koblet til riktig:
```
AT

OK
```
Når man mottar OK tilbake er det som regel et godt tegn.

Etter dette koblet jeg den til wifi nettverket mitt, med denne kommandoen:
```
AT+CWJAP=\"Wifi SSID\",\"Wifi Passord\"\r"

OK
```
I innstillingene til ruteren min kunne jeg verifisere at den var tilkoblet.

### Programmering

Jeg måtte kode et program til Arduinoen som automatiserte å putte inn disse kommandoene, siden det er variasjoner av de som skal brukes til å forespørre en webhook.  
`SoftwareSerial` er en pakke for Arduino som gjør det lett å sende kommandoer til moduler som er oppkoblet med serie porter.    
Her er koden jeg lagde for å automatisk koble meg til wifi hver gang Arduinoen blir skrudd på.  

```cpp
#include <SoftwareSerial.h> //inkluder SoftwareSerial pakken

SoftwareSerial ESP8266(0, 1); // Si til software serial hvor modulen er koblet inn og hva den skal hete

void setup() {
  ESP8266.begin(115200);  // Start serial kommunikasjonen med en baud rate på 115200

  ESP8266.println("AT+CWJAP=\"Wifi SSID\",\"Wifi Passord\"\r");

}

void loop() {
}
```

En annen kul ting SoftwareSerial kan gjøre er å bruke virtuelle porter som pin 2, og 3 for å kommunisere gjennom serie. Dette hadde fikset konflikten med USB-kablen.
Men når jeg prøvde dette endte det opp med å funke så jeg bare holdt meg til pin 0, og 1 selvom det skapte konflikter. Hva problemet var kommer jeg tilbake til senere.

Koden jeg hadde lagde fungerte, og alt jeg puttet inn i `ESP8266.println("")` ble kjørt som om jeg sendte kommandoen gjennom Serie monitor.  
Jeg skulle nå begynne på å få webhooks til å fungere.

### Webhooks og HTTP requests

Ifølge Espressif (De som lager ESP modulene) er dette kommandoene jeg skal putte inn for å sende en webhook (I dette eksemplet bruker jeg // for kommentarer disse hadde ikke funket om man hadde inkludert dem i kommandoene)

```
AT+CIPSTART="TCP","192.168.125.77",8123 // her starter vi kommunikasjonen med Home Assistant serveren. For IP adressen har jeg valgt tilfeldige tall for tredde og fjere oktett. Men porten 8123 er ekte.

AT+CIPSEND // fortell prosessoren at vi skal sende data, og spesifiser dataen
POST /api/services/media/play
Host: 192.168.125.77:8123
Authorization: Bearer ACCESS TOKEN
Content-Type: application/json

{
  "album": "sports"
}
AT+CIPCLOSE // End tilkoblingen
```

Men dette funket ikke, fordi ingenting skjedde i Home Assistant, jeg prøvde flere variasjoner men ingen funket.  
Wireshark er et program man bruker for å inspisere nettverks-trafikk.  
I wireshark filtrerte jeg på MAC adressen til ESP8266 modulen som jeg hentet fra innstillingene til ruteren min.  
Når jeg plugget inn og ut Arduinoen kunne jeg se at den koblet seg opp mot nettet:  

![Wireshark capture av at ESP8266 kobler til Wifi](https://github.com/simen64/Design-og-redesign/blob/22ef5045d6702a6e93ce154a2b9e5bc327a0faa5/NFC-musikkspiller%20/Bilder/Wireshark_ESP8266_connect.png)

Jeg har strøket over all personlig informasjon som IP adresser og MAC adresser  
Hver av disse linjene er det som kalles en packet.  
Packet nummer 344 er en broadcast for å koble seg til nettet  
Nummer 345 Ser etter DHCP servere på nettet  
Nummer 346 Spør om en IP fra DHCP serveren  
Nummer 347 Sjekker om noen enheter har IPen 192.168.x.x, nummer 348 gjentar dette for å dobbeltsjekke  
Nummer 348 annonserer at den har tatt IPen 192.168.x.x

Mens når jeg sendte kommandoen som skulle sende webhooken, skjedde ingenting i Wireshark.  
For å verifisere at ESP8266 modulen faktisk kunne kommunisere med Home Assistant pinget (En måte å sjekke om man har kommunikasjon til en server eller klient) jeg den med kommandoen `AT+PING="192.168.125.77"`
Og hva skjedde? Jo den kom fram.

![Wireshark capture av ping til HA](https://github.com/simen64/Design-og-redesign/blob/95fce086cf4167f07ed15089a7fa0fab81d15931/NFC-musikkspiller%20/Bilder/ESP8266_Ping.png)

### Problemet

Jo hva var problemet? Når jeg først leste meg opp på hvordan jeg skulle koble opp ESP8266 modulen til arduinoen sto det at jeg måtte passe på fordi ESP modulen tar 3,3V og arduinoen sender ut 5V. Jeg trodde dette bare var for tilkoblingen som gir strøm til modulen, derfor koblet jeg den inn i 3,3V porten til arduinoen. Det jeg glemte å ta inn i konsiderasjon var at de også mente serie portene. Alle arduino portene man bruker til å koble komponenter til sender ut 5V med strøm, mens portene på ESP modulen bare skal ha 3,3V. Jeg tror ikke at jeg har ødelagt modulen, men denne forskjellen i volt kan gjøre at signalet blir korrupt som gjør at det ikke kommer fram, at virtuelle porter ikke funker med `SoftwareSerial`, og det kan ødelegge modulen etterhvert.

### Løsningen

For å fikse dette problemet må man bruke det som heter en biodirectional logic level shift converter, dette er bare et fancy ord for et elektronisk komponent som gjør 5v til 3,3v for data.
Ettersom at dette ikke er noe jeg har liggende, og jeg har ikke materialene til å bygge min egen, må jeg enten kjøpe en eller finne en annen for for hjerne. Siden denne komponenten kostet rundt 150kr bestemte jeg meg for å heller se om jeg kunne finne en annen elektronisk komponent som en hjerne.

## En annen hjerne

Av elektroniske komponenter som jeg har hjemme som ikke er i bruk var det to jeg kunne bruke.  

Første valg er en Raspberry Pi Pico W. Dette er en veldig billig og liten enhet med en mikroprosessor, og den har innebygd wifi! Jeg kjøpte en mengde av disse for eksperimentering for en god stund siden så jeg har en god del liggende. Dette høres bra ut ettersom at det er egentlig alt jeg har bedt om og en annen pluss side er at den kan kodes med python som jeg skjenner bedre enn c++ som arduinoer bruker. Men det er en ting som gjør disse enhetene nesten ubrukelig til alle sånne her litt større prosjekter, lagring. Lagringsplassen på en Pico W er bare 2 MB! Dette kan kanskje være nok for den rene koden pluss firmwaret (det som gjør at koden kjører på enheten) Men det det ikke er plass til er en mengde med pakker for å styre komponenter, wifi etc.

Det andre valget mitt er en Raspberry Pi 1b+ Dette er en veldig gammel generasjon av hoved linjen til Raspberry Pi, men for et prosjekt som dette kan det funke. Denne raspberry PIen er egentlig en mini pc som kjører Linux, noe jeg er godt kjent med hvordan man setter opp og holder oppe. Dette gir en rekke med fordeler som at den kan kjøre flere ting samtidig, den kjører fortsatt python (eller alt annent jeg vil bruke), den har nok lagring, den har massevis av porter til å koble til komponenter. Eneste tingen med denne veldig gamle versjonen er at den ikke kommer med innebygd wifi, dette planlegger jeg å fikse med å koble til en wifi USB adapter. Som du kanskje har forstått er dette planen. Men hvor kom denne fra? Jeg har hatt denne liggende lenge siden jeg fikk den fra stefaren min siden han ikke brukte den lenger. Nylig har jeg brukt den til å hoste en discord bot, men den brukes nesten aldri lenger så det skal ikke ha noe å si.

### Wifi adapter

Stefaren min hadde også en gammel usb wifi adapter liggende som jeg kunne få. Problemet med de fleste wifi adaptere er at de ikke har drivere for Linux, heldigvis hadde den eldgamele D-Link adapteren en driver som het `carl9170` som jeg kunne laste ned med pakken `firmware-linux-free` Etter det var det bare å putte navnet og passordet på nettverket mitt i raspberry PIen sin `wpa-supplicant.txt` fil, og etter en restart hadde jeg Wifi! Men det kan jo selvfølgelig ikke gå problemløst. Det viste seg at denne adapteren var veldig ustabil og SSH tilkoblingen min (En måte å kommunisere trådløst mellom to PCer) falt ut hele tiden. Jeg kom på at jeg hadde lånt en annen wifi adapter til Herman for en stund siden. Jeg spurte han om han fortsatt brukte den, noe han ikke gjorde. Etter å ha hentet den plugget jeg den inn og alt funket uton noe mere styr.

## Nettside

Jeg bestemte meg for å prøve å lage en nettside til prosjektet som gjør det lett å legge til album og sanger. Det jeg ikke visste var at denne nettsiden ville bli et veldig mye mer komplisert prosjekt enn det jeg trodde. og det ville ta opp mange flere timer enn det jeg trodde.

### Struktur

Jeg har personlig aldri kodet i HTML, CSS, Javascript, eller Flask, som er alle de programmeringsspråkene man bruker til å lage en nettside, så dette var helt nytt for meg. Målet med denne nettsiden er å gjøre det lett å legge til nye album i databasen til musikkspilleren. Dette betyr at nettsiden trenger en front end (det brukeren ser på skjermen) og en back end (det som skjer bak i serveren som å legge sangene til en database)
Det første jeg satt ut på å lære var HTML, som er strukturen til nettsiden. I min mening virker ikke HTMl som en veldig vanskelig ting å bruke. Man kan jo selvfølgelig gjøre det mer vanskelig med å lage mere komplekse nettsider. Teknisk sett er heller ikke HTML et programmeringsspråk, men et markeringsspråk for å strukturere tekst.
Her er koden for titlen på nettsiden:  
```html
<!DOCTYPE html>
<html>
<head>

<title>Moderne vinylspiller</title>

<h1>Moderne Vinylspiller, Album database:</h1>

</head>
<body>
</body>
</html> 
```
Alt dette gjør, er å vise en tittel som sier: Moderne Vinylspiller, Album database  
Neste jeg bestemte for å finne ut hvordan man gjorde var å legge til en tabell. Dette er hvor man skal kunne se alle albumene.  
Igjen så var ikke dette så veldig vanskelig:
```html
<table id="album_table">
    <tr>
        <th>Album-cover</th>
        <th>Album navn</th>
        <th>Album ID</th>
    </tr>
    <tr>

    </tr>
</table> 
```
### Det er kanskje ikke den fineste nettsiden, men den får fram poenget.

![Nettside med tabell](https://github.com/simen64/Design-og-redesign/blob/efcd7c3f0cea810994046d6398d68d4006d614df/NFC-musikkspiller%20/Bilder/Nettside_tabell.png)

Senere bestemte jeg meg for at nettsiden skulle støtte både album og sanger så jeg redigerte titlene litt. Den nye "Delete" knappen kommer jeg tilbake til.

![Nytt nettside design](https://github.com/simen64/Design-og-redesign/blob/d7908f4cdbdf0de4cb119cf444a9f5163ef35dfc/NFC-musikkspiller%20/Bilder/newest_website_design.png)

### Funksjonalitet

Så nå har vi sånn ca. hvordan nettsiden skal se ut, og hvordan den tar input, men den vanskelige delen er å få den til å faktisk ha funksjonalitet.
Jeg har laget et veldig simplifisert flowchart på hvordan nettsiden funker, men jeg skal gå mere inn i dybden.  

![Nettside flowchart](https://github.com/simen64/Design-og-redesign/blob/5e27eaa167fa5a92ebe3d79af23bebaeb501e0a6/NFC-musikkspiller%20/Bilder/Nettside%20flowchart.jpg)

### Prosessen i detaljer

La oss gå gjennom hvordan nettsiden fungerer i mere detalje. Vi kan starte med front enden, altså hvordan tabellen blir generert.  
For at tabellen skal bli generert, trenger den å se i databasen med alle albumene og sangene.

### Databasen

Som jeg viser i flowcharten, har jeg bestemt meg for å bruke JSON som databasen min i en seperat fil som heter `albums.json`. JSON er et tekstformat som er laget for å gjøre det lett å lagre små mengder informasjon.  
Det er bygget opp sånn her:
```JSON
{
    "cover": "https://news.artnet.com/app/news-upload/2023/06/HAPO7184_M_Pink_Floyd_DSOTM_Photo_Cover_RT_PF_GT-1024x1024.jpg",
    "name": "Sample album",
    "uri": "spotify:album:2WT1pbYjLJciAR26yMebkH",
    "id": "5841841343875"
},
{
    "cover": "https://i.scdn.co/image/ab67616d0000b27360a89b781c62ffe2136e4396",
    "name": "Superache",
    "uri": "spotify:album:5hIOd0FvjlgG4uLjXHkFWI",
    "id": "13843847223479"
}
```
Måten den er strukturert gjør det lett for programmet mitt å lete gjennom alle albumene for å finne den som matcher "tagen" som ble scannet.

### Flask

Måten jeg har kodet webserveren er i Python med et tilegg som heter Flask. Flask gjør det lett å sette opp nettsider med data som blir sendt også videre.
Flask er delt opp i funksjoner for hver underlink. En funksjon er en blokk med kode som kan tilkalles andre steder i koden.
I dette eksemplet sier vi at nettsiden vår har linken `nettside.no`  
I flask kan vi definere en funksjon som det her:

```python
@app.route('/')
def home():
   return "Hei nettside!"
```

Dette betyr at når brukeren går til `nettside.no/` vil de bli vist det her:  
![Hei nettside](https://github.com/simen64/Design-og-redesign/blob/be3dd6c51b5579e2808c9d8c2619789154e282b6/NFC-musikkspiller%20/Bilder/Hei_nettside.png)

Definerer vi en funksjon som det her:

```python
@app.route('/kul_tekst')
def home():
   return "Kul tekst!"
```

Betyr det at hvis brukeren nå går til `nettside.no/kul_tekst` vil det her bli vist:  
![Kul tekst](https://github.com/simen64/Design-og-redesign/blob/ca2a529635c0485c5d01dc841723bdc2cac77889/NFC-musikkspiller%20/Bilder/kul_tekst.png)

Så for hjemsiden til nettsiden, må vi vise fram tabellen jeg har vist tidligere. Så vi definerer en funksjon for `/` Her bruker vi `return render_template` for å laste inn filen som har nettsiden og tabellen jeg gikk over i [struktur](#struktur) delen. Filen heter `index.html`

```python
@app.route('/')
def home():
   data = load()
   return render_template("index.html", data=data)
```
Men for å skjønne hva `data = load()` og `data=data` gjør må vi først se på hva `load()` gjør.

```python
def load():
   with open("database.json", 'r') as file:
         return json.load(file)
```

Funksjonen er ganske lett. Den åpner opp filen `database.json` og leser den (derfor er "r" der) dette puttes i variablen `file`
så returnerer vi inneholdet til databasen til det som opprinnelig tilkalte funksjonen. Denne funksjonen kommer til å bli brukt flere ganger i koden, så ha i bakhode hva den gjør.  
Nå vet vi at i vår opprinnelige funksjon for hjemsiden til nettsiden blir inneholdet til databasen lagret i `data`  
Med `data=data` sender vi denne informasjonen over til `index.html` som inneholder strukturen til nettsiden, men også javacript funksjonen som genererer tabellen. Det å sende over denne informasjonen heter "Jinja".

### Generering av tabellen i Javascript

Javascript er et annet programmeringsspråk som brukes for laging av nettsider. I mitt tilfelle er det det som genererer tabellen med sangene og albumene fra databasen.  

Så for å motta dataen fra Jinja må vi definere en variabel som vi kaller `data` og putte dataen i JSON format fra Jinja der.

```js
var data = {{ data|tojson }};
```

Etter dette, på samme måte som vi definerte en funksjon i python, definerer vi en funksjon i javascript med dataen fra Jinja

```js
function buildTable(data){}
```

For at Javascript skal vite at vi snakker om tabellen vi lagde i [struktur](#struktur) delen, har vi gitt tabellen IDen: `table`
Derfor kan vi bruke denne linjen med kode for å si til Javascript at det er denne tabellen vi snakker om. Dette blir puttet i variablen `table`

```js
var table = document.getElementById('table')
```

Denne delen ser veldig komplisert ut, men enkelt forklart gjør den det neste vi skal gå gjennom for hvert element i databasen.
```js
for (var i = 0; i < data.length; i++){}
```

Dette er kodeblokken som blir gjentatt for hvert element i databasen:
```js
var row = `<tr>
               <td style="text-align: center;"><img src="${data[i].cover}" width="100" height="100"></td>

                  <td>${data[i].name}</td>

                  <td>${data[i].id}</td>

                  <td>
                     <form action="/delete" method="post" onsubmit="return confirm('Are you sure you want to delete that album?')";>
                        <button type="submit" name="delete" value="${data[i].id}">Delete</button>
                     </form>
               </td>

            </tr>`
			table.innerHTML += row
```

Vi skal gå gjennom hver linje.  

```js
var row =
```
Betyr rett å slett at alt inni dette er en rad i tabellen. Og alle de bokstavene du ser i krokodilletegn som `<tr>` forteller HTML (det vi bruker til å kode strukturen til nettsiden) hvordan den skal vise dataen vi gir den. `<tr>` betyr at dette er en "tabel row"

```js
<td style="text-align: center;"><img src="${data[i].cover}" width="100" height="100"></td>
```

`<td>` betyr "table data" og dette er for album eller sang coveret. Vi starter med å bruke `style=` for å si at bildet skal være i midten med `text-align: center;` HTML sin innebygde `<img src= >` funksjon viser et bilde fra linken spesifisert fra `src=` Den litt kompliserte `${data[i].cover}` delen kort forklart henter verdien `cover` fra `data` variablen. Som hvis vi ser på databasen igjen ser at `cover` inneholder en link til cover bildet.

```json
{
   "cover": "https://news.artnet.com/app/news-upload/2023/06/HAPO7184_M_Pink_Floyd_DSOTM_Photo_Cover_RT_PF_GT-1024x1024.jpg",
   "name": "Sample album",
   "uri": "spotify:album:2WT1pbYjLJciAR26yMebkH",
   "id": "5841841343875"
}
```
`Width` og `height` sier seg selv og bestemmer at bilde skal være 100x100 piksler stort.

```js
<td>${data[i].name}</td>

<td>${data[i].id}</td>
```
For både navnet og IDen til sangen eller albumet bruker vi samme måte til å hente informasjonen fra `data variablen`

```js
<td>
   <form action="/delete" method="post" onsubmit="return confirm('Are you sure you want to delete that album?')";>
      <button type="submit" name="delete" value="${data[i].id}">Delete</button>
   </form>
</td>
```
Dette er den mest kompliserte av alle dataene i tabellen. Her lager vi en "Delete"-knapp for hvert album eller sang. Vi starter med å putte alt i en `<form action>` Dette er en måte å sende data over til webserveren ved hjelp av POST request (en link som kan inneholde data) Her er det bare en "submit" knapp, hvor det står "Delete". Linken jeg har spesifisert denne til å sende til er `/delete` Jeg skal om litt forklare hvordan dette funker i på server-siden. Vi ser også at det er en `onsubmit` funksjon her, dette her gjør at når du klikker på "Delete" kommer det opp et vindu som spør om du er sikker på at du vil slette det, og du kan velge "Ok" eller "Cancel". Dette er for å forhidre at man med uhell sletter album eller sanger.
På `<button>` tagen spesifiserer vi en value, dette er det som blir sendt til serveren. I denne valuen henter vi ut IDen til albumet eller sangen på samme måte vi har gjort på de andre radene. Dette brukes så webserveren vet hva som skal slettes.

#### Server-siden
For at albumet eller sangen skal slettes, må det gjennom webserveren. I form-actionen over har vi allerede bestemt at IDen til det som skal slettes må sendes til `/delete` Derfor definerer vi dette i Flask:

```python
@app.route("/delete",methods = ["POST", "GET"])
def delete():
```
Her er en ny ting, `methods` Dette sier at vi kan motta både POST og GET (det man vanligvis bruker for å se en nettside) -requests. Når man klikker på "Delete" knappen, er den en POST request som inneholder IDen til albumet eller sangen.

```python
if request.method == "POST":
```
Vi startet med å sjekke om det er en POST request for å vite om vi faktisk skal slette et album.

```python
id = request.form["delete"]
```
Så bruker vi `request.form` for å hente informasjonen fra POST requesten, og putte den i variablen `id`

```python
temp = load()
```
Etter vi har IDen bruker vi `load()` funksjonen igjen for å laste databasen inn i variablen `temp`

```python
for item in temp:
   if 'id' in item and item['id'] == id:

      temp.remove(item)

      with open("database.json", "w") as file:
         json.dump(temp, file, indent=4)

   else:
      pass
```
Dette er algoritmen som sletter albumet eller sangen, la oss gå gjennom det.  
```python
for item in temp:
```
Det betyr at vi gjør det her for hvert element i databasen, samme konsept som i Javascript.
```python
if 'id' in item and item['id'] == id:
```
Her bruker vi en `if` funksjon for å sjekke om IDen til albumen eller sangen matcher med IDen vi har fått beskjed om å slette.
```python
temp.remove(item)

with open("database.json", "w") as file:
   json.dump(temp, file, indent=4)
```
Så hvis IDene matcher sletter vi den sangen eller albumet fra databasen. Etter det bruker vi `with open` på samme måte som i `load()` funksjonen, bare at nå bruker vi "w" for å indikere at vi skal skrive til filen. Så skriver vi den oppdaterte informasjonen uten den slettede elementet til databasen igjen.
```python
return redirect(url_for("home"))
```
Etter alt dette bruker vi dette for å sende brukeren tilbake til hjemsiden.

#### Tilbake til Javascript

Siste del av funksjonen vår for å bygge ut tabellen er det her:
```js
table.innerHTML += row
```
Dette er det som faktisk setter sammen tabellen.

Utafor funksjonen som bygger tabellen kjører vi det her:
```js
buildTable(data)
```
Dette tilkaller funksjonen, og gjør at hver gang siden lastes inn på nytt oppdateres tabellen.

### Input

For at denne nettsiden skal gjøre det den skal, trenger den en måte å ta input fra en bruker for å så putte det i en database.  
Brukeren må putte inn en spotify URI (Spotify sin måte å identifisere albumer og sanger) og en knapp for å legge til.
For å gjøre dette brukte jeg det som kalles for en `form action` Dette er en funksjon som tar en input, og så sender informasjonen til serveren med en link. Dette kalles for en POST request. POST er måten en nettside kan sende ting til servere.

```html
<form id="Form" action="/send_data" method="post" onsubmit="return showAlert()">
    <p>Enter Album / Song Link or URI</p>
    <p><input type="text" name="raw-input" /></p>
    <p><input type="submit" value="Add album or song" /></p>
</form>
```

Etter brukeren har klikket på "Add album or song" utføres javascript funksjonen `showAlert()` Denne funksjonen forteller brukeren at de skal plassere "tagen" som skal kobles til denne sangen eller albumet på scanneren. Etter at den har blitt scannet sendes dataen over til serveren. Hva som skjer med dataen, kommer jeg tilbake til.

```javascript
function showAlert() {
        // Show the alert
        window.alert('Plasser NFC/RFID tag på skanneren, og vent til siden er ferdig med å laste');
        
        // Return true to allow the form submission
        return true;
    }
```

#### Igjen, ikke det fineste, men det funker
![Nettside input](https://github.com/simen64/Design-og-redesign/blob/2ae3e525a9f1c3b587786947fbb12024ea22d071/NFC-musikkspiller%20/Bilder/nettside-input.png)  
(Dette skjermbildet ble tatt før jeg endret knappen til: "Add album or song")

#### Motta input i Flask

For å motta dataen i webserveren, så den kan bli puttet i databasen må vi definere en funksjon for linken der dataen sendes. Som her er til `/send_data`

```python
@app.route('/send_data',methods = ['POST', 'GET'])
def album_data():
   if request.method == 'POST':
```
På lik måte som når vi lagde funksjonen for "Delete-knappen" sjekker vi først om det er en POST request (altså at linken inneholder data)
```python
raw_input = request.form["raw-input"]
```
Dette er også veldig likt som "Delete" funksjonen, hvor vi putter Spotify URIen i variablen `raw_input`

#### Link til URI
Som jeg nevnte måtte man putte inn en Spotify URI, for å gjøre denne prosessen enklere har jeg kodet en funksjon som gjør linker om til URIer. Så nå kan man putte inn begge to i nettsiden.  
Her er hvordan det funker.

```python
def link_to_id(link):
   link = link.replace("https://open.spotify.com/album/", "")
   link = link.replace("https://open.spotify.com/track/", "")
   link = link.split("?")
   print(link)
   link.pop(1)
   id = link[0]
   return id

if "https://" in raw_input:
   
   if "album" in raw_input:
      id = link_to_id(raw_input)
      raw_input = "spotify:album:" + id

   elif "track" in raw_input:
      id = link_to_id(raw_input)
      raw_input = "spotify:track:" + id
```

La oss gå gjennom hver seksjon.  
Vi starter med å definere en funksjon som heter `link_to_id` med `def link_to_id(link):` Det at `link` er i parantes betyr at når man tilkaller funksjonen gir man den også informasjonen til `link` I dette eksemplet la oss si at linken vi gir til funksjonen ser slik ut: `https://open.spotify.com/track/7Grz4hgSBRdEPj6Vxm991i?si=aeb28778c8f44a99` Målet med denne funksjonen er å ta linken, og gjøre den om til bare IDen som i dette eksemplet er `7Grz4hgSBRdEPj6Vxm991i`
De to linjene:
```python
link = link.replace("https://open.spotify.com/album/", "")
link = link.replace("https://open.spotify.com/track/", "")
```
Bytter ut både `https://open.spotify.com/album/` og `https://open.spotify.com/track/` med tomrom, grunnen til at vi har begge er fordi `/album/`er for album, og `/track/` er for sanger.  
I vårt eksempel er det en sang, så nå står vi igjen med:
```
7Grz4hgSBRdEPj6Vxm991i?si=aeb28778c8f44a99
```
Det vi vil ha er IDen, som her er:
```
7Grz4hgSBRdEPj6Vxm991i
```
Det betyr at vi må fjerne alt etter og inkludert spørsmålstegnet.  
```python
link = link.split("?")
``` 
Dette splitter opp linken vår i to. Nå står vi igjen med en liste som inneholder:
```python
["7Grz4hgSBRdEPj6Vxm991i", "?si=aeb28778c8f44a99"]
```
Dette betyr at vi bare trenger å fjerne element nummer 1 i listen (I python starter alt med 0, så liste element nummer 1 vil være `?si=aeb28778c8f44a99`)  
Vi fjerner dette med:
```python
link.pop(1)
```
Så definerer vi id som liste element 0, med:
```python
id = link[0]
```
Sist men ikke minst returner vi dette til det som opprinnelig tilkalte funksjonen.
```python
return id
```

Nå som vi vet hvordan denne funksjonen fungerer kan vi gå videre til resten av koden.  
Etter at vi har fått inputet fra brukeren som her er linken, sjekker vi om det er en link eller en URI.  
Dette gjør vi med:
```python
if "https://" in raw_input:
```
Det sjekker om `https://` er i det brukeren ga oss. Hvis det er det kan vi være ganske sikre på at det er en link.  
Etter dette må vi sjekke om det er en album eller en sang.
```python
if "album" in raw_input:
      id = link_to_id(raw_input)
      raw_input = "spotify:album:" + id
```
Dette gjør vi med å sjekke om ordet `album` er i linken. Hvis det er et album tilkaller vi funksjonen vår som gjør linken om til en id, dette betyr at vi får tilbake: `7Grz4hgSBRdEPj6Vxm991i`  
Så for å gjøre dette til en gyldig Spotify URI som kan sendes til spotify legger vi til `spotify:album:` Da står vi igjen med: `spotify:album:7Grz4hgSBRdEPj6Vxm991i` som er en gyldig spotify URI  
Funksjonen for sanger er nesten det samme bare bytte ut `album` med `track`:
```python
elif "track" in raw_input:
      id = link_to_id(raw_input)
      raw_input = "spotify:track:" + id
```

#### Lagre dataen

Nå står vi igjen med en Spotify URI som i dette eksemplet ser sånn her ut: `spotify:album:7Grz4hgSBRdEPj6Vxm991i`  
Her er den fulle koden (Uten delen for sanger):  

```python
if "album" in raw_input:

         album_spotify_id = raw_input.replace("spotify:album:", "")
         print(album_spotify_id)

         #Use spotifys api to get info about the album
         album_info = sp.album(album_spotify_id)

         #Get the album name and cover
         album_link = album_info['images'][0]['url']
         album_name = album_info["name"]

         #Structure the new data
         data = {
            "cover": album_link,
            "name": album_name,
            "uri" : raw_input,
         }

      session['data'] = data

      return redirect(url_for("scan"))
```

Vi skal jo selvfølgelig gå gjennom hver del.  
Som du kanskje ser sjekker vi igjen om det er et album eller en sang. Jeg kommer bare til å gå over album funksjonen, fordi begge er ganske like.
```python
if "album" in raw_input:
```
Dette er måten jeg sjekker om det er et album eller ikke, og siden vår URI inneholder "album" vet vi at det er et album.  
Nå skal vi gjøre noe som kanskje virker litt idiotisk med tanke på det vi akkuratt gjorde i `link_to_id` funksjonen. Men vi lager en ny variabel hvor vi fjerner `spotify:album:` fra URIen så vi bare står igjen med IDen som ser slik ut: `7Grz4hgSBRdEPj6Vxm991i`  
Med det her henter vi informasjon om albumet med hjelp fra Spotify, og lagrer det i variablen `album_indo`
```python
album_info = sp.album(album_spotify_id)
```
Ut fra vår nyinnhentet data om albumet kan vi splitte dataen opp til informasjonen vi faktisk trenger:
```python
album_link = album_info['images'][0]['url']
album_name = album_info["name"]
```
`album_link` for linker til album coveret, og `album_name` for navnet til albumet.  
Etter dette strukturer vi dataen i formatet som brukes i databasen:
```python
data = {
   "cover": album_link,
   "name": album_name,
   "uri" : raw_input,
}
```
Men istedenfor å skrive dette rett til databasen lagrer vi det i en session:
```python
session['data'] = data
```
Noe som er lagret i en session er det samme som det "cookies" er, som man må akseptere for å bruke nettsiden.
Grunnen til at vi ikke skriver det rett til databasen er fordi det er en ting vi mangler, derfor sender vi brukeren til en annen link:
```python
return redirect(url_for("scan"))
```
Det vi mangler er IDen til "tagen" som skal scannes for å spille musikken. Som du kanskje husker, når man legger til et nytt album eller en ny sang, ber den deg scanne NFC-tagen din. Det er det vi skal gjøre nå.
```python
@app.route("/scan")
def scan():
```
Som vi har gjort for alle andre linker definerer vi dem først i Flask.  
Dette er koden som scanner NFC-tagen:
```python
id = reader.read()

id_from_scan = id[0]
id_from_scan = str(id_from_scan)

GPIO.cleanup()
```
`id = reader.read()` ber scanneren om å lete etter en tag, når en tag har blitt scannet lagres dataen den finner i variablen `id` og koden fortsetter.

#### Scanner problemet

Planen vår originalt å skrive et tall til "tagene" som leseren skal kunne lese. Når jeg først skrev et program for å lese en tag gjorde jeg det sånn her:
```python
id, text = reader.read()
print(id)
print(text)
```
Dette skal i teorien printe IDen til tagen (Alle NFC-tager har en ID som blir gitt under produksjon som ikke kan endres) og teksten skrevet på tagen. Resultatet jeg fikk av dette var:
```
58274839234
"AUTH ERROR!!
AUTH ERROR(status2reg & 0x08) != 0"
```
Som man ser først fungerer det å printe IDen, men teksten ikke så bra. "AUTH ERROR" betyr at noe har gått galt under en autentikasjon med tagen, selvom tagen ikke har noe passord eller enkrypsjon. På linje 3 ser vi `0x08` dette er en referanse til et sted i minne til tagen. Etter litt googling fant jeg ut at ikke bare det var jeg som hadde dette problemet. Det som gjør at det feiler er at programmet som kjører på scanneren ble sist oppdatert for 7 år siden, og tagene jeg har er nyere enn det. Så autentikasjonen dems fungerer ikke. Men hvordan skulle jeg nå gjøre prosjektet mitt? Jo siden IDen fortsatt fungerer kan jeg bruke den til å forbinde dem med album. Dette gjør også at man slipper å skrive en ID til en tag. Derfor scanner man tagen når man legger den til i nettsiden.

#### Tilbake til input

```python
id = reader.read()

id_from_scan = id[0]
id_from_scan = str(id_from_scan)

GPIO.cleanup()
```
Som sagt er dette koden jeg bruker nå.  
IDen man får fra scanneren er formatert i det som kalles for en "tuple" som er slik ut:
```python
("519383492", " ")
```
Det vi vil ha er bare det tallet, som en string (strings er tekstformat i programmering)  
Derfor setter vi `id_from_scan` til element nummer 0 i tuplen som gir oss dette:
```
519383492
```
Problemet her er at dette er en integer og ikke en string (Integers er tall i programmering)  
Så vi bruker dette for å gjøre det om til en string:
```
id_from_scan = str(id_from_scan)
```
Nå står vi igjen med det vi trenger, IDen i en string:
```python
"519383492"
```

Etter vi har fått IDen bruker vi `load()` funksjonen igjen for å laste databasen av album til variablen temp.
```python
temp = load()
```
Så kjører vi det som virker som en ganske komplisert funksjon:
```python
for item in temp:
   if 'id' in item and item['id'] == id_from_scan:
      print("Error, cant have two albums / songs with the same ID")
      return redirect(url_for("ID_conflict"))
```
I "menneske språk" betyr dette: for hvert element i databasen, sjekk om IDen matcher med IDen fra scannen, hvis den gjør det si ERROR  
Dette er for å forhindre at to album har samme tag forbundet med seg. På samme måte som på hjem funksjonen bruker vi `return redirect` for å sende brukeren til en annen link. Funksjonen for denne linken ser sånn her ut:
```python
@app.route("/ID_conflict")
def ID_conflict():
   return render_template("ID_conflict.html")
```
Den ligner veldig på hjem funksjonen, og det er fordi den gjør nesten det samme. Denne viser fram HTML filen `ID_conflict.html`  
Koden for denne nettsiden er veldig simpel og ser sånn her ut:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error ID conflict</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            text-align: center;
            padding: 50px;
        }

        .error-message {
            font-size: 24px;
            color: #000000;
            margin-bottom: 20px;
        }

        .home-button {
            display: inline-block;
            padding: 10px 20px;
            background-color: #c1c1c1;
            color: #000000;
            font-size: x-large;
            text-decoration: none;
            border-radius: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="error-message">
        <p>Error, you cant have two albums bound to the same NFC/RFID tag</p>
    </div>

    <button class="home-button" onclick="window.location.href = '/'">Go back home</button>
</body>
</html>

```
Hvis man ignorerer alt innenfor `<style>` tagene, ser man at dette egentlig bare er en error melding og en knapp for å gå tilbake  
![ID conflict](https://github.com/simen64/Design-og-redesign/blob/6948e8086821f71447895406d89acf95056f7057/NFC-musikkspiller%20/Bilder/Id_conflict.png)

Men hvis vår "if" funksjon ikke finner noen matchende IDer i databasen kan den gå videre.  
Hvis du husker så puttet vi dataen vi fikk om albumet eller sangen fra spotify i en session cookie som så slik ut:
```python
data = {
   "cover":track_album_cover,
   "name":track_name,
   "uri": raw_input
}
```
Denne dataen henter vi inn igjen til en variabel vi kaller `data`
```python
data = session.get('data')
```
Så med den here linjen legger vi til "id" til dataen som inneholder IDen vi fikk fra scanneren:
```python
data['id'] = id_from_scan
```
Nå ser data variablen vår sånn her ut:
```python
data = {
   "cover":track_album_cover,
   "name":track_name,
   "uri": raw_input,
   "id": id_from_scan
}
```
Siden vi har lastet databasen vår inn i variablen `temp` kan vi "appende" (legge til) denne nye dataen til datbasen:
```python
temp.append(data)
```
Når dette er gjort kan vi skrive den nye dataen til database filen:
```python
with open("database.json", "w") as file:
   json.dump(temp, file, indent=4)
```
Sist men ikke minst sender vi brukeren tilbake hjem:
```python
return redirect(url_for("home"))
```
Og når brukeren laster inn hjem siden bygger javascript tabellen på nytt som nå har med den nylige lagt til sangen eller albumet.