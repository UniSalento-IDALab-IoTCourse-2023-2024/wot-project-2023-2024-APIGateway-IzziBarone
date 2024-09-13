# Usa l'immagine Python ufficiale
FROM python:3.9-slim

# Imposta la directory di lavoro nel container
WORKDIR /app

# Copia i file di requirements
COPY requirements.txt requirements.txt

# Installa le dipendenze
RUN pip install -r requirements.txt

# Copia tutto il codice nel container
COPY . .

EXPOSE 80

ENV FLASK_APP=app.py
ENV FLASK_ENV=development


CMD ["flask", "run", "--host=0.0.0.0", "--port=80", "--debug"]