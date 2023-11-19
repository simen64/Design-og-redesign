
# En moderne vinyl / musikk spiller

## Ideen

Idden er å ha en boks hvor man kan scanne en eller annen form for fysisk ting for å spille av musikk. Denne fysiske tingen skal ha album coveret på seg så man kan se hvilke album man spiller av. Litt som en vinylspiller.

## Planen

### Hjernen

Hjernen til prosjektet skal være en SBC (single board computer) eller en mikroprosesor. Dette kan være en Arduino, Raspberry Pi, eller en form for ESP development board. Jeg har en god del variasjoner av disse  som ligger å støver, ettersom at jeg har kjøpt en god del av dem til enten prosjekter som ikke ble noe av eller bare for å eksperimentere. Denne "Hjernen" skal styre alt, som å spille av musikken, finne ut hvilke album som er scannet, og holde koden til prosjektet. Hvis hjernen er en SBC, kan jeg også bruke det som en server i tilegg til å være en musikkspiller.

### Scanneren

For å scanne albumet skal jeg feste NFC-klistremerker på det som skal være den fysiske tingen. Disse NFC-klistremerkene har jeg hatt en bunke av liggende å støve, ettersom jeg kjøpte masse av dem for å bruke rundt i huset til automasjoner.
NFC-klistremerkene oppererer med teknologien NfcA, Mifare Ultralight, og Ndef.
Scanneren jeg har tenkt til å bruke er en RC5200 RFID scanner. Selvom denen scanneren egentlig er laget for en annen teknologi (RFID istedenfor NFC) støtter den mifare ultralight, som skal gjøre det mulig å scanne mine NFC klistremerker. Når NFC-klistremerket har blitt scannet finner den IDen til albumet, og sender det til hjernen.

### Å spille av musikk

For å spill av musikk har jeg tenkt til å gå gjennom Home assistant. Home assistant er et self hosted smarthus kontrollsenter, her har jeg tilkoblet høytalerne jeg tenker å bruke. Home assistant støøter webhooks som er en måte for enheter å sende data en vei til en server ved hjelp av http (web linker) Når et album er scannet skal SBCen finne ut hvilke album det er, sende dette med en webhook over til homeassistant, som gjennom Spotify sin API spiller det av på høytaleren jeg har bestemt.

## Flowchart
![Musikkspiller_flowchart](https://github.com/simen64/Design-og-redesign/blob/b5c3e3b5bfac3fbb8e957e4738b0917208530f8e/NFC-musikkspiller%20/Bilder/Musikkspiller_flowchart.jpg)

## Arduino

Planen først var å bruke en Arduino som hjernen. Arduinoer er et elektronikk-brett med en mikroprosessor. De er veldig kjent for å brukes i elektronikk prosjekter som det her. Arduinoen har strøm, og data utganger som gjør den bra til å koble til komponenter. Jeg har hatt noen Arduinoer av forrige generajon liggende siden 2019, og har ikke egentlig brukt dem sins. Jeg fikk de til julegave sammen med masse andre elektroniske komponenter, som endte opp med å komme til nytte nå 4 år senere.

For at prosjektet skal fungere trenger den å ha tilgang til Wifi, noe min arduino ikke har. Heldigvis har jeg også en ESP8266 modul som jeg også fikk sammen med Arduinoen. En esp8266 er også en mikroprosessor, bare at den har innebygd wifi. Det som er med den modulen jeg har er at den ikke har en USB til å programmere den, heller ikke nok GPIO pins (Porter for å koble til komponenter) Fordi den mangler dette koblet jeg den opp til Arduinoen min gjennom serial (en måte å sende data på gjennom ledninger)

## Oppkobling
![Arduino oppkobling](https://github.com/simen64/Design-og-redesign/blob/86e651944495e410128a51a4ffa52c13428fa7e2/NFC-musikkspiller%20/Bilder/Arduino%20oppkobling.png)

### Serial kommunikasjon

For å kommunisere med ESP8266 modulen kan jeg bruke en serial monitor for å sende kommandoer til prosessoren, en sånn serial monitor er bygd inn i programvaren Arduino IDE, som er programmet jeg bruker til å kode til arduinoen.
Et problem jeg endte opp med å ha var at siden jeg hadde koblet ESP8266 modulen til Arduinoen sine serial pins, ble det konflikt med USBen som lastet koden over. Derfor måtte jeg plugge ut modulen vær gang jeg lastet opp ny kode, for å så plugge den inn igjen. Koden jeg lastet opp til Arduinoen inneholdte ikke noe, fordi jeg for nå bare trengte å bruke serial kommandoer for å kommunisere med ESP8266 modulen.

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

Jeg måtte kode et program til Arduinoen som automatiserte å putte inn disse kommandoene, siden det er variasjoner av de som skal brukes til å requeste en webhook.
`SoftwareSerial` er en pakke for Arduino som gjør det lett å sende kommandoer til moduler som er oppkoblet med serial pins.
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

En annen kul ting SoftwareSerial kan gjøre er å bruke virtuelle pins som pin 2, og 3 for å kommunisere gjennom serial. Dette hadde fikset konflikten med USB-kablen.
Men når jeg prøvde dette endte det opp med å funke så jeg bare holdt meg til pin 0, og 1 selvom det skapte konflikter. Hva problemet var kommer jeg tilbake til senere.

Koden jeg hadde lagde fungerte, og alt jeg puttet inn i `ESP8266.println("")` ble kjørt som om jeg sendte kommandoen gjennom serial monitor.
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
For å verifisere at ESP8266 modulen faktisk kunne kommunisere med Home Assistant pinget jeg den med kommandoen `AT+PING="192.168.125.77"`
Og hva skjedde? Jo den kom fram.

![Wireshark capture av ping til HA](https://github.com/simen64/Design-og-redesign/blob/95fce086cf4167f07ed15089a7fa0fab81d15931/NFC-musikkspiller%20/Bilder/ESP8266_Ping.png)
