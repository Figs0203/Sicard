# Serving Schema

## Sprint 1 - estado real

La capa de serving real en Sprint 1 usa Firestore como proyeccion temporal.

## Coleccion `flights_v1`

Proposito:

- serving batch para la API REST

Documento:

- ID del documento: `flight_id`

Campos canonicos:

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

Patrones de consulta:

- lista acotada de vuelos
- filtro por aerolinea
- filtro por fecha

## Coleccion `live_flights`

Proposito:

- serving live temporal para la API

Documento:

- ID del documento: `icao24`

Campos canonicos:

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

Patrones de consulta:

- ultimos vuelos live
- vuelo por `icao24`
- conteo live

## Target Cassandra documentado

No implementado todavia en Sprint 1.

Tablas objetivo previstas:

### `flights_by_date`

Motivacion:

- consultas por fecha y lectura paginada de vuelos batch

Particion esperada:

- `flight_date`

### `flight_by_id`

Motivacion:

- lookup puntual por identificador de vuelo o evento

### `live_flights_by_icao`

Motivacion:

- lectura rapida del ultimo estado live por aeronave

## Regla de diseno

Primero se definen los patrones de consulta y luego la tabla fisica. Esa es la razon por la cual Cassandra se documenta como target y no como componente ya cerrado en Sprint 1.
