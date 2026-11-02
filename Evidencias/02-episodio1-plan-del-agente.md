Leí SPEC.md, AGENTS.md e inventario.json (no hay reservas/ ni tests/ todavía). Plan antes de tocar nada:
Archivos a crear (3 + 1 auxiliar)
- reservas/__init__.py — paquete vacío.
- reservas/dominio.py — toda la lógica, sin reloj ni BD.
- tests/test_dominio.py — unittest, CA-01 a CA-06.
- tests/ sin __init__.py (alcanza con discover -s tests).
Modelo de reservas
- Reserva (dataclass): id ("R-0001"…), unidad, solicitante (recortado), inicio/fin como datetime, estado en {"activa", "cancelada"}. La cancelación solo cambia estado (R6); los IDs los pasa quien llama (nunca se reutilizan, nada de reloj).
- Las funciones reciben existentes: list[Reserva] como parámetro.
Funciones en dominio.py
- cargar_inventario(ruta) → dict id→equipo desde inventario.json.
- parsear_fecha(txt) → regex estricta AAAA-MM-DDTHH:MM + strptime, que rechaza 2026-02-30T10:00.
- validar_reserva(...) → unidad conocida, solicitante no vacío/espacios, inicio < fin; lanza EntradaInvalida(ValueError).
- hay_superposicion(i1,f1,i2,f2) → única función, semiabierta: a < d and c < b.
- activas_superpuestas(existentes, unidad, ini, fin) → lista de bloqueos (R5, la usan creación y consulta).
- crear_reserva(...) → valida + superposición (lanza Superposicion), devuelve Reserva activa.
- consultar_disponibilidad(...) → mismas validaciones misma regla; devuelve las reservas activas que impiden (vacío = libre).
Tests (CA-01…CA-06): creación válida; 10:30–11:30 rechazada; 11:00–12:00 aceptada; MIC-02 simultáneo aceptado; entradas inválidas (MIC-99, "   ", fecha inexistente, igual, invertida); cancelada no bloquea; y que consulta = creación.
Al terminar ejecuto python -m unittest discover -s tests -v y muestro la salida real. ¿Procedo?

Respuesta:
Sí, procedé con ese plan. Una precisión: consultar_disponibilidad no recibe
solicitante, así que validá solo unidad, fechas e inicio anterior al fin,
reutilizando las mismas funciones de validación que usa crear_reserva (no
dupliques esa lógica). Asegurate de que
python -m unittest discover -s tests -v funcione ejecutado desde la raíz
del repositorio. No hagas commits.