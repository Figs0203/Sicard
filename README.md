# FlightTracker

Plataforma DataOps para integrar vuelos historicos BTS, datos maestros OpenFlights y una rama near-real-time basada en OpenSky.

## Estado real de Sprint 1

Sprint 1 ya no se evalua como "crear Gold". El estado validado es:

- input BTS limpio
- Silver limpio en Parquet
- Gold corregido en BigQuery
- serving batch en Firestore `flights_v1`
- API REST en Cloud Run
- skeleton near-real-time documentado y parcialmente operativo

Estado confirmado al cierre:

- `flighttracker_gold.fact_flights` fue reconstruida sin la duplicacion x9 detectada inicialmente
- `fact_flights` quedo con `542695` filas, `542695` `flight_id` distintos y `0` nulos
- `dim_airline`, `dim_airport` y `dim_date` fueron corregidas
- la API responde `/health`, `/flights` y endpoints `/live/*`
- `validate.sh` pasa completamente

Limitacion conocida:

- OpenSky no debe presentarse como polling productivo estable desde Cloud Run, porque la llamada real a `opensky-network.org` sigue fallando por timeout desde ese entorno

Referencia:

- `docs/sprint1/evidencias/08-opensky-streaming-deviation.md`

## Arquitectura implementada

### Batch

`BTS CSV -> Cloud Storage RAW -> Eventarc -> split_and_publish_bts -> Pub/Sub -> validate_and_persist_bts -> Firestore -> Scheduler -> start_batch_pipeline -> Dataproc/Spark -> Silver -> Gold BigQuery`

### Serving

- Firestore `flights_v1` para vuelos batch normalizados
- Firestore `live_flights` para el ultimo estado live por `icao24`
- Cloud Run `get-flights-api` como capa HTTP

### Datos maestros

- Cloud SQL PostgreSQL con tablas `airlines` y `airports`

Arquitectura de referencia final documentada:

- `docs/sprint1/arquitectura/reference-architecture-final.md`

## Estructura del repo

```text
Sicard/
|-- README.md
|-- CHANGELOG.md
|-- docs/
|   |-- decisiones/
|   `-- sprint1/
|       |-- arquitectura/
|       |-- data-assessment/
|       |-- evidencias/
|       |-- modelos/
|       `-- presentacion/
|-- infrastructure/
|   |-- scripts/
|   `-- terraform/
|-- pipelines/
|   `-- batch/
|       `-- spark_jobs/
|-- backend/
|   |-- api/
|   `-- functions/
|-- database/
|   `-- scripts/
|-- frontend/
|-- tests/
|-- docker/
|-- .github/
`-- .env.example
```

Ubicaciones clave:

- Terraform: `infrastructure/terraform`
- Scripts operativos: `infrastructure/scripts`
- ETL batch BTS: `pipelines/batch/spark_jobs/bts_etl.py`
- Gold rebuild: `pipelines/batch/spark_jobs/gold_etl_v6.py`
- API: `backend/api/get_flights`
- Cloud Functions: `backend/functions`
- Perfilamiento y DQ: `docs/sprint1/data-assessment`

## Requisitos locales

Para ejecutar la reproduccion desde Cloud Shell o una shell equivalente:

- `git`
- `gcloud`
- `terraform`
- `jq`
- `curl`
- `bq`
- `zip`
- `python3`

Adicionalmente:

- sesion activa en GCP con permisos sobre el proyecto
- acceso de lectura al bucket RAW si se quiere regenerar el profiling

## Reproduccion rapida de Sprint 1

### 1. Clonar o actualizar el repo

```bash
git clone https://github.com/Figs0203/Sicard.git
cd Sicard
git pull origin main
```

### 2. Bootstrap de prerrequisitos

```bash
bash infrastructure/scripts/bootstrap.sh \
  --project-id flighttracker-505314 \
  --skip-docker-check
```

Que hace:

- valida herramientas base
- valida autenticacion en `gcloud`
- fija el proyecto activo
- habilita APIs fundacionales
- verifica o crea el bucket del backend Terraform

Que no hace:

- no ejecuta `terraform apply`
- no despliega recursos de negocio

### 3. Plan controlado de despliegue

```bash
bash infrastructure/scripts/deploy.sh \
  --project-id flighttracker-505314 \
  --skip-api-build
```

Comportamiento actual:

- empaqueta los zips de Cloud Functions gestionadas por Terraform
- puede subir artefactos a `gs://flighttracker-function-sources`
- corre `terraform init`, `terraform validate` y `terraform plan`
- solo ejecuta `apply` si se pasa `--apply`

Nota Sprint 1:

- el workflow fue validado en modo `plan-only`
- no se debe correr `terraform apply` a ciegas fuera del procedimiento acordado del equipo

### 4. Validacion operativa

```bash
bash infrastructure/scripts/validate.sh \
  --project-id flighttracker-505314
```

Checks incluidos:

