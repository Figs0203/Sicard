# FlightTracker - Plataforma de Monitoreo y Análisis Predictivo de Tráfico Aéreo

---

## Descripcion del Proyecto

**FlightTracker** es una plataforma DataOps para el monitoreo y analisis predictivo del trafico aereo. Integra datos en tiempo real (OpenSky Network) con datos historicos masivos (BTS) para proporcionar una vision unificada de la operacion aerea. El proyecto se desarrolla como parte del curso **Proyecto Ingenieria de Datos (SI4002)** de la Universidad EAFIT.

El sistema resuelve los siguientes desafios del sector de la aviacion comercial:
- Monitoreo en tiempo real: Visualizacion de la ubicacion y estado de vuelos activos.
- Analisis historico: Identificacion de patrones de retraso por aerolinea, ruta y causas.
- Alertas tempranas: Notificacion automatica ante indicios de retrasos o desviaciones.
- Consumo de datos: API REST y dashboards para diferentes stakeholders (aerolineas, aeropuertos, autoridades).

---

## Arquitectura Implementada (Sprint 1)

El **Sprint 1 (Walking Skeleton)** ha desplegado una arquitectura serverless en **Google Cloud Platform (GCP)** con los siguientes componentes:

| Capa | Tecnologia | Proposito |
|------|------------|-----------|
| **Ingesta** | Cloud Functions (2a gen) + Eventarc + Pub/Sub | Recibe archivos CSV, los divide en filas y publica en Pub/Sub |
| **Procesamiento Batch** | Dataproc (Apache Spark) | Transforma datos RAW -> Silver (Parquet) con limpieza y validacion |
| **Orquestacion** | Cloud Scheduler + Cloud Function | Ejecuta el pipeline batch diariamente a las 8:00 AM (Colombia) |
| **Persistencia Operacional** | Firestore (temporal) | Almacena vuelos con `flight_id` deterministico (idempotencia) |
| **Base Transaccional** | Cloud SQL (PostgreSQL) | Tablas maestras de aerolineas y aeropuertos (OpenFlights) |
| **API REST** | Cloud Run (FastAPI) | Endpoints para consultar vuelos (filtros por aerolinea, fecha) |
| **Infraestructura** | Terraform | Gestion de recursos como codigo (reproducible y versionado) |

### Flujo de Datos (Batch)

```
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
    │
    ▼
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

---

## Datos Gestionados

| Fuente | Tipo | Naturaleza | Volumen | Estado |
|:---|:---|:---|:---|:---:|
| **BTS On-Time Performance** | Historica | Batch (CSV) | 545,003 registros (Enero 2026) | Procesado en Silver |
| **OpenFlights** | Maestra | Batch | 14,110 aeropuertos, 6,162 aerolineas | Cargado en PostgreSQL |
| **OpenSky Network** | Telemetria | Streaming (API) | Snapshot de vuelos activos | Productor listo, consumidor pendiente (Sprint 2) |

---

## Logros del Sprint 1

- Pipeline batch funcional end-to-end con datos reales.
- Idempotencia garantizada (`flight_id` como hash de clave de negocio).
- Capa Silver generada en Parquet (55.78 MiB) actualizada diariamente.
- API REST operativa con `flight_id`, `carrier`, `flight_number`.
- Infraestructura gestionada con Terraform.
- ADR (Architecture Decision Record) documentando la migracion a Cassandra.
- Orquestacion automatizada diaria (Cloud Scheduler + Cloud Function).

---

## Metricas de Calidad de Datos (DQS)

En el perfilamiento inicial (Fase 2) se evaluaron 5 dimensiones:

| Dimension | Peso | OpenFlights | OpenSky | BTS |
|-----------|------|-------------|---------|-----|
| Completitud | 30% | 0.98 | 0.92 | 0.99 |
| Validez | 25% | 0.96 | 0.91 | 0.97 |
| Unicidad | 20% | 0.95 | 0.95 | 0.98 |
| Consistencia | 15% | 0.94 | 0.93 | 0.96 |
| Exactitud | 10% | 0.96 | 0.90 | 0.95 |
| **DQS Total** | | **0.9572** | **0.9248** | **0.9712** |

DQS = 0.30(Completitud) + 0.25(Validez) + 0.20(Unicidad) + 0.15(Consistencia) + 0.10(Exactitud)

---

## Estructura del Repositorio

Sicard/
├── README.md <- Este archivo
├── Sprint-0/
│ ├── Sprint0.pdf # Propuesta inicial y arquitectura conceptual
│ └── sicard.docx # Documentacion preliminar
└── Sprint-1/
├── flighttracker-pipeline/ # Codigo fuente completo del Sprint 1
│ ├── functions/ # Cloud Functions (validate, split, persist, orquestador)
│ ├── spark_jobs/ # Script de ETL (PySpark)
│ ├── api/get_flights/ # API REST (FastAPI + repositorio)
│ ├── scripts/ # Scripts auxiliares (carga de OpenFlights)
│ └── docs/ # Documentacion (ADR, guias)
├── flighttracker-terraform/ # Infraestructura como codigo
│ ├── main.tf # Recursos principales
│ ├── variables.tf # Variables de entrada
│ └── migration.tf # Migracion de estado (suscripciones)
├── FlightTracker_Perfilamiento.ipynb # Notebook de perfilamiento (Fase 2)
└── README.md # Documentacion detallada del Sprint 1

---

## Proximos Pasos (Sprint 2)

1. Migrar a **Cassandra** como capa de serving (baja latencia <500 ms).
   - Adaptador `CassandraFlightRepository` para la API.
   - Proyeccion en paralelo desde Firestore y backfill desde Silver.
2. Implementar el **consumidor de streaming** (OpenSky -> Spark Structured Streaming -> Cassandra).
3. Generar la **capa Gold** (modelo en estrella) con BigQuery o Parquet.
4. **Gobernanza avanzada**: OpenMetadata, Great Expectations, linaje de datos.
5. **DataOps**: CI/CD con GitHub Actions, Dockerizacion de funciones.
6. **Dashboards en Grafana**: Visualizacion de KPIs operacionales (puntualidad, retrasos, cancelaciones).

---

## Equipo de Trabajo

| Rol | Nombre | Email EAFIT | Email Gmail |
|-----|--------|-------------|-------------|
| Arquitecto de Datos / Lider Tecnico | Agustin Figueroa Sierra | afigueroas@eafit.edu.co | figuesicsi@gmail.com |
| Ingeniero de Datos - Streaming | Gabriela Lucia Martinez Mercado | glmartinem@eafit.edu.co | gabymartinez12319@gmail.com |
| Ingeniero de Datos - Batch | Juan Carlos Munoz Trejos | jcmunozt@eafit.edu.co | jcarlosmt00@gmail.com |
| Responsable de Gobernanza y Calidad | Juan Simon Ospina Martinez | jsospinam@eafit.edu.co | juansimonreal@gmail.com |

---

## Estado Actual del Proyecto

- [x] **Sprint 0**: Propuesta inicial, arquitectura conceptual y definicion del equipo.
- [x] **Sprint 1**: Walking Skeleton completo (ingesta, Spark, API, Terraform, orquestacion).
- [x] **Perfilamiento de datos**: Evaluacion de calidad y DQS para las 3 fuentes.
- [ ] **Sprint 2**: Migracion a Cassandra, streaming, gobernanza y dashboards.
- [ ] **Sprint Final**: DataOps, CI/CD, presentacion ejecutiva.

---

## Licencia

Este proyecto se desarrolla con fines academicos para la Universidad EAFIT. Todos los derechos reservados.
