# Evidencia 08 - OpenSky streaming deviation

**Fecha:** 2026-08-25  
**Punto del plan:** Workstream C / `C8`

## Objetivo del Sprint 1

Implementar un walking skeleton near-real-time:

`Cloud Scheduler -> OpenSky Producer -> Pub/Sub -> Consumer -> Firestore live_flights -> API live`

## Lo que si quedo validado

### 1. Topicos dedicados

Se crearon:

- `opensky-states-v1`
- `opensky-states-dlq`

Con esto OpenSky dejo de compartir el contrato `bts-flights-rows`.

### 2. Productor desplegado

Servicio:

- `opensky-producer` en Cloud Run `us-central1`

Validacion:

- `GET /health` respondio `{"status":"healthy"}`

### 3. Publicacion y proyeccion manual validadas

Se publico un evento manual en `opensky-states-v1` con `icao24=abc123`.

Resultado:

- `project_opensky_state` proyecto el documento en `live_flights`
- la API respondió correctamente:
  - `GET /live/flights?limit=5`
  - `GET /live/flights/abc123`
  - `GET /live/count`

## Lo que fallo

### 4. Polling real desde Cloud Run a OpenSky

Invocacion autenticada al productor:

```text
POST https://opensky-producer-310107974919.us-central1.run.app/
```

Respuesta observada:

```json
{
  "status": "error",
  "topic": "opensky-states-v1",
  "duration_ms": 60049,
  "message": "HTTPSConnectionPool(host='opensky-network.org', port=443): Max retries exceeded with url: /api/states/all?lamin=-5&lomin=-82&lamax=16&lomax=-66 (Caused by ConnectTimeoutError(..., 'Connection to opensky-network.org timed out. (connect timeout=60.0)'))"
}
```

### 5. Contraprueba desde Cloud Shell

Desde Cloud Shell, la misma fuente respondió correctamente:

```text
http_code=200 time_connect=0.160295 time_total=1.134100 size_download=1068935
```

### 6. Contraprueba del servicio contra otro endpoint

Cuando `OPENSKY_URL` se cambió temporalmente a `https://httpbin.org/json`, el productor respondió:

```json
{
  "status": "success",
  "states_received": 0,
  "states_published": 0,
  "states_skipped": 0,
  "topic": "opensky-states-v1"
}
```

Esto demuestra que:

- Cloud Run sí puede salir a Internet
- el servicio sí puede responder
- la publicación a Pub/Sub sí funciona
- el problema observado quedó acotado a la conectividad específica con OpenSky desde Cloud Run

## Decision de Sprint 1

Para la entrega de Sprint 1:

- **sí** se puede demostrar la rama live con evento manual end-to-end
- **no** se debe afirmar que el polling real de OpenSky ya es estable o productivo
- el job `poll-opensky` queda fuera del cierre formal hasta resolver el timeout

## Estado

**Desviacion formal aceptada para Sprint 1, con evidencia técnica.**
