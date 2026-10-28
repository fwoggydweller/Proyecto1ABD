import datetime
import math
from typing import List

from flask_login import UserMixin
from sqlalchemy import String, ForeignKey, Column
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from . import db
from . import db
from werkzeug.security import generate_password_hash, check_password_hash


class Pelicula(db.Model):
    id: Mapped[int] =  mapped_column(primary_key=True)
    titulo: Mapped[str] =  mapped_column()
    resumen: Mapped[str] =  mapped_column()
    presupuesto: Mapped[float] =  mapped_column()
    ganancias: Mapped[int] =  mapped_column()
    popularidad: Mapped[float] =  mapped_column()
    url_imagen: Mapped[str] =  mapped_column()
    def __repr__(self):
        return (f'Pelicula(id={self.id}, titulo={self.titulo}, resumen={self.resumen},'
                f'presupuesto={self.presupuesto}, ganancias={self.ganancias},'
                f'popularidad={self.popularidad}, url_imagen={self.url_imagen})')

class Persona(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column()
    cumple: Mapped[datetime.datetime] = mapped_column(nullable=True)
    biografia: Mapped[str] = mapped_column()
    popularidad: Mapped[float] = mapped_column(nullable=True)
    url_imagen: Mapped[str] = mapped_column()
    en_mercado: Mapped[bool] = mapped_column(default=False)
    def __repr__(self):
        return f'Persona(id={self.id} , nombre={self.nombre} , cumple={self.cumple} , biografia={self.biografia} , popularidad= {self.popularidad}, url_imagen={self.url_imagen} , en_mercado={self.en_mercado})'
    @property
    def cache(self):
        return math.ceil(self.popularidad) if self.popularidad is not None else 1

    def computar_penalizacion(self, dias: int) -> float:
        return self.cache*min(0.05 * dias, 0.25)

class Dirige(db.Model):
    id_persona: Mapped[int] = mapped_column(ForeignKey(Persona.id), primary_key=True)
    id_pelicula: Mapped[int] = mapped_column(ForeignKey(Pelicula.id), primary_key=True)
    def __repr__(self):
        return f'Dirige(id_Persona={self.id_persona}, id_pelicula={self.id_pelicula})'

class Actua(db.Model):
    id_persona: Mapped[int] = mapped_column(ForeignKey(Persona.id), primary_key=True)
    id_pelicula: Mapped[int] = mapped_column(ForeignKey(Pelicula.id), primary_key=True)
    papel: Mapped[str] = mapped_column()
    def __repr__(self):
        return f'Actua(id_persona={self.id_persona}, id_pelicula={self.id_pelicula}, papel={self.papel})'

class Usuario(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    presupuesto: Mapped[float] = mapped_column(default=100)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    def __repr__(self):
        return f'Usuario(id={self.id}, email={self.email}, presupuesto={self.presupuesto}, password_hash={self.password_hash})'

    @property
    def password(self):
        raise AttributeError('No se puede leer el atributo password')

        # Especificando `nombre_propiedad.setter`, definimos la función setter. Esta función
        # se invoca siempre que asignemos al atributo un nuevo valor. En este caso, cuando hagamos usuario.password

    @password.setter
    def password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)


    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class Contrato(db.Model):
    id_Persona: Mapped[int] = mapped_column(ForeignKey(Persona.id), primary_key=True)
    id_Usuario: Mapped[int] = mapped_column(ForeignKey(Usuario.id))
    fecha: Mapped[datetime.datetime] = mapped_column()
    def __repr__(self):
        return f'Contrato(id_Persona={self.id_Persona}, id_Usuario={self.id_Usuario}, fecha={self.fecha})'
