# Evidencia 03: Episodio 1, verificación humana

- Fecha: 2026-11-02
- Ejecutado por: yo (persona), en la terminal de VS Code
- Comando: python -m unittest discover -s tests -v
- Python 3.15.2, Windows 10

## Ejecución 1: código tal como lo dejó el agente
Resultado: 12 pruebas, OK
(pegá la salida completa)

## Ejecución 2: prueba de sensibilidad
Cambié `<` por `<=` en hay_superposicion para comprobar que las pruebas
detectan el error. Resultado: FAILED (failures=1, errors=1); fallaron
test_CA_02_limite_consecutivo_aceptado y
test_intervalos_consecutivos_no_superpuestos.
(pegá la salida completa que me mostraste)

## Ejecución 3: restaurado
Volví a `<`. Resultado: (completá con lo que veas)
(pegá la salida completa)

## Revisión del código
- hay_superposicion usa `<`: (sí / no)
- Creación y consulta usan la misma función de superposición: (sí / no)
- No hay datetime.now() ni date.today(): (sí / no)
- SPEC.md e inventario.json sin cambios: (sí / no)

## Decisión
(Aceptar / corregir) porque (motivo).