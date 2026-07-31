# Usa una imagen base oficial de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Configura el PYTHONPATH manualmente, sin usar $PYTHONPATH
ENV PYTHONPATH="/app/app"

# Copia los archivos de requirements y los instala
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente a la imagen, incluida la carpeta app/
COPY . .

# Expone el puerto que usará el contenedor
EXPOSE 8080

# Ejecuta la aplicación con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "8", "--timeout", "300", "app.main:app"]