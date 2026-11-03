# Evidencia 03: Episodio 1, verificación humana

- Fecha: 2026-11-02
- Ejecutado por: yo (persona), en la terminal de VS Code
- Comando: python -m unittest discover -s tests -v
- Python 3.15.2, Windows 10
- Lo que informó el agente está en [02-episodio1-plan-del-agente.md](02-episodio1-plan-del-agente.md).
  Este archivo es lo que ejecuté y observé yo.

## Ejecución 1: código tal como lo dejó el agente
Resultado: Ran 12 tests, OK.

```
PS C:\Users\Usuario\Downloads\Desafio_Agente> python -m unittest discover -s tests -v
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

----------------------------------------------------------------------
Ran 12 tests in 0.019s

OK
```

## Ejecución 2: prueba de sensibilidad
La idea de esta prueba me la propuso el asistente de chat; la ejecuté yo.
Cambié `<` por `<=` en `hay_superposicion` para comprobar que las pruebas
detectan el error. Resultado: FAILED (failures=1, errors=1). Fallaron
test_CA_02_limite_consecutivo_aceptado (ERROR: la creación lanzó Superposicion)
y test_intervalos_consecutivos_no_superpuestos (FAIL). Las otras diez pasaron.

```
test_creacion_valida (test_dominio.CreacionValida.test_creacion_valida) ... ok
test_CA_01_superposicion_rechazada (test_dominio.CriteriosDeAceptacion.test_CA_01_superposicion_rechazada) ... ok
test_CA_02_limite_consecutivo_aceptado (test_dominio.CriteriosDeAceptacion.test_CA_02_limite_consecutivo_aceptado) ... ERROR
test_CA_03_unidades_distintas_simultaneas (test_dominio.CriteriosDeAceptacion.test_CA_03_unidades_distintas_simultaneas) ... ok
test_CA_04_entradas_invalidas (test_dominio.CriteriosDeAceptacion.test_CA_04_entradas_invalidas) ... ok
test_CA_05_cancelada_no_bloquea (test_dominio.CriteriosDeAceptacion.test_CA_05_cancelada_no_bloquea) ... ok
test_CA_06_disponibilidad_coincide_con_creacion (test_dominio.CriteriosDeAceptacion.test_CA_06_disponibilidad_coincide_con_creacion) ... ok
test_consulta_informa_reservas_que_bloquean (test_dominio.CriteriosDeAceptacion.test_consulta_informa_reservas_que_bloquean) ... ok
test_consulta_no_recibe_solicitante (test_dominio.CriteriosDeAceptacion.test_consulta_no_recibe_solicitante) ... ok
test_RF_01_carga_inventario (test_dominio.Inventario.test_RF_01_carga_inventario) ... ok
test_intervalos_consecutivos_no_superpuestos (test_dominio.SuperposicionSemiabierta.test_intervalos_consecutivos_no_superpuestos) ... FAIL
test_intervalos_que_se_solapan (test_dominio.SuperposicionSemiabierta.test_intervalos_que_se_solapan) ... ok

======================================================================
ERROR: test_CA_02_limite_consecutivo_aceptado (test_dominio.CriteriosDeAceptacion.test_CA_02_limite_consecutivo_aceptado)
----------------------------------------------------------------------
reservas.dominio.Superposicion: superposición con reserva(s): R-0001

======================================================================
FAIL: test_intervalos_consecutivos_no_superpuestos (test_dominio.SuperposicionSemiabierta.test_intervalos_consecutivos_no_superpuestos)
----------------------------------------------------------------------
AssertionError: True is not false

----------------------------------------------------------------------
Ran 12 tests in 0.023s

FAILED (failures=1, errors=1)
```
(El detalle completo de los errores se recortó; quedan las líneas que muestran
la causa.)

## Ejecución 3: restaurado

Volví a `<` en `hay_superposicion`. No guardé la salida de esa ejecución. El
código restaurado quedó en el commit
[bcac158](https://github.com/WolfFenrir22/Desafio_Agente/commit/bcac158), y en
las ejecuciones posteriores del Episodio 2 las pruebas de dominio pasaron
(ver [04-episodio2.md](04-episodio2.md)).

## Revisión del código
Comprobé estos puntos sobre el commit del Episodio 1 (`bcac158`), con estos
comandos desde la raíz del repositorio:

| Punto | Comando | Resultado esperado | Lo que vi |
|---|---|---|---|
| `hay_superposicion` usa `<` | `git grep -n -A8 "def hay_superposicion" bcac158 -- reservas/dominio.py` | la condición usa `<`, sin `<=` | (pegá o escribí lo que viste) |
| Creación y consulta usan la misma función | `git grep -n "hay_superposicion\|activas_superpuestas" bcac158 -- reservas/dominio.py` | `crear_reserva` y `consultar_disponibilidad` llaman a `activas_superpuestas` | (pegá o escribí lo que viste) |
| Sin reloj del sistema | `git grep -n "datetime.now\|date.today" bcac158 -- reservas` | sin resultados | (sin resultados / lo que apareció) |
| SPEC.md e inventario.json sin cambios | `git diff --stat 2098530 bcac158 -- SPEC.md inventario.json` | sin salida | (sin salida / lo que apareció) |

## Decisión
Acepté el resultado del Episodio 1. El plan del agente me pareció adecuado, las
12 pruebas pasaron cuando las ejecuté yo, y detectaron el error que introduje
a propósito (`<=`). No hubo correcciones al agente: mi precisión sobre la consulta
de disponibilidad fue una aclaración al plan, no una falla suya.