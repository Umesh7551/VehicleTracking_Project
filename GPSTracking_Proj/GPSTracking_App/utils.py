import requests
from django.http import JsonResponse

from .models import Tracker_data


def send_tracker_data_to_api(request):
    # Retrieve tracker data with status '01'
    tracker_data = Tracker_data.objects.filter(status='01')

    # Prepare data to send to the API endpoint
    payload = {
        "authkey": "cdb92fa3-edd2-5df2-9d74-8db76d31e8f8",
        "vendor": "gps_vendor_name",
        "version": "2.0",
        "data": []
    }
    for data in tracker_data:
        payload['data'].append({
            "vehiclename": data.car_id,
            "location": {
                "latitude": data.latitude,
                "longitude": data.longitude,
                "speed": data.speed,
                "accuracy": data.accuracy,
                # "timestamp": data.timestamp,
                "panic": data.panic,
                # "rfid": data.rfid,
                "ignition": data.ignition
            }
        })

    # Send data to the API endpoint
    response = requests.post("http://vru.verayu.io/lib/process_location_update_tp.php", json=payload)

    if response.status_code == 200:
        # Update status to '00' for the sent data
        tracker_data.update(status='00')
        return JsonResponse({"message": "Data sent and status updated successfully"}, status=200)
    else:
        return JsonResponse({"error": "Failed to send data to API"}, status=response.status_code)
