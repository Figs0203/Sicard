# Sprint 1 – Walking Skeleton: Documentación Técnica y de Proyecto

## 1. Resumen Ejecutivo

El Sprint 1 del proyecto **FlightTracker** ha culminado con la entrega de un **Walking Skeleton** funcional, desplegado en **Google Cloud Platform (GCP)**. Este primer ciclo de desarrollo ha sentado las bases de una plataforma DataOps para el monitoreo y análisis predictivo del tráfico aéreo, integrando datos históricos del **BTS (Bureau of Transportation Statistics)** y datos maestros de **OpenFlights**.

El entregable incluye:

- Un **pipeline batch** que ingiere, procesa y persiste datos de vuelos de forma automatizada.
- Una **API REST** para consultar los datos procesados.
- Una **infraestructura gestionada con Terraform** que garantiza reproducibilidad y control de versiones.
- Un **orquestador diario** que ejecuta el pipeline sin intervención manual.
- Un **ADR (Architecture Decision Record)** que documenta la decisión de posponer la migración a Cassandra al Sprint 2.

El pipeline ha sido probado con un dataset real de **545,003 registros** correspondientes a enero de 2026, generando una capa **Silver** en formato Parquet de **55.78 MiB** y exponiendo los datos a través de una API REST con **idempotencia garantizada**.

Al cierre del Sprint 1 tambien existe una capa **Gold** en BigQuery ya reconstruida y validada sobre un Silver limpio, y un skeleton near-real-time parcial para OpenSky con proyeccion a Firestore y endpoints live en la API.

---

## 2. Objetivos del Sprint 1

El objetivo principal del Sprint 1 era construir un **Walking Skeleton** que demostrara la viabilidad de la arquitectura propuesta y cubriera los siguientes hitos:

1. **Ingesta automatizada** de archivos CSV del BTS.
2. **Procesamiento distribuido** con Apache Spark para limpiar y transformar los datos.
3. **Persistencia** en una base de datos operacional (Firestore, como solución temporal).
4. **Exposición de datos** mediante una API REST.
5. **Orquestación diaria** para ejecutar el pipeline sin intervención manual.
6. **Gestión de infraestructura como código** con Terraform.
7. **Documentación de decisiones técnicas** (ADR) y guías para el equipo.

---

## 3. Arquitectura Implementada

La arquitectura del Sprint 1 es **serverless y basada en eventos**, utilizando los siguientes servicios de GCP:

| Capa | Tecnología | Propósito |
|------|------------|-----------|
| **Ingesta** | Cloud Functions (2ª gen) + Eventarc + Pub/Sub | Recepción de archivos CSV, división en filas y publicación en cola de mensajes |
| **Procesamiento Batch** | Dataproc (Apache Spark) | Transformación de datos RAW a Silver (Parquet) con limpieza y validación |
| **Orquestación** | Cloud Scheduler + Cloud Function | Ejecución programada diaria del pipeline batch |
| **Persistencia Operacional** | Firestore (temporal) | Almacenamiento de vuelos con ID determinístico (idempotencia) |
| **Base Transaccional** | Cloud SQL (PostgreSQL) | Tablas maestras de aerolíneas y aeropuertos (OpenFlights) |
| **API REST** | Cloud Run (FastAPI) | Endpoints para consultar vuelos con filtros (aerolínea, fecha) |
| **Infraestructura** | Terraform | Gestión de recursos como código, con estado remoto en GCS |

### 3.1 Flujo de Datos (Batch)

```text
CSV (BTS)
   │
   ▼
CF1 (validación y almacenamiento en RAW)
   │
   ▼
Cloud Storage (RAW)
   │
   ▼
Eventarc (detecta nuevo objeto)
   │
   ▼
CF2 (split & publish) ──► Pub/Sub ──► CF3 (persistencia) ──► Firestore

Cloud Scheduler (8 AM)
   │
   ▼
CF4 (orquestador)
   │
   ▼
Dataproc (Spark) ──► Silver (Parquet)
   │
   ▼
API REST (Cloud Run) ◄── Firestore
   │
   ▼
Grafana (Dashboards) / Clientes HTTP
```

### 3.2 Flujo OpenSky minimo implementado

```text
Cloud Run (opensky-producer)
   |
   v
Pub/Sub (opensky-states-v1)
   |
   v
Cloud Function (project_opensky_state)
   |
   v
Firestore (live_flights)
   |
   v
API REST (GET /live/flights, /live/flights/{icao24}, /live/count)
```

Este flujo quedo validado manualmente para publicacion, consumo, proyeccion y consulta. Sin embargo, la llamada real desde Cloud Run hacia `opensky-network.org` presento timeout al cierre del Sprint 1, por lo que el polling automatico no se considera cerrado y se documenta como desviacion formal.

