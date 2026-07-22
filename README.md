# FlightTracker - Plataforma de Monitoreo y Analisis Predictivo de Trafico Aereo

---

## Descripcion del Proyecto

FlightTracker es una plataforma integral de monitoreo y analisis de trafico aereo que integra datos en tiempo real con datos historicos para proporcionar una vision unificada de la operacion aerea. El proyecto se desarrolla como parte del curso Proyecto Ingenieria de Datos (SI4002) de la Universidad EAFIT.

El sistema esta disenado para resolver los siguientes desafios del sector de la aviacion comercial:

- Monitoreo en tiempo real: Visualizacion de la ubicacion y estado de vuelos activos.
- Analisis historico: Identificacion de patrones de retraso por aerolinea, ruta y causas especificas.
- Alertas tempranas: Notificacion automatica ante indicios de retrasos o desviaciones.
- Consumo de datos: API REST y dashboards para diferentes stakeholders.

---

## Fuentes de Datos Propuestas

| Fuente | Tipo | Descripcion |
|--------|------|-------------|
| OpenSky Network API | Streaming (Tiempo Real) | Datos ADS-B de vuelos activos (posicion, altitud, velocidad, etc.) |
| BTS On-Time Performance | Batch (Historico) | Registros detallados de vuelos comerciales domesticos en EE.UU. |
| OpenFlights Airports | Maestro (Estatica) | Listado de aeropuertos internacionales con coordenadas y codigos IATA/ICAO |

---

## Arquitectura Conceptual

El proyecto propone una arquitectura hibrida que combina procesamiento batch y streaming, siguiendo el patron Lambda junto con un enfoque de Data Lakehouse. La arquitectura se organiza en las siguientes capas:

1.  Capa de Ingesta
    - Ingesta en tiempo real: Consumo de la API de OpenSky mediante un productor que publica los eventos en un sistema de mensajeria.
    - Ingesta batch: Descarga programada de archivos CSV del BTS mediante un orquestador de flujos de trabajo.

2.  Capa de Almacenamiento
    - Data Lakehouse con zonas Bronze (datos crudos), Silver (datos depurados y validados) y Gold (datos modelados para analisis).
    - Formato de tabla abierto que soporte transaccionalidad y actualizaciones incrementales.

3.  Capa de Procesamiento
    - Procesamiento streaming: Calculo de metricas en ventanas deslizantes, deteccion de anomalias y generacion de alertas en tiempo real.
    - Procesamiento batch: Limpieza, transformacion y construccion de un modelo analitico en estrella para consultas historicas.

4.  Capa de Consumo (Serving Layer)
    - API REST para consultar el estado de vuelos, alertas activas y metricas agregadas.
    - Dashboard ejecutivo con indicadores clave de rendimiento (KPIs).
    - Mapa interactivo para visualizar la posicion de vuelos en tiempo real con codificacion de colores segun su nivel de retraso.

---

## Tecnologias Consideradas

| Capa | Tecnologias Propuestas |
|------|------------------------|
| Ingesta Streaming | Apache Kafka / Redpanda |
| Ingesta Batch | Apache Airflow / Prefect |
| Almacenamiento | Delta Lake / Apache Iceberg sobre S3 o GCS |
| Procesamiento Streaming | Spark Structured Streaming / Apache Flink |
| Procesamiento Batch | Apache Spark / AWS Glue |
| Transformacion (ELT) | dbt |
| API | FastAPI / Flask |
| Visualizacion | Power BI / Looker Studio / Kepler.gl |
| CI/CD | GitHub Actions / GitLab CI |
| Monitoreo | Prometheus + Grafana / AWS CloudWatch |
| Lenguajes | Python, SQL, PySpark |

---

## Equipo

| Rol | Nombre | Email EAFIT | Email Gmail |
|-----|--------|-------------|-------------|
| Arquitecto de Datos / Lider Tecnico | Agustin Figueroa Sierra | afigueroas@eafit.edu.co | figuesicsi@gmail.com |
| Ingeniero de Datos - Streaming | Gabriela Lucia Martinez Mercado | glmartinem@eafit.edu.co | gabymartinez12319@gmail.com |
| Ingeniero de Datos - Batch | Juan Carlos Muñoz Trejos | jcmunozt@eafit.edu.co | jcarlosmt00@gmail.com |
| Responsable de Gobernanza y Calidad | Juan Simon Ospina Martinez | jsospinam@eafit.edu.co | juansimonreal@gmail.com |

---

## Estado Actual del Proyecto

El proyecto se encuentra en la fase inicial (Sprint 0). Se ha completado el documento preliminar que incluye la definicion del problema, la identificacion de fuentes de datos, la propuesta de arquitectura y la planificacion de sprints. Los siguientes pasos inmediatos son:

1.  Resolucion de dudas con el equipo docente.
2.  Creacion del repositorio Git y configuracion inicial.
3.  Seleccion definitiva del proveedor de nube y configuracion de cuentas.
4.  Inicio de la fase de descubrimiento y perfilamiento de datos (Fase 2).
5.  Elaboracion del primer prototipo de ingesta desde la API de OpenSky.

---

## Licencia

Este proyecto se desarrolla con fines academicos. Todos los derechos reservados.

---

## Contacto

Para cualquier duda o sugerencia, por favor contacte a los miembros del equipo a traves de sus correos electronicos.
