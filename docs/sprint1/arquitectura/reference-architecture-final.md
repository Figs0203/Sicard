# Arquitectura de Referencia Final - FlightTracker

## Objetivo

Consolidar la arquitectura de referencia final del proyecto usando Sprint 0 como contrato de alto nivel y Sprint 1 como limite de implementacion realmente validada.

Este documento no reemplaza los diagramas separados. Su funcion es fijar la narrativa arquitectonica correcta antes de dibujar:

- que problema resuelve la plataforma
- cual es la arquitectura objetivo
- que partes quedaron realmente implementadas en Sprint 1
- que desviaciones fueron aceptadas

## Relacion con Sprint 0

Sprint 0 definio cuatro compromisos estructurales que siguen guiando la arquitectura final:

1. integrar tres fuentes heterogeneas: BTS, OpenSky y OpenFlights
2. combinar batch historico y near-real-time
3. organizar el dato en capas tipo lakehouse
4. exponer productos de consumo analitico y operacional

La diferencia es que Sprint 1 cerro un walking skeleton funcional, no la vision completa prometida como TO-BE.

## Problema arquitectonico

El dominio parte de una situacion AS-IS fragmentada:

- datos operacionales dispersos
- baja integracion entre fuentes
- alta latencia para analitica
- poca trazabilidad y gobierno
- ausencia de una capa de serving unificada para consumo rapido

La arquitectura objetivo busca resolver eso con una plataforma cloud que:

- ingiere eventos live y datasets historicos
- limpia y versiona el dato
- separa verdad analitica de serving
- habilita consultas batch y live
- soporta calidad, catalogo, linaje y operacion reproducible

## Arquitectura objetivo TO-BE

### Fuentes

- `BTS` como fuente historica batch
- `OpenSky` como fuente near-real-time
- `OpenFlights` como maestro de aerolineas, aeropuertos y rutas

### Ingesta

- productor live para OpenSky
- ingesta batch para BTS
- carga de maestros OpenFlights
- capa de mensajeria para desacoplar productores y consumidores

### Procesamiento

- procesamiento batch distribuido con Spark sobre Dataproc
- procesamiento near-real-time con un motor de streaming
- reglas de calidad sobre entradas, capas curadas y modelos analiticos

### Almacenamiento

- lakehouse por capas `Bronze -> Silver -> Gold`
- base transaccional relacional para maestros y soporte operacional
- serving de baja latencia para consultas batch y live

### Consumo

- API REST
- dashboards ejecutivos
- consultas analiticas sobre Gold
- productos de monitoreo live

### Gobernanza y operacion

- catalogo de datos
- linaje
- reglas de calidad
- CI/CD y automatizacion
- monitoreo y alertamiento

## Principios de arquitectura

### 1. Separacion entre verdad analitica y proyeccion operacional

- Silver es la fuente de verdad del batch limpio
- Gold es la capa analitica consultable
- el serving no define la verdad del dato

### 2. Contratos canonicos antes que acoplamientos por tecnologia

- `event_id` y `flight_id` se definen por contrato
- la API depende de repositorios logicos, no de un SDK concreto

### 3. Batch y live comparten dominio, no necesariamente el mismo storage

- el batch optimiza consistencia, reconstruccion y KPI
- el live optimiza lectura del ultimo estado conocido

### 4. Infraestructura declarada y validable

- Terraform debe reflejar el estado canonico
- scripts operativos deben permitir bootstrap, plan, validacion y destroy seguro

## Capas de la arquitectura final

### 1. Source layer

- BTS CSV
- OpenSky API
- OpenFlights datasets

### 2. Landing and messaging layer

- Cloud Storage RAW
- Pub/Sub para contratos operacionales y live

### 3. Processing layer

- Cloud Functions para validacion, particion de archivos y proyeccion
- Dataproc/Spark para batch
- motor live objetivo para streaming continuo

### 4. Curated and analytics layer

- Silver en Parquet
- Gold en BigQuery con `fact_flights`, dimensiones y agregados KPI

### 5. Serving layer

- objetivo final: Cassandra
- estado Sprint 1: Firestore temporal

### 6. Consumption layer

- Cloud Run `get-flights-api`
- dashboards y productos visuales posteriores

### 7. Governance and operations layer

- profiling y DQ reproducible
- Terraform
- scripts operativos
- observabilidad y alertas como trabajo posterior

## Estado implementado y validado en Sprint 1

### Implementado

- BTS limpio como input batch productivo
- Silver limpio en Parquet
- Gold corregido en BigQuery
- Cloud SQL para maestros OpenFlights
- Firestore `flights_v1` como serving batch temporal
- Firestore `live_flights` como serving live temporal
- API REST con endpoints batch y live
- Cloud Scheduler + `start_batch_pipeline` para orquestacion diaria
- validacion reproducible con `bootstrap.sh`, `deploy.sh`, `validate.sh`, `destroy.sh`

### Validado con evidencia

- Gold sin duplicacion x9
- KPI batch consultable en BigQuery
- API `/health`, `/flights` y `/live/*`
- skeleton near-real-time probado con evento manual
- profiling y DQ reproducibles
- seguridad basica de Cloud SQL endurecida

## Brecha entre arquitectura objetivo y Sprint 1

### Componentes objetivo aun no cerrados

- Cassandra como serving final
- Airflow o Composer como orquestacion avanzada
- polling automatico estable de OpenSky
- alertas operativas
- dashboards ejecutivos y mapa interactivo
- catalogo, linaje y gobierno avanzados

### Desviaciones aceptadas

- Firestore reemplaza temporalmente a Cassandra
- Cloud Scheduler + Cloud Function reemplazan temporalmente Airflow
- OpenSky queda probado solo en modo skeleton con evento manual
- la topologia regional queda separada entre `us-central1` y `us-east1`

Documento de soporte:

- `docs/decisiones/ADR-002-sprint1-accepted-deviations.md`

## Decision arquitectonica de cierre para Sprint 1

La arquitectura final del proyecto sigue siendo una plataforma cloud de datos para batch, near-real-time, serving y analitica gobernada. Sin embargo, al cierre de Sprint 1 debe comunicarse asi:

- la arquitectura objetivo sigue siendo lakehouse + serving de baja latencia + gobierno del dato
- la implementacion validada del sprint cubre batch productivo, Gold confiable, API operativa y skeleton live
- los componentes no cerrados deben mostrarse como target o backlog, no como estado actual

## Referencias

- `docs/decisiones/ADR-001-canonical-flight-store-and-cassandra-readiness.md`
- `docs/decisiones/ADR-002-sprint1-accepted-deviations.md`
- `docs/sprint1/arquitectura/business-question-mapping.md`
- `docs/sprint1/modelos/physical.md`
- `docs/sprint1/modelos/gold-star-schema.md`
- `docs/sprint1/modelos/serving-schema.md`
