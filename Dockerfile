# Usamos una imagen base de Python
FROM python:3.9

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar archivos del proyecto al contenedor
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto en el que correrá la app
EXPOSE 5000

# Comando para correr la aplicación con Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
