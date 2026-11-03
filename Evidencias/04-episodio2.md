# Evidencia 04: Episodio 2 (cancelación y persistencia)

- Fecha: 2026-11-02
- Herramienta: OpenCode 1.19.5, modelo mostrado: MiMo-V2.6-Flash Free

## Instrucción que le di
(Leé SPEC.md, AGENTS.md y reservas/dominio.py.
Quiero agregar dos cosas, sin interfaz gráfica: 1. Cancelar una reserva (RF-07), en dominio.py: cambia solo su estado a  "cancelada" y falla si no existe o ya estaba cancelada.
2. Guardar las reservas en SQLite (RF-09), en reservas/repositorio.py: que se recuperen al cerrar y volver a abrir, con identificadores R-0001, R-0002... que nunca se reutilicen. La ruta de la base se recibe por parámetro. Al crear una reserva, la comprobación de superposición y el guardado deben hacerse en la misma transacción. Agregá además un comando para reiniciar los datos (borra las reservas y recarga el inventario) que pida confirmación. Antes de tocar nada, decime qué archivos vas a crear o modificar.Después hacé pruebas con unittest usando bases de datos temporales:reservas activas y canceladas que se recuperan tras reabrir (CA-07),cancelar libera el horario y conserva el registro (CA-05), cancelar una inexistente o ya cancelada, y que los identificadores no se reutilicen. No toques SPEC.md ni inventario.json. No hagas commits. Al terminar, mostrame la salida real de python -m unittest discover -s tests -v.)

## Plan del agente antes de actuar
(Modificar reservas/dominio.py: reemplazar cancelar por cancelar_reserva(reservas, identificador) (RF-07: busca por id, falla con ReservaNoEncontrada si no existe y ReservaYaCancelada si ya estaba; solo cambia el estado).
Crear reservas/repositorio.py: tabla con CREATE TABLE IF NOT EXISTS; listar_reservas, consultar_disponibilidad (delega en dominio, R5), crear_reserva con BEGIN IMMEDIATE (leer + calcular id + comprobar superposición + INSERT en una sola transacción, commit antes de devolver), cancelar_reserva (transacción + commit), reiniciar_datos(ruta, ruta_inventario, confirmado) que exige confirmación, y comando CLI python -m reservas.repositorio [ruta] que pide confirmación con input().
Modificar tests/test_dominio.py: CA-05 y CA-06 pasan a usar cancelar_reserva; agrego test de RF-07.
Crear tests/test_repositorio.py: CA-07, CA-05 con base temporal, cancelar inexistente/yá cancelada, ids no reutilizados, creación fallida no consume id, reinicio con/sin confirmación.
No toco SPEC.md ni inventario.json, sin commits.)

## Decisión
(Aceptar) porque (funcionaba bien sin ningun error mediante las pruebas realizadas).

## Informe del agente 
(Hecho, 23 tests en verde. Resumen de cambios:
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
test_reinicio_requiere_confirmacion (test_repositorio.Persistencia.test_reinicio_requiere_confirmacion) ... ok)

## Mi verificación 

- Comando: python -m unittest discover -s tests -v
- Python 3.15.2, Windows 10, ejecutado en la terminal de VS Code

### Ejecución normal
Resultado: Ran 23 tests, OK
(test_cancelar_inexistente (test_dominio.CancelacionRF07.test_cancelar_inexistente) ... ok
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

OK)

### Prueba de sensibilidad A: repositorio.py
Cambio: (linea 139 con el valor de retorno de cancelar, de la funcion "cancelar_reserva")
Resultado: FAILED (failures=3, errors=1).
Fallaron: test_CA_05_cancelar_libera_horario_y_conserva_registro,
test_CA_07_recupera_activa_y_cancelada_tras_reabrir,
test_cancelar_reserva_ya_cancelada y test_identificadores_no_se_reutilizan.
Restauré con git checkout.

### Prueba de sensibilidad B: dominio.py
Cambio: en cancelar_reserva, desactivé con # la línea
`reserva.estado = ESTADO_CANCELADA` (línea 142).
Resultado: FAILED (failures=5, errors=1).
Fallaron: test_cancelar_ya_cancelada y test_CA_05_cancelada_no_bloquea
(test_dominio), y en test_repositorio: test_CA_05_cancelar_libera_horario_y_conserva_registro,
test_CA_07_recupera_activa_y_cancelada_tras_reabrir,
test_cancelar_reserva_ya_cancelada y test_identificadores_no_se_reutilizan.
(pegá la salida completa que me mostraste)

### Restaurado
Ejecuté git checkout -- reservas/dominio.py y volví a correr las pruebas.
Resultado: (completá con lo que veas: debería ser Ran 23 tests, OK)
(pegá la salida completa)

### Conclusión
Las pruebas de cancelación y persistencia detectan los dos cambios que hice
a propósito, así que controlan lo que dicen controlar.

