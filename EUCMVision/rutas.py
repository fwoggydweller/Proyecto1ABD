"""
Módulo de Python que contiene las rutas
"""
import datetime
from flask import current_app as app, render_template, redirect, url_for, flash, abort, request
from .formularios import GenerarQuizForm
from . import mongo
from .trivia import generar_n_preguntas_aleatoriamente
from .render_utils import render_pagination


@app.route("/")
@app.route("/ediciones")
def mostrar_ediciones():
    # Muestra la lista de ediciones, utilizando una paginacion.
    # Os proporciono los metodos para cargar la pagina actual y
    # renderizar la respuesta (con el elemento pagination). Vosotros teneis que hacer
    # la carga de informacion la base de datos. En particular, debeis cuantos documentos
    # hay en total para computar "total_elementos" (podeis utilizar el metodo "count_documents").

    # Pagina actual de resultados
    pagina = int(request.args.get('page', 1))

    # Numero de elementos por pagina
    elementos_por_pagina = 5

    # AQUI VA VUESTRO CODIGO
    festivales = list(mongo.db.festivales.find({}))
    total_elementos = len(festivales)
    #Descomentad cuando cargueis la informacion
    paginacion = render_pagination(pagina, elementos_por_pagina, total_elementos, 'mostrar_ediciones')

    return render_template("mostrar_ediciones.html", festivales=festivales,
                            pagination=paginacion, pagina=pagina)


@app.route("/edicion/<int:anyo>")
def mostrar_festival(anyo: int):
    # Mostrar la lista de participaciones, dado un anyo.
    # Devuelve un error 404 si no se encuentra presente ese anyo.
    # Como respuesta, renderiza el template "mostrar_actuaciones_edicion.html"
    res = mongo.db.festivales.find_one({'anyo':anyo}) #te devuelve el festival para ese año, con la lista de participantes
    if res:
        return render_template("mostrar_actuaciones_edicion.html", anyo=res["anyo"],
                               pais_organizador=res["pais"], ciudad=res["ciudad"],
                               participaciones=res["concursantes"])
    else:
        abort(404)



@app.route('/jugar')
def jugar_quiz():
    # Jugar a un quiz. Esta funcion NO la teneis que modificar
    # (salvo probar diferentes num_preguntas si quereis un quiz mas largo).
    # Hay dos opciones: si no venimos de 'generar_quiz',
    # la lista de anyos y paises es vacia. Este caso se procesa en "OperacionesEurovision",
    # ya que si las listas son vacias, se asume que no hay ninguna restriccion.
    # Esta informacion se la proporcionamos al metodo "generar_n_preguntas_aleatoriamente", el cual devuelve
    # "n" preguntas que extienden a Trivia. Hay que proporcionar estas preguntas con el metodo "to_dict()" (para
    # convertir en diccionario) a la funcion "funcion_quiz_json"
    anyos = request.args.getlist("anyos", type=int)
    paises = request.args.getlist("paises")
    nombre = request.args.get("nombre", None)
    num_preguntas = 3

    preguntas_aleatorias = generar_n_preguntas_aleatoriamente(num_preguntas, anyos, paises, mongo.db["festivales"])

    preguntas = {"preguntas": [pregunta.to_dict() for pregunta in preguntas_aleatorias]}

    # Solo guardamos un nombre si no es nulo ni vacio
    if nombre:
        preguntas["_id"] = nombre

    return render_template("juego.html", preguntas=preguntas, guardable=nombre is not None)


@app.route('/quiz', methods=['GET', 'POST'])
def generar_quiz():
    # Generacion de un quiz personalizado.
    # Para crear un Quiz, tenemos que crear un formulario "GenerarQuizForm", el cual
    # debe recibir la lista de anyos y la lista de paises disponibles en la base de datos en su constructor.
    # La lista de anyos debe ir ordenada de forma descendente, y la lista de paises de forma ascendente.
    # El formulario se debe renderizar con "crear_quiz.html"
    # Una vez el formulario se valide correctamente, debemos redireccionar a la funcion de vista
    # 'jugar_quiz', que debe recibir la lista de anyos (variable "anyos"), la lista de paises (variable "paises")
    # y el nombre del formulario (variable "nombre"). Estas variables se leen con request.args.get
    DictAnyos = list(mongo.db.festivales.aggregate([{'$sort' : {'anyo':-1, '_id':1}}, {'$project' : {'anyo':1, '_id':0}}]))
    anyos = []
    for anyo in DictAnyos:
        anyos.append(anyo['anyo'])
    DictPaises = list(mongo.db.festivales.aggregate([{'$sort' : {'pais':1, '_id':1}}, {'$project' : {'pais':1, '_id':0}}]))
    paises = []
    for pais in DictPaises:
        paises.append(pais['pais'])
    formulario = GenerarQuizForm(anyos=anyos, paises=paises)
    if formulario.validate_on_submit():
        return redirect(url_for("jugar_quiz", anyos=anyos, paises=paises, nombre=formulario.nombre.data))

    return render_template("crear_quiz.html", form=formulario)


