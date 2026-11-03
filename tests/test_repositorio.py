"""Pruebas de persistencia: CA-05 y CA-07, identificadores y reinicio."""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from unittest import mock

from reservas import dominio
from reservas import repositorio

RUTA_INVENTARIO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "inventario.json",
)


class CasoBase(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.ruta = os.path.join(temporal.name, "reservas_prueba.db")
        self.inventario = dominio.cargar_inventario(RUTA_INVENTARIO)

    def crear(
        self,
        unidad="MIC-01",
        solicitante="Ana Prueba",
        inicio="2026-11-05T10:00",
        fin="2026-11-05T11:00",
    ):
        return repositorio.crear_reserva(
            self.ruta,
            self.inventario,
            unidad,
            solicitante,
            inicio,
            fin,
        )


class Persistencia(CasoBase):
    def test_CA_07_recupera_activa_y_cancelada_tras_reabrir(self):
        activa = self.crear(
            inicio="2026-11-05T10:00", fin="2026-11-05T11:00"
        )
        otra = self.crear(
            unidad="OSC-01",
            inicio="2026-11-05T09:00",
            fin="2026-11-05T10:00",
        )
        repositorio.cancelar_reserva(self.ruta, otra.id)

        recuperadas = repositorio.listar_reservas(self.ruta)
        por_id = {reserva.id: reserva for reserva in recuperadas}

        self.assertEqual(sorted(por_id), ["R-0001", "R-0002"])
        self.assertEqual(por_id[activa.id].estado, dominio.ESTADO_ACTIVA)
        self.assertEqual(por_id[otra.id].estado, dominio.ESTADO_CANCELADA)
        self.assertEqual(por_id[otra.id].unidad, "OSC-01")
        self.assertEqual(por_id[otra.id].solicitante, "Ana Prueba")
        self.assertEqual(por_id[otra.id].inicio, datetime(2026, 11, 5, 9, 0))
        self.assertEqual(por_id[otra.id].fin, datetime(2026, 11, 5, 10, 0))

    def test_CA_05_cancelar_libera_horario_y_conserva_registro(self):
        reserva = self.crear()
        cancelada = repositorio.cancelar_reserva(self.ruta, reserva.id)

        self.assertEqual(cancelada.estado, dominio.ESTADO_CANCELADA)
        registradas = repositorio.listar_reservas(self.ruta)
        self.assertEqual(len(registradas), 1)
        self.assertEqual(registradas[0].id, "R-0001")
        self.assertEqual(registradas[0].estado, dominio.ESTADO_CANCELADA)

        bloqueos = repositorio.consultar_disponibilidad(
            self.ruta,
            self.inventario,
            "MIC-01",
            "2026-11-05T10:30",
            "2026-11-05T11:30",
        )
        self.assertEqual(bloqueos, [])

        nueva = self.crear(
            inicio="2026-11-05T10:30", fin="2026-11-05T11:30"
        )
        self.assertEqual(nueva.id, "R-0002")
        self.assertEqual(nueva.estado, dominio.ESTADO_ACTIVA)

    def test_cancelar_reserva_inexistente(self):
        self.crear()
        with self.assertRaises(dominio.ReservaNoEncontrada):
            repositorio.cancelar_reserva(self.ruta, "R-9999")
        estados = [
            reserva.estado
            for reserva in repositorio.listar_reservas(self.ruta)
        ]
        self.assertEqual(estados, [dominio.ESTADO_ACTIVA])

    def test_cancelar_reserva_ya_cancelada(self):
        reserva = self.crear()
        repositorio.cancelar_reserva(self.ruta, reserva.id)
        with self.assertRaises(dominio.ReservaYaCancelada):
            repositorio.cancelar_reserva(self.ruta, reserva.id)
        estados = [
            r.estado for r in repositorio.listar_reservas(self.ruta)
        ]
        self.assertEqual(estados, [dominio.ESTADO_CANCELADA])

    def test_identificadores_no_se_reutilizan(self):
        primera = self.crear()
        segunda = self.crear(unidad="OSC-01")
        repositorio.cancelar_reserva(self.ruta, primera.id)
        tercera = self.crear(
            inicio="2026-11-05T10:30", fin="2026-11-05T11:30"
        )
        cuarta = self.crear(
            unidad="OSC-01",
            inicio="2026-11-05T13:00",
            fin="2026-11-05T14:00",
        )
        self.assertEqual(
            [primera.id, segunda.id, tercera.id, cuarta.id],
            ["R-0001", "R-0002", "R-0003", "R-0004"],
        )

    def test_creacion_fallida_no_guarda_ni_consume_id(self):
        self.crear()
        with self.assertRaises(dominio.Superposicion):
            self.crear(
                inicio="2026-11-05T10:30", fin="2026-11-05T11:30"
            )
        with self.assertRaises(dominio.EntradaInvalida):
            repositorio.crear_reserva(
                self.ruta,
                self.inventario,
                "MIC-99",
                "Ana Prueba",
                "2026-11-05T12:00",
                "2026-11-05T13:00",
            )
        ids = [
            reserva.id
            for reserva in repositorio.listar_reservas(self.ruta)
        ]
        self.assertEqual(ids, ["R-0001"])
        nueva = self.crear(unidad="OSC-01")
        self.assertEqual(nueva.id, "R-0002")

    def test_consulta_informa_bloqueo_persistido(self):
        self.crear()
        bloqueos = repositorio.consultar_disponibilidad(
            self.ruta,
            self.inventario,
            "MIC-01",
            "2026-11-05T10:30",
            "2026-11-05T11:30",
        )
        self.assertEqual([reserva.id for reserva in bloqueos], ["R-0001"])

    def test_reinicio_requiere_confirmacion(self):
        self.crear()
        with self.assertRaises(repositorio.ReinicioRechazado):
            repositorio.reiniciar_datos(
                self.ruta, RUTA_INVENTARIO, confirmado=False
            )
        self.assertEqual(len(repositorio.listar_reservas(self.ruta)), 1)

        inventario = repositorio.reiniciar_datos(
            self.ruta, RUTA_INVENTARIO, confirmado=True
        )
        self.assertEqual(repositorio.listar_reservas(self.ruta), [])
        self.assertEqual(set(inventario), set(self.inventario))

    def test_comando_reinicio_pide_confirmacion(self):
        self.crear()
        with mock.patch("builtins.input", return_value="n"):
            with redirect_stdout(io.StringIO()):
                codigo = repositorio.main(
                    [self.ruta], ruta_inventario=RUTA_INVENTARIO
                )
        self.assertEqual(codigo, 1)
        self.assertEqual(len(repositorio.listar_reservas(self.ruta)), 1)

        with mock.patch("builtins.input", return_value="s"):
            with redirect_stdout(io.StringIO()):
                codigo = repositorio.main(
                    [self.ruta], ruta_inventario=RUTA_INVENTARIO
                )
        self.assertEqual(codigo, 0)
        self.assertEqual(repositorio.listar_reservas(self.ruta), [])


if __name__ == "__main__":
    unittest.main()
