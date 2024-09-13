# SmartLocAI API Gateway

![apidashboard](https://drive.google.com/uc?export=view&id=1nLfyO8j-ET7qwEC6WuSksV5xHHLruYg-)

## Overview

L'**API Gateway** di **SmartLocAI** funge da punto di ingresso centrale per tutte le richieste provenienti dai client, gestendo la distribuzione delle chiamate ai vari servizi backend. Fornisce una gestione unificata degli endpoint per i servizi **DataService**, **LocalizationService**, semplificando la comunicazione tra i vari componenti del sistema e assicurando una gestione centralizzata della sicurezza, delle autorizzazioni e del monitoraggio delle richieste.

L'API Gateway consente inoltre agli utenti di aggiungere nuovi endpoint, testare le rotte esistenti, modificare e rimuovere rotte, facilitando la gestione dinamica dell'API.

### Funzionalità Principali

1. **Gestione degli Endpoint**:
   - Permette agli utenti di aggiungere, modificare e rimuovere endpoint per i vari servizi backend.
   - Gli utenti possono specificare un endpoint interno e associarlo a un URL esterno, consentendo l'inoltro delle richieste al servizio corretto.

2. **Test delle Rotte**:
   - L'API Gateway offre una funzionalità di test per verificare il corretto funzionamento delle rotte configurate. È possibile selezionare un endpoint, specificare il metodo HTTP e passare parametri di query per testare l'output delle chiamate.

3. **Monitoraggio delle Rotte**:
   - Gli utenti possono visualizzare un elenco delle rotte attive, inclusi gli endpoint interni ed esterni, e rimuovere o aggiornare le rotte se necessario.

### Come Iniziare

1. Clona il repository:
   ```bash
   git clone https://github.com/link-api-gateway.git
   ```

2. Installa le dipendenze:
   ```bash
   docker compose up -d
   ```
