"""Pruebas de dominio: criterios de aceptación CA-01 a CA-06."""

import inspect
import os
import unittest
from datetime import datetime

from reservas import dominio

RUTA_INVENTARIO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "inventario.json",
)


class CasoBase(unittest.TestCase):
    def setUp(self):
        self.inventario = dominio.cargar_inventario(RUTA_INVENTARIO)

    def crear(
        self,
        unidad="MIC-01",
        solicitante="Ana Prueba",
        inicio="2026-11-05T10:00",
        fin="2026-11-05T11:00",
        identificador="R-0001",
        existentes=None,
    ):
        if existentes is None:
            existentes = []
        return dominio.crear_reserva(
            self.inventario,
            existentes,
            unidad,
            solicitante,
            inicio,
            fin,
            identificador,
        )

    def resultado_consulta(self, existentes, unidad, inicio, fin):
        try:
            bloqueos = dominio.consultar_disponibilidad(
                self.inventario, existentes, unidad, inicio, fin
            )
        except dominio.EntradaInvalida as exc:
            return False, exc
        return not bloqueos, None

    def resultado_creacion(self, existentes, unidad, inicio, fin, identificador):
        try:
            self.crear(
                unidad=unidad,
                inicio=inicio,
                fin=fin,
                identificador=identificador,
                existentes=existentes,
            )
        except (dominio.EntradaInvalida, dominio.Superposicion) as exc:
            return False, exc
        return True, None

    def verificar_paridad(
        self, existentes, unidad, inicio, fin, identificador
    ):
        libre_consulta, error_consulta = self.resultado_consulta(
            existentes, unidad, inicio, fin
        )
        aceptada_creacion, error_creacion = self.resultado_creacion(
            existentes, unidad, inicio, fin, identificador
        )
        self.assertEqual(libre_consulta, aceptada_creacion)
        if error_consulta is not None and error_creacion is not None:
            self.assertIs(type(error_consulta), type(error_creacion))


class Inventario(CasoBase):
    def test_RF_01_carga_inventario(self):
        self.assertEqual(
            set(self.inventario),
            {"MIC-01", "MIC-02", "OSC-01", "MUL-01", "FUE-01"},
        )
        self.assertEqual(self.inventario["MIC-01"], "Microscopio digital")


class CreacionValida(CasoBase):
    def test_creacion_valida(self):
        reserva = self.crear(solicitante="  Ana Prueba  ")
        self.assertEqual(reserva.id, "R-0001")
        self.assertEqual(reserva.unidad, "MIC-01")
        self.assertEqual(reserva.solicitante, "Ana Prueba")
        self.assertEqual(reserva.estado, dominio.ESTADO_ACTIVA)
        self.assertEqual(reserva.inicio, datetime(2026, 11, 5, 10, 0))
        self.assertEqual(reserva.fin, datetime(2026, 11, 5, 11, 0))


