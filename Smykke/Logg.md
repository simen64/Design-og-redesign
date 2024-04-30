# Smykke logg

## Idé 1, smart smykke

Når jeg først fikk vite at vi skulle lage noe som er et smykke var det første jeg begynte å tenke på var hvordan jeg kunne lage noe med elektronikk.  
Jeg tenkte jeg kunne lage en type smart smykke. Første jeg tenkte var å prøve å ha et kamera som kunne sende det det så til ChatGPT så man kunne få realtime svar på ting. Som hvis du for eksempel ser en plante kan du bruke smykket til å ta et bilde og be chatgpt finne ut hvilke plante det er.  
Her er første sketch:
# Insert bilde

Etter litt mere tenking innså jeg at dette kom til å bli et vanskelig prosjekt. Jeg har en vesentlig liten mikrokontroller som kunne kjørt programmet, men hvordan skulle brukeren få svaret fra chatgpt? Derfor tegnet jeg denne sketchen hvor smykket var koblet til to øreplugger:
# Insert bilde

## Idé 2, pip-boy

I spillene fra Fallout serien har de fleste karakterene det som kalles en "pip-boy" som ser sånn her ut:

<img src="https://www.cnet.com/a/img/resize/88604796f7a4401b74b72b7258d056ace8cfc31d/hub/2012/10/29/85bd157f-cc2e-11e2-9a4a-0291187b029a/pip_1.jpg?auto=webp&fit=crop&height=675&width=1200" alt="pip boy" width="400"/>

Pip-boyen er en type datamaskin i form av et stort armbånd. Jeg ville lage en form av det bare litt mindre. Her er min skisse av det, en mikrokontroller men en liten skjerm og noen knapper:
# Insert image

## Problemene

Begge disse to ideene har samme problem, mangel på deler. Jeg har en raspberry pi zero som er en liten Linux datamaskin jeg kan bruke som hjernen i begge prosjektene. Det jeg mangler for begge er ett form for batteri. Man kan jo ikke akkuratt gå rundt med en powerbank i lomma. Batteriet jeg hadde trengt å bruke hadde vært et lipo batteri. Eller også kjent som et lithium-ion polymer batteri, det betyr at det polymer electrolyte istedenfor liquid electrolyte som i vanlige batterier
