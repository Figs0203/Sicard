# Evidencia 10 - Deploy workflow validado en modo seguro

**Fecha:** 2026-08-25  
**Punto del plan:** `G2. deploy.sh`

## Comando ejecutado en Cloud Shell

```bash
bash infrastructure/scripts/deploy.sh \
  --project-id flighttracker-505314 \
  --skip-api-build
```

## Resultado validado

El script completó correctamente:

- validación de cuenta activa de `gcloud`
- empaquetado de funciones Terraform-managed
- carga de artefactos a `gs://flighttracker-function-sources`
- `terraform init`
- `terraform validate`
- `terraform plan`

También dejó guardado el plan en:

```text
/home/jsospinam/Sicard/.artifacts/tfplan.dev
```

## Drift detectado por el plan

El plan no quedó limpio. Terraform propuso **3 cambios**:

1. `split_and_publish_bts`
   - `retry_policy`: `DO_NOT_RETRY` -> `RETRY_POLICY_RETRY`
   - memoria: `512M` -> `512Mi`
2. `validate_and_persist_bts`
   - `retry_policy`: `DO_NOT_RETRY` -> `RETRY_POLICY_RETRY`
   - `trigger_region`: `us-central1` -> `us-east1`
3. `validate_and_store_bts`
   - agrega `description`
   - `max_instance_count`: `100` -> `10`

## Interpretación

El script de deploy **sí funciona** como workflow reproducible de Sprint 1, pero también confirma que:

- Terraform todavía tiene drift
- **no** se debe correr `terraform apply` todavía
- el cambio más sensible sigue siendo `validate_and_persist_bts` intentando mover `trigger_region` de `us-central1` a `us-east1`

## Estado

- `deploy.sh`: **completado**
- `terraform plan` limpio: **pendiente**
- `terraform apply` seguro: **pendiente**
