"""
Módulo de Python que contiene el enrutado
"""
import datetime
import functools
from typing import List
import os
import datetime
import psycopg2
import psycopg2.extras
from typing import Optional, List, Tuple

import self
from sqlalchemy import create_engine, text, update, delete, select, func, distinct, and_
from sqlalchemy.orm import Session, aliased, joinedload, selectinload, load_only
from flask import current_app as app, render_template, redirect, url_for, flash, abort, make_response
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import select, func, desc
from sqlalchemy.orm import load_only, selectinload, joinedload
from sqlalchemy.exc import IntegrityError
from app.formularios import SignInForm, SignupForm
from . import db
from flask_login import login_user, logout_user
from flask import current_app as app, flash, redirect, url_for
from .modelos import Pelicula, Dirige, Persona, Actua, Contrato, Usuario


# NOTA: la descripcion de las variables que recibe cada template
# se encuentra explicadas en la cabecera del archivo correspondiente.

@app.route("/")
@app.route("/peliculas")
def listar_peliculas():
    """
    Ruta que muestra informacion de varias peliculas,
    utilizando una paginacion. Solo acepta metodos "GET".

    Cada pagina debe mostrar 20 peliculas, y las
    peliculas se deben mostrar ordenadas
    por popularidad y ganancias de forma descendente.

    Devuelve como respuesta el template
    `listar_peliculas.html` renderizado.
    """
    page = db.paginate(select(Pelicula)
                       .order_by(Pelicula.popularidad.desc(), Pelicula.ganancias.desc()), per_page=20)
    if page == None:
        abort(404)
    else:
        return render_template("listar_peliculas.html", page=page)
@app.route("/pelicula/<int:id_pelicula>")
def mostrar_pelicula(id_pelicula: int):
    """
    Ruta que muestra la informacion completa de una pelicula.
    Si no existe ninguna pelicula con el id, la funcion debe abortar con un error 404.
    En caso contrario, debe renderizar el template "mostrar_pelicula_completa.html".
    """

    infoPeli = db.session.scalars(select(Pelicula)
                    .where(id_pelicula == Pelicula.id)).first() #first es para objetos
    if infoPeli is None:
        abort(404)
    else:
        infoDir = db.session.scalars(select(Persona).select_from(Pelicula).join(Dirige, Dirige.id_pelicula==Pelicula.id).join(Persona, Persona.id==Dirige.id_persona).where(id_pelicula == Pelicula.id)).fetchall()
        infoActor = db.session.execute(select(Persona.id, Persona.nombre, Actua.papel).select_from(Pelicula).join(Actua, Actua.id_pelicula==Pelicula.id).join(Persona, Persona.id==Actua.id_persona).where(id_pelicula == Pelicula.id)).fetchall()
        return render_template("mostrar_pelicula_completa.html", pelicula=infoPeli, directores=infoDir, actores=infoActor)

@app.route("/persona/<int:id_persona>")
def mostrar_persona(id_persona: int):
    """
    Ruta que muestra la informacion completa de una persona.
    Si no existe ninguna persona con el id, la
    funcion debe abortar con un error 404.
    En caso contrario, debe renderizar el template
    "mostrar_persona.html".
    """
    infoPersona = db.session.scalars(select(Persona).where(id_persona == Persona.id)).first()
    if infoPersona == None:
        abort(404)
    else:
        infoDirige = db.session.execute(select(Pelicula.id, Pelicula.titulo).select_from(Persona).join(Dirige, Dirige.id_persona==Persona.id).join(Pelicula, Pelicula.id == Dirige.id_pelicula).where(id_persona == Persona.id)).fetchall()
        infoActua = db.session.execute(select(Pelicula.id, Pelicula.titulo, Actua.papel).select_from(Persona).join(Actua, Actua.id_persona==Persona.id).join(Pelicula, Pelicula.id == Actua.id_pelicula).where(id_persona == Persona.id)).fetchall()
        return render_template("mostrar_persona.html", persona=infoPersona, dirige=infoDirige, actua=infoActua)

# LOGIN MANAGER: Descomentar para login manager
from . import login_manager

