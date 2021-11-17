from time import sleep
from models import Event
from ipf_api_client import IPFClient
from config import settings


def do_long_process(event: Event):
    print("Sleep 5 seconds")
    sleep(5)
    print(event.__dict__)


def ipf_webhook(event: Event):
    if event.test:
        print("Test event")
    elif event.status == 'completed' and (event.snapshot or event.snapshot_id):
        if event.type == 'intent-verification' and event.action == 'calculate':
            intent_completed(event)
        elif event.type == 'snapshot' and event.action == 'discover':
            discover_completed(event)


def intent_completed(event: Event):
    print(f"Intent completed for snapshot {event.snapshot_id}")


def discover_completed(event: Event):
    ipf = IPFClient(settings.ipf_instance, token=settings.ipf_token, verify=False, snapshot_id=event.snapshot.id)
    devices = ipf.inventory.devices.all()
    print(f"Total devices in Snapshot are: {len(devices)}")