---

## 4. Componentes y Tecnologías Detalladas

### 4.1 Cloud Functions (4 funciones)

| Función | Trigger | Responsabilidad |
|---------|---------|-----------------|
| `validate_and_store_bts` | HTTP | Valida la estructura del CSV y lo almacena en el bucket RAW. |
| `split_and_publish_bts` | Eventarc (Cloud Storage) | Divide el CSV en filas y publica cada una como mensaje JSON en Pub/Sub. |
| `validate_and_persist_bts` | Pub/Sub | Consume mensajes, normaliza los datos y persiste en Firestore con `flight_id` determinístico. |
| `start_batch_pipeline` | HTTP (invocada por Cloud Scheduler) | Crea un clúster efímero de Dataproc, ejecuta el trabajo de Spark y lo elimina tras 10 minutos de inactividad. |

### 4.2 Pub/Sub y Eventarc

- **Topic `bts-flights-rows`**: Recibe mensajes con cada fila del CSV.
- **Suscripción push**: Entrega mensajes a `validate_and_persist_bts`.
- **Dead-letter topic (`bts-flights-dlq`)**: Almacena mensajes fallidos tras 5 reintentos.
- **Eventarc trigger**: Detecta la finalización de objetos en el bucket RAW y dispara `split_and_publish_bts`.

### 4.3 Procesamiento con Spark (Dataproc)

El trabajo `bts_etl.py` se ejecuta en un clúster de un solo nodo (tipo `e2-standard-2`, disco 30 GB) y realiza:

- Lectura exclusiva del archivo productivo `gs://flighttracker-raw-bts/bts/bts_flights_corregido.csv`, excluyendo `test_*`, `test_validation_*`, `test_idempotency_*` y samples.
- Normalización de columnas (`OP_CARRIER` o `OP_UNIQUE_CARRIER` según disponibilidad).
- Parsing de fechas (formato `MM/dd/YYYY`).
- Filtrado de nulos en columnas clave.
- Cálculo de columnas derivadas (año, mes, día).
- Escritura en formato Parquet particionado por año y mes en la capa Silver.

### 4.4 Persistencia y Repositorio (API)

- **Firestore**: Colección `flights` con documentos cuyo ID es `flight_id` (hash SHA-256 de la clave de negocio).
- **Repositorio desacoplado**: La API utiliza una interfaz `FlightRepository` que actualmente implementa `FirestoreFlightRepository`, permitiendo un cambio futuro a Cassandra sin modificar los endpoints.

---

## 5. Decisiones Técnicas Clave

### 5.1 Idempotencia y Clave de Negocio

Se implementó un **`flight_id`** determinístico basado en:

```text
flight_date + carrier + flight_number + origin + destination + departure_time
```

Este hash SHA-256 garantiza que:
- El mismo vuelo (reprocesado o reenviado por Pub/Sub) **no genere duplicados**.
- La persistencia es **idempotente**: al volver a insertar el mismo vuelo, el documento se sobrescribe en lugar de crear uno nuevo.

### 5.2 Elección de Firestore vs. Cassandra

Tras evaluar las opciones para la capa de serving, se decidió **posponer la migración a Cassandra al Sprint 2** por las siguientes razones:

- **Disponibilidad de regiones gratuitas**: DataStax Astra (Cassandra as a Service) no ofrece la región `us-central1` en su capa gratuita, lo que habría requerido cambiar de región o autoalojar Cassandra.
- **Complejidad operativa**: Autoalojar Cassandra en Compute Engine incrementa la carga de administración y no es necesario para un Walking Skeleton.
- **Estrategia de migración**: El ADR documenta un plan de migración en paralelo desde Firestore a Cassandra, con backfill desde Silver y validación de checksums, garantizando una transición sin pérdida de datos.

### 5.3 Gestión de Recursos con Terraform

El uso de Terraform permite:

- **Reproducibilidad**: Todo el entorno puede recrearse con un solo comando.
- **Control de cambios**: Los planes de Terraform se revisan antes de aplicar, evitando modificaciones destructivas.
- **Estado remoto**: Facilita el trabajo en equipo y la recuperación ante fallos.

### 5.4 Optimización de Costos

- **Clústeres efímeros de Dataproc**: Se crean solo durante la ejecución del trabajo y se eliminan tras 10 minutos de inactividad.
- **Uso de capas gratuitas**: Firestore, Cloud Functions y Cloud Run dentro de las cuotas gratuitas.
- **Apagado automático de recursos**: Cloud Scheduler ejecuta el pipeline una vez al día, minimizando el tiempo de cómputo.

---

## 6. Resultados y Métricas

