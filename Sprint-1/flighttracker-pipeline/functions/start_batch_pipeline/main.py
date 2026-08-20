import functions_framework
from google.cloud import dataproc_v1
import os
import datetime

PROJECT_ID = os.environ.get('GCP_PROJECT_ID', 'flighttracker-505314')
REGION = os.environ.get('GCP_REGION', 'us-east1')
JOB_URI = "gs://flighttracker-scripts/bts_etl.py"
ZONE = "us-east1-c"

@functions_framework.http
def start_batch_pipeline(request):
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    cluster_name = f"bts-prod-{timestamp}"
    print(f"🚀 Starting orchestration for cluster: {cluster_name}")

    cluster_client = dataproc_v1.ClusterControllerClient(
        client_options={"api_endpoint": f"{REGION}-dataproc.googleapis.com"}
    )
    job_client = dataproc_v1.JobControllerClient(
        client_options={"api_endpoint": f"{REGION}-dataproc.googleapis.com"}
    )

    try:
        # Clúster de un solo nodo, sin workers secundarios, disco de 30 GB
        cluster = {
            "cluster_name": cluster_name,
            "config": {
                "master_config": {
                    "machine_type_uri": "e2-standard-2",
                    "num_instances": 1,
                    "disk_config": {
                        "boot_disk_type": "pd-standard",
                        "boot_disk_size_gb": 30
                    }
                },
                "software_config": {
                    "image_version": "2.0-debian10"
                },
                "gce_cluster_config": {
                    "zone_uri": ZONE
                },
                "lifecycle_config": {
                    "idle_delete_ttl": "600s"
                }
            },
            "labels": {"job": "bts-etl", "environment": "production"}
        }

        print(f"⏳ Creating cluster {cluster_name}...")
        create_operation = cluster_client.create_cluster(
            project_id=PROJECT_ID,
            region=REGION,
            cluster=cluster
        )
        create_operation.result()
        print(f"✅ Cluster {cluster_name} created.")

        # Enviar el trabajo de Spark
        job = {
            "placement": {"cluster_name": cluster_name},
            "pyspark_job": {"main_python_file_uri": JOB_URI}
        }

        print(f"⏳ Submitting job to {cluster_name}...")
        submit_response = job_client.submit_job(
            project_id=PROJECT_ID,
            region=REGION,
            job=job
        )
        job_id = submit_response.reference.job_id
        print(f"✅ Job submitted successfully! Job ID: {job_id}")

        return (f"Success: Job {job_id} submitted on cluster {cluster_name}. "
                f"Cluster will auto-terminate.", 200)

    except Exception as e:
        error_msg = f"❌ Orchestration failed: {str(e)}"
        print(error_msg)
        return error_msg, 500
