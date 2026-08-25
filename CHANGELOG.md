# Changelog

## Sprint 1 Workspace Restructure - 2026-08-24

- Reorganized the repository into `docs`, `infrastructure`, `pipelines`, `backend`, `database`, `tests`, `docker`, and `.github`.
- Moved Terraform to `infrastructure/terraform`.
- Moved the BTS ETL job to `pipelines/batch/spark_jobs`.
- Moved the API and Cloud Functions to `backend`.
- Moved database seed utilities to `database/scripts`.
- Moved ADRs and Sprint documentation to `docs`.
