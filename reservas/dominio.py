"""Reglas de dominio del sistema de reservas de laboratorio.

No depende de la interfaz gráfica ni del reloj del sistema.
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime

ESTADO_ACTIVA = "activa"
ESTADO_CANCELADA = "cancelada"

_FORMATO_FECHA = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}")
_PARSEO_FECHA = "%Y-%m-%dT%H:%M"


class EntradaInvalida(ValueError):
    """RF-03: unidad desconocida, solicitante vacío o fechas inválidas."""


class Superposicion(ValueError):
    """RF-04: superposición con una reserva activa de la misma unidad."""


@dataclass
class Reserva:
    id: str
    unidad: str
    solicitante: str
    inicio: datetime
    fin: datetime
    estado: str = ESTADO_ACTIVA


def cargar_inventario(ruta):
    """RF-01: carga el inventario desde inventario.json."""
    with open(ruta, encoding="utf-8") as archivo:
        datos = json.load(archivo)
    return {item["id"]: item["equipo"] for item in datos}


def parsear_fecha(texto):
    if not isinstance(texto, str) or _FORMATO_FECHA.fullmatch(texto) is None:
        raise EntradaInvalida("fecha con formato inválido: {!r}".format(texto))
    try:
        return datetime.strptime(texto, _PARSEO_FECHA)
    except ValueError as exc:
        raise EntradaInvalida("fecha inexistente: {!r}".format(texto)) from exc


def validar_unidad(inventario, unidad):
    if unidad not in inventario:
        raise EntradaInvalida("unidad desconocida: {!r}".format(unidad))


def validar_solicitante(solicitante):
    if not isinstance(solicitante, str) or not solicitante.strip():
        raise EntradaInvalida("solicitante vacío o solo espacios")
    return solicitante.strip()


def validar_rango(inicio, fin):
    instante_inicio = parsear_fecha(inicio)
    instante_fin = parsear_fecha(fin)
    if not instante_inicio < instante_fin:
        raise EntradaInvalida(
            "el inicio debe ser estrictamente anterior al fin"
        )
    return instante_inicio, instante_fin


def hay_superposicion(inicio1, fin1, inicio2, fin2):
    """R2: intervalos semiabiertos [inicio, fin)."""
    return inicio1 < fin2 and inicio2 < fin1


def activas_superpuestas(existentes, unidad, inicio, fin):
    return [
        reserva
        for reserva in existentes
        if reserva.estado == ESTADO_ACTIVA
        and reserva.unidad == unidad
        and hay_superposicion(inicio, fin, reserva.inicio, reserva.fin)
    ]


def consultar_disponibilidad(inventario, existentes, unidad, inicio, fin):
    """RF-06: devuelve las reservas activas que impiden ese intervalo."""
    validar_unidad(inventario, unidad)
    instante_inicio, instante_fin = validar_rango(inicio, fin)
    return activas_superpuestas(
        existentes, unidad, instante_inicio, instante_fin
    )


def crear_reserva(
    inventario,
    existentes,
    unidad,
    solicitante,
    inicio,
    fin,
    nuevo_id,
):
    """RF-02: valida y devuelve una reserva activa con el id indicado."""
    validar_unidad(inventario, unidad)
    instante_inicio, instante_fin = validar_rango(inicio, fin)
    nombre = validar_solicitante(solicitante)
    bloqueos = activas_superpuestas(
        existentes, unidad, instante_inicio, instante_fin
    )
    if bloqueos:
        ids = ", ".join(reserva.id for reserva in bloqueos)
        raise Superposicion("superposición con reserva(s): {}".format(ids))
    return Reserva(
        id=nuevo_id,
        unidad=unidad,
        solicitante=nombre,
        inicio=instante_inicio,
        fin=instante_fin,
        estado=ESTADO_ACTIVA,
    )


def cancelar(reserva):
    """R6: solo cambia el estado; conserva id y datos."""
    if reserva.estado == ESTADO_CANCELADA:
        raise EntradaInvalida(
            "la reserva {} ya está cancelada".format(reserva.id)
        )
    reserva.estado = ESTADO_CANCELADA
    return reserva
