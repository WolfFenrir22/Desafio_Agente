# Sistema de reservas de laboratorio

Aplicación local para consultar disponibilidad, reservar y cancelar unidades de
un laboratorio sin perder el historial. Trabajo individual "Desarrollo de un
sistema de reservas con agentes", construido con un agente de programación.

Secciones: [1. Especificación breve](#1-especificación-breve) ·
[2. Solución](#2-solución) · [3. Preparación del agente](#3-preparación-del-agente) ·
[4. Registro de decisiones y delegación](#4-registro-de-decisiones-y-delegación)

## 1. Especificación breve

Especificación completa: [SPEC.md](SPEC.md) (versión 0.3).

**Problema.** La coordinación de un laboratorio registra pedidos en mensajes y una
planilla. A veces confirma la misma unidad en horarios superpuestos y a veces una
cancelación sigue bloqueando el horario.

**Alcance.** Leer el inventario inicial, consultar disponibilidad por unidad e
intervalo, crear reservas, cancelarlas conservando el registro, listarlas y
persistirlas. Fuera de alcance: administrar el inventario, autenticación, roles,
notificaciones, pagos, integraciones, despliegue y concurrencia distribuida.

**Reglas.**
- Una reserva activa ocupa su intervalo; una cancelada no bloquea.
- Los intervalos son semiabiertos [inicio, fin): dos intervalos [a, b) y [c, d)
  se superponen si a < d y c < b.
- No se permiten reservas activas superpuestas de la misma unidad. Se permiten
  las consecutivas y las simultáneas de unidades distintas.
- La consulta de disponibilidad usa las mismas validaciones y la misma regla.
- Cancelar conserva identificador y datos; solo cambia el estado.

**Requisitos verificables** (detalle en SPEC.md): RF-01 carga del inventario;
RF-02 crear reserva; RF-03 validaciones (unidad desconocida, solicitante vacío o
solo espacios, fecha inválida, inicio no anterior al fin); RF-04 rechazo de
superposición; RF-05 consecutivas y unidades distintas; RF-06 consulta de
disponibilidad; RF-07 cancelación; RF-08 listado; RF-09 persistencia; RF-10
interfaz gráfica mínima. RNF: solo biblioteca estándar y pruebas que no dependen
de la fecha ni de una cuenta de modelo.

**Supuestos.**
- Fecha y hora: ISO 8601 `AAAA-MM-DDTHH:MM` (ej. `2026-11-05T10:00`), sin segundos.
- Zona horaria: hora local de Buenos Aires, sin conversiones.
- Fechas pasadas: se permiten (no se compara con el reloj; así las pruebas son
  reproducibles).
- Sin límite de duración ni de anticipación; un intervalo puede cruzar la medianoche.
- Identificadores `R-0001`, `R-0002`... que no se reutilizan, salvo que se
  reinicien los datos de forma explícita (vuelven a `R-0001`).
- Solicitantes ficticios.

**Criterios de aceptación.** CA-01 a CA-11 en SPEC.md. Ejemplo: con MIC-01
reservado de 10:00 a 11:00, se rechaza 10:30 a 11:30, se permite 11:00 a 12:00 y
se permite MIC-02 de 10:00 a 11:00.

**Evolución de la especificación (recuperable en Git).**
- 0.1: versión inicial, commit [1f79d89](https://github.com/WolfFenrir22/Desafio_Agente/commit/1f79d89).
- 0.2: se aclara que el reinicio de datos reinicia la numeración, decisión del
  Episodio 2, commit [8336d04](https://github.com/WolfFenrir22/Desafio_Agente/commit/8336d04).
- 0.3: corrijo versión y formato y completo los criterios de aceptación (CA-08 a CA-11), commit [9d92cb3](https://github.com/WolfFenrir22/Desafio_Agente/commit/9d92cb3).

## 2. Solución

**Estructura.**

```
inventario.json          inventario inicial (5 unidades)
reservas/dominio.py      reglas y validaciones (sin base de datos ni interfaz)
reservas/repositorio.py  persistencia en SQLite
reservas/gui.py          interfaz gráfica mínima (Tkinter)
tests/                   pruebas automáticas (unittest)
SPEC.md  AGENTS.md  PROGRESS.md  Evidencias/
```

**Decisiones técnicas.** Python con solo biblioteca estándar (`sqlite3`,
`tkinter`, `unittest`), por eso no hay dependencias ni archivos de bloqueo. SQLite
para persistir en un único archivo. La lógica de negocio está separada de la
interfaz para poder probarla sin ventana. Al crear una reserva, la comprobación de
superposición y el guardado ocurren en la misma transacción.

**Requisitos previos y versiones** con las que se desarrolló y probó:
Windows 10, Python 3.15.2 (incluye Tkinter y SQLite), Git 2.56.0.windows.4.
Node v26.13.0 y npm 11.20.0 solo se usaron para instalar el agente, no la
aplicación. No se probó con otras versiones ni sistemas operativos.

**Instalación y carga inicial.**

```
git clone https://github.com/WolfFenrir22/Desafio_Agente.git
cd Desafio_Agente
```

No hay nada que instalar. El inventario se lee de `inventario.json`; la base
`reservas.db` se crea sola la primera vez (`CREATE TABLE IF NOT EXISTS`).

**Comandos.**

```
python -m reservas.gui                          abre la ventana
python -m reservas.repositorio [ruta_db]        reinicia los datos (pide confirmación)
python -m unittest discover -s tests -v         ejecuta las pruebas
```

**Datos y reinicio.** Las reservas persisten en `reservas.db`, en la raíz del
proyecto (excluido de Git). **El comando de reinicio borra todas las reservas**
(activas y canceladas), recarga el inventario y reinicia la numeración en
`R-0001`. Pide confirmación y nada borra datos de forma implícita. Para borrar un
archivo de prueba sin tocar el real, pasale otra ruta como `prueba.db`.

**Ejemplo de uso en la ventana.**
Entrada: unidad `MIC-01`, inicio `2026-11-05T10:00`, fin `2026-11-05T11:00`,
solicitante `Ana Prueba`, botón Reservar.
Salida: nueva fila en la tabla: `R-0001  MIC-01  Ana Prueba  2026-11-05T10:00  2026-11-05T11:00  activa`.
Si luego se reserva `MIC-01` de `10:30` a `11:30`, aparece un mensaje de error y la
tabla no cambia.

**Pruebas.** 23 pruebas automáticas con `unittest`, con bases de datos
temporales. Cubren: creación válida, rechazo de superposición, límites
consecutivos, unidades distintas simultáneas, entradas inválidas, cancelación que
conserva el registro y libera el horario, cancelar una reserva inexistente o ya
cancelada, identificadores no reutilizados y persistencia de reservas activas y
canceladas tras cerrar y reabrir. Resultado de mi ejecución al cierre de cada
episodio: 12 pruebas OK (Episodio 1) y 23 pruebas OK (Episodios 2 y 3); ver
[Evidencias](Evidencias/).

**Verificación manual de la ventana** (las pruebas automáticas no cubren la
interfaz): procedimiento y resultados observados en
[Evidencias/05-episodio3.md](Evidencias/05-episodio3.md); captura de la tabla tras
reabrir la aplicación en [Evidencias/05-ventana.jpeg](Evidencias/05-ventana.jpeg).

**Pendientes y limitaciones.**
- La interfaz gráfica no tiene pruebas automáticas, solo el procedimiento manual.
- Se probó únicamente en Windows 10 con Python 3.15.2.
- No hay control de acceso ni gestión de concurrencia más allá de la transacción
  de SQLite.
- Se permiten reservas en el pasado y sin límite de duración, por decisión de diseño.
- El inventario no se administra desde la aplicación.

## 3. Preparación del agente

**Entorno y modelo.** OpenCode 1.19.5, ejecutado en la terminal integrada de
VS Code. Modelo mostrado por la interfaz: `MiMo-V2.6-Flash Free`; su versión exacta
no es visible. Función: escribir el código y las pruebas por tramos, con revisión
humana de cada resultado.

**Motivo de la elección.** Necesitaba un agente gratuito que actuara sobre el
repositorio con herramientas reales. Descarté: Claude Code (requiere un plan de
pago), Gemini CLI (dejó de atender cuentas individuales gratuitas el 18 de junio
de 2026) y Antigravity CLI (código cerrado y cuota semanal no publicada).
OpenCode es de código abierto y permite usar un modelo gratuito sin tarjeta.

**Instrucciones usadas.** [AGENTS.md](AGENTS.md), escrito en la raíz del
repositorio. Extracto abreviado (el texto completo está en el archivo):

```
- Python, solo biblioteca estándar. No instales dependencias.
- La lógica de negocio NO debe depender de la interfaz gráfica ni leer el reloj.
- Los intervalos son semiabiertos [inicio, fin).
- La consulta de disponibilidad y la creación usan la misma función.
- Antes de decir que terminaste, ejecutá las pruebas y mostrá la salida real.
- No hagas commits de Git: los hace la persona, después de revisar.
```

**Contexto suministrado y excluido.** En cada episodio el agente leyó SPEC.md,
AGENTS.md y los archivos de código relevantes. Se excluyeron claves, tokens y datos
reales; se usaron solicitantes ficticios (por ejemplo "Ana Prueba"). No se guardaron claves ni tokens en el repositorio.

**Permisos, controles y aprobaciones.** En los Episodios 1 y 3 el agente presentó su plan y esperó mi confirmación antes de modificar archivos (en el Episodio 1 le agregué una precisión). En el Episodio 2 mostró su plan pero siguió sin esperar mi respuesta.. AGENTS.md prohíbe commits del agente: todos los
commits los hice yo después de revisar los cambios en Source Control y de ejecutar
las pruebas por mi cuenta. Fuera de la confirmación para empezar, OpenCode no me pidió aprobar comandos específicos.

**Adaptación específica comprobable.** Regla de intervalos semiabiertos en
AGENTS.md, para que una reserva que termina a las 11:00 no choque con otra que
empieza a las 11:00. Evidencia de uso: el agente resumió esa regla al preguntarle
qué instrucciones veía ([Evidencias/01-agente-lee-instrucciones.md](Evidencias/01-agente-lee-instrucciones.md)), y las pruebas CA-02 y
`test_intervalos_consecutivos_no_superpuestos` la verifican. Al cambiar a propósito
`<` por `<=` en `hay_superposicion`, esas dos pruebas fallaron
([Evidencias/03-episodio1-verificacion.md](Evidencias/03-episodio1-verificacion.md)). También se adaptó un procedimiento de persistencia
(confirmar cada alta y cancelación antes de devolver, crear tablas solo si no
existen, borrar solo con el comando explícito), verificado con las pruebas del
Episodio 2 ([Evidencias/04-episodio2.md](Evidencias/04-episodio2.md)).

**Retención del progreso.** [PROGRESS.md](PROGRESS.md), versionado en Git, con
entorno, decisiones y una sección por episodio.

**Uso de un asistente de chat.**Uso de un asistente de chat.** Usé un asistente de chat (Claude) para entender la consigna, preparar borradores iniciales de SPEC.md y AGENTS.md y de los pedidos
al agente, proponerme las pruebas de sensibilidad, ordenar y redactar el texto de
los archivos de evidencia y del README a partir de los resultados que yo le
informé, y revisar los planes del agente (en el Episodio 3 aprobé el plan antes de
revisarlo con él). El código de la aplicación y las pruebas lo escribió OpenCode;
ejecuté yo las pruebas y las verificaciones, y las decisiones de aceptar son mías.

## 4. Registro de decisiones y delegación

**Decisiones significativas.**

| Decisión | Motivo | Alternativa | Consecuencia |
|---|---|---|---|
| Python con solo biblioteca estándar | Reproducible sin instalar nada | Frameworks externos | Interfaz gráfica sencilla |
| SQLite en lugar de JSON | Un solo archivo, transacciones | Archivo JSON | Hay que cuidar la base en las pruebas |
| Interfaz con Tkinter | Viene con Python | Consola o API local | Su prueba es manual |
| Permitir fechas pasadas | Pruebas reproducibles | Rechazarlas con un reloj falso | Menos realista |
| Reinicio de datos reinicia la numeración | Se borran todos los datos | Mantener la numeración | SPEC 0.2 |
| Agente sin permiso de commit | Que la persona revise antes | Commits automáticos | Más trabajo manual |

**Qué informó el agente y qué ejecuté yo.** Lo informado por el agente está
copiado en cada archivo de Evidencias bajo "Informe del agente". Lo que ejecuté
yo (pruebas, pruebas de sensibilidad, revisión del código y procedimiento manual)
está bajo "Mi verificación". Ambos se distinguen.

### Episodio 1: lógica de dominio
- **Objetivo y requisito:** RF-02 a RF-06 (validaciones, superposición,
  disponibilidad).
- **Contexto e instrucción:** el agente leyó SPEC.md, AGENTS.md e inventario.json;
  le pedí `reservas/dominio.py` y `tests/test_dominio.py`, avisando antes qué
  archivos crearía. Precisé que la consulta no recibe solicitante.
- **Resultado del agente:** creó los tres archivos e informó 12 pruebas OK.
- **Decisión humana:** acepté. Ejecuté las pruebas (12 OK) y cambié `<` por `<=`
  a propósito: fallaron las pruebas de límites consecutivos; restauré y volvieron
  a pasar. No hubo correcciones al agente.
- **Evidencia:** commit [bcac158](https://github.com/WolfFenrir22/Desafio_Agente/commit/bcac158),
  [Evidencias/02-episodio1-plan-del-agente.md](Evidencias/02-episodio1-plan-del-agente.md) y [Evidencias/03-episodio1-verificacion.md](Evidencias/03-episodio1-verificacion.md).

### Episodio 2: cancelación y persistencia
- **Objetivo y requisito:** RF-07 y RF-09.
- **Contexto e instrucción:** SPEC.md, AGENTS.md y `dominio.py`; le pedí
  `cancelar_reserva`, `reservas/repositorio.py` con SQLite, un comando de reinicio
  con confirmación y pruebas con bases temporales.
- **Resultado del agente:** implementó lo pedido e informó 23 pruebas OK.
- **Decisión humana:** acepté. Ejecuté las 23 pruebas y dos pruebas de
  sensibilidad (desactivar una línea en `repositorio.py` y la asignación de estado
  en `cancelar_reserva`); fallaron varias pruebas y, al restaurar, volvieron a
  pasar. Decidí documentar en SPEC 0.2 que el reinicio reinicia la numeración. No
  hubo correcciones al agente.
- **Evidencia:** commits [29f5ec0](https://github.com/WolfFenrir22/Desafio_Agente/commit/29f5ec0)
  y [8336d04](https://github.com/WolfFenrir22/Desafio_Agente/commit/8336d04);
  [Evidencias/04-episodio2.md](Evidencias/04-episodio2.md).

### Episodio 3: interfaz gráfica
- **Objetivo y requisito:** RF-10.
- **Contexto e instrucción:** SPEC.md, AGENTS.md, `dominio.py` y `repositorio.py`;
  le pedí `reservas/gui.py` que solo llame al repositorio y que avisara antes qué
  archivos tocaría.
- **Resultado del agente:** creó `gui.py` y agregó `cargar_inventario` en
  `repositorio.py`; informó 23 pruebas OK. Dijo haber borrado un `reservas.db`
  vacío creado por su propia prueba.
- **Decisión humana:** acepté. Ejecuté las pruebas (23 OK), revisé en Source
  Control que el cambio en `repositorio.py` fuera solo esa función, revisé `gui.py`
  y probé la ventana en 11 pasos, incluida la persistencia al reabrir. No hubo
  correcciones al agente.
- **Evidencia:** el código está en el commit [67daca2](https://github.com/WolfFenrir22/Desafio_Agente/commit/67daca2);
  la evidencia ([Evidencias/05-episodio3.md](Evidencias/05-episodio3.md) y
  [Evidencias/05-ventana.jpeg](Evidencias/05-ventana.jpeg)) se agregó después, en el
  commit [0ffca81](https://github.com/WolfFenrir22/Desafio_Agente/commit/0ffca81).