# Usar una imagen base adecuada
FROM python:3.11-slim

# Instalar herramientas de compilación y dependencias
RUN apt-get update && apt-get install -y gcc build-essential libssl-dev libffi-dev

# Crear un directorio de trabajo
WORKDIR /app

# Copiar requirements.txt y otros archivos necesarios
COPY requirements.txt .

# Instalar dependencias generales
RUN pip install --upgrade pip setuptools wheel

# Instalar dependencias del sistema
RUN pip install -r requirements.txt

# Instalar httptools manualmente
RUN git clone https://github.com/MagicStack/httptools.git && \
    cd httptools && \
    python setup.py install

# Copiar tu aplicación
COPY . .

# Configurar variables de entorno, etc.

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "443"]
