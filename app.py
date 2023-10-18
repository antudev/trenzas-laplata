from flask import Flask, render_template, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, exc, event, select 


app = Flask(__name__)

# Configura la conexión a la base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://trenzado_user:v9q8ouITxUvyJJl48ZPzC7plccsr2bdT@dpg-cko6buujmi5c73e748tg-a/trenzado'

# Inicializa la extensión SQLAlchemy
db = SQLAlchemy(app)

# Función para realizar el "ping" de la conexión
def ping_connection(connection, branch):
    if branch:
        return

    try:
        # Realiza una consulta SELECT 1
        connection.scalar(select(1))
    except exc.DBAPIError as err:
        if err.connection_invalidated:
            # La conexión se invalidó, intenta nuevamente
            connection.scalar(select(1))
        else:
            raise

# Configura la carpeta de plantillas (templates)
app.template_folder = 'templates'

    
class trenzado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    
    precios_descripciones = db.relationship('PrecioDescripcion', backref='trenzado', lazy=True)

class PrecioDescripcion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    precio = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    
    trenzado_id = db.Column(db.Integer, db.ForeignKey('trenzado.id'), nullable=False)


@app.route('/')
def base():
    trenzados_data = []

    tipos_de_trenzado = trenzado.query.all()

    for tipo_trenzado in tipos_de_trenzado:
        trenzado_info = {'tipo': tipo_trenzado.tipo, 'precios': {}}

        for precio_descripcion in tipo_trenzado.precios_descripciones:
            desc = precio_descripcion.descripcion
            if 'rapado lateral/alto degrade' in desc:
                key = 'poca_rapadoalto_degrade'
            elif 'rapado lateral/alto' in desc:
                key = 'poca_rapadoalto'
            elif 'cabeza completa degrade' in desc:
                key = 'mucha_degrade'
            elif 'cabeza completa' in desc:
                key = 'mucha'
            trenzado_info['precios'][key] = precio_descripcion.precio

        trenzados_data.append(trenzado_info)
    
    lisasImages = [
        url_for('static', filename='images/tipos/lisas/PeloLiso1.jpg'),
        url_for('static', filename='images/tipos/lisas/PeloLiso2.jpg'),
        url_for('static', filename='images/tipos/lisas/PeloLiso3.jpg'),
        url_for('static', filename='images/tipos/lisas//PeloLiso4.jpg'),
        url_for('static', filename='images/tipos/lisas/PeloLiso5.jpg')
    ]  

    degradeImages = [
        url_for('static', filename='images/tipos/degrade/PeloDegrade1.jpg'),
        url_for('static', filename='images/tipos/degrade/PeloDegrade2.jpg'),
        url_for('static', filename='images/tipos/degrade/PeloDegrade3.jpg'),
        url_for('static', filename='images/tipos/degrade/PeloDegrade4.jpg'),
        url_for('static', filename='images/tipos/degrade/PeloDegrade5.jpg')
    ]

    return render_template('base.html', trenzados_data=trenzados_data, lisasImages=lisasImages, degradeImages=degradeImages)


@app.route('/precios')
def mostrar_precios():
    trenzados = trenzado.query.all()
    return render_template('precios.html', trenzados=trenzados)

# Aplicaciones tipos.de.trenzado
@app.route('/tipos_de_trenzado')
def tipos_de_trenzado():
    tipos = trenzado.query.all()
    return render_template('tipos_de_trenzado.html', tipos=tipos)


