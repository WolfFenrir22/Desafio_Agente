# Especificación: sistema de reservas de laboratorio

Versión 0.1 (2026-11-02). Los cambios posteriores se registran al final y en Git.

## 1. Problema
La coordinación de un laboratorio registra pedidos en mensajes y una planilla.
A veces confirma la misma unidad en horarios superpuestos, y a veces una
cancelación sigue bloqueando el horario. Necesita consultar disponibilidad,
reservar y cancelar sin perder el historial.

## 2. Alcance
Dentro: leer el inventario inicial, consultar disponibilidad por unidad e
intervalo, crear reservas, cancelarlas conservando el registro, listar
reservas y persistir los datos entre reinicios.
Fuera: administrar el inventario, autenticación y roles, notificaciones,
pagos, integraciones externas, despliegue y concurrencia distribuida.

## 3. Inventario (cada ID es una unidad física distinta)
MIC-01 y MIC-02 (microscopio digital), OSC-01 (osciloscopio),
MUL-01 (multímetro), FUE-01 (fuente de alimentación).
Se cargan desde `inventario.json`.

## 4. Reglas
- R1. Una reserva activa ocupa su intervalo; una cancelada no bloquea.
- R2. Dos intervalos [a, b) y [c, d) se superponen si a < d y c < b.
  Los intervalos son semiabiertos: el fin no se ocupa.
- R3. No se permiten reservas activas superpuestas de la misma unidad.
- R4. Se permiten reservas consecutivas (el fin de una es el inicio de otra)
  y reservas simultáneas de unidades distintas.
- R5. La consulta de disponibilidad usa exactamente las mismas validaciones
  y la misma regla de superposición que la creación.
- R6. Cancelar conserva el identificador y todos los datos; solo cambia el
  estado a "cancelada".

## 5. Requisitos verificables
- RF-01 Cargar el inventario desde `inventario.json`.
- RF-02 Crear una reserva con unidad, solicitante, inicio y fin; se le asigna
  un identificador y queda en estado "activa".
- RF-03 Rechazar, sin guardar nada: unidad desconocida; solicitante vacío o
  solo espacios; fecha u hora inexistente o con formato inválido; inicio
  que no sea estrictamente anterior al fin.
- RF-04 Rechazar la superposición con una reserva activa de la misma unidad.
- RF-05 Aceptar reservas consecutivas y simultáneas de unidades distintas.
- RF-06 Consultar la disponibilidad de una unidad en un intervalo; si no está
  libre, informar las reservas activas que lo impiden.
- RF-07 Cancelar una reserva activa por identificador; rechazar si no existe
  o ya estaba cancelada.
- RF-08 Listar las reservas, activas y canceladas.
- RF-09 Persistir reservas y estados; recuperarlos al reiniciar sin perder datos.
- RF-10 Interfaz gráfica mínima que permita consultar, reservar, cancelar
  y listar.
- RNF-01 Solo biblioteca estándar de Python (sin dependencias externas).
- RNF-02 Las pruebas se ejecutan sin conexión ni cuenta de modelo, y no
  dependen de la fecha ni de la hora actuales.

## 6. Supuestos y decisiones
- Fecha y hora: texto ISO 8601 `AAAA-MM-DDTHH:MM` (por ejemplo
  `2026-11-05T10:00`), sin segundos ni zona.
- Zona horaria: hora local de Buenos Aires; no se hacen conversiones.
- Fechas pasadas: se permiten (no se compara con el reloj), para que las
  pruebas sean reproducibles.
- Límites: sin duración mínima o máxima y sin límite de anticipación.
  Un intervalo puede cruzar la medianoche.
- Identificadores: `R-0001`, `R-0002`, ... incrementales; nunca se reutilizan,
  ni siquiera tras cancelar.
- Unidad: el ID debe coincidir exactamente con el del inventario.
- Solicitante: texto ficticio; se recortan espacios al inicio y al final.
- Almacenamiento: SQLite en `reservas.db` (fuera de Git).
-Tras un reinicio explícito de datos, la numeración vuelve a R-0001.

## 7. Criterios de aceptación
- CA-01 Con MIC-01 reservado de 10:00 a 11:00, reservar MIC-01 de 10:30 a 11:30
  se rechaza.
- CA-02 En ese mismo caso, reservar MIC-01 de 11:00 a 12:00 se acepta.
- CA-03 En ese mismo caso, reservar MIC-02 de 10:00 a 11:00 se acepta.
- CA-04 Rechazos de RF-03: unidad "MIC-99", solicitante "   ", fecha
  "2026-02-30T10:00", inicio igual al fin, e inicio posterior al fin.
- CA-05 Cancelar la reserva de MIC-01 de 10:00 a 11:00 conserva su registro
  con estado "cancelada", y luego MIC-01 de 10:30 a 11:30 se acepta.
- CA-06 La consulta de disponibilidad coincide siempre con lo que aceptaría
  la creación para los mismos datos.
- CA-07 Tras crear una reserva activa y otra cancelada, cerrar y reabrir la
  aplicación mantiene ambas con sus estados.

## 8. Historial de cambios
- 0.1 (2026-11-02): versión inicial.
- 0.2 (2026-11-02): aclaro que el reinicio de datos reinicia la numeración de identificadores (decisión del Episodio 2).

