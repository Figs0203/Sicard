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

La evidencia no permite afirmar la causa raiz especifica (bloqueo dirigido, politica de red del proveedor u otra). Solo permite afirmar que no hay conectividad desde Google Cloud hacia `opensky-network.org` en el momento de la prueba.

## Estado

**Diagnosticado** para Sprint 1. La confirmacion de la causa raiz y la resolucion quedan como item de Sprint 2.
