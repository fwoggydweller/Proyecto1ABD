from pathlib import Path
import random
from csv import DictReader
from app import create_app, db
from app.modelos import Persona, Pelicula, Dirige, Actua, Contrato, Usuario
from sqlalchemy import select, func, update, delete
def reinicia_estado_juego():

    db.session.execute(delete(Contrato))  # Elimino todos los contratos
    db.session.commit()
    db.session.execute(
        update(Usuario).values(presupuesto=100))  # Resetteo a valor por defecto (actualmente es cien) el presupuesto
    db.session.commit()

if __name__ == '__main__':
    # Creo una instancia de la aplicacion para inicializar la base de datos
    flask_app = create_app()

    # Para ejecutar codigo en el contexto de la aplicacion, debemos utilizar
    # esta sentencia
    with flask_app.app_context():
        reinicia_estado_juego()