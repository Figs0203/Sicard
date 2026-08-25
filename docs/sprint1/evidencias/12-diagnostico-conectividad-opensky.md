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

## Verificacion adicional 2026-08-25 - el snapshot en `live_flights` no es ingesta activa

Una primera lectura de `live_flights` parecia mostrar datos reales entrando de forma activa (aeronaves sobre Bolivia, Paraguay y Ecuador). Dos verificaciones adicionales descartan esa lectura:

**1. La posicion de esas aeronaves no cambia entre consultas.** Dos llamadas a `/live/flights?limit=5` con ~10 minutos de diferencia devolvieron, para los mismos `icao24` (`e94c8e`, `e8810a`, `e84071`), el mismo `observed_at` y las mismas coordenadas/velocidad exactas. Solo `processed_at` avanzaba. Una aeronave real en vuelo no permanece en la misma posicion 10 minutos: es un snapshot antiguo que algo sigue reescribiendo, no una posicion fresca.

**2. Los logs del productor no muestran ninguna llamada a OpenSky.** 

```bash
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="opensky-producer"' \
  --project=flighttracker-505314 \
  --limit=20 \
  --format="table(timestamp, textPayload)"
```

Las ultimas 20 entradas (ventana 21:15-22:00 UTC) son unicamente chequeos de salud (`GET / HTTP/1.1" 200` desde `169.254.169.126`, IP interna de probe de Cloud Run) cada 5 minutos. Ninguna entrada muestra al productor intentando consultar OpenSky.

**Conclusion de esta verificacion:** no hay evidencia de que el productor este actualmente conectado a OpenSky ni consumiendo datos frescos. Los documentos "reales" visibles en `live_flights` son un snapshot que quedo de una ejecucion anterior y que algun proceso sigue reescribiendo (mecanismo exacto sin confirmar - posible reintento o redelivery de un mensaje de Pub/Sub), no prueba de conectividad activa.

**Nota sobre la cifra de `/live/count`:** el endpoint esta implementado en `backend/api/get_flights/main.py` como `list_live_flights(500)` seguido de `len(results)` - es decir, esta topeado en 500 y no es un conteo real de la coleccion. El resultado debe leerse como "al menos 500 documentos", nunca como una cifra exacta.

## Estado

**Diagnosticado** para Sprint 1: no hay conectividad activa confirmada hacia OpenSky, ni por `curl` directo desde Cloud Shell ni por el productor desplegado (sus logs no muestran intentos de consulta en la ventana revisada). El esqueleto live (topico, funcion de proyeccion, API) esta desplegado y operativo para datos ya persistidos, pero la ingesta continua de datos frescos de OpenSky no esta confirmada. La causa raiz y la resolucion quedan como item de Sprint 2, junto con corregir `/live/count` para que refleje un conteo real de la coleccion y con entender el mecanismo que reescribe `processed_at` sin datos nuevos.
