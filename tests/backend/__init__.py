from pathlib import Path
from writer.ss_types import InstancePath

test_app_dir = Path(__file__).resolve().parent / 'basic_test_app'
test_multiapp_dir = Path(__file__).resolve().parent / 'testmultiapp'
test_basicauth_dir = Path(__file__).resolve().parent / 'testbasicauth'
testobsoleteapp = Path(__file__).resolve().parent / 'testobsoleteapp'

def parse_instance_path(flat_instance_path: str) -> InstancePath:
    segments = [segment.split(":") for segment in flat_instance_path.split(",")]
    instance_path = [{"componentId": segment[0], "instanceNumber": int(segment[1])} for segment in segments]
    return instance_path