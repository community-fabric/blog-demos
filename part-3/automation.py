from time import sleep
from models import Event
from ipf_api_client import IPFClient
from config import settings


def do_long_process(event: Event):
    print("Sleep 5 seconds")
    sleep(5)
    print(event.__dict__)


def ipf_webhook(event: Event):
    if event.type != 'intent-verification' or event.action != 'calculate' or event.status != 'completed':
        intent_completed(event)
    elif event.type != 'snapshot' or event.action != 'discover' or event.status != 'completed':
        discover_completed(event)


def intent_completed(event: Event):
    print(event.__dict__)


def discover_completed(event: Event):
    ipf = IPFClient(settings.ipf_instance, token=settings.ipf_token, verify=False, snapshot_id=event.snapshot.id)
    devices = ipf.inventory.devices.all()
    print(f"Total devices in Snapshot are: {len(devices)}")

