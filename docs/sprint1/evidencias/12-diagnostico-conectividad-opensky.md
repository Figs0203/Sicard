# Evidencia 12 - Diagnostico de conectividad hacia OpenSky

**Fecha:** 2026-08-25  
**Punto del plan:** diagnostico de conectividad externa hacia `opensky-network.org`

## Objetivo

Acotar la causa del timeout ya conocido al consultar OpenSky desde el entorno de Google Cloud, mediante una prueba comparativa desde dos origenes distintos.

## Prueba comparativa

| Origen | Resultado |
|---|---|
| Cloud Shell (Google Cloud) | `http_code=000` - conexion nunca establecida, timeout a 20 s |
| Red residencial | El servidor responde (`http_code=403` en la raiz del sitio) |

## Interpretacion

Un `http_code=000` significa que no hubo respuesta HTTP de ningun tipo: no es limite de tasa (daria `429`) ni restriccion de endpoint (`401`/`403`). El servidor si responde desde una red residencial, por lo que la causa no esta en la configuracion del servicio desplegado.

El pendiente tecnico pasa de "algo falla en nuestra configuracion" a "la fuente externa no acepta trafico desde nuestro proveedor de nube" - una restriccion externa, diagnosticada con evidencia comparativa.

## Limite del diagnostico

La evidencia no permite afirmar la causa raiz especifica (bloqueo dirigido, politica de red del proveedor u otra). Solo permite afirmar que la conexion directa por `curl` desde Cloud Shell hacia `opensky-network.org` no se establece en el momento de la prueba.

## Actualizacion 2026-08-25 - el productor desplegado si tiene conectividad

La prueba anterior solo evalua una conexion directa por `curl` desde Cloud Shell. Es una ruta de red distinta a la que usa el servicio `opensky-producer` ya desplegado en Cloud Run.

Verificacion reejecutada el mismo dia:

```bash
curl -sS -o /dev/null -w "http_code=%{http_code}\n" --max-time 20 https://opensky-network.org
```

```text
http_code=000
```

Confirma que el timeout directo desde Cloud Shell persiste. Sin embargo, la coleccion `live_flights` muestra ingesta real y activa proveniente del productor desplegado:

```bash
curl -sS "https://get-flights-api-310107974919.us-central1.run.app/live/count"
curl -sS "https://get-flights-api-310107974919.us-central1.run.app/live/flights?limit=5"
```

```text
{"status":"success","count":500}
```

La respuesta de `/live/flights` incluyo aeronaves reales sobre Bolivia (`icao24=e94c8e`), Paraguay (`icao24=e8810a`) y Ecuador (`icao24=e84071`), con `processed_at` de minutos antes de la consulta - no corresponden a los eventos de prueba insertados manualmente (`abc123`, `test123`).

**Nota sobre la cifra de `/live/count`:** el endpoint esta implementado en `backend/api/get_flights/main.py` como `list_live_flights(500)` seguido de `len(results)` - es decir, esta topeado en 500 y no es un conteo real de la coleccion. El resultado debe leerse como "al menos 500 documentos", nunca como una cifra exacta.

## Estado

**Diagnosticado con matiz** para Sprint 1: la conexion directa por `curl` desde Cloud Shell hacia OpenSky no se establece, pero el servicio productor desplegado en Cloud Run si tiene conectividad y esta ingiriendo datos reales de forma activa. La causa especifica de por que la ruta de Cloud Shell falla queda como item de Sprint 2, junto con corregir `/live/count` para que refleje un conteo real de la coleccion.
