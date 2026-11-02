# Instrucciones para el agente

Proyecto: sistema de reservas de laboratorio. Leé `SPEC.md` antes de actuar.
Es la fuente de verdad; si algo no está claro, preguntá, no inventes requisitos.

## Reglas técnicas
- Python, solo biblioteca estándar (`sqlite3`, `tkinter`, `unittest`).
  No instales dependencias.
- Estructura: `reservas/dominio.py` (reglas y validaciones),
  `reservas/repositorio.py` (SQLite) y `reservas/gui.py` (Tkinter).
- La lógica de negocio NO debe depender de la interfaz gráfica ni leer el
  reloj del sistema. Las funciones reciben la ruta de la base de datos como
  parámetro para poder probarlas con una base temporal.
- Los intervalos son semiabiertos [inicio, fin): una reserva que termina a
  las 11:00 NO se superpone con otra que empieza a las 11:00.
- La consulta de disponibilidad y la creación deben usar la misma función
  de validación y de superposición. No dupliques esa lógica.

## Procedimiento de persistencia
- Cada alta y cada cancelación se confirman (commit de SQLite) antes de
  devolver el resultado.
- Al iniciar, la aplicación abre la base existente sin borrarla. Crear las
  tablas solo si no existen (`CREATE TABLE IF NOT EXISTS`).
- Borrar datos solo con el comando explícito de reinicio, nunca de forma
  implícita.

## Proceso de trabajo
- Trabajá en pasos chicos y explicá qué archivos vas a modificar antes de
  hacerlo.
- Antes de decir que terminaste, ejecutá `python -m unittest discover -s tests`
  y mostrá la salida real. No afirmes que las pruebas pasan si no las ejecutaste.
- No hagas commits de Git: los hace la persona, después de revisar.
- Usá solo datos ficticios (por ejemplo "Ana Prueba"). No escribas claves,
  tokens ni datos personales en ningún archivo.
- No modifiques `SPEC.md` ni `inventario.json` sin que se te pida.