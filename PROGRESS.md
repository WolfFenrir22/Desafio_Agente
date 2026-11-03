# Progreso y decisiones

## Entorno (2026-11-02)
- Sistema: Windows 10
- Git 2.56.0.windows.4, Python 3.15.2, Node v26.13.0, npm 11.20.0
- Agente: OpenCode 1.19.5, ejecutado en la terminal de VS Code
- Modelo: MiMo-V2.6-Flash Free (nombre visible en la interfaz; versión
  exacta del modelo no visible)

## Registro
- 2026-11-02: especificación inicial v0.1 e inventario (primer commit,
  [1f79d89](https://github.com/WolfFenrir22/Desafio_Agente/commit/1f79d89)).
- 2026-11-02: agrego AGENTS.md con las instrucciones del agente
  ([d4257f6](https://github.com/WolfFenrir22/Desafio_Agente/commit/d4257f6)).
- 2026-11-02: comprobé que OpenCode lee AGENTS.md, ver
  [Evidencias/01-agente-lee-instrucciones.md](Evidencias/01-agente-lee-instrucciones.md)
  ([2098530](https://github.com/WolfFenrir22/Desafio_Agente/commit/2098530)).
- 2026-11-02: Episodio 1 (lógica de dominio), commit bcac158.
- 2026-11-03: Episodio 2 (cancelación y persistencia), commit 29f5ec0, y
  SPEC 0.2, commit 8336d04.
- 2026-11-03: Episodio 3 (interfaz gráfica), commit 67daca2.
- 2026-11-03: README y evidencia del Episodio 3, commit 0ffca81.
- 2026-11-03: SPEC 0.3 (corrección de versión y formato, criterios de
  aceptación CA-08 a CA-11), commit (completar con el código).

## Episodio 1: lógica de dominio (2026-11-02)
- Objetivo y requisito: RF-02 a RF-06.
- Contexto e instrucción: ver
  [Evidencias/02-episodio1-plan-del-agente.md](Evidencias/02-episodio1-plan-del-agente.md).
  Al plan del agente le agregué una precisión: la consulta de disponibilidad no
  recibe solicitante.
- Resultado del agente: creó reservas/__init__.py, reservas/dominio.py y
  tests/test_dominio.py; informó 12 pruebas OK.
- Mi verificación: ver
  [Evidencias/03-episodio1-verificacion.md](Evidencias/03-episodio1-verificacion.md).
  Ejecuté yo las pruebas (12 OK). Cambié `<` por `<=` en hay_superposicion a
  propósito para comprobar que las pruebas detectan el error: fallaron las dos
  pruebas de límites consecutivos. Restauré y volvieron a pasar.
- Decisión: acepté. El plan del agente me pareció adecuado, las 12 pruebas
  pasaron cuando las ejecuté yo y detectaron el error que introduje a propósito.
  No hubo correcciones al agente.
- Pendiente: cancelar (RF-07) queda para el Episodio 2.
- Commit: [bcac158](https://github.com/WolfFenrir22/Desafio_Agente/commit/bcac158)

## Episodio 2: cancelación y persistencia (agente: 2026-11-02; verificación y commit: 2026-11-03)
- Objetivo y requisito: RF-07 y RF-09 (cancelar y guardar en SQLite).
- Contexto e instrucción: ver
  [Evidencias/04-episodio2.md](Evidencias/04-episodio2.md).
- Resultado del agente: cancelar_reserva en dominio.py, reservas/repositorio.py
  con SQLite, comando de reinicio, 23 pruebas.
- Mi verificación: ejecuté las pruebas
  (`python -m unittest discover -s tests -v`: 23 OK), hice dos pruebas de
  sensibilidad (una línea de repositorio.py y la asignación de estado en
  cancelar_reserva): fallaron varias pruebas y, al restaurar, volvieron a pasar.
  Detalle y revisión del código en
  [Evidencias/04-episodio2.md](Evidencias/04-episodio2.md).
- Decisión: acepté, porque funcionaba de acuerdo a lo solicitado y las pruebas
  detectaron los errores que introduje a propósito. Además decidí documentar en
  SPEC 0.2 que el reinicio reinicia la numeración. No hubo correcciones al agente.
- Pendiente: interfaz gráfica (Episodio 3).
- Commit: [29f5ec0](https://github.com/WolfFenrir22/Desafio_Agente/commit/29f5ec0)
- Cambio en la especificación (SPEC 0.2): [8336d04](https://github.com/WolfFenrir22/Desafio_Agente/commit/8336d04)

## Episodio 3: interfaz gráfica (2026-11-03)
- Objetivo y requisito: RF-10, interfaz gráfica mínima con Tkinter para
  consultar disponibilidad, reservar, cancelar y listar reservas.
- Contexto e instrucción: el agente leyó SPEC.md, AGENTS.md, dominio.py y
  repositorio.py. Le pedí crear reservas/gui.py usando solo funciones de
  repositorio.py, sin duplicar reglas de negocio, y que avisara antes qué
  archivos tocaría. Pedido completo y plan en
  [Evidencias/05-episodio3.md](Evidencias/05-episodio3.md).
- Resultado del agente: creó reservas/gui.py y agregó en repositorio.py la
  función cargar_inventario (una función que delega en dominio.py). Informó
  23 pruebas OK. Pidió permiso para empezar y se lo di. Dijo haber borrado un
  reservas.db vacío que había creado su propia prueba.
- Mi verificación:
  - Ejecuté yo las pruebas: 23 OK.
  - Revisé en Source Control que el cambio en repositorio.py fuera solo la
    función nueva.
  - Revisé gui.py y repositorio.py con las búsquedas indicadas, sin
    hallazgos.
  - Probé la ventana a mano en 11 pasos con datos ficticios (tabla completa
    en [Evidencias/05-episodio3.md](Evidencias/05-episodio3.md)); todos
    coincidieron con lo esperado, incluida la persistencia al cerrar y reabrir
    ([Evidencias/05-ventana.jpeg](Evidencias/05-ventana.jpeg)).
  - Las pruebas automáticas no cubren la ventana: esa parte se comprueba solo
    con el procedimiento manual.
- Decisión: acepté el resultado, porque las 23 pruebas siguen pasando, la
  ventana cumplió los 11 pasos, gui.py solo llama al repositorio y el único
  cambio en repositorio.py fue la función cargar_inventario. No hubo
  correcciones al agente en este episodio.
- Pendiente: entrega.
- Commit: [67daca2](https://github.com/WolfFenrir22/Desafio_Agente/commit/67daca2).
  La evidencia (`05-episodio3.md` y `05-ventana.jpeg`) se agregó después, en el
  commit [0ffca81](https://github.com/WolfFenrir22/Desafio_Agente/commit/0ffca81).