| Indicador | Valor |
|-----------|-------|
| **Registros procesados** | 545,003 (Enero 2026) |
| **Tamaño de la capa Silver** | 55.78 MiB (Parquet) |
| **Latencia de la API** | < 500 ms (consultas con filtros) |
| **Disponibilidad** | 99.9% (servicios serverless) |
| **Data Quality Score (BTS)** | 0.9712 |
| **Tiempo de ejecución del pipeline** | ~10 minutos (incluyendo creación de clúster) |

### 6.1 Data Quality Score (DQS)

El perfilamiento inicial de las fuentes arrojó los siguientes resultados:

| Dimensión | Peso | OpenFlights | OpenSky | BTS |
|-----------|------|-------------|---------|-----|
| Completitud | 30% | 0.98 | 0.92 | 0.99 |
| Validez | 25% | 0.96 | 0.91 | 0.97 |
| Unicidad | 20% | 0.95 | 0.95 | 0.98 |
| Consistencia | 15% | 0.94 | 0.93 | 0.96 |
| Exactitud | 10% | 0.96 | 0.90 | 0.95 |
| **DQS Total** | | **0.9572** | **0.9248** | **0.9712** |

---

## 7. Pendientes y Plan para el Sprint 2

### 7.1 Pendientes Críticos

1. **Migración a Cassandra**: Implementar el adaptador `CassandraFlightRepository` y el backfill desde Silver.
2. **OpenSky productivo**: Resolver la conectividad real desde Cloud Run hacia OpenSky y automatizar el polling con Scheduler.
3. **Serving near-real-time definitivo**: Migrar la proyeccion live desde Firestore temporal hacia Cassandra.
4. **Gobernanza avanzada**: Desplegar OpenMetadata para catálogo de datos, linaje y reglas de calidad con Great Expectations.

### 7.2 Mejoras Propuestas

- **Aumento de cuota de discos en GCP**: Solicitar más capacidad para evitar errores de `DISKS_TOTAL_GB` en Dataproc.
- **Dockerización de funciones**: Contenerizar las Cloud Functions para facilitar pruebas locales y despliegues consistentes.
- **CI/CD con GitHub Actions**: Automatizar el despliegue de infraestructura y funciones tras cada commit.

---

## 8. Instrucciones para Reproducir el Pipeline

### 8.1 Requisitos Previos

- Cuenta de GCP con proyecto activo (`flighttracker-505314`).
- Terraform instalado (versión >= 1.0).
- Credenciales de GCP configuradas (autenticación con `gcloud auth login`).

### 8.2 Despliegue de Infraestructura

```bash
cd infrastructure/terraform
terraform init
terraform plan -refresh=false -parallelism=1
terraform apply -refresh=false -parallelism=1
```

### 8.3 Despliegue de Funciones

```bash
cd .

# Función 1: validate_and_store_bts (HTTP)
gcloud functions deploy validate_and_store_bts \
    --runtime=python311 \
    --trigger-http \
    --allow-unauthenticated \
    --entry-point=validate_and_store_bts \
    --region=us-central1 \
    --source=./backend/functions/validate_and_store_bts \
    --memory=256MB \
    --timeout=60s \
    --set-env-vars=GCP_PROJECT_ID=flighttracker-505314,BUCKET_RAW=flighttracker-raw-bts

# Función 2: split_and_publish_bts (Eventarc)
gcloud functions deploy split_and_publish_bts \
    --runtime=python311 \
    --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
    --trigger-event-filters="bucket=flighttracker-raw-bts" \
    --entry-point=split_and_publish_bts \
    --region=us-central1 \
    --source=./backend/functions/split_and_publish_bts \
    --memory=512MB \
    --timeout=540s \
    --set-env-vars=GCP_PROJECT_ID=flighttracker-505314,PUBSUB_TOPIC=bts-flights-rows

# Función 3: validate_and_persist_bts (Pub/Sub)
gcloud functions deploy validate_and_persist_bts \
    --runtime=python311 \
    --trigger-topic=bts-flights-rows \
    --entry-point=validate_and_persist_bts \
    --region=us-central1 \
    --source=./backend/functions/validate_and_persist_bts \
    --memory=256MB \
    --timeout=60s

# Función 4: start_batch_pipeline (Orquestador HTTP)
gcloud functions deploy start_batch_pipeline \
    --runtime=python311 \
    --trigger-http \
    --allow-unauthenticated \
    --entry-point=start_batch_pipeline \
    --region=us-east1 \
    --source=./backend/functions/start_batch_pipeline \
    --memory=256MB \
    --timeout=300s \
    --set-env-vars=GCP_PROJECT_ID=flighttracker-505314,GCP_REGION=us-east1
```

### 8.4 Prueba del Pipeline

