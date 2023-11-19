
# En moderne vinyl / musikk spiller

## Ideen

Idden er å ha en boks hvor man kan scanne en eller annen form for fysisk ting for å spille av musikk. Denne fysiske tingen skal ha album coveret på seg så man kan se hvilke album man spiller av. Litt som en vinylspiller.

## Planen

### Hjernen

Hjernen til prosjektet skal være en SBC (single board computer) Dette kan være en Arduino, Raspberry pi, eller en form for ESP development board. Denne "Hjernen" skal styre alt som å spille av musikken, finne ut hvilke album som er scannet, og hoste koden til prosjektet.

### Scanneren

For å scanne albumet skal jeg feste NFC klistremerker på det som skal være den fysiske tingen. Disse NFC klistremerkene har jeg hatt en bunke av liggende å støve, ettersom jeg kjøpte masse av dem for å bruke rundt i huset til automasjoner.
NFC klistremerkene oppererer med teknologien NfcA, Mifare Ultralight, og Ndef.
Scanneren jeg har tenkt til å bruke er en RC5200 RFID scanner. Selvom denen scanneren egentlig er laget for en annen teknologi (RFID istedenfor NFC) støtter den mifare ultralight, som skal gjøre det mulig å scanne mine NFC klistremerker.

### Å spille av musikk

For å spill av musikk har jeg tenkt til å gå gjennom Home assistant. Home assistant er et self hosted smarthus kontrollsenter, her har jeg tilkoblet høytalerne jeg tenker å bruke. Home assistant støøter webhooks som er en måte for enheter å sende data en vei til en server ved hjelp av http (web linker) Når et album er scannet skal SBCen finne ut hvilke album det er, sende dette med en webhook over til homeassistant, som gjennom Spotify sin API spiller det av på høytaleren jeg har bestemt.


![Musikkspiller_flowchart](https://github.com/simen64/Design-og-redesign/assets/97337442/8a0ea1aa-618e-45fd-b188-cb79835bd02c)
