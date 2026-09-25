
import os
import io
import csv
import json
import time
import datetime
import requests

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
PRODUCT_ID = os.environ.get("PRODUCT_ID", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

REST_URL = f"{SUPABASE_URL}/rest/v1"
SB_HEADERS = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
}

SOURCE_BUCKET = "uploads"
RESULT_BUCKET = "results"


def download_file(bucket, file_path):
    if file_path.startswith(bucket + "/"):
        file_path = file_path[len(bucket) + 1:]
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{file_path}"
    resp = requests.get(url, headers={"Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "apikey": SUPABASE_SERVICE_KEY})
    resp.raise_for_status()
    return resp.content


def upload_file(bucket, file_path, data, content_type="text/csv"):
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{file_path}"
    resp = requests.post(url, headers={**SB_HEADERS, "Content-Type": content_type, "x-upsert": "true"}, data=data)
    resp.raise_for_status()
    return resp


def fetch_pending_jobs():
    url = f"{REST_URL}/jobs?status=eq.pending&job_type=eq.process_upload&product_id=eq.{PRODUCT_ID}&select=*"
    resp = requests.get(url, headers=SB_HEADERS)
    resp.raise_for_status()
    return resp.json()


def update_job(job_id, payload):
    url = f"{REST_URL}/jobs?id=eq.{job_id}"
    resp = requests.patch(url, headers={**SB_HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"}, json=payload)
    resp.raise_for_status()
    return resp


def insert_notification(product_id, customer_id, title, body, notif_type):
    try:
        url = f"{REST_URL}/notifications"
        payload = {
            "product_id": product_id,
            "customer_id": customer_id,
            "title": title,
            "body": body,
            "type": notif_type,
            "read": False,
        }
        requests.post(url, headers={**SB_HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"}, json=payload)
    except Exception as e:
        print(f"notification insert failed: {e}")


def process_job(job):
    job_id = job["id"]
    customer_id = job["customer_id"]
    input_file_path = job["input_file_path"]
    print(f"Processing job {job_id} file {input_file_path}")

    file_bytes = download_file(SOURCE_BUCKET, input_file_path)

    import processor
    records = processor.process_file(file_bytes)

    inserted = 0
    for r in records:
        try:
            requests.post(
                REST_URL + "/records",
                headers={**SB_HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
                json={
                    "product_id": PRODUCT_ID,
                    "customer_id": customer_id,
                    "title": r["title"],
                    "status": r["status"],
                    "details": r["details"],
                    "source_file_path": job["input_file_path"],
                    "due_date": r.get("due_date"),
                },
            )
            inserted += 1
        except Exception as e:
            print(f"record insert failed: {e}")

    result_rows = [{"title": r["title"], "status": r["status"], "details": r["details"]} for r in records]
    buf = io.StringIO()
    if result_rows:
        writer = csv.DictWriter(buf, fieldnames=["title", "status", "details"])
        writer.writeheader()
        for row in result_rows:
            out = dict(row)
            out["details"] = json.dumps(row["details"])
            writer.writerow(out)
    result_bytes = buf.getvalue().encode("utf-8")

    base = os.path.basename(input_file_path)
    result_path = f"{job_id}/{base}.results.csv"
    upload_file(RESULT_BUCKET, result_path, result_bytes, content_type="text/csv")

    now = datetime.datetime.utcnow().isoformat()
    update_job(job_id, {
        "status": "completed",
        "output_file_path": f"{RESULT_BUCKET}/{result_path}",
        "result_summary": {"records_created": inserted, "total_records": len(records)},
        "completed_at": now,
    })

    insert_notification(PRODUCT_ID, customer_id, "Processing complete",
                        "Your upload has been processed successfully.", "success")
    print(f"Job {job_id} completed with {inserted} records")


def fail_job(job, error):
    job_id = job["id"]
    customer_id = job["customer_id"]
    now = datetime.datetime.utcnow().isoformat()
    try:
        update_job(job_id, {
            "status": "failed",
            "result_summary": {"error": str(error)},
            "completed_at": now,
        })
    except Exception as e:
        print(f"failed to mark job failed: {e}")
    insert_notification(PRODUCT_ID, customer_id, "Processing failed",
                        "There was an error processing your upload.", "error")
    print(f"Job {job_id} failed: {error}")


def poll():
    while True:
        try:
            jobs = fetch_pending_jobs()
            for job in jobs:
                try:
                    process_job(job)
                except Exception as e:
                    fail_job(job, e)
        except Exception as e:
            print(f"poll error: {e}")
        time.sleep(10)


if __name__ == "__main__":
    print("Poller started")
    poll()
