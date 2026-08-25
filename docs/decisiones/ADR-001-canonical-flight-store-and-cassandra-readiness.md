# ADR-001: Store canonico de vuelos y preparación para Cassandra

**Estado:** Aprobado para implementación del Sprint 1

## Decisión

La fuente de verdad analítica del batch será la capa **Silver** en Parquet. Firestore será una proyección operacional temporal para la API, no la fuente de verdad ni una dependencia directa de los componentes de transformación.

El flujo objetivo es:

`RAW (GCS) -> Dataproc/Spark -> Silver (Parquet) -> flights-curated-v1 (Pub/Sub) -> flight-projector -> FlightStore -> API`

`flight-projector` implementará una única interfaz de persistencia (`FlightStore`). Durante Sprint 1 el adaptador será `FirestoreFlightStore`; para Cassandra se añadirá `CassandraFlightStore` sin cambiar el contrato del evento ni los endpoints de la API.

La API solo podrá depender de `FlightRepository` y de DTOs de dominio; no importará SDK ni tipos de Firestore.

## Contrato de evento: `flight.curated.v1`

Cada evento debe incluir, como mínimo:

- `event_id`: SHA-256 de `source_uri + source_generation + row_number`. Es idempotente para reintentos del mismo evento de origen.
- `flight_id`: SHA-256 de la clave de negocio normalizada basada en `flight_date`, `carrier`, `flight_number`, `origin`, `destination` y hora programada; mientras BTS no exponga hora programada, usar `dep_time` y documentar la limitación para vuelos cancelados.
- `schema_version`: `1`.
- `source_uri`, `source_generation`, `ingested_at`, `processed_at`.
- Datos normalizados: fecha ISO, carrier, número, origen, destino, horas, retrasos, cancelación, distancia y reglas de calidad aplicadas.

El documento Firestore usará `flight_id` como ID y conservará `event_id` como trazabilidad de origen. Así, Pub/Sub mantiene semántica *at-least-once* sin crear documentos repetidos, incluso tras reingestar el mismo vuelo.

## Compatibilidad con Cassandra

Cassandra no se conectará desde la API mediante consultas ad hoc. El adaptador Cassandra expondrá los mismos métodos del repositorio y modelará tablas para los patrones de consulta aprobados, inicialmente:

- `flights_by_date`: partición por `flight_date` y bucket de fecha, orden por hora/flight_key.
- `flight_by_id`: consulta puntual por `event_id`.

La migración será por proyección en paralelo: consumir `flight.curated.v1` en un nuevo consumidor Cassandra, hacer backfill desde Silver, validar conteos y checksums, y cambiar el adaptador de lectura de la API. Firestore no se desmantelará hasta terminar la reconciliación y la ventana de reversión.

## Reglas operacionales

1. Solo un consumidor-proyector por destino y tópico. No se mantienen dos suscripciones activas que escriban en la misma colección.
2. Rechazos de calidad y errores no recuperables van a DLQ con `event_id`, motivo y metadatos de origen.
3. La conciliación de cada archivo cumple: `filas Silver = proyectadas + rechazadas + DLQ`.
4. Las transformaciones y el contrato se versionan; un cambio incompatible crea `flight.curated.v2`.

## Terraform como control de infraestructura

Todo recurso persistente debe declararse en Terraform: tópicos, suscripciones, Eventarc, funciones/Cloud Run, Scheduler, IAM, buckets, Firestore temporal, alertas y parámetros de escalamiento. Los recursos ya existentes se importarán al estado antes de eliminar duplicados.

La secuencia segura es: inventario -> módulos Terraform -> `terraform import` -> `terraform plan` sin cambios inesperados -> despliegue del nuevo proyector idempotente -> pruebas -> retiro de recursos heredados mediante Terraform.

## Consecuencias inmediatas

- `split_and_publish_bts` deja de ser el escritor lógico de Firestore; su transición debe publicar eventos canónicos o ser reemplazada por un publicador posterior a Silver.
- `validate_and_persist_bts` se convierte en el proyector Firestore idempotente y se renombrará cuando se cree el componente administrado por Terraform.
- Las dos suscripciones actuales de `bts-flights-rows` y las dos APIs regionales no se eliminarán manualmente: primero se identificará el recurso canónico en Terraform y luego se retirarán con un plan aplicado.