@login_manager.user_loader
def carga_usuario(id_usuario: str):
    """
     Tal y como dicen los apuntes, simplemente debe
    cargar el objeto Usuario asociado a id_usuario si existe.
     """
    return db.session.get(Usuario, id_usuario)

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    """
    Registro en el sistema.
    Acepta tanto peticiones 'GET' como 'POST'.

    En esta funcion de vista, se debe renderizar
    el formulario de registro de nuevos usuarios
    con el template "sign_up.html". Una vez el usuario introduzca
    datos correctamente y se valide el usuario, se comprueba
    si ese usuario estaba ya registrado en el sistema previamente.
    En tal caso, se manda un mensaje flash
    "Ya existe un usuario con este email" y se vuelve
    a mostrar el formulario de nuevo.

    Si el usuario se ha registrado correctamente, se
    almacena en el sistema y se devuelve
    como respuesta una redirección a la función de vista
    que muestra las personas que se pueda
    contratar ("mostrar_mercado")
    con el usuario que se acaba de registrar.
    El usuario se debe loggear.
    """
    formulario = SignupForm()

    if(formulario.validate_on_submit()):
        existe = db.session.scalars(select(Usuario.email).select_from(Usuario).where(Usuario.email == formulario.email.data)).fetchall()
        if(existe): #Si el usuario está registrado, salta error
            flash("No se puede registrar ya que ya existe un usuario con ese email.")
        else: #Si no, lo añade
            usr = Usuario(email=formulario.data["email"])
            usr.password = (formulario.data["password"])
            db.session.add(usr)
            db.session.commit()
            login_user(usr)
            return redirect(url_for('mostrar_mercado'))
    return render_template("sign_up.html", form=formulario)

@app.route("/log_out")
@login_required
def log_out():
    """
    Desconexión de un usuario de la aplicación.
    Hay que comprobar que el usuario estaba previamente loggeado.
    Acciones requeridas:
        * Hacer log-out del usuario
        * Mandar un mensaje flash avisando que la desconexion ha sido correcta
        * Redireccionar a la pagina de inicio
    """
    logout_user()
    flash("Desconexión realizada con éxito")
    return redirect(url_for('sign_in'))


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    """
    Acceso de un usuario ya registrado.
    Acepta tanto peticiones 'GET' como 'POST'.

    En esta funcion de vista, se debe renderizar
    el formulario de acceso con el template "sign_in.html".
    Una vez el usuario introduzca datos correctamente,
    se comprueba si hay un usuario con ese email.
    De no ser así, se lanza un mensaje flash con
    "El email introducido no tiene un usuario asociado"
    y se vuelve a mostrar el formulario de acceso.

    En caso de que el email sí exista, se comprueba si
    la contraseña introducida es correcta. En tal caso,
    se hace login del usuario en el sistema, y se redirige
    a la función de `mostrar_mercado`.

    Si la contraseña es incorrecta, se lanza un mensaje
    flash con "Contraseña incorrecta" y se vuelve a renderizar
    el formulario de acceso.
    """
    formulario = SignupForm()
    if(formulario.validate_on_submit()):
        usr = db.session.scalars(select(Usuario).where(formulario.data["email"] == Usuario.email)).first()
        if(usr != None):
            if(not usr.check_password(formulario.data["password"])):
                flash("Contraseña incorrecta")
            else:
                login_user(usr)
                return redirect(url_for('mostrar_mercado'))
        else:
            flash("No hay un usuario con ese email")

    return render_template("sign_in.html", form=formulario)


@app.route("/mercado")
@login_required
def mostrar_mercado():
    """
    Funcion de vista que devuelve las personas que
    se encuentran disponibles en el mercado actualmente
    para contratar. Solo acepta metodos 'GET'.

    Para mostrar las personas disponibles, debemos
    considerar una paginacion que cargue a lo sumo 16 elementos,
    ordenados de forma descendente por su popularidad y forma ascendente
    por su nombre.

    Devuelve el template "mostrar_mercado.html" renderizado.
    """
    pag = db.paginate(select(Persona).where(Persona.en_mercado == True).order_by(Persona.popularidad.desc(), Persona.nombre.asc()), per_page=16)

    return render_template("mostrar_mercado.html", page=pag, presupuesto=current_user.presupuesto)


