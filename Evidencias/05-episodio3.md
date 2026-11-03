plan del agente:
Archivos que voy a tocar:
1. Crear reservas/gui.py — ventana Tkinter con combobox de unidad (desde inventario.json), campos inicio/fin/solicitante, botones Consultar/Reservar/Cancelar, tabla de todas las reservas y barra de estado. Solo llama a repositorio.py (consultar, crear, cancelar, listar); los errores se muestran con messagebox sin cerrar la app.
2. Modificar reservas/repositorio.py — agregar una función pública cargar_inventario(ruta) (3 líneas, delega en dominio.cargar_inventario) para que la GUI dependa solo del repositorio. No toca lógica existente.
No toco SPEC.md, inventario.json ni las pruebas. 

el agente pidió permiso para empezar y se lo di

# Evidencia 05: Episodio 3 (interfaz gráfica)

- Fecha: 2026-11-03
- Herramienta: OpenCode 1.19.5, modelo mostrado: MiMo-V2.6-Flash Free

## Instrucción que le di
Leé SPEC.md, AGENTS.md, reservas/dominio.py y reservas/repositorio.py.Tarea: interfaz gráfica mínima con tkinter (RF-10) en reservas/gui.py,que se abra con `python -m reservas.gui`.La ventana debe permitir: elegir la unidad (desde el inventario), escribirinicio y fin (formato AAAA-MM-DDTHH:MM) y el solicitante, y tres botones:Consultar disponibilidad, Reservar y Cancelar (la reserva seleccionada enla tabla). Una tabla con todas las reservas, activas y canceladas, que seactualice después de cada operación. Los errores (entrada inválida,
superposición, etc.) se muestran en un mensaje sin cerrar la aplicación.La interfaz solo debe llamar a funciones de repositorio.py; no dupliquesreglas de negocio. La base por defecto es reservas.db en la raíz. Mantenelasimple, sin estilos elaborados.Antes de tocar nada, decime qué archivos vas a crear o modificar. No toquesSPEC.md, inventario.json ni las pruebas existentes. No hagas commits.Al terminar, ejecutá las pruebas existentes, mostrame la salida real y
decime cómo abrir la ventana.

## Plan del agente
Archivos: crear reservas/gui.py; modificar reservas/repositorio.py para
agregar cargar_inventario(ruta). No tocar SPEC.md, inventario.json ni las
pruebas. El agente pidió permiso para empezar y se lo di sin una revisión
previa de otra persona.

## Informe del agente 
Archivos:
- Creado reservas/gui.py (ventana Tkinter, RF-10).
- Modificado reservas/repositorio.py:67 — solo agregué cargar_inventario() como passthrough para que la GUI use únicamente el repositorio.
Pruebas reales (python -m unittest discover -s tests -v):
...
test_reinicio_requiere_confirmacion ... ok
----------------------------------------------------------------------
Ran 23 tests in 0.486s

OK
(También verifiqué que reservas.gui importa y que la ventana se construye sin errores; borré el reservas.db vacío que dejó esa prueba.)
Cómo abrir la ventana (desde la raíz del proyecto):
python -m reservas.gui
Elegí la unidad en el combo, escribí inicio/fin (AAAA-MM-DDTHH:MM) y solicitante, y usá los tres botones; la tabla se refresca tras cada operación y los errores aparecen en un cuadro de diálogo sin cerrar la app.
Observación: dijo haber borrado un reservas.db vacío que había creado su
propia prueba.

## Mi verificación 
- Comando: python -m unittest discover -s tests -v
- Resultado: (pegá tu salida; debería ser Ran 23 tests, OK)
- Cambio en repositorio.py revisado en Source Control: (solo agregó
  cargar_inventario / otra cosa)
- Revisión de gui.py: (qué encontraste con la búsqueda del paso 1)

## Prueba manual de la ventana
(python -m reservas.gui; datos ficticios; ejecutada y observada por mí el 2026-11-03)

| Paso | Acción | Esperado | Observado |
|---|---|---|---|
| 1 | Abrir la ventana | Tabla vacía | Se cumplió: la ventana abrió con la tabla vacía |
| 2 | MIC-01, 2026-11-05T10:00 a 2026-11-05T11:00, solicitante Ana Prueba | R-0001 activa | Se cumplió: se creó R-0001 activa |
| 3 | MIC-01, 10:30 a 11:30 del mismo día | Mensaje de superposición, tabla igual | Se cumplió: se rechazó con mensaje y la tabla no cambió |
| 4 | MIC-01, 11:00 a 12:00 | Se acepta (R-0002) | Se cumplió: se aceptó como R-0002 |
| 5 | MIC-02, 10:00 a 11:00 | Se acepta (R-0003) | Se cumplió: se aceptó como R-0003 |
| 6 | Solicitante con solo espacios | Se rechaza | Se cumplió: se rechazó |
| 7 | Fecha 2026-02-30T10:00 | Se rechaza | Se cumplió: se rechazó |
| 8 | Consultar MIC-01, 10:30 a 11:00 | Informa R-0001 como bloqueo | Se cumplió: informó R-0001 como bloqueo |
| 9 | Cancelar R-0001 (seleccionada) | Sigue en la tabla como cancelada | Se cumplió: R-0001 quedó en la tabla con estado cancelada |
| 10 | MIC-01, 10:00 a 11:00 | Se acepta (R-0004) | Se cumplió: se aceptó como R-0004 |
| 11 | Cerrar la ventana y volver a abrirla | Las reservas siguen, con sus estados | Se cumplió: al reabrir siguen R-0001 cancelada y R-0002, R-0003 y R-0004 activas (ver 05-ventana.png) |

Nota: al reabrir escribí `python -m reservas.gui.` con un punto final por error;
Python dio ModuleNotFoundError. Lo repetí sin el punto y funcionó. No es una falla
del agente.

## Decisión
Aceptar (as 23 pruebas pasan, la ventana funciona en los 11 pasos, gui.py solo llama al repositorio, y el cambio en repositorio.py fue solo la función cargar_inventario)