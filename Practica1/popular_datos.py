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

max = 0

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
            global max
            max = max + 1

def randomiza_personas():
    min = int(max/2)
    ran = random.randint(min, max)
    i = 0
    while(i<ran):
        User = db.session.scalar(select(Persona.id).order_by(func.random()).limit(1))
        if (User):
            db.session.execute(update(Persona).where(Persona.id == User).values(en_mercado=True))
        i= i+1

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
    randomiza_personas()
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