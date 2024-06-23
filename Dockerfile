ARG PORT=443

FROM cypress/browsers:latest

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev

# Crear el entorno virtual
RUN python3 -m venv /opt/venv

# Copiar el archivo requirements.txt y activar el entorno virtual
COPY requirements.txt .
ENV PATH="/opt/venv/bin:$PATH"

# Instalar las dependencias en el entorno virtual
RUN /opt/venv/bin/pip install --upgrade pip
RUN /opt/venv/bin/pip install -r requirements.txt

# Copiar el resto del código
COPY . .

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
