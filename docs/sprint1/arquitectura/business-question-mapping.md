# Matriz de Preguntas de Negocio - Sprint 1

## Objetivo

Conectar cada pregunta de negocio demostrable en Sprint 1 con su fuente de datos, transformacion, storage o serving, y producto observable.

## Alcance

Esta matriz solo cubre preguntas que hoy pueden responderse con evidencia real del sprint.

No incluye como "cerrado" lo siguiente:

- polling productivo estable de OpenSky
- Cassandra como serving final
- Airflow o Composer como orquestador implementado

## Matriz

| Pregunta de negocio | Fuente principal | Procesamiento | Storage o serving | Producto demostrable |
|---|---|---|---|---|
| Que rutas y aerolineas muestran mejor puntualidad historica en enero de 2026 | BTS historico + OpenFlights | `bts_etl.py` limpia BTS, `gold_etl_v6.py` reconstruye Gold y calcula `agg_on_time_performance` | BigQuery `flighttracker_gold.agg_on_time_performance` + `dim_airline` + `dim_airport` | consulta KPI batch validada en `docs/sprint1/evidencias/06-bigquery-kpi.txt` |
| Como se distribuyen los retrasos historicos del dataset limpio | BTS historico | `gold_etl_v6.py` genera `agg_delay_distribution` desde Silver limpio | BigQuery `flighttracker_gold.agg_delay_distribution` | tabla agregada disponible para analitica y presentacion |
| Cuantos vuelos historicos validos quedaron luego de eliminar la duplicacion x9 y los `flight_id` nulos | BTS historico | limpieza de input BTS, reconstruccion de Silver y Gold con `flight_id` alineado al contrato canonico | BigQuery `flighttracker_gold.fact_flights` | verificacion estructural del fact validada en Sprint 1 |
| Que vuelos batch puede consultar hoy un consumidor HTTP por fecha o aerolinea | BTS historico | `validate_and_persist_bts` normaliza y proyecta `flight.curated.v1` a `flights_v1` | Firestore `flights_v1` + Cloud Run `get-flights-api` | `GET /flights`, `GET /health` y filtros batch |
| Cual es el ultimo estado conocido de una aeronave live publicada manualmente | OpenSky snapshot publicado manualmente a Pub/Sub | `project_opensky_state` normaliza por `icao24` y sobrescribe el ultimo estado | Firestore `live_flights` + Cloud Run `get-flights-api` | `GET /live/flights`, `GET /live/flights/{icao24}`, `GET /live/count` |
| Existe una rama near-real-time demostrable aunque el polling real no este cerrado | OpenSky + Pub/Sub | productor publica al topic dedicado y el consumidor proyecta a Firestore; el polling real queda documentado como desviacion | Pub/Sub `opensky-states-v1`, Firestore `live_flights`, API live | skeleton live validado con evento manual y limitacion formal documentada |
| Cual es la calidad observada de las fuentes usadas en Sprint 1 | BTS limpio + OpenFlights + snapshot live exportado desde API | `generate_profiles.py` perfila y calcula metricas por dataset | `docs/sprint1/data-assessment/results/*` | `dq_summary.csv` y perfiles JSON reproducibles |

## Lectura por dominio

### Analitica batch

- Fuente de verdad: Silver limpio
- Capa de consulta: BigQuery Gold
- KPI principal validado: puntualidad por aerolinea y ruta

### Serving operacional batch

- Fuente de eventos: `flight.curated.v1`
- Proyeccion temporal: Firestore `flights_v1`
- Producto: API batch

### Serving near-real-time

- Fuente actual validada: evento manual OpenSky
- Proyeccion temporal: Firestore `live_flights`
- Producto: API live

## Limitaciones explicitas

- la matriz no debe usarse para afirmar que OpenSky ya opera en polling automatico estable
- la matriz no debe usarse para afirmar que Cassandra ya es el serving productivo
- la matriz no reemplaza la evidencia tecnica; solo la organiza

## Referencias

- `docs/sprint1/evidencias/06-bigquery-kpi.txt`
- `docs/sprint1/evidencias/07-firestore-serving-normalization.md`
- `docs/sprint1/evidencias/08-opensky-streaming-deviation.md`
- `docs/sprint1/data-assessment/results/dq_summary.csv`
- `docs/sprint1/modelos/gold-star-schema.md`
- `docs/sprint1/modelos/serving-schema.md`