class CriteriosDeAceptacion(CasoBase):
    def test_CA_01_superposicion_rechazada(self):
        existentes = [self.crear()]
        with self.assertRaises(dominio.Superposicion):
            self.crear(
                inicio="2026-11-05T10:30",
                fin="2026-11-05T11:30",
                identificador="R-0002",
                existentes=existentes,
            )

    def test_CA_02_limite_consecutivo_aceptado(self):
        existentes = [self.crear()]
        reserva = self.crear(
            inicio="2026-11-05T11:00",
            fin="2026-11-05T12:00",
            identificador="R-0002",
            existentes=existentes,
        )
        self.assertEqual(reserva.estado, dominio.ESTADO_ACTIVA)

    def test_CA_03_unidades_distintas_simultaneas(self):
        existentes = [self.crear()]
        reserva = self.crear(
            unidad="MIC-02",
            identificador="R-0002",
            existentes=existentes,
        )
        self.assertEqual(reserva.unidad, "MIC-02")
        self.assertEqual(reserva.estado, dominio.ESTADO_ACTIVA)

    def test_CA_04_entradas_invalidas(self):
        casos = {
            "unidad desconocida": {"unidad": "MIC-99"},
            "solicitante vacío": {"solicitante": ""},
            "solicitante solo espacios": {"solicitante": "   "},
            "fecha inexistente": {"inicio": "2026-02-30T10:00"},
            "fin inexistente": {"fin": "2026-13-01T10:00"},
            "formato inválido": {"inicio": "2026-11-05 10:00"},
            "inicio igual al fin": {
                "inicio": "2026-11-05T10:00",
                "fin": "2026-11-05T10:00",
            },
            "inicio posterior al fin": {
                "inicio": "2026-11-05T11:00",
                "fin": "2026-11-05T10:00",
            },
        }
        for nombre, datos in casos.items():
            with self.subTest(nombre):
                with self.assertRaises(dominio.EntradaInvalida):
                    self.crear(**datos)

    def test_CA_05_cancelada_no_bloquea(self):
        original = self.crear()
        dominio.cancelar(original)
        self.assertEqual(original.estado, dominio.ESTADO_CANCELADA)
        self.assertEqual(original.id, "R-0001")
        self.assertEqual(original.unidad, "MIC-01")
        self.assertEqual(original.solicitante, "Ana Prueba")
        self.assertEqual(original.inicio, datetime(2026, 11, 5, 10, 0))
        self.assertEqual(original.fin, datetime(2026, 11, 5, 11, 0))
        reserva = self.crear(
            inicio="2026-11-05T10:30",
            fin="2026-11-05T11:30",
            identificador="R-0002",
            existentes=[original],
        )
        self.assertEqual(reserva.estado, dominio.ESTADO_ACTIVA)

    def test_CA_06_disponibilidad_coincide_con_creacion(self):
        activa = self.crear()
        existentes = [activa]
        casos = [
            ("MIC-01", "2026-11-05T10:30", "2026-11-05T11:30"),
            ("MIC-01", "2026-11-05T11:00", "2026-11-05T12:00"),
            ("MIC-02", "2026-11-05T10:00", "2026-11-05T11:00"),
            ("MIC-99", "2026-11-05T12:00", "2026-11-05T13:00"),
            ("MIC-01", "2026-02-30T10:00", "2026-11-05T13:00"),
            ("MIC-01", "2026-11-05 12:00", "2026-11-05T13:00"),
            ("MIC-01", "2026-11-05T12:00", "2026-11-05T12:00"),
            ("MIC-01", "2026-11-05T13:00", "2026-11-05T12:00"),
        ]
        for indice, (unidad, inicio, fin) in enumerate(casos, start=2):
            with self.subTest(unidad=unidad, inicio=inicio, fin=fin):
                self.verificar_paridad(
                    existentes,
                    unidad,
                    inicio,
                    fin,
                    "R-{:04d}".format(indice),
                )
        dominio.cancelar(activa)
        self.verificar_paridad(
            existentes,
            "MIC-01",
            "2026-11-05T10:30",
            "2026-11-05T11:30",
            "R-0010",
        )

    def test_consulta_informa_reservas_que_bloquean(self):
        activa = self.crear()
        bloqueos = dominio.consultar_disponibilidad(
            self.inventario,
            [activa],
            "MIC-01",
            "2026-11-05T10:30",
            "2026-11-05T11:30",
        )
        self.assertEqual([reserva.id for reserva in bloqueos], ["R-0001"])

    def test_consulta_no_recibe_solicitante(self):
        parametros = inspect.signature(
            dominio.consultar_disponibilidad
        ).parameters
        self.assertNotIn("solicitante", parametros)


class SuperposicionSemiabierta(CasoBase):
    def test_intervalos_consecutivos_no_superpuestos(self):
        fin = datetime(2026, 11, 5, 11, 0)
        otro_inicio = datetime(2026, 11, 5, 11, 0)
        self.assertFalse(
            dominio.hay_superposicion(
                datetime(2026, 11, 5, 10, 0), fin, otro_inicio,
                datetime(2026, 11, 5, 12, 0),
            )
        )

    def test_intervalos_que_se_solapan(self):
        self.assertTrue(
            dominio.hay_superposicion(
                datetime(2026, 11, 5, 10, 0),
                datetime(2026, 11, 5, 11, 0),
                datetime(2026, 11, 5, 10, 30),
                datetime(2026, 11, 5, 11, 30),
            )
        )


if __name__ == "__main__":
    unittest.main()
