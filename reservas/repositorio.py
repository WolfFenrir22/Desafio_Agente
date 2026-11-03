"""Persistencia de reservas en SQLite (RF-07, RF-08, RF-09).

La ruta de la base de datos se recibe por parámetro en cada función.
"""

import sqlite3
import sys

from . import dominio

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS reservas (
    id TEXT PRIMARY KEY,
    unidad TEXT NOT NULL,
    solicitante TEXT NOT NULL,
    inicio TEXT NOT NULL,
    fin TEXT NOT NULL,
    estado TEXT NOT NULL
)
"""

_RUTA_DEFECTO = "reservas.db"
_INVENTARIO_DEFECTO = "inventario.json"
_CONFIRMACIONES = ("s", "si", "sí")


class ReinicioRechazado(ValueError):
    """El comando de reinicio de datos no fue confirmado."""


def _abrir(ruta):
    conexion = sqlite3.connect(ruta)
    conexion.row_factory = sqlite3.Row
    conexion.execute(_ESQUEMA)
    conexion.commit()
    return conexion


def _fila_a_reserva(fila):
    return dominio.Reserva(
        id=fila["id"],
        unidad=fila["unidad"],
        solicitante=fila["solicitante"],
        inicio=dominio.parsear_fecha(fila["inicio"]),
        fin=dominio.parsear_fecha(fila["fin"]),
        estado=fila["estado"],
    )


def _leer_reservas(conexion):
    filas = conexion.execute(
        "SELECT id, unidad, solicitante, inicio, fin, estado"
        " FROM reservas ORDER BY id"
    ).fetchall()
    return [_fila_a_reserva(fila) for fila in filas]


def _proximo_id(conexion):
    fila = conexion.execute(
        "SELECT MAX(CAST(SUBSTR(id, 3) AS INTEGER)) AS maximo"
        " FROM reservas"
    ).fetchone()
    maximo = fila["maximo"] or 0
    return "R-{:04d}".format(maximo + 1)


def cargar_inventario(ruta_inventario=_INVENTARIO_DEFECTO):
    """RF-01: carga el inventario (para que la interfaz use el repositorio)."""
    return dominio.cargar_inventario(ruta_inventario)


def listar_reservas(ruta):
    """RF-08: devuelve todas las reservas, activas y canceladas."""
    conexion = _abrir(ruta)
    try:
        return _leer_reservas(conexion)
    finally:
        conexion.close()


def consultar_disponibilidad(ruta, inventario, unidad, inicio, fin):
    """RF-06: usa las mismas validaciones y superposición que la creación."""
    return dominio.consultar_disponibilidad(
        inventario,
        listar_reservas(ruta),
        unidad,
        inicio,
        fin,
    )


def crear_reserva(ruta, inventario, unidad, solicitante, inicio, fin):
    """RF-02: superposición e inserción resueltas en una transacción."""
    conexion = _abrir(ruta)
    try:
        conexion.execute("BEGIN IMMEDIATE")
        try:
            existentes = _leer_reservas(conexion)
            reserva = dominio.crear_reserva(
                inventario,
                existentes,
                unidad,
                solicitante,
                inicio,
                fin,
                _proximo_id(conexion),
            )
            conexion.execute(
                "INSERT INTO reservas (id, unidad, solicitante,"
                " inicio, fin, estado) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    reserva.id,
                    reserva.unidad,
                    reserva.solicitante,
                    reserva.inicio.isoformat(timespec="minutes"),
                    reserva.fin.isoformat(timespec="minutes"),
                    reserva.estado,
                ),
            )
            conexion.commit()
            return reserva
        except BaseException:
            conexion.rollback()
            raise
    finally:
        conexion.close()


def cancelar_reserva(ruta, identificador):
    """RF-07: cancela por id y confirma el cambio antes de devolver."""
    conexion = _abrir(ruta)
    try:
        conexion.execute("BEGIN IMMEDIATE")
        try:
            cancelada = dominio.cancelar_reserva(
                _leer_reservas(conexion),
                identificador,
            )
            conexion.execute(
                "UPDATE reservas SET estado = ? WHERE id = ?",
                (cancelada.estado, cancelada.id),
            )
            conexion.commit()
            return cancelada
        except BaseException:
            conexion.rollback()
            raise
    finally:
        conexion.close()


def reiniciar_datos(ruta, ruta_inventario, confirmado):
    """Borra las reservas solo con confirmación y recarga el inventario."""
    if not confirmado:
        raise ReinicioRechazado("reinicio de datos sin confirmar")
    inventario = dominio.cargar_inventario(ruta_inventario)
    conexion = _abrir(ruta)
    try:
        with conexion:
            conexion.execute("DELETE FROM reservas")
    finally:
        conexion.close()
    return inventario


def main(argv=None, ruta_inventario=_INVENTARIO_DEFECTO):
    if argv is None:
        argv = sys.argv[1:]
    ruta = argv[0] if argv else _RUTA_DEFECTO
    respuesta = input(
        "¿Borrar todas las reservas de {}? [s/N]: ".format(ruta)
    ).strip().lower()
    try:
        inventario = reiniciar_datos(
            ruta, ruta_inventario, respuesta in _CONFIRMACIONES
        )
    except ReinicioRechazado:
        print("Reinicio cancelado: no se modificó nada.")
        return 1
    print(
        "Reservas borradas. Inventario recargado: {} unidades.".format(
            len(inventario)
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
