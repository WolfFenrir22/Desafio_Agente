# Evidencia 01: el agente lee AGENTS.md

- Fecha: 2026-11-02
- Herramienta: OpenCode 1.19.5 (terminal de VS Code)
- Modelo mostrado en la interfaz: MiMo-V2.6-Flash Free
- Versión de AGENTS.md que estaba en el repositorio: commit
  [d4257f6](https://github.com/WolfFenrir22/Desafio_Agente/commit/d4257f6)
- Pregunta: "¿Qué instrucciones del proyecto estás viendo? Resumilas, no modifiques archivos."

## Respuesta del agente (copiada; solo agregué las viñetas de formato)
- Proyecto: sistema de reservas de laboratorio. SPEC.md es la fuente de verdad; si algo no está claro, preguntar, no inventar.
- Técnicas: solo biblioteca estándar (Python con sqlite3, tkinter, unittest), sin instalar dependencias. Estructura: reservas/dominio.py, reservas/repositorio.py, reservas/gui.py.
- Reglas clave: la lógica de negocio no depende de la GUI ni del reloj del sistema; recibe la ruta de la BD por parámetro. Intervalos semiabiertos [inicio, fin). Disponibilidad y creación usan la misma función de validación/superposición.
- Persistencia: commit antes de devolver resultados; CREATE TABLE IF NOT EXISTS al iniciar; borrar solo con reinicio explícito.
- Proceso: pasos chicos, avisar qué archivos voy a modificar, correr python -m unittest discover -s tests antes de decir que terminé, no commitear (lo hace la persona), datos ficticios, no tocar SPEC.md ni inventario.json salvo pedido.

## Observación
El agente resumió las reglas de AGENTS.md. Esto muestra que las ve, no que
las cumpla. El cumplimiento se revisó en cada episodio de delegación:
[Evidencias/02-episodio1-plan-del-agente.md](02-episodio1-plan-del-agente.md),
[Evidencias/04-episodio2.md](04-episodio2.md) y
[Evidencias/05-episodio3.md](05-episodio3.md).