@app.route('/contratar/<int:id_persona>', methods=["POST"])
@login_required
def contratar_persona(id_persona: int):
    """
    Ruta asociada a la contratacion de una persona. Este funcion
    solo acepta peticiones 'POST'.

    Hay varias situaciones que debemos comprobar antes de hacer la
    contratacion. En cada caso, lanzamos un mensaje flash y redirigimos
    a la funcion de "mostrar_mercado":

        * El id_persona no es un id valido -> "No existe ninguna persona con id {id_persona}".
        * La persona no se encuentra disponible en el mercado ->
            "La persona con id {id_persona} no se encuentra disponible en el mercado".
        * La persona ha sido contratada previamente.
            - Si el usuario es distinto al actual -> "Alguien se te ha adelantado con el contrato...".
            - Si el usuario es el actual ->  "A este le tienes ya contratado...".
        * El usuario actual no tiene suficientes fondos para hacer la contratacion
            -> "No hay suficientes fondos: tienes {fondos} y contratar a la persona con id {id_persona} cuesta {coste}".

    Despues de comprobar las situaciones anteriores,
    añade el contrato a la lista de contratos del usuario
    actual, quita a la persona del mercado y actualiza los
    fondos disponibles del usuario actual despues de la compra.

    Una vez se ha realizado correctamente las acciones, se
    lanza un mensaje flash con el mensaje
    "Se ha contratado correctamente a la persona con id {id_persona}"
    y se redirige a la funcion de "mostrar_mercado".
    """
    pers = db.session.scalars(select(Persona).where(Persona.id == id_persona)).first()
    contrato = db.session.scalars(select(Contrato).where(Contrato.id_Persona == id_persona)).first()
    if(pers == None):
        flash(f"No existe ninguna persona con el id {id_persona}")
    elif (pers.en_mercado == False):
        flash(f"La persona con id {id_persona} no se encuentra disponible en el mercado")
    elif (contrato != None): #* La persona ha sido contratada previamente. - Si el usuario es distinto al actual -> "Alguien se te ha adelantado con el contrato...". - Si el usuario es el actual ->  "A este le tienes ya contratado...".
        if(contrato.id_usuario != current_user.id):
            flash(f"Alguien se te ha adelantado con el contrato...")
        else:
            flash(f"A este le tienes ya contratado...")
    elif(pers.cache > current_user.presupuesto):
        flash(f"No hay suficientes fondos: tienes {current_user.presupuesto} y contratar a la persona con id {id_persona} cuesta {pers.cache}")
    else: #Se puede contratar
        fecha = datetime.datetime.now()
        db.session.add( Contrato( id_Persona=id_persona, id_Usuario=current_user.id, fecha=fecha ))
        db.session.execute(update(Persona).where(Persona.id == id_persona). values(en_mercado=False))
        current_user.presupuesto = current_user.presupuesto - pers.cache
        db.session.commit()
        flash(f"Se ha contratado correctamente a la persona con id {id_persona}")
        return redirect(url_for('mostrar_mercado'))


@app.route('/mis_fichajes')
@login_required
def mostrar_fichajes():
    """
    Funcion de vista que devuelve las personas que
    ha contratado el usuario actualmente loggeado.
    Solo acepta metodos 'GET'.

    Para acceder a las personas contratadas, debemos
    considerar una paginacion que cargue a lo sumo 4 elementos,
    ordenados de forma descendente por la fecha en la que fue contratada,
    y en caso de empate, de forma ascendente por el id de la persona.

    Devuelve el template "mostrar_contratos.html" renderizado
    correctamente con esta informacion.
    """
    pag = db.paginate(select(Persona, Contrato).join_from(Persona, Contrato, Persona.id == Contrato.id_Persona).where(Contrato.id_Usuario == current_user.id).order_by(Contrato.fecha.desc(), Persona.id.asc()),per_page=4)
    contrato = db.session.scalars(select(Contrato).where(Contrato.id_Usuario == current_user.id)).fetchall()
    dict = {}
    for c in contrato:
        p = db.session.scalars(select(Persona).where(Persona.id == c.id_Persona)).first()
        dias = c.fecha - datetime.datetime.today()
        dias = dias.days
        dict[c.id_Persona] = p.computar_penalizacion(dias)
    return render_template("mostrar_contratos.html", page=pag, penalizaciones=dict)


