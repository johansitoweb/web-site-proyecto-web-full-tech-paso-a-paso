from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
import json
from datetime import datetime
import random
from flask import send_file
from fpdf import FPDF
import os
import re

# INSTALAR LAS LIBRERIAS PARA CORRER EL PROGRAMA!!!!
# pip install Flask
# pip install werkzeug
# pip install fpdf
# pip install Flask werkzeug fpdf 

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


# Variables globales
peliculas_adultos = ["Venom El Ultimo Baile", "Terrifier 3 El Payaso Siniestro", "Sonrie 2", "Robot Salvaje", "La Leyenda Del Dragon" ]
peliculas_todo_publico = ["Robot Salvaje", "La Leyenda Del Dragon"]
asientos_ocupados = 30                      
PRECIO_ENTRADA = 8000

# Inicializar asientos
def inicializar_asientos(filas, columnas):
    return [["O" for _ in range(columnas)] for _ in range(filas)]

def ocupar_asientos_aleatoriamente(matriz, num_asientos_ocupados): 
    filas = len(matriz)
    columnas = len(matriz[0])
    asientos_disponibles = [(fila, col) for fila in range(filas) for col in range(columnas)]
    asientos_ocupados = random.sample(asientos_disponibles, num_asientos_ocupados)
    for fila, col in asientos_ocupados:
        matriz[fila][col] = "X"

def buscar_usuario_por_nombre(usuarios, nombre_buscado, indice=0):
    if indice >= len(usuarios):
        return None 

    if usuarios[indice]['nombre'] == nombre_buscado:
        return usuarios[indice]  

    return buscar_usuario_por_nombre(usuarios, nombre_buscado, indice + 1)

@app.route('/')
def index():
    return render_template('index.html')

class ExcepcionDatosUsuario(Exception):
    def __init__(self, mensaje):
        self.mensaje = mensaje
        super().__init__(self.mensaje)

@app.route('/iniciar_sesion', methods=['GET', 'POST'])
def iniciar_sesion():
    if request.method == 'POST':
        try:
            # Obtener los datos del formulario
            nombre = request.form.get('nombre')
            contraseña = request.form.get('contraseña')

            # Validación básica de los campos
            if not nombre or not contraseña:
                raise ExcepcionDatosUsuario('Todos los campos son requeridos.')

            # Cargar los usuarios existentes
            usuarios = cargar_usuarios()

            # Buscar el usuario con el nombre proporcionado
            usuario_encontrado = buscar_usuario_por_nombre(usuarios, nombre)
            
            # Verificar si el usuario fue encontrado y si la contraseña es correcta
            if not usuario_encontrado or usuario_encontrado['contraseña'] != contraseña:
                raise ExcepcionDatosUsuario('Usuario o contraseña incorrectos.')

            # Si todo está bien, guardar los datos del usuario en la sesión
            session['nombre'] = usuario_encontrado['nombre']
            session['edad'] = usuario_encontrado['edad']
            session['mail'] = usuario_encontrado['mail']

            # Redirigir a la página de selección de fecha
            return redirect(url_for('seleccionar_fecha'))

        except ExcepcionDatosUsuario as e:
            flash(str(e))
            return redirect(url_for('iniciar_sesion'))
    
    return render_template('iniciar_sesion.html')

# Función para cargar los usuarios desde el archivo JSON
def cargar_usuarios():
    try:
        with open('usuarios.json', 'r') as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return []

# Función para guardar los usuarios en el archivo JSON
def guardar_usuarios(usuarios):
    with open('usuarios.json', 'w') as archivo:
        json.dump(usuarios, archivo, indent=4)

# Función para verificar la contraseña
def verificar_contraseña(usuario, contraseña):
    return check_password_hash(usuario['contraseña'], contraseña)

@app.route('/crear_usuario', methods=['GET', 'POST'])

def crear_usuario():
    def es_nombre_valido(nombre):
        patron=r'^[a-zA-Z\s]+$'
        return re.match(patron,nombre)
        
    def es_correo_valido(mail):
        patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'  # Expresión regular para correo
        return re.match(patron, mail)

    if request.method == 'POST':
        nombre = request.form['nombre']
        edad = request.form['edad']
        contraseña = request.form['contraseña']
        mail = request.form['mail']
        
        usuarios = cargar_usuarios()

        #validar nombre
        if not es_nombre_valido(nombre):
            flash('El nombre solo puede contener letras y espacios.')
            return redirect(url_for('crear_usuario'))
        
        #validar mail
        if not es_correo_valido(mail):
            flash('El correo electrónico no es válido.')
            return redirect(url_for('crear_usuario'))

        for usuario in usuarios:
            if usuario['mail'] == mail:
                flash('Usuario existente')
                return redirect(url_for('crear_usuario'))
        
        nuevo_usuario = {
            'nombre': nombre,
            'edad': edad,
            'contraseña': contraseña,
            'mail': mail
        }
        usuarios.append(nuevo_usuario)

        guardar_usuarios(usuarios)

        return redirect(url_for('iniciar_sesion'))

    return render_template('crear_usuario.html')

