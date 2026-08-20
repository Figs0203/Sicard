import functions_framework
from google.cloud import firestore
import json
from datetime import datetime, timezone
import base64
import hashlib


def _normalise_date(value):
    value = str(value or "").strip()
    for date_format in ("%Y-%m-%d", "%m/%d/%Y %I:%M:%S %p", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, date_format).date().isoformat()
        except ValueError:
            pass
    return value


def _normalise_record(row):
    carrier = str(row.get("carrier") or row.get("OP_CARRIER") or row.get("OP_UNIQUE_CARRIER") or "").strip().upper()
    flight_date = _normalise_date(row.get("flight_date") or row.get("FL_DATE"))
    origin = str(row.get("origin") or row.get("ORIGIN") or "").strip().upper()
    destination = str(row.get("destination") or row.get("DEST") or "").strip().upper()
    flight_number = str(row.get("flight_number") or row.get("OP_CARRIER_FL_NUM") or "").strip()
    departure_time = str(row.get("DEP_TIME") or "").strip()

    if not all((flight_date, carrier, flight_number, origin, destination)):
        raise ValueError("Invalid flight event: required business fields are missing")

    business_identity = "|".join(
        [flight_date, carrier, flight_number, origin, destination, departure_time]
    )
    normalised = dict(row)
    normalised.update(
        {
            "schema_version": row.get("schema_version", "flight.curated.v1"),
            "flight_id": row.get("flight_id") or hashlib.sha256(business_identity.encode("utf-8")).hexdigest(),
            "flight_date": flight_date,
            "carrier": carrier,
            "flight_number": flight_number,
            "origin": origin,
            "destination": destination,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            # Compatibility aliases while Firestore remains the temporal projection.
            "FL_DATE": flight_date,
            "OP_CARRIER": carrier,
            "OP_CARRIER_FL_NUM": flight_number,
            "ORIGIN": origin,
            "DEST": destination,
        }
    )
    return normalised


@functions_framework.cloud_event
def validate_and_persist_bts(cloud_event):
    message_data = base64.b64decode(cloud_event.data['message']['data']).decode('utf-8')
    row = json.loads(message_data)

    try:
        row = _normalise_record(row)
    except ValueError as e:
        print(f"Invalid record: {e}")
        return

    db = firestore.Client()
    # Pub/Sub and Eventarc are at-least-once; a deterministic document ID is required.
    doc_ref = db.collection('flights').document(row['flight_id'])
    doc_ref.set(row)
    print(f"Flight persisted: {row['carrier']}{row['flight_number']} ({row['flight_id']})")
