ARG PORT=443

FROM cypress/browsers:latest


# Dockerfile
FROM railwayapp/python:3.11

WORKDIR /main

# Instalar dependencias del sistema y herramientas
RUN apt-get update && apt-get install -y python3-venv

# Copiar y instalar requerimientos
COPY requirements.txt requirements.txt
RUN python3 -m venv venv
RUN . venv/bin/activate && pip install -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

CMD ["python", "main.py"]