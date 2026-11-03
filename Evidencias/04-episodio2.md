# Evidencia 04: Episodio 2 (cancelación y persistencia)

- Fechas: pedido y trabajo del agente el 2026-11-02; mi verificación y el commit el 2026-11-03
- Herramienta: OpenCode 1.19.5, modelo mostrado: MiMo-V2.6-Flash Free
- Lo que informó el agente está en las secciones 2 y 3. Lo que ejecuté yo está en la sección 4.

## 1. Instrucción que le di
(Texto preparado con ayuda del asistente de chat; es el que le envié. Se reformateó solo el salto de línea.)

```
Leé SPEC.md, AGENTS.md y reservas/dominio.py.

Quiero agregar dos cosas, sin interfaz gráfica:
1. Cancelar una reserva (RF-07), en dominio.py: cambia solo su estado a
   "cancelada" y falla si no existe o ya estaba cancelada.
2. Guardar las reservas en SQLite (RF-09), en reservas/repositorio.py:
   que se recuperen al cerrar y volver a abrir, con identificadores R-0001,
   R-0002... que nunca se reutilicen. La ruta de la base se recibe por
   parámetro. Al crear una reserva, la comprobación de superposición y el
   guardado deben hacerse en la misma transacción.
Agregá además un comando para reiniciar los datos (borra las reservas y
recarga el inventario) que pida confirmación.

Antes de tocar nada, decime qué archivos vas a crear o modificar.
Después hacé pruebas con unittest usando bases de datos temporales:
reservas activas y canceladas que se recuperan tras reabrir (CA-07),
cancelar libera el horario y conserva el registro (CA-05), cancelar una
inexistente o ya cancelada, y que los identificadores no se reutilicen.
No toques SPEC.md ni inventario.json. No hagas commits. Al terminar,
mostrame la salida real de python -m unittest discover -s tests -v.
```

## 2. Plan del agente antes de actuar
Modificar reservas/dominio.py: reemplazar cancelar por cancelar_reserva(reservas, identificador) (RF-07: busca por id, falla con ReservaNoEncontrada si no existe y ReservaYaCancelada si ya estaba; solo cambia el estado).
Crear reservas/repositorio.py: tabla con CREATE TABLE IF NOT EXISTS; listar_reservas, consultar_disponibilidad (delega en dominio, R5), crear_reserva con BEGIN IMMEDIATE (leer + calcular id + comprobar superposición + INSERT en una sola transacción, commit antes de devolver), cancelar_reserva (transacción + commit), reiniciar_datos(ruta, ruta_inventario, confirmado) que exige confirmación, y comando CLI python -m reservas.repositorio [ruta] que pide confirmación con input().
Modificar tests/test_dominio.py: CA-05 y CA-06 pasan a usar cancelar_reserva; agrego test de RF-07.
Crear tests/test_repositorio.py: CA-07, CA-05 con base temporal, cancelar inexistente/yá cancelada, ids no reutilizados, creación fallida no consume id, reinicio con/sin confirmación.
No toco SPEC.md ni inventario.json, sin commits.

(ELEGÍ UNA frase y borrá la otra.)
- Después de mostrar su plan, el agente esperó mi confirmación y le respondí que sí.
- Después de mostrar su plan, el agente siguió sin esperar mi confirmación.

## 3. Informe final del agente (lo que dijo; no es mi verificación)
Hecho, 23 tests en verde. Resumen de cambios:
- reservas/dominio.py: cancelar_reserva(reservas, identificador) con ReservaNoEncontrada / ReservaYaCancelada; solo cambia el estado (R6).
- reservas/repositorio.py (nuevo): listar_reservas, consultar_disponibilidad, crear_reserva (BEGIN IMMEDIATE → leer + id + superposición + INSERT, rollback si falla, commit antes de devolver), cancelar_reserva, reiniciar_datos(ruta, ruta_inventario, confirmado) y comando python -m reservas.repositorio [ruta_db] que pide confirmación con input().
- tests/test_dominio.py + RF-07; tests/test_repositorio.py (nuevo) con bases temporales vía tempfile.
Salida real de python -m unittest discover -s tests -v desde la raíz:
test_cancelar_inexistente (test_dominio.CancelacionRF07.test_cancelar_inexistente) ... ok
test_cancelar_ya_cancelada (test_dominio.CancelacionRF07.test_cancelar_ya_cancelada) ... ok
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
test_CA_05_cancelar_libera_horario_y_conserva_registro (test_repositorio.Persistencia.test_CA_05_cancelar_libera_horario_y_conserva_registro) ... ok
test_CA_07_recupera_activa_y_cancelada_tras_reabrir (test_repositorio.Persistencia.test_CA_07_recupera_activa_y_cancelada_tras_reabrir) ... ok
test_cancelar_reserva_inexistente (test_repositorio.Persistencia.test_cancelar_reserva_inexistente) ... ok
test_cancelar_reserva_ya_cancelada (test_repositorio.Persistencia.test_cancelar_reserva_ya_cancelada) ... ok
test_comando_reinicio_pide_confirmacion (test_repositorio.Persistencia.test_comando_reinicio_pide_confirmacion) ... ok
test_consulta_informa_bloqueo_persistido (test_repositorio.Persistencia.test_consulta_informa_bloqueo_persistido) ... ok
test_creacion_fallida_no_guarda_ni_consume_id (test_repositorio.Persistencia.test_creacion_fallida_no_guarda_ni_consume_id) ... ok
test_identificadores_no_se_reutilizan (test_repositorio.Persistencia.test_identificadores_no_se_reutilizan) ... ok
test_reinicio_requiere_confirmacion (test_repositorio.Persistencia.test_reinicio_requiere_confirmacion) ... ok

