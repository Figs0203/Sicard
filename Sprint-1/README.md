# FlightTracker — Sprint 1: Descubrimiento y Perfilamiento de Datos

## ¿Qué es esto?
Notebook de perfilamiento de calidad de datos para el proyecto **FlightTracker** de la materia de Ingeniería de Datos. Cubre las tres fuentes del proyecto y genera un reporte completo con Data Quality Score (DQS).

## Fuentes de datos
| Fuente | Tipo | Acceso |
|--------|------|--------|
| **OpenFlights** | Maestra (aeropuertos, aerolíneas, rutas) | Automático (CSV público en GitHub) |
| **OpenSky Network** | Streaming (vuelos en tiempo real) | Automático (API REST pública) |
| **BTS** | Batch histórico (puntualidad EE.UU.) | Manual o sintético (ver abajo) |

## Cómo ejecutar

### Opción A: Google Colab (recomendado, sin instalaciones)
1. Abre [Google Colab](https://colab.research.google.com)
2. Sube el archivo `FlightTracker_Perfilamiento.ipynb`
3. Haz clic en **Runtime → Run all**

### Opción B: Jupyter Local
```bash
pip install jupyter pandas matplotlib seaborn requests openpyxl
jupyter notebook FlightTracker_Perfilamiento.ipynb
```

## Datos de BTS (opcional)
Para usar datos reales de BTS en vez de los sintéticos:
1. Ve a: https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGJ
2. Selecciona Año: 2024, Mes: Enero
3. Descarga el CSV y renómbralo `bts_flights.csv`
4. Ponlo en la carpeta `data/`

Sin este paso, el notebook genera datos sintéticos realistas automáticamente.

## Entregable
El notebook genera automáticamente:
- Perfilamiento en 5 dimensiones (completitud, unicidad, validez, consistencia, exactitud)
- Data Quality Score (DQS) ponderado por fuente
- Visualizaciones EDA
- Tabla resumen de hallazgos y retos de calidad