@app.route('/seleccionar_fecha', methods=['GET', 'POST'])
def seleccionar_fecha():
    # Verificar si el usuario ha iniciado sesión
    if 'nombre' not in session:
        flash('Por favor, inicie sesión primero.', 'error')
        return redirect(url_for('iniciar_sesion'))

    # Obtener los datos del usuario desde la sesión
    nombre = session['nombre']
    edad = session['edad']
    mail = session['mail']

    if request.method == 'POST':
        fecha = request.form['fecha']
        print(f"Fecha seleccionada: {fecha}")

        # Verifica que la fecha haya sido seleccionada
        if not fecha:
            flash('Debe seleccionar una fecha.', 'error')
            return redirect(url_for('seleccionar_fecha'))

        # Redirigir a la página de selección de horario con la fecha seleccionada
        return redirect(url_for('seleccionar_horario', fecha=fecha))

    return render_template('seleccionar_fecha.html', nombre=nombre, edad=edad, mail=mail)

@app.route('/seleccionar_horario')
def seleccionar_horario():
    nombre = request.args.get('nombre')
    edad = request.args.get('edad')
    fecha = request.args.get('fecha')
    return render_template('seleccionar_horario.html', nombre=nombre, edad=edad, fecha=fecha)

# Lista de películas con sus imágenes correspondientes
peliculas_con_imagenes = [
    {'nombre': 'Venom El Ultimo Baile', 'imagen': 'static/img/venom.jpg'},
    {'nombre': 'Terrifier 3 El Payaso Siniestro', 'imagen': 'static/img/terrifier-3.jpg'},
    {'nombre': 'Sonrie 2', 'imagen': 'static/img/sonrie2.jpg'},
    {'nombre': 'Robot Salvaje', 'imagen': 'static/img/robot-salvaje.jpg'},
    {'nombre': 'La Leyenda Del Dragon', 'imagen': 'static/img/la-leyenda-del-dragon.jpg'}
]

@app.route('/seleccionar_pelicula', methods=['GET', 'POST'])
def seleccionar_pelicula():
    if 'nombre' not in session:
        flash('Por favor, inicie sesión primero.', 'error')
        return redirect(url_for('iniciar_sesion'))

    nombre = session['nombre']
    edad_str = session['edad']
    fecha = request.args.get('fecha')

    if request.method == 'POST':
        nombre = session['nombre']
        edad_str = session['edad']
        fecha = request.form.get('fecha')

    if not nombre or not edad_str or not fecha:
        flash("Faltan datos necesarios para seleccionar la película.")
        return redirect(url_for('index'))

    try:
        edad = int(edad_str)
    except ValueError:
        flash("La edad debe ser un número válido.")
        return redirect(url_for('index'))

    peliculas_adultos = peliculas_con_imagenes[:5] 
    peliculas_todo_publico = peliculas_con_imagenes[3:] 

    peliculas_seleccionadas = peliculas_adultos if edad >= 18 else peliculas_todo_publico

    return render_template('seleccionar_pelicula.html', nombre=nombre, edad=edad, fecha=fecha,peliculas=peliculas_seleccionadas)

@app.route('/confirmar_pelicula', methods=['POST'])
def confirmar_pelicula():
    nombre = session['nombre']
    edad = session['edad']
    fecha = request.form['fecha']
    pelicula_seleccionada = request.form['pelicula']
    return redirect(url_for('seleccionar_asientos', nombre=nombre, edad=edad, fecha=fecha, pelicula=pelicula_seleccionada))

@app.route('/seleccionar_asientos', methods=['GET', 'POST'])
def seleccionar_asientos():
    nombre = session['nombre']
    edad = session['edad']
    fecha = request.args.get('fecha')
    pelicula = request.args.get('pelicula')

    filas, columnas = 16, 14
    matriz = inicializar_asientos(filas, columnas)
    ocupar_asientos_aleatoriamente(matriz, asientos_ocupados)

    if request.method == 'POST':
        asientos_seleccionados = request.form.getlist('asientos')
        return redirect(url_for('realizar_pago', 
                                nombre=nombre, 
                                edad=edad, 
                                fecha=fecha, 
                                pelicula=pelicula, 
                                asientos_seleccionados=",".join(asientos_seleccionados)))

    return render_template('seleccionar_asientos.html', nombre=nombre, edad=edad, fecha=fecha,pelicula=pelicula, matriz=matriz)

