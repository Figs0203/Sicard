# Modelo Fisico

## Alcance

Este documento describe unicamente estructuras fisicas reales o explicitamente preparadas en Sprint 1.

## Cloud SQL

Base transaccional maestra usada para OpenFlights:

- tabla `airlines`
- tabla `airports`

Documento detallado:

- `cloudsql-schema.sql`

## Firestore

Colecciones reales en Sprint 1:

### `flights_v1`

Proyeccion operacional batch normalizada.

Campos relevantes:

- `flight_id`
- `event_id`
- `schema_version`
- `processed_at`
- `flight_date`
- `carrier`
- `flight_number`
- `origin`
- `destination`
- `dep_time`
- `dep_delay`
- `arr_time`
- `arr_delay`
- `cancelled`
- `air_time`
- `distance`
- `source_uri`
- `source_generation`
- `source_row_number`

### `live_flights`

Proyeccion temporal de OpenSky.

Campos relevantes:

- `icao24`
- `event_id`
- `schema_version`
- `observed_at`
- `processed_at`
- `callsign`
- `origin_country`
- `longitude`
- `latitude`
- `baro_altitude`
- `velocity`
- `heading`
- `on_ground`

## BigQuery Gold

Dataset real:

- `flighttracker_gold`

Tablas reales:

- `fact_flights`
- `dim_airline`
- `dim_airport`
- `dim_date`
- `agg_on_time_performance`
- `agg_delay_distribution`

Documento detallado:

- `gold-star-schema.md`

## Serving target documentado

Para Sprint 2 se documenta el target Cassandra, pero no se presenta como implementado en Sprint 1.

Documento detallado:

- `serving-schema.md`