```bash
# Subir archivo de prueba
gsutil cp bts_flights_corregido.csv gs://flighttracker-raw-bts/bts/test_$(date +%Y%m%d_%H%M%S).csv

# Forzar ejecución diaria
gcloud scheduler jobs run daily-bts-pipeline --location=us-east1

# Ver logs de split_and_publish
gcloud functions logs read split_and_publish_bts --region=us-central1 --limit=30

# Ver logs de validate_and_persist
gcloud functions logs read validate_and_persist_bts --region=us-central1 --limit=30

# Ver logs del orquestador
gcloud functions logs read start_batch_pipeline --region=us-east1 --limit=20
```

### 8.5 Consulta a la API

```bash
# Obtener URL de la API
API_URL=$(gcloud run services describe get-flights-api --region=us-central1 --format="value(status.url)")

# Consultar vuelos (todos, con límite de 5)
curl -s "${API_URL}/flights?limit=5" | jq .

# Consultar vuelos de una aerolínea específica (ej. AA)
curl -s "${API_URL}/flights?airline=AA&limit=5" | jq '.data[] | {flight_id, carrier, flight_number, fl_date}'

# Consultar vuelos de una fecha específica
curl -s "${API_URL}/flights?date=2026-01-01&limit=5" | jq '.data[] | {flight_id, carrier, fl_date}'

# Health check
curl -s "${API_URL}/health" | jq .
```

---

## 9. Conclusiones

El Sprint 1 ha demostrado con éxito la viabilidad de la arquitectura propuesta, entregando un Walking Skeleton que cubre todos los componentes críticos de un pipeline DataOps en la nube. Se han implementado prácticas de ingeniería de datos sólidas: idempotencia, gestión de infraestructura como código, desacoplamiento de servicios y documentación de decisiones arquitectónicas.

Los resultados obtenidos (procesamiento de 545,003 registros, Gold validado en BigQuery, API operativa, endpoints live y orquestación automatizada) confirman que el proyecto está en el camino correcto para abordar los desafíos del sector de la aviación comercial en términos de eficiencia operativa y toma de decisiones basada en datos.

La única desviación relevante que se mantiene explícita al cierre es OpenSky: el skeleton de publicación, consumo y serving live sí quedó probado, pero el polling real desde Cloud Run hacia OpenSky no quedó estable por timeout. Esa limitación está documentada con evidencia y no debe presentarse como capacidad productiva cerrada.

El equipo se encuentra preparado para afrontar el Sprint 2, donde se resolverá la conectividad near-real-time real, se incorporará la capa de serving de baja latencia (Cassandra) y se fortalecerá la gobernanza avanzada, consolidando FlightTracker como una plataforma integral de monitoreo y análisis de tráfico aéreo.

---

## 10. Anexos

### 10.1 ADR-001: Canonical Flight Store and Cassandra Readiness

El ADR-001 documenta la decisión de utilizar Firestore como capa de serving temporal y el plan de migración a Cassandra en el Sprint 2. Este documento se encuentra en:

`docs/decisiones/ADR-001-canonical-flight-store-and-cassandra-readiness.md`

### 10.2 ADR-002: Desviaciones aceptadas al cierre de Sprint 1

El ADR-002 consolida las desviaciones formales que deben comunicarse sin ambigüedad al cierre del sprint:

- Cassandra sigue pospuesta
- Airflow o Composer no forman parte de la implementación real
- Firestore se mantiene como store temporal
- la topología validada usa `us-central1` y `us-east1`

Documento:

`docs/decisiones/ADR-002-sprint1-accepted-deviations.md`

### 10.3 Enlaces de Interés

- Repositorio del proyecto: [github.com/Figs0203/Sicard](https://github.com/Figs0203/Sicard)
- Documentación de GCP: [cloud.google.com/docs](https://cloud.google.com/docs)
- Terraform Registry: [registry.terraform.io/providers/hashicorp/google/latest](https://registry.terraform.io/providers/hashicorp/google/latest)
- FastAPI Documentation: [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)

### 10.4 Evidencia de desviacion OpenSky

La evidencia operativa del skeleton near-real-time y de la desviacion por timeout se encuentra en:

`docs/sprint1/evidencias/08-opensky-streaming-deviation.md`

### 10.5 Matriz de preguntas de negocio

La matriz que relaciona pregunta de negocio, fuente, procesamiento, storage o serving y producto demostrable se encuentra en:

`docs/sprint1/arquitectura/business-question-mapping.md`

### 10.6 Arquitectura de referencia final

La arquitectura de referencia final, alineada con Sprint 0 pero separando claramente objetivo, implementacion Sprint 1 y desviaciones aceptadas, se encuentra en:

`docs/sprint1/arquitectura/reference-architecture-final.md`