@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    pregunta = data['pregunta'].lower()
    
    respuesta = "Lo siento, no entiendo tu pregunta. este chat puede ser de ayuda para resolver tus dudas sobre distintos temas como: 1. Turnos 2. Precios 3. Tipos de trenzado 4. Duración de los turno 5. Dolor en el proceso de trenzado 6. Consejos para cuidar tus trenzas 7. Picazón en el cuero cabelludo 8. Recomendaciones sobre cabello decolorado ¿En qué tema específico te gustaría obtener información?"

    if 'turno' in pregunta:
        respuesta = "Para coordinar un turno, envíame un mensaje por WhatsApp o Instagram siguiendo estos pasos:\n1. Envíame un video de tu cabello suelto y luego haciendo una cola de caballo alta para evaluar el largo, la cantidad y el tipo de rapado (si lo hay).\n2. Aclara si tienes flequillo que no quieras trenzar.\n3. Indica el grosor y el color de las extensiones que deseas (si buscas un aspecto natural, te recomiendo elegir el mismo color que tu cabello; en caso de querer otro color, puedes solicitar camuflaje)."


    elif 'tipos de trenzados' in pregunta or 'tipos' in pregunta or 'tipo' in pregunta:
        tipos = ', '.join([tipo.tipo for tipo in trenzado.query.all()])
        respuesta = f"Ofrecemos los siguientes tipos de trenzados: {tipos}."
    
    # Agregar lógica para manejar preguntas sobre tipos específicos de trenzados y precios
    elif 'precios' in pregunta or 'precio' in pregunta:
        # Aquí obtendremos la lista de precios y la agregaremos a la respuesta
        lista_precios = obtener_lista_de_precios()  # Debes implementar esta función.
        respuesta = f"Tenemos un listado de precios para diferentes tipos de trenzados:\n{lista_precios}\n"
        
    elif 'duracion' in pregunta or 'tardan' in pregunta:
        respuesta = "La duración de un turno varía según el trabajo, pero suele ser aproximadamente 4 horas. ¿Tienes alguna otra pregunta?"

    elif 'doloroso' in pregunta or 'dolor' in pregunta:
        respuesta = "El proceso de trenzado generalmente no es doloroso, aunque la experiencia puede variar según la sensibilidad de cada persona. Si tienes una sensibilidad alta o no estás acostumbradx a peinados tirantes, házmelo saber para que el enganche de las trenzas sea menos tirante."

    elif 'no recomendable' in pregunta:
        respuesta = "No es recomendable hacerse trenzas si tienes el cabello decolorado recientemente desde la raíz y está muy maltratado. En ese caso, te recomiendo dejar crecer unos centímetros de raíz y recuperar el largo. También, si notas que estás perdiendo más de 100 cabellos al día, es aconsejable consultar con un profesional."

    elif 'tips' in pregunta or 'cuidar' in pregunta:
        respuesta = "Aquí tienes algunos consejos para cuidar tus trenzas:\n1. Lava tus trenzas una o dos veces por semana. Evita el exceso de agua, ya que puede reducir su durabilidad.\n2. Diluye el champú en agua y masajea suavemente el cuero cabelludo con la yema de los dedos. El uso de acondicionador es opcional.\n3. Hidrata tu cuero cabelludo ocasionalmente con aceite para evitar que tu cabello natural se reseque.\n4. Lava las trenzas por la mañana para que se sequen durante el día y evita dormir con las trenzas mojadas para prevenir olores a humedad.\n5. Usa un pañuelo de satén para dormir, lo cual evitará el frizz en la raíz.\n6. Las trenzas pueden durar hasta dos meses o más si sigues estos cuidados."

    elif 'picazón' in pregunta:
        respuesta = "Si te hiciste trenzas y estás experimentando picazón y/o zonas rojas, aquí tienes algunos consejos para aliviarlo:\n1. Rocía una mezcla de 50% de agua y 50% de vinagre de manzana en el cuero cabelludo o en las zonas que pican. Deja actuar durante 15 minutos y luego enjuaga con abundante agua.\n2. Prueba con romero: Hierve una taza y media de agua y agrega romero en cantidad adecuada. Deja enfriar y colócalo en el cuero cabelludo o las zonas con picazón. No es necesario enjuagar.\n3. Aplica Aloe Vera en el cuero cabelludo y deja que actúe, sin necesidad de enjuague."

    return jsonify({'respuesta': respuesta})

# Función para obtener la lista de precios desde la base de datos
def obtener_lista_de_precios():
    precios = {}
    tipos_de_trenzado = trenzado.query.all()
    for tipo in tipos_de_trenzado:
        precios_descripciones = tipo.precios_descripciones
        precios[tipo.tipo] = {}
        for precio_desc in precios_descripciones:
            precios[tipo.tipo][precio_desc.descripcion] = precio_desc.precio

    # Formatea la lista de precios
    lista_precios = ""
    for tipo, descripcion_precio in precios.items():
        lista_precios += f"{tipo}:\n"
        for descripcion, precio in descripcion_precio.items():
            lista_precios += f"  - {descripcion}: ${precio}\n"

    return lista_precios