@app.route('/realizar_pago', methods=['POST'])
def realizar_pago():
    nombre = session['nombre']
    edad = session['edad']
    fecha = request.form['fecha']
    pelicula = request.form['pelicula']
    cantidad_entradas = int(request.form['cantidad_entradas'])

    asientos_seleccionados = request.form.get('asientos_seleccionados', '')
    asientos_lista = asientos_seleccionados.split(',') if asientos_seleccionados else []

    try:
        if len(asientos_lista) != cantidad_entradas:
            raise ValueError(f"Debes seleccionar exactamente {cantidad_entradas} asientos. Actualmente seleccionaste {len(asientos_lista)}.")
    except ValueError as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for('seleccionar_asientos', nombre=nombre, edad=edad, fecha=fecha, pelicula=pelicula, cantidad_entradas=cantidad_entradas))

    total = cantidad_entradas * PRECIO_ENTRADA

    return render_template('realizar_pago.html', nombre=nombre, edad=edad, fecha=fecha, pelicula=pelicula, 
                           cantidad_entradas=cantidad_entradas, total=total, asientos_lista=asientos_lista)

# Método para confirmar el pago
@app.route('/confirmar_pago', methods=['POST'])
def confirmar_pago():
    # Verificar qué datos llegan
    print(request.form)  # Esto te ayudará a depurar el contenido del formulario
    
    try:
        nombre = request.form['nombre']
        edad = request.form['edad']
        pelicula = request.form['pelicula']
        fecha = request.form['fecha']
        cantidad_entradas = request.form['cantidad_entradas']
        total = request.form['total']
    except KeyError as e:
        flash(f"Error al procesar el formulario: {str(e)}")
        return redirect(url_for('realizar_pago'))  # Redirigir si hay un error

    # Redirigir a la página de impresión de entradas
    return redirect(url_for('imprimir_entrada', 
                            nombre=nombre, 
                            edad=edad, 
                            pelicula=pelicula, 
                            fecha=fecha, 
                            cantidad_entradas=cantidad_entradas, 
                            total=total))

# Ruta para mostrar los datos y permitir la impresión de la entrada
@app.route('/imprimir_entrada')
def imprimir_entrada():
    # Obtener los parámetros de la URL
    nombre = request.args.get('nombre')
    edad = request.args.get('edad')
    pelicula = request.args.get('pelicula')
    fecha = request.args.get('fecha')
    cantidad_entradas = request.args.get('cantidad_entradas')
    total = request.args.get('total')

    # Asegúrate de que los valores estén disponibles
    if not all([nombre, edad, pelicula, fecha,cantidad_entradas, total]):
        return "Error: Datos incompletos", 400 

    # Renderizar la plantilla de impresión de entrada
    return render_template('imprimir_entrada.html',
                           nombre=nombre,
                           edad=edad,
                           pelicula=pelicula,
                           fecha=fecha,
                           cantidad_entradas=cantidad_entradas,
                           total=total)

# Función para generar el PDF
def generate_pdf(nombre, edad, pelicula, fecha,cantidad_entradas, total):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Nombre: {nombre}", ln=True)
    pdf.cell(200, 10, txt=f"Edad: {edad}", ln=True)
    pdf.cell(200, 10, txt=f"Pelicula: {pelicula}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha: {fecha}", ln=True)
    pdf.cell(200, 10, txt=f"Cantidad de Entradas: {cantidad_entradas}", ln=True)
    pdf.cell(200, 10, txt=f"Total: ${total}", ln=True)

    # Usar una ruta temporal válida para Windows
    output_dir = os.path.join(os.getcwd(), 'temp')  # Crear carpeta 'temp' en el directorio actual
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "entrada.pdf")

    pdf.output(output_path)

    return output_path

# Ruta para descargar el PDF
@app.route('/descargar_pdf', methods=['POST'])
def descargar_pdf():
    nombre = request.form['nombre']
    edad = request.form['edad']
    pelicula = request.form['pelicula']
    fecha = request.form['fecha']
    cantidad_entradas = request.form['cantidad_entradas']
    total = request.form['total']

    # Generación del PDF
    pdf_file = generate_pdf(nombre, edad, pelicula, fecha, cantidad_entradas, total)

    # Enviar el archivo PDF generado al usuario para que lo descargue
    return send_file(pdf_file, as_attachment=True, download_name="entrada.pdf")

if __name__ == '__main__':
    app.run(debug=True)