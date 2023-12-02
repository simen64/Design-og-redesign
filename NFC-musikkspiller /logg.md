
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

Jeg bestemte meg for å prøve å lage en nettside til prosjektet som gjør det lett å legge til album. Det jeg ikke visste var at denne nettsiden ville bli et veldig mye mer komplisert prosjekt enn det jeg trodde. og det ville ta opp mange flere timer enn det jeg trodde.

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
Alt dette gjør er å vise en tittel som sier: Moderne Vinylspiller, Album database  
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

### Input

For at denne nettsiden skal gjøre det den skal, trenger den en måte å ta input fra en bruker for å så putte det i en database.  
Brukeren må putte inn en spotidy URI (Spotify sin måte å identifisere albumer og sanger) og en knapp for å legge til.
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
### Igjen, ikke det fineste, men det funker
![Nettside input](https://github.com/simen64/Design-og-redesign/blob/2ae3e525a9f1c3b587786947fbb12024ea22d071/NFC-musikkspiller%20/Bilder/nettside-input.png)
(Dette skjermbildet ble tatt før jeg endret knappen til: "Add album or song")

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
Vi starter med å definere en funksjon som heter `link_to_id` med `def link_to_id(link):` En funksjon er en blokk med kode som kan tilkalles andre steder i koden. Det at `link` er i parantes betyr at når man tilkaller funksjonen gir man den også informasjonen til `link` I dette eksemplet la oss si at linken vi gir til funksjonen ser slik ut: `https://open.spotify.com/track/7Grz4hgSBRdEPj6Vxm991i?si=aeb28778c8f44a99`
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

### Funksjonalitet

Så nå har vi sånn Ca. hvordan nettsiden skal se ut, men den vanskelige delen er å få den til å faktisk ha funksjonalitet.
Jeg har laget et veldig simplifisert flowchart på hvordan nettsiden funker, men jeg skal gå mere inn i dybden.  

![Nettside flowchart](https://github.com/simen64/Design-og-redesign/blob/5e27eaa167fa5a92ebe3d79af23bebaeb501e0a6/NFC-musikkspiller%20/Bilder/Nettside%20flowchart.jpg)

### Prosessen i detaljer

La oss gå gjennom hvordan nettsiden fungerer i mere detlaje. Vi kan starte med front enden, altså hvordan tabellen blir generert.  
For at tabellen skal bli generert trenger den å se i databasen med alle albumene og sangene.

### Databasen

Som jeg viser i flowcharten har jeg bestemt meg for å bruke JSON som databsen min i en seperat fil som heter `albums.json`. JSON er et tekstformat som er laget for å gjøre det lett å lagre små mengder informasjon.  
Det er bygget opp sånn her:
```JSON
{
  "Album Navn":"Sports"
  "Album ID":"0001"
},
{
  "Album Navn":"Rose"
  "Album ID":"0002"
}
```
Måten den er strukturert gjør det lett for programmet mitt å lete gjennom alle albumene for å finne den som matcher tagen som ble scannet.

### Webserveren

Måten jeg har kodet webserveren er i Python med et tilegg som heter Flask, flask gjør det lett å sette opp nettsider med data som blir sendt ogsåvidere.

