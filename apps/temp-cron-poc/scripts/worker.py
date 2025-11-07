import asyncio

from common import TEMPORAL_SERVER_URL
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import RunScheduledBranchWorkflow, run_scheduled_branch


async def main():
    client = await Client.connect(TEMPORAL_SERVER_URL)
    worker = Worker(
        client,
        task_queue="scheduled-blueprints",
        workflows=[RunScheduledBranchWorkflow],
        activities=[run_scheduled_branch],
    )
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())