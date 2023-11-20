
# En moderne vinyl / musikk spiller

## Ideen

Idden er å ha en boks hvor man kan scanne en eller annen form for fysisk ting for å spille av musikk. Denne fysiske tingen skal ha album coveret på seg så man kan se hvilke album man spiller av. Litt som en vinylspiller.

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



## Nettside

### Struktur

Jeg har personlig aldri kodet i HTML, CSS, Javascript, eller Flask som er alle de programmeringsspråkene man bruker til å lage en nettside så dette var helt nytt for meg. Målet med denne nettsiden er å gjøre det lett å legge til nye album i databasen til musikkspilleren. Dette betyr at nettsiden trenger en front end (det brukeren ser på skjermen) og en back end (det som skjer bak i serveren som å legge sangene til en database)
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
        <td>
            <div style="text-align: center;">
             <img src="https://upload.wikimedia.org/wikipedia/en/9/9c/Sports_Modern_Baseball_album.jpg" width="100" height="100">
            </div>
        </td>
        <td>Sports Modern Baseball</td>
        <td>0001</td>
    </tr>
</table> 
```
### Det er kanskje ikke den fineste nettsiden, men den får fram poenget.

![Nettside med tabell](https://github.com/simen64/Design-og-redesign/blob/efcd7c3f0cea810994046d6398d68d4006d614df/NFC-musikkspiller%20/Bilder/Nettside_tabell.png)

### Input

For at denne nettsiden skal gjøre det den skal trenger den en måte å ta input fra en bruker for å så putte det i en database.  
Brukeren må putte inn to ting, et navn på albumet, en link til et album-cover, og en knapp for å legge til. Ne Det kan hende at jeg legger til mulighet for å laste opp bilder i framtiden.  
Enkleste måten for å få input i HTML er å bruke `input` tagen med en `label for`over den:
```html
<label for="album_cover_input"> Album cover link:</label>

<input type="text" id="album_cover_input" name="album_cover_input">

<label for="album_name_input"> Album navn:</label>

<input type="text" id="album_name_input" name="album_name_input">

<button onclick="addNewRow()">Add New Album</button>
```
### Igjen, ikke det fineste, men det funker
![Nettside input](https://github.com/simen64/Design-og-redesign/blob/e9e177adc302d0795266fffd2479a5351e68fdb0/NFC-musikkspiller%20/Bilder/nettside_input.png)

### Funksjonalitet
