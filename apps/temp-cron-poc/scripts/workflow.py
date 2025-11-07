from datetime import timedelta

from common import BASE_URL, JobParams
from temporalio import activity, workflow


@activity.defn(name="run_scheduled_branch")
async def run_scheduled_branch(input: JobParams) -> str:
    import requests
    response = requests.post(f"{BASE_URL}/blueprint/{input.blueprint_id}?branch_id={input.branch_id}")
    return response.text


@workflow.defn
class RunScheduledBranchWorkflow:
    @workflow.run
    async def run(self, input: JobParams) -> str:
        return await workflow.execute_activity(
            run_scheduled_branch, input, start_to_close_timeout=timedelta(minutes=60)
        )
