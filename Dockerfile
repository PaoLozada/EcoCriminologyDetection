ARG PORT=443

FROM cypress/browsers:latest

# Instalar Python, virtualenv y herramientas de desarrollo
RUN apt-get update && apt-get install -y python3 python3-venv python3-pip build-essential libssl-dev libffi-dev python3-dev

# Crear un entorno virtual
RUN python3 -m venv /opt/venv

# Activar el entorno virtual y actualizar pip
RUN /opt/venv/bin/pip install --upgrade pip

# Copiar el archivo requirements.txt
COPY requirements.txt .

# Instalar dependencias en el entorno virtual
RUN /opt/venv/bin/pip install --upgrade 'setuptools<60' wheel
RUN apt-get install -y gcc
RUN /opt/venv/bin/pip install --prefer-binary httptools==0.4.0
RUN /opt/venv/bin/pip install -r requirements.txt

# Copiar el resto del código
COPY . .

# Establecer la variable de entorno para usar el entorno virtual
ENV PATH="/opt/venv/bin:$PATH"

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "443"]
