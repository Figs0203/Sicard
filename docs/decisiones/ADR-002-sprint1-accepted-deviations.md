# ADR-002: Desviaciones aceptadas al cierre de Sprint 1

## Estado

Aprobado para Sprint 1.

## Fecha

2026-08-25

## Contexto

La arquitectura objetivo presentada al inicio del proyecto no coincide en todos sus componentes con la implementacion realmente cerrada en Sprint 1. Para evitar presentar como "terminado" lo que sigue siendo transitorio o aplazado, este ADR consolida las desviaciones aceptadas por el equipo al cierre del sprint.

Estas desviaciones no invalidan el walking skeleton. Su funcion es dejar explicito que el producto demostrado en Sprint 1 es una version operativa minima, con varios componentes temporales o pospuestos hacia Sprint 2.

## Desviacion 1: Cassandra pospuesta

### Objetivo original

Usar Cassandra como capa de serving de baja latencia para consultas batch y live.

### Estado real en Sprint 1

Cassandra no fue implementada.

El serving real quedo soportado por:

- Firestore `flights_v1` para vuelos batch normalizados
- Firestore `live_flights` para el ultimo estado live por `icao24`
- API `get-flights-api` desacoplada mediante `FlightRepository`

### Justificacion

- la ruta de menor riesgo para cerrar Sprint 1 fue asegurar primero el contrato canonico del dato
- Firestore permitio validar idempotencia, serving y API sin bloquear el sprint por operacion de Cassandra
- el repositorio ya quedo preparado para migrar el adaptador sin romper el contrato HTTP

### Impacto

- Cassandra sigue siendo target de Sprint 2
- no debe presentarse como componente desplegado ni validado en Sprint 1

## Desviacion 2: Airflow/Composer pospuesto

### Objetivo original

Contar con una orquestacion mas rica tipo DAG para batch y, eventualmente, para procesos de mayor complejidad operacional.

### Estado real en Sprint 1

La orquestacion real quedo resuelta con:

- Cloud Scheduler `daily-bts-pipeline`
- Cloud Function `start_batch_pipeline`
- Dataproc efimero para ejecutar Spark

### Justificacion

- el requerimiento de Sprint 1 era demostrar ejecucion automatizada diaria, no un stack completo de orquestacion enterprise
- Cloud Scheduler + Cloud Function resolvio el walking skeleton con menor complejidad operativa y menor costo
- el principal riesgo de Sprint 1 estaba en limpiar BTS, estabilizar Silver/Gold y evitar duplicados, no en la expresividad del orquestador

### Impacto

- Airflow o Composer no deben aparecer como implementados en Sprint 1
- cualquier diagrama o narrativa que los muestre debe tratarlos como arquitectura objetivo o backlog, no como estado actual

## Desviacion 3: Firestore como store temporal

### Objetivo original

Separar claramente la fuente de verdad analitica de la capa de serving y dejar la rama operacional lista para un store mas apropiado para latencia y escalabilidad.

### Estado real en Sprint 1

Firestore se uso como proyeccion operacional temporal.

Reglas aceptadas:

- Silver es la fuente de verdad del batch
- Gold en BigQuery es la capa analitica consultable
- Firestore no es la fuente de verdad analitica
- Firestore sirve como read model temporal para la API

### Justificacion

- permitio demostrar persistencia operacional y endpoints reales antes de la migracion a Cassandra
- la API ya depende de un puerto logico y no del SDK de Firestore como parte del contrato externo
- se validaron `flights_v1` y `live_flights` como colecciones consistentes para Sprint 1

### Impacto

- Firestore debe describirse como solucion temporal
- su presencia no reemplaza la decision futura de migrar el serving a Cassandra

## Desviacion 4: Regiones separadas

### Objetivo original

Mantener una topologia simple y consistente por regiones.

### Estado real en Sprint 1

La implementacion validada quedo dividida entre regiones:

- `us-central1` para datos y serving principal
- `us-east1` para batch/orquestacion

Asignacion real observada:

- Cloud SQL, buckets, funciones operacionales y API principal en `us-central1`
- `start_batch_pipeline` y `daily-bts-pipeline` en `us-east1`

### Justificacion

- ya existian recursos operativos desplegados en esas regiones
- mover recursos sensibles durante Sprint 1 agregaba riesgo innecesario
- se priorizo alinear Terraform con el estado canonico validado antes que forzar una migracion regional completa

### Impacto

- Terraform de Sprint 1 debe reflejar exactamente esta separacion regional
- no debe afirmarse que toda la plataforma corre en una sola region
- la unificacion o rediseño regional queda como trabajo posterior

## Decision

Se aceptan formalmente estas desviaciones al cierre de Sprint 1:

1. Cassandra queda pospuesta a Sprint 2.
2. Airflow o Composer no forman parte de la implementacion cerrada del sprint.
3. Firestore se mantiene como serving temporal.
4. La plataforma queda operando en una topologia regional mixta `us-central1` y `us-east1`.

## Consecuencias

- los entregables deben distinguir entre arquitectura objetivo y arquitectura implementada
- los scripts, README y evidencias deben describir el estado real validado
- las demos y presentaciones no deben vender como productivo lo que aun es transitorio o aplazado

## Referencias

- `docs/decisiones/ADR-001-canonical-flight-store-and-cassandra-readiness.md`
- `docs/sprint1/evidencias/08-opensky-streaming-deviation.md`
- `docs/sprint1/evidencias/11-terraform-plan-clean.md`
- `docs/sprint1/evidencias/12-validation-workflow-pass.md`
