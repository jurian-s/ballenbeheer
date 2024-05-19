# How to Build
Use python 3.11 to make a virtual environment
Install required modules with "pip install requirements.txt"
Build the .exe with "pyside6-deploy Ballenbestand.py"
(If you don't want the console to be visible, you can use the generated spec file, add --disable-console in the extra-args for Nuitka)

# How to use
Om het Ballenbeheer programma te gebruiken heb je Ballenbestand.exe en ballenbestand.json nodig
(De .json file is de database, ik raad aan om iets van versie beheer te gebruiken (Zoals GIT), om mocht er iets mis mee gaan je altijd terug kan gaan naar een oudere versie.

## Tellen van ballen
Om ballen te tellen selecteer je nadat je de .exe hebt opgestart, Start telling. Hierna selecteer je de locatie waarvan je de ballen aan het tellen bent.
Vervolgens kan je het balnummer typen, en wordt hij geteld als je op enter drukt. Je kan in de label zien welke bal je als laatst hebt geteld.
Als je een bal dubbel telt, herkend hij dit, en wordt de bal alleen enkel geteld. Mocht volgens de database de bal eigenlijk op een andere plek horen krijg je een melding.
Je kan kiezen om de bal te tellen (en van locatie te laten wisselen), of om de bal niet te tellen. 
Als het balnummer onbekend is, krijg je een popup om de bal toe te voegen, als jaar van de bal wordt automatisch het huidige jaar gebruikt.

## Export functie
Als je op Exporteer drukt kan je een overzicht opslaan van alle ballen in de geselecteerde tellingen als .csv bestand.

## Statistieken
Hier kan je de waarde/het aantal ballen per telling zien.

## Beheer ballenbestand
### Locaties
Hier kan je de database onderhouden. Voor locaties kan je nieuwe locaties toevoegen, locaties verwijderen en de naam van een locatie aanpassen

### Balsoorten
Hier kan je baltypes toevoegen, verwijderen of aanpassen. Dit gaat om de naam van het baltype, en de afschrijving van het type bal per jaar

### Tellingen
Hier kan je tellingen verwijderen en aanpassen. Ook kan je een telling importeren uit een ander ballenbestand. Dit is handig als er tegelijk met twee verschillende laptops tellingen zijn gedaan.
Als je een telling importeert, worden automatisch de benodigde ballen, balsoorten en locaties toegevoegd.

### Ballen
Hier kan je ballen aanpassen (Het type, de locatie en het jaar waar de bal in gebruik  is genomen). Ook kan alle ballen verwijderen die in geeneen van de tellingen in de database geteld zijn.