if __name__ == '__main__':
    
    from app import db
    from app import Turno, trenzado, PrecioDescripcion
    with app.app_context():
        db.create_all()

        if trenzado.query.count() == 0:
            # Creación de instancias de Trenzado
            
            tipo_small = trenzado(tipo='small.finas')
            tipo_medium = trenzado(tipo='medium.medianas')
            tipo_large = trenzado(tipo='large.grande')
            tipo_jumbo = trenzado(tipo='jumbo.extragrande')

            # Agregar instancias de Trenzado a la sesión
            db.session.add_all([tipo_small, tipo_medium, tipo_large, tipo_jumbo])
            db.session.commit()

            # Instancias de PrecioDescripcion y relación con Trenzado

            precio_small_rapadoalto = PrecioDescripcion(precio=21000, descripcion='rapado lateral/alto')
            precio_small_muchacantidad = PrecioDescripcion(precio=24000, descripcion='cabeza completa')
            tipo_small.precios_descripciones.extend([precio_small_rapadoalto, precio_small_muchacantidad])

            precio_medium_rapadoalto = PrecioDescripcion(precio=20000, descripcion='rapado lateral/alto')
            precio_medium_muchacantidad = PrecioDescripcion(precio=23000, descripcion='cabeza completa')
            tipo_medium.precios_descripciones.extend([precio_medium_rapadoalto, precio_medium_muchacantidad])

            precio_large_rapadoalto = PrecioDescripcion(precio=18000, descripcion='rapado lateral/alto')
            precio_large_muchacantidad = PrecioDescripcion(precio=21800, descripcion='cabeza completa')
            tipo_large.precios_descripciones.extend([precio_large_rapadoalto, precio_large_muchacantidad])
            
            precio_jumbo_rapadoalto = PrecioDescripcion(precio=17000, descripcion='rapado lateral/alto')
            precio_jumbo_muchacantidad = PrecioDescripcion(precio=20000, descripcion='cabeza completa')
            tipo_jumbo.precios_descripciones.extend([precio_jumbo_rapadoalto, precio_jumbo_muchacantidad])

            # Instancias de PrecioDescripcion para colores degradé
                        

            precio_small_rapadoalto_degrade = PrecioDescripcion(precio=21300, descripcion='rapado lateral/alto degrade')
            precio_small_muchacantidad_degrade = PrecioDescripcion(precio=24400, descripcion='cabeza completa degrade')
            tipo_small.precios_descripciones.extend([precio_small_rapadoalto_degrade, precio_small_muchacantidad_degrade])

            precio_medium_rapadoalto_degrade = PrecioDescripcion(precio=20300, descripcion='rapado lateral/alto degrade')
            precio_medium_muchacantidad_degrade = PrecioDescripcion(precio=23400, descripcion='cabeza completa degrade')
            tipo_medium.precios_descripciones.extend([precio_medium_rapadoalto_degrade, precio_medium_muchacantidad_degrade])

            precio_large_rapadoalto_degrade = PrecioDescripcion(precio=18300, descripcion='rapado lateral/alto degrade')
            precio_large_muchacantidad_degrade = PrecioDescripcion(precio=22200, descripcion='cabeza completa degrade')
            tipo_large.precios_descripciones.extend([precio_large_rapadoalto_degrade, precio_large_muchacantidad_degrade])
            
            precio_jumbo_rapadoalto_degrade = PrecioDescripcion(precio=17300, descripcion='rapado lateral/alto degrade')
            precio_jumbo_muchacantidad_degrade = PrecioDescripcion(precio=20400, descripcion='cabeza completa degrade')
            tipo_jumbo.precios_descripciones.extend([precio_jumbo_rapadoalto_degrade, precio_jumbo_muchacantidad_degrade])

            # Instancias de PrecioDescripcion a la sesión y confirmar los cambios
            db.session.add_all([
                precio_small_rapadoalto, precio_small_muchacantidad,
                precio_medium_rapadoalto, precio_medium_muchacantidad,
                precio_large_rapadoalto, precio_large_muchacantidad,
                precio_jumbo_rapadoalto, precio_jumbo_muchacantidad,
                precio_small_rapadoalto_degrade, precio_small_muchacantidad_degrade,
                precio_medium_rapadoalto_degrade, precio_medium_muchacantidad_degrade,
                precio_large_rapadoalto_degrade, precio_large_muchacantidad_degrade,
                precio_jumbo_rapadoalto_degrade, precio_jumbo_muchacantidad_degrade
            ])
            db.session.commit()

        app.run()
