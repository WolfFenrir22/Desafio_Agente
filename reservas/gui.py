"""Interfaz gráfica mínima del sistema de reservas (RF-10).

Solo llama a funciones de reservas.repositorio; las reglas de negocio
viven en reservas.dominio y no se repiten acá.

Uso: python -m reservas.gui
"""

import tkinter as tk
from tkinter import messagebox, ttk

from . import repositorio

_RUTA_BASE = "reservas.db"
_RUTA_INVENTARIO = "inventario.json"
_PISTA_FORMATO = "Formato de fecha: AAAA-MM-DDTHH:MM (ej. 2026-11-05T10:00)"


class Aplicacion:
    def __init__(self, raiz, inventario):
        self.raiz = raiz
        self.ruta = _RUTA_BASE
        self.inventario = inventario

        raiz.title("Reservas de laboratorio")
        raiz.minsize(660, 380)

        formulario = tk.Frame(raiz)
        formulario.pack(fill="x", padx=8, pady=(8, 4))
        formulario.columnconfigure(1, weight=1)

        tk.Label(formulario, text="Unidad").grid(
            row=0, column=0, sticky="w", pady=2
        )
        self.unidad = ttk.Combobox(
            formulario, values=list(inventario), state="readonly"
        )
        self.unidad.grid(row=0, column=1, sticky="ew", padx=4, pady=2)

        tk.Label(formulario, text="Inicio").grid(
            row=1, column=0, sticky="w", pady=2
        )
        self.inicio = tk.Entry(formulario)
        self.inicio.grid(row=1, column=1, sticky="ew", padx=4, pady=2)

        tk.Label(formulario, text="Fin").grid(
            row=2, column=0, sticky="w", pady=2
        )
        self.fin = tk.Entry(formulario)
        self.fin.grid(row=2, column=1, sticky="ew", padx=4, pady=2)

        tk.Label(formulario, text="Solicitante").grid(
            row=3, column=0, sticky="w", pady=2
        )
        self.solicitante = tk.Entry(formulario)
        self.solicitante.grid(row=3, column=1, sticky="ew", padx=4, pady=2)

        tk.Label(formulario, text=_PISTA_FORMATO, fg="gray").grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(4, 0)
        )

        botones = tk.Frame(raiz)
        botones.pack(fill="x", padx=8, pady=4)
        tk.Button(
            botones, text="Consultar disponibilidad", command=self.consultar
        ).pack(side="left", padx=(0, 4))
        tk.Button(botones, text="Reservar", command=self.reservar).pack(
            side="left", padx=4
        )
        tk.Button(botones, text="Cancelar", command=self.cancelar).pack(
            side="left", padx=4
        )

        marco_tabla = tk.Frame(raiz)
        marco_tabla.pack(fill="both", expand=True, padx=8, pady=4)
        columnas = ("id", "unidad", "solicitante", "inicio", "fin", "estado")
        self.tabla = ttk.Treeview(
            marco_tabla, columns=columnas, show="headings",
            selectmode="browse",
        )
        anchos = {
            "id": 70, "unidad": 80, "solicitante": 160,
            "inicio": 130, "fin": 130, "estado": 90,
        }
        for columna in columnas:
            self.tabla.heading(columna, text=columna.capitalize())
            self.tabla.column(columna, width=anchos[columna], anchor="w")
        desplazamiento = ttk.Scrollbar(
            marco_tabla, orient="vertical", command=self.tabla.yview
        )
        self.tabla.configure(yscrollcommand=desplazamiento.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        desplazamiento.pack(side="right", fill="y")

        self.mensaje = tk.Label(
            raiz, text="", anchor="w", relief="sunken", padx=4
        )
        self.mensaje.pack(fill="x", padx=8, pady=(4, 8))

        self._actualizar_tabla()

    def _mostrar(self, texto):
        self.mensaje.configure(text=texto)

    def _error(self, exc):
        messagebox.showerror("Error", str(exc), parent=self.raiz)

    def _actualizar_tabla(self):
        self.tabla.delete(*self.tabla.get_children())
        for reserva in repositorio.listar_reservas(self.ruta):
            self.tabla.insert(
                "", "end",
                values=(
                    reserva.id,
                    reserva.unidad,
                    reserva.solicitante,
                    reserva.inicio.isoformat(timespec="minutes"),
                    reserva.fin.isoformat(timespec="minutes"),
                    reserva.estado,
                ),
            )

    def consultar(self):
        try:
            bloqueos = repositorio.consultar_disponibilidad(
                self.ruta,
                self.inventario,
                self.unidad.get(),
                self.inicio.get(),
                self.fin.get(),
            )
        except ValueError as exc:
            self._error(exc)
            return
        if bloqueos:
            ids = ", ".join(reserva.id for reserva in bloqueos)
            self._mostrar("No disponible: bloqueada por {}.".format(ids))
        else:
            self._mostrar("Disponible: el intervalo está libre.")

    def reservar(self):
        try:
            reserva = repositorio.crear_reserva(
                self.ruta,
                self.inventario,
                self.unidad.get(),
                self.solicitante.get(),
                self.inicio.get(),
                self.fin.get(),
            )
        except ValueError as exc:
            self._error(exc)
            return
        self._actualizar_tabla()
        self._mostrar("Reserva {} creada (activa).".format(reserva.id))

    def cancelar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showerror(
                "Error",
                "Seleccione una reserva en la tabla para cancelarla.",
                parent=self.raiz,
            )
            return
        identificador = self.tabla.item(seleccion[0], "values")[0]
        try:
            cancelada = repositorio.cancelar_reserva(self.ruta, identificador)
        except ValueError as exc:
            self._error(exc)
            return
        self._actualizar_tabla()
        self._mostrar("Reserva {} cancelada.".format(cancelada.id))


def main():
    raiz = tk.Tk()
    raiz.withdraw()
    try:
        inventario = repositorio.cargar_inventario(_RUTA_INVENTARIO)
    except (OSError, ValueError) as exc:
        messagebox.showerror(
            "Error",
            "No se pudo cargar el inventario: {}".format(exc),
            parent=raiz,
        )
        raiz.destroy()
        return 1
    raiz.deiconify()
    Aplicacion(raiz, inventario)
    raiz.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
