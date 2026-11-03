# Progreso y decisiones

## Entorno (2026-11-02)
- Sistema: Windows 10
- Git 2.56.0.windows.4, Python 3.15.2, Node v26.13.0, npm 11.20.0
- Agente: OpenCode 1.19.5, ejecutado en la terminal de VS Code
- Modelo: MiMo-V2.6-Flash Free (nombre visible en la interfaz; versión
  exacta del modelo no visible)

## Registro
- 2026-11-02: especificación inicial v0.1 e inventario (primer commit).
- 2026-11-02: agrego AGENTS.md con las instrucciones del agente.
- 2026-11-02: comprobé que OpenCode lee AGENTS.md (ver evidencia/01...)

la operación de cancelar queda para el Episodio 2. Anotalo en PROGRESS.md para no olvidarlo.

## Episodio 1: lógica de dominio (2026-11-02)
- Objetivo y requisito: RF-02 a RF-06.
- Contexto e instrucción: ver evidencia/02-episodio1-plan-del-agente.md
- Resultado del agente: creó reservas/__init__.py, reservas/dominio.py y
  tests/test_dominio.py; informó 12 pruebas OK.
- Mi verificación: ver evidencia/03-episodio1-verificacion.md
- Decisión: (aceptar) porque (me parecio bien lo que planeaba realizar).
- Pendiente: cancelar (RF-07) queda para el Episodio 2.
- Commit: [bcac158](https://github.com/WolfFenrir22/Desafio_Agente/commit/bcac158)

## Episodio 2: cancelación y persistencia (2026-11-02)
- Objetivo y requisito: RF-07 y RF-09 (cancelar y guardar en SQLite).
- Contexto e instrucción: ver evidencia/04-episodio2.md
- Resultado del agente: cancelar_reserva en dominio.py, reservas/repositorio.py
  con SQLite, comando de reinicio, 23 pruebas.
- Mi verificación: ejecuté las pruebas (python -m unittest discover -s tests -v), prueba de sensibilidad
  (ver 04-episodio2.md en la carpeta Evidencias), revisión del código (ver 04-episodio2.md en la carpeta Evidencias).
- Decisión: (aceptar) porque (Funcionaba de acuerdo a lo que se solicito). Además decidí documentar en
  SPEC 0.2 que el reinicio reinicia la numeración.
- Pendiente: interfaz gráfica (Episodio 3).
- Commit: [29f5ec0](https://github.com/WolfFenrir22/Desafio_Agente/commit/29f5ec0)
- Cambio en la especificación (SPEC 0.2): [8336d04](https://github.com/WolfFenrir22/Desafio_Agente/commit/8336d04)