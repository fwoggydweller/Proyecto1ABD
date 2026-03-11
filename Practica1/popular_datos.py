"""
Modulo que permite cargar los datos de csvs en la aplicacion.
Si la base de datos se encuentra creada, la borra y la vuelve a crear
desde 0.
"""
from pathlib import Path
import random
from csv import DictReader
from app import create_app, db
from app.modelos import Persona, Pelicula, Dirige, Actua
from sqlalchemy import select, func, update


def carga_personas():
    with open('data/people.csv', 'r') as f:
        csv_reader = DictReader(f)
        for row in csv_reader:
            db.session.add(Persona(id=row["person_id"],
                                   nombre=row["name"],
                                   popularidad=row["popularity"],
                                   biografia=row["biography"],
                                   cumple=row["birthday"] if row["birthday"] != '' else None,
                                   url_imagen=row["profile_url"],
                                   en_mercado=False
                                   ))



def carga_pelis():
    with open('data/movies.csv', 'r') as f:
        already = set()
        csv_reader = DictReader(f)
        for row in csv_reader:
            if row["movie_id"] not in already:
                already.add(row["movie_id"])
                db.session.add(Pelicula(
                    id=row["movie_id"],
                    titulo=row["title"],
                    resumen=row["overview"],
                    presupuesto=float(row["budget"]) // 10**6,
                    ganancias=float(row["revenue"]) // 10**6,
                    popularidad=row["popularity"],
                    url_imagen=row["poster_url"]
                ))

def carga_actua():
    with open('data/acts.csv', 'r') as f:
        already = set()
        csv_reader = DictReader(f)
        for row in csv_reader:
            tupla_peli_persona = row["movie_id"], row["person_id"]
            if tupla_peli_persona not in already:
                already.add(tupla_peli_persona)

                db.session.add(Actua(id_pelicula=row["movie_id"],
                                     id_persona=row["person_id"],
                                     papel=row["character"]))

def carga_dirige():
    already = set()
    with open('data/directs.csv', 'r') as f:
        csv_reader = DictReader(f)
        for row in csv_reader:
            tupla_peli_persona = row["movie_id"], row["person_id"]
            if tupla_peli_persona not in already:
                already.add(tupla_peli_persona)
                db.session.add(Dirige(id_pelicula=row["movie_id"],
                                      id_persona=row["person_id"]))

def popular_datos():
    carga_personas()
    carga_pelis()
    db.session.commit()

    carga_actua()
    carga_dirige()
    db.session.commit()


def borrar_crear_base_de_datos():
    db.drop_all()
    db.create_all()

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        borrar_crear_base_de_datos()
        popular_datos()