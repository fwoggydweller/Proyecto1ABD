"""
Modulo que contiene diferentes modelos de consulta para la seccion de "trivia".
"""
import random
from typing import List
from abc import ABC, abstractmethod
from .operaciones_coleccion import OperacionesEurovision


# Clases para encapsular las preguntas y respuestas generadas aleatoriamente
class Trivia(ABC):
    """
    Clase abstracta con los metodos que deben implementar todas las preguntas de trivia.
    """
    @abstractmethod
    def __init__(self, parametros: OperacionesEurovision):
        self.parametros = parametros

    @property
    @abstractmethod
    def pregunta(self) -> str:
        """
        Pregunta que se debe mostrar
        """
        pass

    @property
    @abstractmethod
    def opciones_invalidas(self) -> List[str]:
        """
        Lista de opciones invalidas. Deben ser exactamente 3
        """
        pass

    @property
    @abstractmethod
    def respuesta(self) -> str:
        """
        Respuesta correcta
        """
        pass

    @property
    @abstractmethod
    def puntuacion(self) -> int:
        """
        Puntuacion asociada a la pregunta
        """
        pass

    def to_dict(self):
        # Sorteamos aleatoriamente las respuestas
        respuestas = [self.respuesta, *self.opciones_invalidas]
        random.shuffle(respuestas)

        # Funcion que genera la informacion que pasamos al script de trivia en el formato adecuado
        return {"pregunta": self.pregunta,
                "correcta": respuestas.index(self.respuesta),
                "respuestas": respuestas,
                "puntuacion": self.puntuacion,
                "tipo": "pregunta"}


class PrimerAnyoParticipacion(Trivia):
    """
    Pregunta que anyo fue el primero en el que participo un pais seleccionado aleatoriamente
    """

    def __init__(self, parametros: OperacionesEurovision):
        super().__init__(parametros)

        query = parametros._restringir_anyo() + [{"$unwind": '$concursantes'}] + parametros._restringir_pais_participante() + [{"$sort": {"anyo": -1}}, {"$limit": 1}, {"$project": {"_id": 0, "anyo": 1, "pais": 1}}]
        solucion = next(parametros.agregacion(query), None)

        if(solucion != None):
            self._respuesta = str(solucion["anyo"])
            self.pais = str(solucion["pais"])
            queryInv = [{"$match": {"anyo": {"$ne": self._respuesta}}}]
            self._opciones_invalidas = parametros.anyo_aleatorio(3, queryInv)
        else:
            a_validos = []
            self._respuesta = "Desconocido"
            self._opciones_invalidas = a_validos




    @property
    def pregunta(self) -> str:
        return f"¿En qué año participó por primera vez {self.pais}?"

    @property
    def opciones_invalidas(self) -> List[str]:
        return self._opciones_invalidas

    @property
    def respuesta(self) -> str:
        return self._respuesta

    @property
    def puntuacion(self) -> int:
        """
        Puntuacion asociada a la pregunta
        """
        return 2


class CancionPais(Trivia):
    """
    Pregunta de que pais es el interprete de una cancion, dada el titulo de la cancion
    """

    def __init__(self, parametros: OperacionesEurovision):
        # Obtenemos una participacion para la respuesta
        super().__init__(parametros)
        query = parametros._restringir_anyo() + [{"$unwind": '$concursantes'}] + parametros._restringir_pais_participante() + [{"$sample": {"size":1}}, {"$project": {"_id": 0, "pais": "$concursantes.pais", "cancion": "$concursantes.cancion"}}]
        solucion = next(parametros.agregacion(query), None)

        p_validos = []

        if(solucion != None):
            self._respuesta = str(solucion["pais"])
            self._cancion = str(solucion["cancion"])
            queryInv = [{"$match": {"pais": {"$ne": self._respuesta}}}]
            self._opciones_invalidas = parametros.paises_participantes_aleatorios(3, queryInv)

        else:

            self._respuesta = "Desconocido"
            self._cancion = "Desconocido"
            self._opciones_invalidas = p_validos


    @property
    def pregunta(self) -> str:
        return f"¿De que país es el intérprete de la canción '{self._cancion}'?"

    @property
    def opciones_invalidas(self) -> List[str]:
        return self._opciones_invalidas

    @property
    def respuesta(self) -> str:
        return self._respuesta

    @property
    def puntuacion(self) -> int:
        """
        Puntuacion asociada a la pregunta
        """
        return 1


