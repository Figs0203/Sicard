# FlightTracker - Plataforma de Monitoreo y Análisis Predictivo de Tráfico Aéreo

---

## 📋 Descripción del Proyecto

**FlightTracker** es una plataforma integral de monitoreo y análisis de tráfico aéreo que integra datos en tiempo real con datos históricos para proporcionar una visión unificada de la operación aérea. El proyecto se desarrolla como parte del curso **Proyecto Ingeniería de Datos (SI4002)** de la Universidad EAFIT.

El sistema está diseñado para resolver los siguientes desafíos del sector de la aviación comercial:
- **Monitoreo en tiempo real**: Visualización de la ubicación y estado de vuelos activos.
- **Análisis histórico**: Identificación de patrones de retraso por aerolínea, ruta y causas específicas.
- **Alertas tempranas**: Notificación automática ante indicios de retrasos o desviaciones.
- **Consumo de datos**: API REST y dashboards para diferentes stakeholders.

---

## 📁 Estructura del Repositorio

El repositorio está organizado por **Sprints** de trabajo:

```
Sicard/
├── README.md                                # Documentación general del proyecto
├── Sprint-0/
│   ├── Sprint0.pdf                          # Propuesta y arquitectura del proyecto
│   └── sicard.docx                          # Documentación preliminar
└── Sprint-1/
    ├── FlightTracker_Perfilamiento.ipynb    # Notebook ejecutable principal de perfilamiento
    ├── README.md                            # Documentación detallada del Sprint 1
    └── data/
        └── bts_flights.csv                  # Dataset histórico real (Enero 2026 - 544,003 registros)
```

---

## 📊 Fuentes de Datos Evaluadas (Sprint 1)

| Fuente | Tipo | Naturaleza | Volumen Procesado | DQS | Estado de Calidad |
|:---|:---|:---|:---|:---:|:---:|
| **OpenFlights** | Maestra | Batch / Estática | 14,110 aeropuertos, 6,162 aerolíneas, 67,663 rutas | **0.9572** | 🟢 EXCELENTE |
| **OpenSky Network** | Telemetría | Streaming / Tiempo Real | Snapshot API REST (vuelos activos) | **0.9248** | 🟢 EXCELENTE |
| **BTS On-Time Performance** | Histórica | Batch Histórico | **544,003 registros (Enero 2026)** | **0.9712** | 🟢 EXCELENTE |

---

## 🏆 Resumen de Calidad y Data Quality Score (DQS)

En el **Sprint 1** se realizó el **descubrimiento y perfilamiento de calidad de datos** evaluando 5 dimensiones clave:
1. **Completitud** (30%): % de valores no nulos por columna.
2. **Validez** (25%): Cumplimiento de formatos (IATA/ICAO, ISO) y rangos geográficos/físicos.
3. **Unicidad** (20%): Ausencia de duplicados exactos y por clave primaria compuesta.
4. **Consistencia** (15%): Uniformidad categórica y estandarización de formatos de fecha.
5. **Exactitud** (10%): Ausencia de outliers no plausibles y valores físicamente imposibles.

$$\text{DQS} = 0.30(\text{Completitud}) + 0.25(\text{Validez}) + 0.20(\text{Unicidad}) + 0.15(\text{Consistencia}) + 0.10(\text{Exactitud})$$

---

## 🔍 Principales Hallazgos de Calidad

* **OpenFlights**: Uso de `\N` para datos nulos en IATA/ICAO/Alias, e inclusión de estaciones de tren/ferrys (`type != 'airport'`).
* **OpenSky Network**: Latitud y longitud son nulas cuando el avión está en pista (`on_ground == True`), lo cual es comportamiento normal de transpondedores ADS-B.
* **BTS On-Time Performance**: Nulos semánticos en tiempos de retraso para los **25,635 vuelos cancelados** en Enero 2026 (~4.71% de la operación).

---

## 🛠️ Plan de Acción para Pipelines ETL (Sprint 2)

* **OpenFlights**: Reemplazo sintáctico de `\N` por `NULL`, normalización de nombres de países y filtrado por `type == 'airport'`.
* **OpenSky**: Separación de flujos (aviones en pista vs. en vuelo) y descarte de lecturas anómalas (`velocity.between(0, 1500)`).
* **BTS**: Casteo de `FL_DATE` a fecha pura, asignación de bandera `IS_CANCELLED` y deduplicación por clave primaria compuesta.

---

## 🏗️ Arquitectura Conceptual

El proyecto propone una arquitectura híbrida que combina procesamiento batch y streaming (Patrón Lambda / Lakehouse):
1. **Capa de Ingesta**: Productores streaming para OpenSky Network y orquestación batch (Airflow/Prefect) para BTS.
2. **Capa de Almacenamiento**: Data Lakehouse con zonas Bronze, Silver y Gold en Delta Lake / Apache Iceberg.
3. **Capa de Procesamiento**: Spark Structured Streaming y PySpark para transformaciones y analítica.
4. **Capa de Consumo**: API REST con FastAPI, dashboard ejecutivo y mapa interactivo con seguimiento en tiempo real.

---

## 👥 Equipo de Trabajo

| Rol | Nombre | Email EAFIT | Email Gmail |
|-----|--------|-------------|-------------|
| Arquitecto de Datos / Líder Técnico | Agustín Figueroa Sierra | afigueroas@eafit.edu.co | figuesicsi@gmail.com |
| Ingeniero de Datos - Streaming | Gabriela Lucía Martínez Mercado | glmartinem@eafit.edu.co | gabymartinez12319@gmail.com |
| Ingeniero de Datos - Batch | Juan Carlos Muñoz Trejos | jcmunozt@eafit.edu.co | jcarlosmt00@gmail.com |
| Responsable de Gobernanza y Calidad | Juan Simón Ospina Martínez | jsospinam@eafit.edu.co | juansimonreal@gmail.com |

---

## 📅 Estado Actual del Proyecto

- [x] **Sprint 0**: Propuesta inicial, arquitectura conceptual y definición del equipo.
- [x] **Sprint 1**: Descubrimiento, perfilamiento de datos, cálculo de DQS y desarrollo del notebook de perfilamiento (`Sprint-1/FlightTracker_Perfilamiento.ipynb`).
- [ ] **Sprint 2**: Construcción de pipelines de ingesta (Bronze/Silver) y reglas de validación en producción.

---

## 📄 Licencia

Este proyecto se desarrolla con fines académicos para la Universidad EAFIT. Todos los derechos reservados.
