import asyncio

import requests
from common import BASE_URL, TEMPORAL_SERVER_URL, JobParams
from temporalio.client import Client, Schedule, ScheduleActionStartWorkflow, ScheduleSpec
from worker import RunScheduledBranchWorkflow

DEMO_BLUEPRINT_ID = "v6zuusbbtjlghecm"

async def deploy(temporal_client: Client, blueprint_id: str):
    cron_triggers = requests.get(f"{BASE_URL}/blueprint/{blueprint_id}/cron-triggers").json()
    await undeploy(temporal_client, blueprint_id)
    for cron_trigger in cron_triggers:
        schedule_id = f"cron-{blueprint_id}-{cron_trigger['id']}"
        await temporal_client.create_schedule(
            id=schedule_id,
            schedule=Schedule(
                action=ScheduleActionStartWorkflow(
                RunScheduledBranchWorkflow.run,
                JobParams(blueprint_id=blueprint_id, branch_id=cron_trigger["id"]),
                id=schedule_id,
                task_queue="scheduled-blueprints",
            ),
                spec=ScheduleSpec(
                    cron_expressions=[cron_trigger["cron_expression"]],
                    time_zone_name=cron_trigger["timezone"],
                ),
            )
        )
        print(f"[CREATED]: {schedule_id}")

async def undeploy(temporal_client: Client, blueprint_id: str):
    schedules = await temporal_client.list_schedules()
    async for schedule in schedules:
        if schedule.id.startswith(f"cron-{blueprint_id}-"):
            handle = temporal_client.get_schedule_handle(schedule.id)
            await handle.delete()
            print(f"[DELETED]: {schedule.id}")

async def main():
    temporal_client = await Client.connect(TEMPORAL_SERVER_URL)
    print("[CONNECTED]: Connected to temporal server!")
    await deploy(temporal_client, DEMO_BLUEPRINT_ID)
    print("[DEPLOYED]: Blueprint schedules deployed!")
    

if __name__ == "__main__":
    asyncio.run(main())