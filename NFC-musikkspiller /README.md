
# En moderne vinyl / musikk spiller

## Ideen

Ideen er å ha en boks hvor man kan scanne en eller annen form for fysisk ting for å spille av musikk. Denne fysiske tingen skal ha albumcoveret på seg så man kan se hvilke album man spiller av. Litt som en vinylspiller.

Funksjoner jeg vil ha med:
- Spille av musikk gjennom Home Assistant og Spotify
- Lett måte å legge til ny musikk
- fint utseende
- lys 
- kunne pause musikken når man tar av platen

## Video

[Video showcase av prosjektet](https://youtu.be/5ZSzAxJ7XmM)

## Planen

### Hjernen

Hjernen til prosjektet skal være en SBC (single board computer) eller en mikroprosesor. Dette kan være en Arduino, Raspberry Pi, eller en form for ESP development board. Jeg har en god del variasjoner av disse  som ligger å støver, ettersom at jeg har kjøpt en god del av dem til enten prosjekter som ikke ble noe av eller bare for å eksperimentere. Denne "Hjernen" skal styre alt, som å spille av musikken, finne ut hvilke album som er scannet, og holde koden til prosjektet. Hvis hjernen er en SBC, kan jeg også bruke det som en server i tilegg til å være en musikkspiller.

### Scanneren

For å scanne albumet skal jeg feste NFC-klistremerker på det som skal være den fysiske tingen. Et NFC-klistremerke / NFC-tag er et lite klistremerke med en veldig liten databrikke som kan holde små mengder med data, som en ID til et album. Disse NFC-klistremerkene har jeg hatt en bunke av liggende å støve, ettersom jeg kjøpte masse av dem for å bruke rundt i huset til automasjoner.
NFC-klistremerkene oppererer med teknologien NfcA, Mifare Ultralight, og Ndef.
For å lese av NFC-klistremerket, har tenkt til å bruke en RC5200 RFID scanner. Selvom denne scanneren egentlig er laget for en annen teknologi (RFID istedenfor NFC) støtter den Mifare ultralight, som skal gjøre det mulig å scanne mine NFC klistremerker. Når NFC-klistremerket har blitt scannet finner den IDen til albumet, og sender det til hjernen.

### Å spille av musikk

For å spille av musikk har jeg tenkt til å gå gjennom Home assistant. Home assistant er et self hosted smarthus kontrollsenter, her har jeg tilkoblet høytalerne jeg tenker å bruke. Home assistant støtter webhooks, som er en måte for enheter å sende data en vei til en server ved hjelp av http (web linker) Når et album er scannet skal SBCen finne ut hvilke album det er, sende dette med en webhook over til Homeassistant, som gjennom Spotify sin API spiller det av på høytaleren jeg har bestemt.

## Flowchart
![Musikkspiller_flowchart](https://github.com/simen64/Design-og-redesign/blob/b5c3e3b5bfac3fbb8e957e4738b0917208530f8e/NFC-musikkspiller%20/Bilder/Musikkspiller_flowchart.jpg)

# Arduino

Planen først var å bruke en Arduino som hjernen. Arduinoer er elektronikk-brett med en mikroprosessor. De er veldig kjent for å brukes i elektronikk prosjekter som det her. Arduinoen har strøm, og datautganger som gjør den bra til å koble til komponenter. Jeg har hatt noen Arduinoer av forrige generajon liggende siden 2019, og har ikke egentlig brukt dem siden. Jeg fikk de til julegave sammen med masse andre elektroniske komponenter, som endte opp med å komme til nytte nå 4 år senere.

For at prosjektet skal fungere trenger den å ha tilgang til Wifi, noe min arduino ikke har. Heldigvis har jeg også en ESP8266 modul som jeg også fikk sammen med Arduinoen. En esp8266 er også en mikroprosessor, bare at den har innebygd wifi. Det som er med den modulen jeg har er at den ikke har en USB til å programmere den, heller ikke nok GPIO porter (Porter for å koble til komponenter) Fordi den mangler dette koblet jeg den opp til Arduinoen min gjennom serie kommunikasjon (en måte å sende data på gjennom ledninger)

## Oppkobling
![Arduino oppkobling](https://github.com/simen64/Design-og-redesign/blob/86e651944495e410128a51a4ffa52c13428fa7e2/NFC-musikkspiller%20/Bilder/Arduino%20oppkobling.png)

## Serie kommunikasjon

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

## Programmering

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

Koden jeg hadde laget fungerte, og alt jeg puttet inn i `ESP8266.println("")` ble kjørt som om jeg sendte kommandoen gjennom Serie monitor.  
Jeg skulle nå begynne på å få webhooks til å fungere.

## Webhooks og HTTP requests

Ifølge Espressif (De som lager ESP modulene) er dette kommandoene jeg skal putte inn for å sende en webhook (I dette eksemplet bruker jeg // for kommentarer, disse hadde ikke funket om man hadde inkludert dem i kommandoene)

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

Jeg har strøket over all personlig informasjon som IP adresser og MAC adresser. Hver av disse linjene er hvordan den kobler seg til nettet.

Mens når jeg sendte kommandoen som skulle sende webhooken, skjedde ingenting i Wireshark.  
For å verifisere at ESP8266 modulen faktisk kunne kommunisere med Home Assistant pinget (En måte å sjekke om man har kommunikasjon til en server eller klient) jeg den med kommandoen `AT+PING="192.168.125.77"`
Og hva skjedde? Jo den kom fram.

![Wireshark capture av ping til HA](https://github.com/simen64/Design-og-redesign/blob/95fce086cf4167f07ed15089a7fa0fab81d15931/NFC-musikkspiller%20/Bilder/ESP8266_Ping.png)

## Problemet

Jo hva var problemet? Når jeg først leste meg opp på hvordan jeg skulle koble opp ESP8266 modulen til arduinoen sto det at jeg måtte passe på fordi ESP modulen tar 3,3V og arduinoen sender ut 5V. Jeg trodde dette bare var for tilkoblingen som gir strøm til modulen, derfor koblet jeg den inn i 3,3V porten til arduinoen. Det jeg glemte å ta inn i konsiderasjon var at de også mente serie portene. Alle arduino portene man bruker til å koble komponenter til sender ut 5V med strøm, mens portene på ESP modulen bare skal ha 3,3V. Jeg tror ikke at jeg har ødelagt modulen, men denne forskjellen i volt kan gjøre at signalet blir korrupt som gjør at det ikke kommer fram, at virtuelle porter ikke funker med `SoftwareSerial`, og det kan ødelegge modulen etterhvert.

## Løsningen

For å fikse dette problemet må man bruke det som heter en biodirectional logic level shift converter, dette er bare et fancy ord for et elektronisk komponent som gjør 5v til 3,3v for data.
Ettersom at dette ikke er noe jeg har liggende, og jeg har ikke materialene til å bygge min egen, må jeg enten kjøpe en eller finne en annen for for hjerne. Siden denne komponenten kostet rundt 150kr bestemte jeg meg for å heller se om jeg kunne finne en annen elektronisk komponent som en hjerne.

# En annen hjerne

Av elektroniske komponenter som jeg har hjemme som ikke er i bruk var det to jeg kunne bruke.  

Første valg er en Raspberry Pi Pico W. Dette er en veldig billig og liten enhet med en mikroprosessor, og den har innebygd wifi! Jeg kjøpte en mengde av disse for eksperimentering for en god stund siden så jeg har en god del liggende. Dette høres bra ut ettersom at det er egentlig alt jeg har bedt om, og en annen pluss side er at den kan kodes med python som jeg kjenner bedre enn c++ som arduinoer bruker. Men det er en ting som gjør disse enhetene nesten ubrukelig til alle sånne her litt større prosjekter; lagring. Lagringsplassen på en Pico W er bare 2 MB! Dette kan kanskje være nok for den rene koden pluss firmwaret (det som gjør at koden kjører på enheten) Men det det ikke er plass til er en mengde med pakker for å styre komponenter, wifi etc.

Det andre valget mitt er en Raspberry Pi 1b+ Dette er en veldig gammel generasjon av hoved linjen til Raspberry Pi, men for et prosjekt som dette kan det funke. Denne raspberry PIen er egentlig en mini pc som kjører Linux, noe jeg er godt kjent med hvordan man setter opp og holder oppe. Dette gir en rekke med fordeler som at den kan kjøre flere ting samtidig, den kjører fortsatt python (eller alt annent jeg vil bruke), den har nok lagring, og den har massevis av porter til å koble til komponenter. Eneste tingen med denne veldig gamle versjonen er at den ikke kommer med innebygd wifi, dette planlegger jeg å fikse med å koble til en wifi USB adapter. Som du kanskje har forstått er dette planen. Men hvor kom denne fra? Jeg har hatt denne liggende lenge siden jeg fikk den fra stefaren min siden han ikke brukte den lenger. Nylig har jeg brukt den til å hoste en discord bot, men den brukes nesten aldri lenger så det skal ikke ha noe å si om jeg bytter ut det med dette prosjektet.

# Raspberry pi

## Lys

NFC leseren fortalte jeg om i introen, men ikke noe om lyset fordi det kom jeg ikke til før jeg hadde betsemt meg for å bruke en raspberry pi. Lyset er en neopixel ring som er en ring med i mitt tilfelle 24 forskjellige og individuelle kontrollerbare led lys. Under i diagrammet er det bilde av den. Dette lyset skal jeg bruke som en visuell indikator for når musikken blir spilt, pauset, etc. 

## Oppkobling

Dette er hvordan jeg koblet til komponentene til Raspberry PIen. To ting her er at breadboardet (det hvite brettet med masse hull i) fjernet jeg på slutten av prosjektet, fordi det er der bare for å gjøre det lettere å prototype. Og at ringen med lys her har bare 12 lys mens min har 24, dette endrer derimot ingenting med oppkoblingen.  

<img src="https://github.com/simen64/Design-og-redesign/blob/7829068d9117b87b6acd530d20255a5e9d8b8f63/NFC-musikkspiller%20/Bilder/Raspberry%20pi%20diagram.png" width="550">

## Wifi adapter

Siden ikke jeg vil at musikkspilleren min må være koblet til ruteren hele tiden trenger den wifi, noe ikke Raspberry Pien jeg bruker har. Derfor trenger jeg en USB wifi adapter. Stefaren min hadde en gammel usb wifi adapter liggende som jeg kunne få. Problemet med de fleste wifi adaptere er at de ikke har drivere for Linux, heldigvis hadde den eldgamle D-Link adapteren en driver som het `carl9170` som jeg kunne laste ned med pakken `firmware-linux-free` Etter det var det bare å putte navnet og passordet på nettverket mitt i raspberry PIen sin `wpa-supplicant.txt` fil, og etter en restart hadde jeg Wifi! Men det kan jo selvfølgelig ikke gå problemløst. Det viste seg at denne adapteren var veldig ustabil og SSH tilkoblingen min (En måte å kommunisere trådløst mellom to PCer) falt ut hele tiden. Jeg kom på at jeg hadde lånt en annen wifi adapter til Herman for en stund siden. Jeg spurte han om han fortsatt brukte den, noe han ikke gjorde. Etter å ha hentet den plugget jeg den inn og alt funket uten noe mere styr.

## Linux

Operativsystemet jeg har tenkt til å kjøre er Raspbian lite, dette er en versjon av Debian linux som er det jeg bruker på PCen min hjemme. Jeg valgte å bruke linux fordi det er et veldgi bra operativ-system for servere fordi det tar lite ressurser, er åpen kildekode, lett å sette opp, og jeg er godt kjent med det.

Første steg for å installere Linux på en raspberry pi er å laste Linux ned på et SD-kort. Dette gjør man med "Raspberry Pi imager" som er et program som automatiserer nedlastingen av Linux til SD-kort som kan brukes på Raspberry Pi. Etter jeg hadde SD-kortet mitt med Linux på kunne jeg koble opp Raspberry Pien til ruteren min med en ethernet kabel, og sette SD-kortet inn. Når jeg hadde koblet til strømmen og ventet litt sjekket jeg ruteren sitt kontrollpanel. Her kunne jeg se at den koblet til nettverket og fått IP adressen `192.168.24.24` (Dette er ikke den faktiske IP adressen, som jeg har valgt å gjemme for sikkerhets grunner)

### SSH

SSH er et åpent kildekode prosjekt som gjør det mulig å koble seg til servere over netttet med terminalen. Fordelen med SSH overfor eldre programmer som Telnet er at SSH er enkryptert så ingen på nettet kan "hack" seg inn å se kommandoene som sendes. For å koble til Raspberry PIen med SSH kjørte jeg denne kommandoen:
```
ssh 192.168.24.24
```
Tilbake fikk jeg feilmeldingen:
```
ssh: connect to host 192.168.24.24 port 22: Connection refused
```
Dette betyr at jeg får kommunikasjon med Raspberry PIen, den vil bare ikke la meg komme inn. Jeg vet at passordet er riktig fordi SSH passordet til raspberry pi er alltid `raspberry` når Linux er nyinstallert.  
Det som var problemet var at SSH var der og serveren var tilkoblet, men SSH hadde ikke blitt aktivert. For å fikse dette måtte jeg ta SD-kortet ut igjen og åpne det på PCen min. I `/boot` mappen plasserte jeg en tom fil kalt `ssh` Dette signaliserer til Linux på startup at den skal aktivere SSH.  
Boom, jeg var tilkoblet.

Første man gjør når man har koblet til med SSH til en ny server er å endre passordet:
```
passwd
(Her skrev jeg passordet mitt)
```
Etter det starter den evig lange prosessen som er å oppdatere systemet. Dette er for å passse på at alt funker, og at serveren er sikker.
```
sudo apt update -y
```
Dette oppdaterer stedene de nye oppdateringene hentes fra.
```
sudo apt upgrade -y
```
Og dette er det som faktisk oppdaterer systemet.  
Denne prosessen tok over en halvtime for meg.

Neste ting jeg satt opp er det som heter "SSH key based authentication" for å styrke sikkerheten. "Key based authentication" er at istedenfor at du bruker et passord for å logge inn til serveren bruker man et sett med en "public key" og en "private key". Dette heter "asymmetric cryptography". Jeg skal prøve å forklare det så lett som mulig.

Når du bruker "asymmetric cryptography" lager man to nøkler, en privat nøkkel, og en offentlig nøkkel. Tenk på den offentlig nøklen din som postkassen din. Alle kan få vite hvor postkassen din er, og alle kan putte beskjeder i postkassen din. Så når noen skal sende deg en melding enkrypterer de den med din offentlige nøkkel. Men bare du kan åpne postkassen din, fordi for å åpne den trenger du den private nøklen din. Denne er viktig å holde sikker. Så fort noen har enkryptert meldingen sin med din offentlige nøkkel kan bare du se den, selv ikke de som sender den kan se hva som er inni. Hvis noen prøver å åpne den enkrypterte meldingen vil de se det som heter "cipher text" som ser litt sånn her ut: iahef89aus9f8us89fmuaruq8urmcd. Umulig å lese. Når du mottar meldingen i postkassen din kan du bruke den private nøklen din til å åpne postkassen og dekryptere / se meldingen. Når du går inn på en nettside og det står at nettsiden er sikker, da bruker du "asymmetric cryptography". Nettsiden gir deg sin offentlige nøkkel som du krypterer dataen din med, og nettsiden bruker sin private nøkkel for å dekrypgtere dataen din. Her er et fint diagram for å visualisere det litt bedre:
![asymmetric cryptography visualisert](https://bitpanda-academy.imgix.net/450037a5-144d-44ef-9db1-7fe7ce1f433d/bitpanda-academy-expert-20-what-is-asymmetric-encryption-infographic.png?auto=compress%2Cformat&fit=min&fm=jpg&q=80&w=2100)

Å sette opp dette for SSH gjør at det bare er min PC som kan koble seg til serveren. Dette forhindrer mange hacke forsøk som "brute force" hvor en hacker prøver alle passord mulig for å komme seg inn i serveren. 
```
ssh-keygen
```
Dette genererer den offentlige og private nøklen din for SSH, og den larger det på PCen din. Så sender vi den offentlige nøklen til serveren:
```
ssh-copy-id 192.168.24.24
```
Sist men ikke minst må vi skru av passord autentikasjon for serveren. Vi starter med å åpne ssh konfigurasjons filen med:
```
sudo nano /etc/ssh/sshd_config
```
Så skrur vi av passord autentikasjon:
```
PasswordAuthentication no
```
Til slutt restarter vi SSH:
```
sudo systemctl restart ssh
```

Nå har vi en sikker tilkobling som vi kan bruke til å sette opp musikkspilleren med.

# Boksen

Som jeg nevnte helt i starten vil jeg holde alle disse elektroniske komponentene i en boks. Jeg valgte en boks laget av tre for flere grunner. Det er et materiale som tåler en god del, nå har jeg ikke tenkt til å kaste musikkspilleren min i veggen så ofte, men det er fint om den ikke faller sammen. Treverk er også noe som ser litt "klassisk" ut ettersom at dette skal etterligne en vinylspiller som er et klassisk / vintage produkt. Denne treboksen startet med å være en boks for dagbøker som morfaren min laget til moren min. Det er derfor den har en låse-mekanisme foran. Så ble det til boksen vi hadde batterier i i huset før, men i sommer 3D printet jeg noen nye holdere for batterier som gjorde denne boksen fri for meg å bruke.  

Her er boksen, på toppen ser du markeringer med blyant. Dette er hvor jeg skulle borre for å trekke ledninger til lyset som skal på toppen.  

<img src="https://github.com/simen64/Design-og-redesign/blob/1a213cbadf311c9393cd7bb952f35feb4e7ce7c3/NFC-musikkspiller%20/Bilder/Boks%20med%20markeringer.jpg" width="450">

Her har jeg borret hullene og trukket ledningene gjennom hullene. Ledningene loddet jeg på neopixel ringen selv.  

<img src="https://github.com/simen64/Design-og-redesign/blob/965f95672e6ce744a616d5b506f4f2a4b86eb31a/NFC-musikkspiller%20/Bilder/trekke%20ledninger%20fra%20neopixel.jpg" width="450">

For at raspberry pien skal få strøm trenger den å bli tilkoblet med en mikro usb ledning. Derfor borret jeg et hull bak boksen til å plugge den inn. Å lage dette hullet var litt krevende ettersom at jeg måtte borre to hull ved siden av hverandre og fjerne midten for å få en avlang form for USB porten.    

<img src="https://github.com/simen64/Design-og-redesign/blob/534500b9ce91cd26394f5a717da05a3c1ab8d751/NFC-musikkspiller%20/Bilder/Hull%20til%20ledning.jpg" width="450">

Boksen ferdig: 

<img src="https://github.com/simen64/Design-og-redesign/blob/a218101a42c0d3fd5787c3c56f63503c5e8253c7/NFC-musikkspiller%20/Bilder/boksen_ferdig.jpg" width="450">

Jeg vurderte å fjerne den metall tingen foran, men jeg synes den legger til en god detalje som kontraster den simple tre boksen.

## Platene

Som den fysiske mediaen hvor jeg skal feste NFC klistremerkene lagde jeg "plater". Dette gjorde jeg ved å 3d modellere en sylinder som passer akkuratt inn i ringen med lys. På bunnen av disse platene puttet jeg NFC klistremerket. På skolen printet jeg ut noen album-cover som jeg brukte RX lim til å lime på toppen av platen.

<img src="https://github.com/simen64/Design-og-redesign/blob/883c6257e839b03e27752e1c5ca066b44942c955/NFC-musikkspiller%20/Bilder/platene.jpg" width="300">

# Nettside

Jeg bestemte meg for å prøve å lage en nettside til prosjektet som gjør det lett å legge til album og sanger. Det jeg ikke visste var at denne nettsiden ville bli et veldig mye mer komplisert prosjekt enn det jeg trodde. og det ville ta opp mange flere timer enn det jeg trodde.

## Struktur

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

## Funksjonalitet

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

Og sånn kan vi fortsette å bygge ut nettsiden vår.

Så for hjemmesiden til nettsiden, må vi vise fram tabellen jeg har vist tidligere. Så vi definerer en funksjon for `/` Her bruker vi `return render_template` for å laste inn filen som har nettsiden og tabellen jeg gikk over i [struktur](#struktur) delen. Filen heter `index.html`

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

Funksjonen `load()` åpner opp databasefilen vår og returnerer inneholdet som en variabel til det som tilkalte funksjonen.

Nå vet vi at i vår opprinnelige funksjon for hjemsiden til nettsiden blir inneholdet til databasen lagret i `data`  
Med `data=data` sender vi denne informasjonen over til `index.html` som er filen med strukturen til nettsiden, men også javacript funksjonen som genererer tabellen. Det å sende over denne informasjonen heter "Jinja".

### Generering av tabellen i Javascript

Javascript er et annet programmeringsspråk som brukes for laging av nettsider. I mitt tilfelle er det det som genererer tabellen med sangene og albumene fra databasen.  

Så for å motta dataen fra Jinja må vi definere en variabel som vi kaller `data` og putte dataen i JSON format fra Jinja der:

```js
var data = {{ data|tojson }};
```
Vi lager en funksjon for å bygge opp tabellen vår i javascript som ser sånn her ut:

```js
function buildTable(data){
   var table = document.getElementById('table')

   for (var i = 0; i < data.length; i++){
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

   }
}
```
Det denne funksjonen gjør er å hente ut dataen vi har i databasen vår, og strukturere den med html.
På slutten er det en til funksjon som lager en slett knapp:

```js
<td>
   <form action="/delete" method="post" onsubmit="return confirm('Are you sure you want to delete that album?')";>
      <button type="submit" name="delete" value="${data[i].id}">Delete</button>
   </form>
</td>
```
Dette lager en "Delete" knapp for å fjerne albumer og sanger, når den er klikket kommer det opp en boks som spør om du er sikker på at du vil slette den. Dataen som blir sendt til serveren når denne trykkes er IDen til albumet. Dette er koden på server siden:

```python
#Define the URL for deleting an album
@app.route("/delete",methods = ["POST", "GET"])
def delete():
   if request.method == "POST":
      id = request.form["delete"]

      print(id)

      temp = load()

      for item in temp:
         if 'id' in item and item['id'] == id:
            print(f"Found album / song with ID {item['id']}")

            temp.remove(item)

            with open("database.json", "w") as file:
               json.dump(temp, file, indent=4)

         else:
            pass

      return redirect(url_for("home"))
```

Dette er en funksjon i Flask som tar IDen sendt av javascript, sjekker om det er en som matcher i databasen, hvis det er det så sletter den den og sender brukeren tilbake til hjemsiden.

#### Tilbake til Javascript

Helt på slutten bruker vi dette:
```js
buildTable(data)
```
Det tilkaller funksjonen, og gjør at hver gang siden lastes inn på nytt oppdateres tabellen.

### Input

For at denne nettsiden skal gjøre det den skal, trenger den en måte å ta input fra en bruker for å så putte det i en database.  
Brukeren må putte inn en spotify URI (Spotify sin måte å identifisere albumer og sanger) og en knapp for å legge til.
For å gjøre dette brukte jeg det som kalles for en `form action` Dette er en funksjon som tar en input, og så sender informasjonen til serveren med en link. Dette kalles for en POST request. POST er måten en nettside kan sende ting til servere.

Her er HTML koden for feltet man putter inn album eller sangen.

```html
<form id="Form" action="/send_data" method="post" onsubmit="return showAlert()">
    <p>Enter Album / Song Link or URI</p>
    <p><input type="text" name="raw-input" /></p>
    <p><input type="submit" value="Add album or song" /></p>
</form>
```

Etter brukeren har klikket på "Add album or song" utføres javascript funksjonen `showAlert()` Denne funksjonen forteller brukeren at de skal plassere "tagen" som skal kobles til denne sangen eller albumet på scanneren. Etter at den har blitt scannet sendes dataen over til serveren. Hva som skjer med dataen, kommer jeg tilbake til.  
Her er `showAlert()` funksjonen:

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

For å motta dataen i webserveren, så den kan bli puttet i databasen, må vi definere en funksjon for linken der dataen sendes. Som her er `/send_data` - dette gjør vi i Flask:

```python
@app.route('/send_data',methods = ['POST', 'GET'])
def album_data():
   if request.method == 'POST':
```
Dataen brukeren sendte til oss blir lagret i en variabel kalt `raw_input`:

```python
raw_input = request.form["raw-input"]
```

#### Link til URI
Som jeg nevnte måtte man putte inn en Spotify URI, for å gjøre denne prosessen enklere har jeg kodet en funksjon som gjør spotify linker om til URIer. Så nå kan man putte inn begge to i nettsiden.  

La oss si at brukeren puttet inn dette i nettsiden:
```
https://open.spotify.com/track/0V5cvmTKsYmF5FmGGEAfmS?si=724171a1adb949e6
```
Funksjonen jeg skrev omgjør denne linken til det her som kan brukes av koden min:
```
spotify:track:0V5cvmTKsYmF5FmGGEAfmS
```

Her er koden for den funksjonen:
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

#### Lagre dataen

Nå står vi igjen med en Spotify URI som i dette eksemplet ser sånn her ut: `spotify:album:7Grz4hgSBRdEPj6Vxm991i`  
Vi vil lagre denne i databasen vår sammen med noe annen info om albumet / sangen.  
Derfor kan vi bruke spotify sin API som lar oss sende inn en spotify id, og så få tilbake blant annet album-coveret og titlen.  
Sånn her ser koden for det ut:
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

elif "track" in raw_input:
   track_spotify_id = raw_input.replace("spotify:track:", "")
   print(track_spotify_id)

   # Use Spotify's API to get info about the track
   track_info = sp.track(track_spotify_id)

   # Get the track name and album
   track_name = track_info["name"]
   track_album_cover = track_info["album"]["images"][0]["url"]

   # Structure the new data
   data = {
      "cover":track_album_cover,
      "name":track_name,
      "uri": raw_input
   }
```

Ikke bare skaffer denne funksjonen her infoen om albumet / sangen, men den strukturer det også i variablen `data` som vi senere skal legge til i databasen. Hvis du ser på koden over er det to ganske like seksjoner, det er fordi det er en for album og en for sanger, men til slutt vil data variablen se sånn her ut uansett:
```json
{
   "cover": "https://news.artnet.com/app/news-upload/2023/06/HAPO7184_M_Pink_Floyd_DSOTM_Photo_Cover_RT_PF_GT-1024x1024.jpg",
   "name": "Sample album",
   "uri": "spotify:album:2WT1pbYjLJciAR26yMebkH",
}
```
Siden vi skal scanne en NFC-tag for å spille av musikken må vi knytte en ID til både en NFC-tag og dataen i databasen. Derfor lagrer vi denne dataen vi har hittil i en "cookie" (som du kanskje er vant med å akseptere når du går inn på nettsider) og så sender vi brukeren videre til en ny side for å få IDen til NFC-tagen.

Som vi har gjort for alle andre linker definerer vi dem først i Flask:
```python
@app.route("/scan")
def scan():
```

Dette er koden som scanner NFC-tagen:
```python
id = reader.read()

id_from_scan = id[0]
id_from_scan = str(id_from_scan)

GPIO.cleanup()
```

`id = reader.read()` ber scanneren om å lete etter en tag, når en tag har blitt scannet lagres dataen den finner i variablen `id` og koden fortsetter.

### Scanner problemet

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
Som man ser først fungerer det å printe IDen, men teksten ikke så bra. "AUTH ERROR" betyr at noe har gått galt under scanningen av tagen. Problemet viste seg å være at programvaren på scanneren var syv år gammelt og funket ikke med mine tager. Heldigvis funket det fortsatt å lese IDen som vi kan bruke istedenfor.
### Tilbake til scanning

Så koden jeg bruker nå ser slik ut:
```python
id = reader.read()
print(f"id: {id}")

id_from_scan = id[0]
id_from_scan = str(id_from_scan)

GPIO.cleanup()
```

Dette gir oss IDen i en string, som vi kan bruke til å knytte en tag sammen med et album eller en sang:
```python
"519383492"
```
Etter vi har fått denne IDen må vi sjekke om denne IDen allerede finnes i databasen, det gjør vi med denne koden her:

```python
for item in temp:
   if 'id' in item and item['id'] == id_from_scan:
      print("Error, cant have two albums / songs with the same ID")
      return redirect(url_for("ID_conflict"))
```
I "menneske språk" betyr dette: for hvert element i databasen, sjekk om IDen matcher med IDen fra scannen, hvis den gjør det si ERROR og send brukeren til denne delen av nettsiden vår:

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

Men hvis vår sikkerhets-funksjon ikke finner noen konfliktende IDer i databasen kan den gå videre.

Hvis du husker så puttet vi dataen vi fikk om albumet eller sangen fra spotify i en session cookie som så slik ut:
```python
{
   "cover": "https://news.artnet.com/app/news-upload/2023/06/HAPO7184_M_Pink_Floyd_DSOTM_Photo_Cover_RT_PF_GT-1024x1024.jpg",
   "name": "Sample album",
   "uri": "spotify:album:2WT1pbYjLJciAR26yMebkH",
}
```

Nå kan vi hente inn denne daten fra cookien vår og legge til IDen vi fikk fra scanneren, så vi står igjen med denne dataen:

```python
data = {
   "cover":track_album_cover,
   "name":track_name,
   "uri": raw_input,
   "id": id_from_scan
}
```
Til slutt lagrer vi denne nye dataen i databsen, og sender brukeren til hjemsiden.

# Å spille av musikk

Helt i starten viste jeg et veldig simpelt diagram på hvordan musikken skal spilles av, men nå skal vi se på det i detalje. Jeg skrev dette programmet i python fordi det er det språket jeg kan. Før vi starter å gå gjennom koden er det noen ting som må nevnes. Denne koden er funksjonsbasert, som betyr at nesten all koden er inni forskjellige funksjoner som blir tilkalt. Dette kan gjøre det litt vanskeligere å forstå sammenhengen mellom forskjellige deler av koden, men heng med.

Vi starter med å gå gjennom hvordan musikk faktisk blir spilt. Det første du må vite er hva en API er. En API er en måte vi i koden vår kan si til spotify eller home assistant; gjør det her. Så når jeg refererer til en "API request" snakker jeg om å be noe som Spotify eller Home Assistant om å gjøre noe.

## Home Assistant

Home Assistant er det som styrer alle smarthus enhetene i huset mitt inkludert høytalere. I Home Assistant har vi et script, dette er litt som et program som kan utføre en rekke med hendelser i huset. I vårt tilfelle skal scriptet spille av musikk gjennom Spotify. Dette gjør vi med en utvidelse som heter "Spotcast" denne lar oss velge en høytaler og en sende en Spotify URI for å spille av musikk. Sånn her ser Home Assistant scriptet ut:
```yaml
service: spotcast.start
data:
  limit: 20
  force_playback: true
  random_song: false
  repeat: "off"
  shuffle: false
  offset: 0
  ignore_fully_played: false
  device_name: Simens Rom Høytaler
  uri: "{{ states('input_text.spotify_uri') }}"
```
De to viktigste tingene her er `device name` som spesifiserer hvilke høytaler som skal brukes og `uri`. URI delen derimot inneholder ikke en URI, men statusen til det som heter en "hjelper". En hjelper er en variabel i Home Assistant som kan holde data. Her inneholder variablen en Spotify URI, hvorfor vi gjør det sånn her kommer vi tilbake til. Konklusjonen er at når dette scriptet kjøres spilles det av musikk på høytaleren.

### Aktivere scriptet fra Python

Naturligvis siden scriptet er det som spiller av musikken trenger vi å aktivere dette fra Python programmet vårt. Heldigvis har Home Assistant en API som vi kan bruke.

Jeg snakket om hvordan scriptet bruker en hjelper for å vite hva den skal spille av. Grunnen til dette er så vi kan endre hva som skal spilles med Python scriptet. Det gjør vi med denne funksjonen her:

```python
def update_helper(Spotify_URI):
    global helper_id, HA_URL, headers
    print("updating helper")

    data = {
    'state': Spotify_URI,
    }

    response = requests.post(f'{HA_URL}/api/states/{helper_id}', headers=headers, json=data)

    if response.status_code == 200:
        print(f'Successfully updated the value of {helper_id}')
    else:
        print(f'Failed to update the value. Status code: {response.status_code}, Response: {response.text}')
```
Denne funksjonen ser vi har `Spotify_URI` i parantes som betyr at når noe tilkaller denne funksjonen sender de også med spotify URIen.  
Funksjonen bruker en HTTP POST request for å sende en beskjed til Home Assistant om at hjelperen skal oppdateres til Spotify URIen som ble sendt med tilkallingen av funksjonen.

Neste funksjon vi trenger er for å faktisk aktivere scriptet.  
```python
def run_script():
    global script_id, HA_URL
    print("running script")

    data = {
    'entity_id': script_id,
    }

    url = f'{HA_URL}/api/services/script/turn_on'

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f'Successfully activated the script: {script_id}')
    else:
        print(f'Failed to activate the script. Status code: {response.status_code}, Response: {response.text}')
```
Vi ser at denne funksjonen er veldig lik. Her sender vi bare rett til Home Assistant "Aktiver dette scriptet vi har valgt for å spille av musikk"

### Scanning, spilling, og pausing

Vi har også en funksjon som gjør selve scanningen, som ser slik ut:

```python
def scanning():
    global current_tag_id
    try:
        while True:
            print("Hold a tag near the reader")
            id = reader.read()
            id = id[0]
            id = str(id)
            print(id)

            
            if id != current_tag_id:
                play_album(id)
            else:
                print("same tag")

            current_tag_id = id
            time.sleep(10) 

    except KeyboardInterrupt:
        GPIO.cleanup()
        raise
```

Sånn denne funksjonen virker er at hvert 10. sekund scanner den etter en tag, hvis tagen er den samme som forrige gang skipper de, men hvis det er en ny tag aktiverer vi scriptet `play_album` og gir IDen til tagen som ble scannet til funksjonen.

Funksjonen `play_album` har to viktige oppgaver. Den ene er å matche IDen fra tagen til en sang eller et album. Og å kjøre funksjonene `update_helper` og `run_script`. Funksjonen ser sånn her ut:

```python
ef play_album(id):
    global Spotify_URI, id_played
    print("playing album")

    data = load()

    for item in data:
        if 'id' in item and item['id'] == id:
            print(f"Found album with ID {item['id']}")
            Spotify_URI = item["uri"]
            id_played = id

            update_helper(Spotify_URI)

            run_script()

            print("Made green with play_album function")
            wipe_to_green()
            break
    else:
        print("no albums with matchind IDs were found")
```
Først tar vi IDen fra tagen og går gjennom databasen for å finne en matchende sang eller album. Så oppdaterer vi hjelperen med `update_helper` funksjonen og det er her vi mater inn hvilke Spotify URI vi skal oppdatere hjelperen til. Etter det kan vu bruke funksjonen `run_script` for å spille av musikken. Og sist men ikke minst tilkaller vi en siste funksjon som heter `wipe_tpo_green`. Dette er animasjonen som gjør lyset grønt på musikkspilleren når noe spilles. Den funksjonen ser sånn ut:

```python
def wipe_to_green():
    for i in range(len(pixels)):
        pixels[i] = (0,255,0)
        pixels.show()
        time.sleep(0.05)
    for i in range(len(pixels)):
        pixels[i] = (0,0,0)
        pixels.show()
        time.sleep(0.05)
```

Nå er det en ting som musikkspilleren mangler som må kodes, og det er at når "platen" blir tatt av spilleren pauses musikken. I tilegg ville jeg ha det sånn at hvis du la på platen innen 1 minutt fra du tok den av fortsatte musikken fra der den pauset, men hvis det går over et minutt og du legger på platen starter det på nytt.

Først må vi ha en funksjon for å pause og spille musikken. Denne funksjonen ligner på `update_helper` funksjonen. Funksjonen kan man mate inn `pause` eller `play` for å spille av eller pause. Her er koden for funksjonen:

```python
def music_control(pause_or_play):
    global spotify_id

    data = {
    "entity_id": spotify_id
    }

    response = requests.post(f'{HA_URL}/api/services/media_player/media_{pause_or_play}', headers=headers, json=data)

    if response.status_code == 200:
        print(f'Successfully paused or played')
    else:
        print(f'Failed to update the value. Status code: {response.status_code}, Response: {response.text}')
```

Å finn en løsning for å vite om platen var der eller ikke viste seg å være litt vanskeligere enn jeg trodde, men dette er hvordan jeg gjorde det. En funksjon scanner kontinuerlig for en tag, hvis den finner en tag oppdateres variablen `tag_countdown` til 5 sekunder. Samtidig i bakgrunnen kjører en annen funksjon som hele tiden teller ned fra verdien til `tag_countdown` og ned til 0. Så hvis ikke en tag er der på 5 sekunder kan vi konkludere at det ikke er en plate der.

Dette er koden for funksjonen som sjekker kontinuerlig for en tag:

```python
def tag_detect():
    global tag_countdown, on_pause, id_played
    while True:
        id = reader.read()
        id = id[0]
        id = str(id)
        print("tag is there")
        tag_countdown = 3
        if on_pause:
            if id == id_played:
                print(f"ID: {id}, id_played: {id_played}")
                music_control("play")
                on_pause = False
                print("Made green with tag_detect function")
                t = threading.Thread(target=wipe_to_green)
                t.start()
            else:
                on_pause = False
```

Og her er funksjonen som teller ned:

```python
def tag_detect_countdown():
    global tag_countdown
    while True:
        tag_countdown = tag_countdown - 1
        if tag_countdown <= -1:
            tag_countdown = -1
        if tag_countdown == 0:
            tag_not_there()

        time.sleep(1)
```

Som man kan se på bunnen av `tag_detect_countdown` funksjonen, så blir funksjonen `tag_not_there` når nedtellingen treffer 0. La oss se på hva den gjør.

`tag_not_there` er en veldig enkel funksjon som ser sånn her ut:

```python
def tag_not_there():
    global on_pause, countdown
    print("tag not there anymore")
    music_control("pause")
    countdown = 60
    on_pause = True
    print("Made lights yellow")
    wipe_to_yellow()
```

Funksjonen gjør 4 ting. Først pauser den musikken, så setter den en ny nedtelling (Ikke bland denne nedtellingen med den forbundet med `tag_detect_countdown`) til 60 sekunder. Så sier vi til resten av programmet at den er på pause med `on_pause = True` Til slutt tilkaller vi funksjonen `wipe_to_yellow` som er lik `wipe_to_green` bare med en gul farge.

Den nye nedtellingen på 60 sekunder brukes til det jeg prøvde å forklare med at hvis det går 1. minutt så spilles sangen av på nytt.
Dette er nesten helt likt som nedtellingen på 5 sekunder og nedtellingsfunksjonen ser nesten helt lik ut:

```python
def pause_countdown():
    global on_pause, current_tag_id, countdown
    countdown = 60
    while True:
        if on_pause:
            countdown = countdown - 1
            if countdown == 0:
                print("COUNT REACHED 0")
                on_pause = False
                current_tag_id = None
                pixels.fill((0,0,0))
                pixels.show()
                print("TURNED OFF PIXELS")
            time.sleep(1)
        else:
            pass
```

Eneste er at denne funksjonen skrur av lysene og resetter programmet så det er klart for en ny plate. Men hva om man legger på platen innen 1 minutt?

Hvis vi ser tilbake på `tag_detect` funksjonen. Er det noe den gjør i tilegg til å resette nedtellingen. Den sjekker om musikken er på pause, og hvis den er det og platen er den samme som når musikken ble satt på pause så spiller den av musikken igjen. Det er det denne delen av funksjonen `tag_detect` gjør:

```python
if on_pause:
   if id == id_played:
      print(f"ID: {id}, id_played: {id_played}")
      music_control("play")
      on_pause = False
      print("Made green with tag_detect function")
      t = threading.Thread(target=wipe_to_green)
      t.start()
   else:
      on_pause = False
```

### Threading

Som jeg har sagt er det flere funksjoner i dette programmet som kjører samtidig, som med nedtellingene. Derfor må vi bruke det som heter en "thread" som lar programmet kjøre flere ting samtidig. Koden for dette ser sånn her ut:

```python
scan_thread = threading.Thread(target=scanning)
tag_detect_thread = threading.Thread(target=tag_detect)
tag_countdown_thread = threading.Thread(target=tag_detect_countdown)
pause_countdown_thread = threading.Thread(target=pause_countdown)

scan_thread.start()
tag_detect_thread.start()
tag_countdown_thread.start()
pause_countdown_thread.start()

scan_thread.join()
tag_detect_thread.join()
tag_countdown_thread.join()
pause_countdown_thread.join()
```

Første "Avsnitt" definerer hvilke funksjoner som skal kjøres samtidig, og det er: `scanning`, `tag_detect`, `tag_detect_countdown`, og `pause_countdown`.  

Andre avsnitt starter alt, og siste avsnitt avslutter dem når programmet stopper.

# Systemd

Hvis du noen gang har lurt på hva i operativsystemet ditt det er som starter alle prosessene som det som styrer wifi, antivirus, brannmur, oppstartsprogrammer etc? Vel i tilfelle til de fleste Linux distrubisjoner er dette Systemd. Det er ofte hatet ettersom at det ikke følger Unix filososifen som sier: "Skriv programmer som gjør én ting, og én ting godt. Systemd gjør mange ting, middels godt, men det har blitt tatt i bruk fordi det er universalt og lett. Det Systemd er er et "init system". I windows når du skal få et program som nettsiden eller programmet for å spille musikk til å starte når systemet starter kan du bare putte det i en mappe, på Linux er det ikke fullt så lett. For at Systemd skal vite hvordan programmet skal startes må vi skrive en konfigurasjonsfil til Systemd.

### Webserveren

Som jeg har gått over er nettsiden skrevet med Flask. Når man kjører et python program med Flask starter den en "devolpment server" dette er veldig bra når man designer nettsiden, men det er tregt og ustabilt for produksjon. Derfor bruker vi "Gunicorn" som er en python web server gatewaysom brukes når man faktisk skal bruke nettsiden og ikke utvikle den.

Dette er konfigurasjonsfilen til Gunicorn som gjør at alle på samme nett kan gå inn på nettsiden:
```python
bind = "0.0.0.0:8000"
workers = 1
worker_class = "sync"
```

Nå som vi har satt opp gunicorn kan vi starte det med kommandoen:
```
gunicorn -b 0.0.0.0:8000 -c gunicorn_config.py webserver:app
```
Ettersom at dette nå funker må vi nå lage konfigurasjonsfilen for Systemd, så webserveren kan starte når musikkspilleren blir plugget inn.
Den konfigurasjonsfilen ser sånn her ut og forteller Systemd hvordan programmet skal starte i hvilke mappe og med hvilke kommandoer:
```
[Unit]
Description=Flask server for NFC music player
After=network.target

[Service]
User=simen
WorkingDirectory=/home/simen/musikkspiller/
ExecStart=/home/simen/musikkspiller/env/bin/gunicorn -c /home/simen/musikkspiller/gunicorn_config.py webserver:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Spilleren

Konfigurasjonen for å starte python scriptet som spiller av sanger og albumer er nesten helt likt som for webserveren, bare at isteden for å kjøre med gunicorn kjører vi rett med python. Og fordi det krever root setter vi brukeren til root.
```
[Unit]
Description=Core functions of playing music with the music player
After=network.target

[Service]
User=root
WorkingDirectory=/home/simen/musikkspiller/
ExecStart=/home/simen/musikkspiller/env/bin/python /home/simen/musikkspiller/play_album.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

```

### Oppdateringer

Som alle burde vite er det ekstremt viktig å holde systemet sitt oppdatert for å passe på at det er sikkert mot nye trusler. For å slippe å måtte SSH inn i musikkspilleren min hver dag for å oppdatere den lagde jeg en service her også for å oppdatere systemt. En ekstremt nyttig ting med Linux er at du har noe som heter en "package manager" som handler alle programmene dine. Dette gjør at du kan oppdatere alt samtid. `apt update` oppdaterer hvor package manageren laster ned pakkene, og `apt upgrade` er det som faktisk oppdaterer systemet og alle programmene. Her er systemd serviceen for å oppdatere systemet når musikkspilleren starter:
```
[Unit]
Description=Update System on Boot
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/apt update
ExecStartPost=/usr/bin/apt upgrade -y

[Install]
WantedBy=default.target

```

# Konklusjon

I konklusjon synes jeg dette prosjektet var veldig gøy å jobbe med. Jeg endte opp med å bruke mye mere tid på det enn det jeg trodde, sikkert 30 timer på programmering alene. Men jeg lærte mye nytt om servere, programmering, databaser, NFC, og nettsider. Og jeg synes at programmering er veldig gøy. Problemløsningen med å finne komponenter som funket og å løse konflikter med koden og komponenter var også en veldig morsom utfordring. Jeg håper at vi har muligheten til å ha flere sånne åpene oppgaver som det her i framtiden.

Jeg vet at denne loggen er veldig lang, men det har vært ganske vanskelig å dytte mange uker med arbeid inn i en logg uten å ikke ta med viktige deler av hvordan ting funker. Mye av loggen består av kode som kan virke litt mye, men jeg anbefaler å ta en titt på de forskjellige kodefilene i GitHub for å se en helhet av koden.

Du kan også prøve å kjøre nettsiden selv! Bare last ned `webserver.py`, sett opp et python virtual enviroment, bruk pip til å laste ned `requirements.txt`, sett opp en `.env` fil, og kjør!