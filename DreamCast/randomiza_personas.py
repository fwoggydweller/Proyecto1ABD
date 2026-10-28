from pathlib import Path
import random
from csv import DictReader
from app import create_app, db
from app.modelos import Persona, Pelicula, Dirige, Actua, Contrato, Usuario
from sqlalchemy import select, func, update

def randomiza_personas(n: int):
    i = 0
    while(i<n):
        User = db.session.scalar(select(Persona.id).order_by(func.random()).limit(1))
        if (User):
            db.session.execute(update(Persona).where(Persona.id == User).values(en_mercado=True))
        i= i+1

if __name__ == '__main__':
    # Creo una instancia de la aplicacion para inicializar la base de datos
    flask_app = create_app()

    # Para ejecutar codigo en el contexto de la aplicacion, debemos utilizar
    # esta sentencia
    with flask_app.app_context():
        n = input("Número de actores a settear activos: ")
        print(f"num: {n}")

        randomiza_personas(int(n))