- `terraform validate`
- API `/health`
- API `/flights`
- API `/live/flights`
- existencia del topic Pub/Sub batch
- probe de Firestore
- filas en BigQuery Gold
- visibilidad del ultimo job de Dataproc
- existencia del Scheduler batch
- presencia del reporte DQ

Resultado esperado validado:

```text
PASS  terraform validate
PASS  api health
PASS  api flights
PASS  api live flights
PASS  pubsub topic exists
PASS  firestore collection probe
PASS  bigquery gold fact rows
PASS  latest dataproc job visible
PASS  scheduler job exists
PASS  dq report presence
```

### 5. Regenerar profiling y DQ

Si ya tienes permisos sobre el bucket RAW:

```bash
gcloud storage cp \
  gs://flighttracker-raw-bts/bts/bts_flights_corregido.csv \
  /tmp/bts_flights_corregido.csv

curl -sS \
  "https://get-flights-api-310107974919.us-central1.run.app/live/flights?limit=50" \
  > /tmp/opensky_live_sample.json

python3 docs/sprint1/data-assessment/generate_profiles.py \
  --bts-csv /tmp/bts_flights_corregido.csv \
  --opensky-json /tmp/opensky_live_sample.json
```

Salida esperada:

- `docs/sprint1/data-assessment/results/bts_profile.json`
- `docs/sprint1/data-assessment/results/openflights_airlines_profile.json`
- `docs/sprint1/data-assessment/results/openflights_airports_profile.json`
- `docs/sprint1/data-assessment/results/opensky_profile.json`
- `docs/sprint1/data-assessment/results/dq_summary.csv`

Valores validados para `dq_summary.csv`:

```text
dataset,row_count,completeness,validity,uniqueness,consistency,accuracy_proxy,dq_score
bts,544003,0.9083,1.0,1.0,1.0,1.0,0.9725
openflights_airlines,6162,0.2493,0.9969,0.7298,0.9969,1.0,0.7195
openflights_airports,7698,1.0,0.9999,1.0,0.9999,1.0,0.9999
opensky,1,1.0,1.0,1.0,1.0,0.0,0.9
```

## Scripts operativos

### `bootstrap.sh`

Prepara prerrequisitos fundacionales del proyecto.

### `deploy.sh`

Empaqueta artefactos y ejecuta Terraform en modo controlado.

### `validate.sh`

Corre la validacion reproducible de Sprint 1.

### `destroy.sh`

Workflow seguro para destruccion controlada.

Guardrails:

- requiere `--confirm destroy-<env>-<project-id>`
- bloquea `prod` salvo que se pase `--allow-prod`
- preserva el backend remoto por defecto

## Modelos y contratos

- Modelo conceptual: `docs/sprint1/modelos/conceptual.md`
- Modelo logico: `docs/sprint1/modelos/logical.md`
- Modelo fisico: `docs/sprint1/modelos/physical.md`
- Esquema Gold: `docs/sprint1/modelos/gold-star-schema.md`
- Esquema serving: `docs/sprint1/modelos/serving-schema.md`
- Esquema Cloud SQL: `docs/sprint1/modelos/cloudsql-schema.sql`

## Evidencias clave

- Gold y KPI batch: `docs/sprint1/evidencias/06-bigquery-kpi.txt`
- Serving batch normalizado: `docs/sprint1/evidencias/07-firestore-serving-normalization.md`
- Desviacion OpenSky: `docs/sprint1/evidencias/08-opensky-streaming-deviation.md`
- Bootstrap: `docs/sprint1/evidencias/09-bootstrap-success.md`
- Deploy plan-only: `docs/sprint1/evidencias/10-deploy-plan-only-validation.md`
- Terraform clean plan: `docs/sprint1/evidencias/11-terraform-plan-clean.md`
- Validation workflow: `docs/sprint1/evidencias/12-validation-workflow-pass.md`
- Destroy guardrails: `docs/sprint1/evidencias/13-destroy-workflow-guardrails.md`

## Mapeo de negocio

La relacion entre pregunta de negocio, fuente, transformacion y producto quedo documentada en:

- `docs/sprint1/arquitectura/business-question-mapping.md`

## Desviaciones aceptadas

Las desviaciones formales de Sprint 1 quedaron consolidadas en:

- `docs/decisiones/ADR-002-sprint1-accepted-deviations.md`

Temas cubiertos:

- Cassandra pospuesta
- Airflow o Composer no implementado
- Firestore como store temporal
- separacion regional `us-central1` y `us-east1`

## Restricciones y deudas abiertas

- OpenSky sigue como desviacion aceptada, no como flujo productivo estable
- Cassandra sigue documentado como target, no como implementacion cerrada
- faltan tareas de minimo privilegio, alertamiento y cierre de deuda operativa
- no se debe presentar Terraform como reproduccion total fuera del alcance validado del Sprint 1

## Equipo

- Agustin Figueroa Sierra
- Gabriela Lucia Martinez Mercado
- Juan Carlos Munoz Trejos
- Juan Simon Ospina Martinez