----------------------------------------------------------------------
Ran 23 tests in 0.403s

OK
Nota: los IDs nunca se reutilizan tras cancelar (el próximo sale del MAX de la tabla); tras un reinicio explícito sí vuelve a empezar en R-0001, porque ahí se borraron los datos a propósito. Sin commits, SPEC.md e inventario.json intactos.

## 4. Mi verificación (lo que ejecuté yo)

- Comando: python -m unittest discover -s tests -v
- Python 3.15.2, Windows 10, ejecutado en la terminal de VS Code

### 4.1 Ejecución normal
Resultado: Ran 23 tests, OK.

```
test_cancelar_inexistente (test_dominio.CancelacionRF07.test_cancelar_inexistente) ... ok
test_cancelar_ya_cancelada (test_dominio.CancelacionRF07.test_cancelar_ya_cancelada) ... ok
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
test_CA_05_cancelar_libera_horario_y_conserva_registro (test_repositorio.Persistencia.test_CA_05_cancelar_libera_horario_y_conserva_registro) ... ok
test_CA_07_recupera_activa_y_cancelada_tras_reabrir (test_repositorio.Persistencia.test_CA_07_recupera_activa_y_cancelada_tras_reabrir) ... ok
test_cancelar_reserva_inexistente (test_repositorio.Persistencia.test_cancelar_reserva_inexistente) ... ok
test_cancelar_reserva_ya_cancelada (test_repositorio.Persistencia.test_cancelar_reserva_ya_cancelada) ... ok
test_comando_reinicio_pide_confirmacion (test_repositorio.Persistencia.test_comando_reinicio_pide_confirmacion) ... ok
test_consulta_informa_bloqueo_persistido (test_repositorio.Persistencia.test_consulta_informa_bloqueo_persistido) ... ok
test_creacion_fallida_no_guarda_ni_consume_id (test_repositorio.Persistencia.test_creacion_fallida_no_guarda_ni_consume_id) ... ok
test_identificadores_no_se_reutilizan (test_repositorio.Persistencia.test_identificadores_no_se_reutilizan) ... ok
test_reinicio_requiere_confirmacion (test_repositorio.Persistencia.test_reinicio_requiere_confirmacion) ... ok

----------------------------------------------------------------------
Ran 23 tests in 0.507s

OK
```