class MejorClasificacion(Trivia):
    """
    Pregunta: ¿Que cancion/pais obtuvo la mejor posicion en un anyo dado?

    Respuesta: las respuestas deben ser de la forma cancion/pais.

    IMPORTANTE: la solucion debe ser unica. Ademas, todos las opciones
    deben haber participado el mismo anyo.
    """
    def __init__(self, parametros: OperacionesEurovision):
        super().__init__(parametros)
        self._anyo = parametros.anyo_aleatorio(1)[0]

        query = parametros._restringir_anyo() + [{"$unwind": '$concursantes'}] + parametros._restringir_pais_participante() + [{"$match": {"anyo": self._anyo}},{"$sort": {"concursantes.resultado": -1}}, {"$limit": 1}, {"$project": {"_id": 0, "pais": "$concursantes.pais", "cancion": "$concursantes.cancion"}}]
        solucion = next(parametros.agregacion(query), None)

        p_sol = []

        if(solucion != None):
            self._respuesta = str(solucion["cancion"] + "/" + str(solucion["pais"]))

            query_opt_inv = parametros._restringir_anyo() + [
                {"$unwind": '$concursantes'}] + parametros._restringir_pais_participante() + [
                                {"$match": {"entry": {"$ne": {"pais": solucion["pais"]}}}}, {"$sample": {"size": 3}}, {
                    "$project": {"_id": 0, "pais": "$concursantes.pais", "cancion": "$concursantes.cancion"}}]
            p_invalidos = parametros.agregacion(query_opt_inv)

            for p in p_invalidos:
                p_sol.append(str(p["cancion"] + "/" + str(p["pais"])))
        else:
            self._respuesta = "Desconocido"


        self._opciones_invalidas = p_sol

    @property
    def pregunta(self) -> str:
        return f"¿Que canción/país obtuvo la mejor posición en {self._anyo}?"

    @property
    def opciones_invalidas(self) -> List[str]:
        return self._opciones_invalidas

    @property
    def respuesta(self) -> str:
        return self._respuesta

    @property
    def puntuacion(self) -> int:
        return 3


class MejorMediaPuntos(Trivia):
    """
    Pregunta que pais ha tenido mejor media de resultados en un periodo determinado.

    IMPORTANTE: la solucion debe ser unica.
    """
    def __init__(self, parametros: OperacionesEurovision):
        super().__init__(parametros)
        a, b = parametros.anyo_aleatorio(2)
        if(a > b):
            self._anyo_inicial = b
            self._anyo_final = a
        else:
            self._anyo_inicial = a
            self._anyo_final = b
        query_paises = parametros._restringir_anyo() + [{"$match": {"anyo": {"$lte": self._anyo_final, "$gte": self._anyo_inicial}}}, {"$unwind": "$concursantes"}, {"$group": {"_id":"$concursantes.pais", "puntMedia": {"$avg": "$concursantes.puntuación"}}}, {"$sort": {"puntMedia": 1}}, {"$limit": 1}]
        solucion = next(parametros.agregacion(query_paises), None)
        if(solucion != None):
            self._respuesta = str(solucion["_id"])
        else:
            self._respuesta = "Desconocido"
        query_paises_inv = parametros._restringir_anyo() + [{"$match": {"anyo": {"$lte": self._anyo_final, "$gte": self._anyo_inicial}}}, {"$unwind": "$concursantes"},{"$group": {"_id":"$concursantes.pais", "puntMedia": {"$avg": "$concursantes.puntuación"}}}, {"$match": {"_id": {"$ne": str(solucion["_id"])}}}, {"$limit": 6}]
        solucion_inv = parametros.agregacion(query_paises_inv)
        sol_inv = []
        for p in solucion_inv:
            sol_inv.append(p["_id"])
        self._opciones_invalidas = sol_inv

    @property
    def pregunta(self) -> str:
        return f"¿Qué país quedó mejor posicionado de media entre los años {self._anyo_inicial} y {self._anyo_final}?"

    @property
    def opciones_invalidas(self) -> List[str]:
        return self._opciones_invalidas

    @property
    def respuesta(self) -> str:
        return self._respuesta

    @property
    def puntuacion(self) -> int:
        return 4