@app.route("/pais/<id_pais>")
def mostrar_actuaciones_pais(id_pais: str):
    # Muestra todas las actuaciones de un pais, ordenadas de forma decreciente en funcion del anyo.
    # Si el id del pais no existe, devuelve un error 404.
    # En esta funcion, utilizamos una paginacion para no cargar todos los resultados
    # de golpe. Os proporciono directamente como cargar la pagina correspondiente (con request.args.get)
    # y como generar la paginacion. Vosotros teneis que obtener cuantos elementos hay en total, y
    # filtrar los elementos que se corresponden a la pagina ("pagina") teniendo en cuenta el numero de elementos
    # que hay en cada pagina ("elementos_por_pagina")

    pagina = int(request.args.get('page', 1))
    elementos_por_pagina = 10
    participaciones = list(mongo.db.festivales.aggregate(
        [{"$unwind": "$concursantes"}, {"$match": {"concursantes.id_pais": id_pais}}, {"$sort": {"anyo": -1}}, {
            "$project": {"_id": 0, "anyo": 1, "ciudad": 1, "pais": "$concursantes.pais", "anyo": "$fecha",
                         "pais_organizador": "$pais", "ciudad": "$ciudad", "artista": "$concursantes.artista",
                         "cancion": "$concursantes.cancion", "resultado": "$concursantes.resultado",
                         "puntuacion": "$concursantes.puntuacion", "url_youtube": "$concursantes.url_youtube"}}]))
    if participaciones:
        """
        Template que muestra las actuaciones de un pais, dada una paginacion. Debe recibir los
 siguientes parametros:
 * "pagina": numero de pagina actual.
 * "pagination": objeto paginacion que se genera con el metodo "render_pagination" del modulo render_utils.
 * "pais": nombre del pais (tiene que ser el nombre, no el id)
 * "participaciones": lista de diccionarios los cuales contienen las siguientes claves:
    - "anyo": anyo en el que se celebro la edicion.
    - "pais_organizador": pais que organizo la edicion.
    - "ciudad": ciudad donde se celebro la edicion.
    - "artista": artista que interpreto la cancion.
    - "cancion": cancion interpretada.
    - "resultado": posicion en la que quedo en ese festival.
    - "puntuacion": puntuacion total.
    - "url_youtube": url del video de youtube con la actuacion.
        """
        total_elementos = len(participaciones)
        # Descomentad cuando cargueis la informacion
        paginacion = render_pagination(pagina, elementos_por_pagina, total_elementos, 'mostrar_actuaciones_pais', id_pais=id_pais)

        return render_template("mostrar_actuaciones_pais.html", pais=participaciones[0]["pais"], participaciones=participaciones, pagination=paginacion, pagina=pagina)
    else:
        abort(404)

@app.route("/upload_contest", methods=["POST"])
def guardar_concurso():
    # Guarda un concurso personalizado.
    # A esta funcion se le invoca al acabar un quiz, si el usuario
    # decide almacenar las preguntas que se han generado.
    # La informacion "data" se guarda en la coleccion "quizzes".
    # Hay que hacer dos cambios sobre el diccionario "data":
    #
    # * Borrar el campo "seleccionado" de cada pregunta,
    #   ya que no nos interesan las respuestas del usuario.
    #
    # * Añadir la fecha de creacion en el campo "creacion"
    #
    # Una vez se ha almacenado la informacion, se redirige a la lista de quizzes.

    # data es el diccionario con la informacion
    data = request.get_json()

    # AQUI VA VUESTRO CODIGO
    #borramos el campo seleccionado de cada pregunta
    for pregunta in data["preguntas"]:
        pregunta["seleccionado"] = None

    data["creacion"] = datetime.datetime.now()
    mongo.db.quizzes.insert_one(data)

    # En este caso, no hacemos un redirect directamente porque desde JS no se reconoce
    # bien. En su lugar, devolvemos la respuesta en un json
    return {'redirect': url_for('mostrar_quizzes')}


@app.route("/quizzes")
def mostrar_quizzes():
    # Muestra la lista de quizzes en la aplicacion, utilizando una paginacion.
    # Os proporciono los metodos para cargar la pagina actual y
    # renderizar la respuesta (con el elemento pagination). Vosotros teneis que hacer
    # la carga de informacion la base de datos y renderizar "listar_quizzes.html".
    # La lista de quizzes se debe cargar en orden decreciente segun la fecha de creacion.

    # Pagina actual de resultados
    pagina = int(request.args.get('page', 1))

    # Numero de elementos por pagina
    elementos_por_pagina = 20

    quizzes = list(mongo.db.quizzes.aggregate([{"$sort": {"creacion":-1}},{"$project": {"nombre": 1, "creacion": 1}}]))

    total_elementos = len(quizzes)

    # Descomentad cuando cargueis la informacion
    paginacion = render_pagination(pagina, elementos_por_pagina, total_elementos, 'mostrar_quizzes')

    return render_template("listar_quizzes.html", quizzes=quizzes,
                            pagination=paginacion, pagina=pagina)



@app.route("/jugar/<nombre_quiz>")
def jugar_quiz_personalizado(nombre_quiz: str):
    # Juega a un quiz que ha sido creado previamente por un usuario
    # Primero, hay que comprobar un quiz con ese nombre en la coleccion
    # "quizzes". En tal caso, cargamos toda la informacion y renderizamos "juego.html".
    # Si no es asi, lanzamos un error 404.
    quizz = mongo.db.quizzes.find_one({"_id": nombre_quiz})
    if(quizz == None):
        abort(404)
    else:
        return render_template("juego.html", preguntas=quizz, guardable=True)