### 4.2 Prueba de sensibilidad A: repositorio.py
La idea de estas pruebas me la propuso el asistente de chat; las ejecuté yo.
Cambio: desactivé (con #) la línea 139 de reservas/repositorio.py, dentro de
`cancelar_reserva`. (COMPLETAR: qué hace esa línea, según el comando
`git show 29f5ec0:reservas/repositorio.py | Select-Object -Skip 134 -First 10`.)
Resultado: FAILED (failures=3, errors=1). Las otras 19 pruebas dieron ok.

```
test_CA_05_cancelar_libera_horario_y_conserva_registro (test_repositorio.Persistencia.test_CA_05_cancelar_libera_horario_y_conserva_registro) ... FAIL
test_CA_07_recupera_activa_y_cancelada_tras_reabrir (test_repositorio.Persistencia.test_CA_07_recupera_activa_y_cancelada_tras_reabrir) ... FAIL
test_cancelar_reserva_ya_cancelada (test_repositorio.Persistencia.test_cancelar_reserva_ya_cancelada) ... FAIL
test_identificadores_no_se_reutilizan (test_repositorio.Persistencia.test_identificadores_no_se_reutilizan) ... ERROR

Ran 23 tests in 0.345s

FAILED (failures=3, errors=1)
```
(Quité de este bloque las pruebas que dieron ok y el detalle de los errores; los nombres y el resumen son los que mostró la terminal.)

Restauré con `git checkout -- reservas/repositorio.py` y volví a ejecutar las
pruebas: Ran 23 tests in 1.757s, OK.

### 4.3 Prueba de sensibilidad B: dominio.py
Cambio: en `cancelar_reserva`, desactivé con # la línea
`reserva.estado = ESTADO_CANCELADA` (línea 142 de reservas/dominio.py).
Resultado: FAILED (failures=5, errors=1). Las otras 17 pruebas dieron ok.

```
test_cancelar_ya_cancelada (test_dominio.CancelacionRF07.test_cancelar_ya_cancelada) ... FAIL
test_CA_05_cancelada_no_bloquea (test_dominio.CriteriosDeAceptacion.test_CA_05_cancelada_no_bloquea) ... FAIL
test_CA_05_cancelar_libera_horario_y_conserva_registro (test_repositorio.Persistencia.test_CA_05_cancelar_libera_horario_y_conserva_registro) ... FAIL
test_CA_07_recupera_activa_y_cancelada_tras_reabrir (test_repositorio.Persistencia.test_CA_07_recupera_activa_y_cancelada_tras_reabrir) ... FAIL
test_cancelar_reserva_ya_cancelada (test_repositorio.Persistencia.test_cancelar_reserva_ya_cancelada) ... FAIL
test_identificadores_no_se_reutilizan (test_repositorio.Persistencia.test_identificadores_no_se_reutilizan) ... ERROR

Ran 23 tests in 0.349s

FAILED (failures=5, errors=1)
```
(Mismo recorte que en 4.2.)

Restauré con `git checkout -- reservas/dominio.py`. No guardé la salida de la
ejecución inmediata posterior. Antes de seguir con el Episodio 3 volví a
ejecutar las pruebas y `git status`, y el resultado fue correcto (pruebas OK y
sin cambios pendientes).

### 4.4 Revisión del código
Comprobé estos puntos sobre el commit del Episodio 2 (`29f5ec0`), con estos
comandos desde la raíz del repositorio:

| Punto | Comando | Resultado esperado | Lo que vi |
|---|---|---|---|
| `hay_superposicion` existe una sola vez | `git grep -n "def hay_superposicion" 29f5ec0 -- reservas` | un solo resultado, en dominio.py | (COMPLETAR) |
| Sin reloj del sistema | `git grep -n "datetime.now\|date.today" 29f5ec0 -- reservas` | sin resultados | (COMPLETAR) |
| La creación usa una transacción | `git grep -n "BEGIN IMMEDIATE" 29f5ec0 -- reservas/repositorio.py` | al menos un resultado | (COMPLETAR) |
| SPEC.md e inventario.json sin cambios | `git diff --stat bcac158 29f5ec0 -- SPEC.md inventario.json` | sin salida | (COMPLETAR) |
| Cambios del agente en pruebas existentes | `git diff bcac158 29f5ec0 -- tests/test_dominio.py` | solo cambios en CA-05 y CA-06 (usar cancelar_reserva) y la prueba de RF-07 agregada, sin pruebas borradas ni afirmaciones debilitadas | (COMPLETAR: qué cambió y si te pareció correcto) |

## 5. Decisión
Acepté el resultado del Episodio 2. Las 23 pruebas pasaron cuando las ejecuté yo
y detectaron los dos errores que introduje a propósito (4.2 y 4.3). No hubo
correcciones al agente.

Además decidí documentar el comportamiento que mencionó el agente en su nota:
tras un reinicio explícito de datos, la numeración vuelve a `R-0001`. Lo registré
en SPEC 0.2 (commit
[8336d04](https://github.com/WolfFenrir22/Desafio_Agente/commit/8336d04)). El
código de este episodio está en el commit
[29f5ec0](https://github.com/WolfFenrir22/Desafio_Agente/commit/29f5ec0).

## 6. Conclusión
Las pruebas de cancelación y persistencia detectan los dos cambios que hice a
propósito. No hice una prueba de sensibilidad sobre CA-06 ni sobre el comando de
reinicio, así que lo que se verificó de esas partes es solo que las pruebas pasan.