@app.route('/despedir/<int:id_persona>', methods=["POST"])
@login_required
def despedir_persona(id_persona: int):
    """
    Ruta asociada al despido de una persona. Este funcion
    solo acepta peticiones 'POST'.

    Hay varias situaciones que debemos comprobar antes de hacer la
    contratacion. En cada caso, lanzamos un mensaje flash y redirigimos
    a la funcion de "mostrar_fichajes":

        * Si la persona no existe -> "No existe ninguna persona con id {id_persona}".
        * Si la persona no se encuentra contratada por el usuario actual ->
            "No tienes contratada a la persona con id {id_persona}"

    Despues de comprobar las situaciones anteriores,
    se elimina el contrato de la lista de contratos del usuario
    actual, la persona pasa a estar disponible en el mercado
    y se reembolsa la diferencia entre el cache de la persona y la
    penalizacion asociada al despido.

    Una vez se ha realizado correctamente las acciones, se
    lanza un mensaje flash con el mensaje
    "Se ha despedido correctamente a la persona con id {id_persona}"
    y se redirige a la funcion de "mostrar_fichajes".
    """
    pers = db.session.scalars(select(Persona).where(Persona.id == id_persona)).first()
    contrato = db.session.scalars(select(Contrato).where(Contrato.id_Persona == id_persona)).first()
    if(pers == None):
        flash(f"No existe ninguna persona con id {id_persona}")
    elif(contrato == None or contrato.id_Usuario != current_user.id):
        flash(f"No tienes contratada a la persona con id {id_persona}")
    else:
        db.session.delete(contrato)
        db.session.execute(update(Persona).where(Persona.id == id_persona).values(en_mercado=True))
        dias = contrato.fecha - datetime.datetime.today()
        dias = dias.days
        current_user.presupuesto = current_user.presupuesto + (pers.cache - pers.computar_penalizacion(dias))
        db.session.commit()
        flash(f"Se ha despedido correctamente a la persona con id {id_persona}")
    return redirect(url_for('mostrar_fichajes'))


@app.route('/clasificacion')
def clasificacion_usuarios():
    """
    Funcion que muestra la clasificacion de los
    usuarios de nuestra aplicacion. La puntuacion
    de cada usuario se computa "ad-hoc" (es decir, no la almacenamos
    en nuestra base de datos). Para computar la puntuacion,
    se considera la siguiente formula:

    * Consideramos todas las peliculas en la que haya actuado alguno de los
      interpretes que posee un usuario dado. Cada pelicula puntua #interpretes * min(popularidad),
      donde:
        - #interpretes es el numero de interpretes que posee ese usuario y que han
          participado en esa pelicula.
        - min(popularidad) es la minima popularidad de estos interpretes.

    * Sumamos #directores * #peliculas, donde #directores es el total de personas
      que han dirigido alguna pelicula, y #peliculas es el numero de peliculas (distintas)
      que han dirigido. Si una pelicula tiene dos directores, solo se suma una vez esa pelicula.

    IMPORTANTE: cargar en memoria todas las personas y peliculas puede ocupar demasiado espacio. Por tanto,
                NO podemos traer toda esa informacion de una vez al programa para gestionarla. Si es necesario
                hacer varias consultas y combinar la informacion de la puntuacion.

    Devuelve el template "clasificacion.html" renderizado.
    """
    # AYUDA: esta consulta se puede resolver combinando 3 subconsultas y una consulta no muy complicadas.
    # Para sacar la informacion de los interpretes, podeis usar dos subconsultas.
    # Sacad la informacion de los directores en una subconsulta distinta. Finalmente, combinad la informacion de
    # los usuarios con la puntuacion de interpretes y de directores.
    currUs = db.session.scalars(select(Usuario)).fetchall()
    ranking = []
    for u in currUs:

        puntPeli = db.session.scalars(
            select(func.count(Actua.id_persona) * func.min(Persona.popularidad)).join(Persona,
                                                                                      Persona.id == Actua.id_persona).join(
                Contrato, Contrato.id_Persona == Persona.id).where(Contrato.id_Usuario == u.id)).fetchall()

        puntDir = db.session.scalars(
            select(func.count(Dirige.id_persona.distinct()) * func.count(Dirige.id_pelicula.distinct())).join(Persona,
                                                                                                              Persona.id == Dirige.id_persona).join(
                Contrato, Contrato.id_Persona == Persona.id).where(Contrato.id_Usuario == u.id)).fetchall()
        aux = 0
        for p in puntPeli:
            aux += p
        for d in puntDir:
            aux += d
        ranking.append((u, aux))
    ranking.sort(key=lambda x: x[1], reverse=True)
    return render_template("clasificacion.html", ranking=ranking)
