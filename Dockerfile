# Usar una imagen base adecuada
FROM python:3.11-slim

# Instalar herramientas de compilación y dependencias
RUN apt-get update && apt-get install -y gcc build-essential libssl-dev libffi-dev git

# Crear un directorio de trabajo
WORKDIR /app

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependencias generales
RUN pip install --upgrade pip setuptools wheel

# Instalar dependencias del sistema
RUN pip install -r requirements.txt

# Instalar httptools manualmente
RUN git clone https://github.com/MagicStack/httptools.git && \
    cd httptools && \
    python setup.py install && \
    cd .. && rm -rf httptools

# Copiar tu aplicación
COPY . .

# Exponer el puerto
EXPOSE 443

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "443"]
