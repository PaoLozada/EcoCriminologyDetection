# Usar una imagen base adecuada que ya incluya las dependencias necesarias
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

# Copiar requirements.txt y otros archivos necesarios
COPY requirements.txt .

# Instalar dependencias generales
RUN pip install --upgrade pip setuptools wheel

# Instalar dependencias desde requirements.txt
RUN pip install -r requirements.txt

# Copiar tu aplicación
COPY . .

# Configurar variables de entorno, etc.

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "443"]
