# Evidencia 02: Episodio 1, pedido, plan e informe del agente

- Fecha: 2026-11-02
- Herramienta: OpenCode 1.19.5 (terminal de VS Code)
- Modelo mostrado en la interfaz: MiMo-V2.6-Flash Free
- Verificación humana de este episodio: [03-episodio1-verificacion.md](03-episodio1-verificacion.md)

## 1. Pedido que le hice al agente
(Texto preparado con ayuda del asistente de chat; es el que le envié.)

```
Leé SPEC.md, AGENTS.md e inventario.json.

Tarea (lógica de dominio, sin base de datos ni interfaz):
Antes de modificar nada, decime en pocas líneas qué archivos vas a crear y
cómo vas a modelar las reservas.

Después creá:
- reservas/__init__.py
- reservas/dominio.py: cargar el inventario desde inventario.json; parsear
  fechas ISO "AAAA-MM-DDTHH:MM" rechazando fechas inexistentes; validar unidad
  conocida, solicitante no vacío ni solo espacios, e inicio estrictamente
  anterior al fin; una única función de superposición de intervalos
  semiabiertos que usen tanto la creación como la consulta de disponibilidad;
  funciones para consultar disponibilidad y decidir si se acepta una reserva
  nueva, recibiendo la lista de reservas existentes como parámetro.
- tests/test_dominio.py con unittest: creación válida, rechazo de
  superposición, límites consecutivos, unidades distintas simultáneas,
  entradas inválidas, y que una reserva cancelada no bloquee (CA-01 a CA-06).

No uses el reloj del sistema. No toques SPEC.md ni inventario.json.
No hagas commits. Al terminar, ejecutá
python -m unittest discover -s tests -v y mostrame la salida real.
```

## 2. Plan del agente (antes de modificar archivos)
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

## 3. Mi respuesta al plan (con una precisión)
(Texto preparado con ayuda del asistente de chat.)

Sí, procedé con ese plan. Una precisión: consultar_disponibilidad no recibe
solicitante, así que validá solo unidad, fechas e inicio anterior al fin,
reutilizando las mismas funciones de validación que usa crear_reserva (no
dupliques esa lógica). Asegurate de que
python -m unittest discover -s tests -v funcione ejecutado desde la raíz
del repositorio. No hagas commits.

Observación: la precisión fue una aclaración mía a un punto ambiguo del plan,
antes de que el agente actuara. No fue una corrección de una falla.
El plan no incluía cancelar reservas: quedó para el Episodio 2.

## 4. Informe final del agente (lo que dijo; no es mi verificación)
Listo. Archivos creados: reservas/__init__.py, reservas/dominio.py, tests/test_dominio.py (sin tocar SPEC.md ni inventario.json, sin commits).
Puntos clave del plan cumplidos:
- consultar_disponibilidad(inventario, existentes, unidad, inicio, fin) no recibe solicitante; reutiliza validar_unidad + validar_rango (las mismas que crear_reserva) y activas_superpuestas/hay_superposicion.
- Sin reloj: los IDs y las reservas existentes los pasa el llamador.
Salida real de python -m unittest discover -s tests -v desde la raíz:
test_creacion_valida (test_dominio.CreacionValida.test_creacion_valida) ... ok
test_CA_01_superposicion_rechazada (test_dominio.CriteriosDeAceptacion.test_CA_01_superposicion_rechazada) ... ok
test_CA_02_limite_consecutivo_aceptado (test_dominio.CriteriosDeAceptacion.test_CA_02_limite_consecutivo_aceptado) ... ok
test_CA_03_unidades_distintas_simultaneas (test_dominio.CriteriosDeAceptacion.test_CA_03_unidades_distintas_simultaneas) ... ok
test_CA_04_entradas_invalidas (test_dominio.CriteriosDeAceptacion.test_CA_04_entradas_invalidas) ... ok
test_CA_05_cancelada_no_bloquea (test_dominio.CriteriosDeAceptacion.test_CA_05_cancelada_no_bloquea) ... ok
test_CA_06_disponibilidad_coincide_con_creacion (test_dominio.CriteriosDeAceptacion.test_CA_06_disponibilidad_coincide_con_creacion) ... ok
test_consulta_informa_reservas_que_bloquean (test_dominio.CriteriosDeAceptacion.test_consulta_informa_reservas_que_bloquean) ... ok
test_consulta_no_recibe_solicitante (test_dominio.CriteriosDeAceptacion.test_consulta_no_recibe_solicitante) ... ok
test_RF_01_carga_inventario (test_dominio.Inventario.test_RF_01_carga_inventario) ... ok
test_intervalos_consecutivos_no_superpuestos (test_dominio.SuperposicionSemiabierta.test_intervalos_consecutivos_no_superpuestos) ... ok
test_intervalos_que_se_solapan (test_dominio.SuperposicionSemiabierta.test_intervalos_que_se_solapan) ... ok
Ran 12 tests in 0.044s
OK