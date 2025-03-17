import type { generateCore } from "@/core";
import { computed, readonly, Ref, ref, unref } from "vue";

function runWorkflow(
	wf: ReturnType<typeof generateCore>,
	workflowComponentId: string,
	branchId?: string,
) {
	return new Promise((res, rej) => {
		wf.forwardEvent(
			new CustomEvent("wf-builtin-run", {
				detail: {
					callback: res,
					handler: branchId
						? `$runWorkflowTriggerBranchById_${branchId}`
						: `$runWorkflowById_${workflowComponentId}`,
				},
			}),
			null,
			true,
		).catch(rej);
	});
}

export function useWorkflowRun(
	wf: ReturnType<typeof generateCore>,
	workflowComponentId: string | Ref<string>,
) {
	const isRunning = ref(false);

	async function run(branchId?: string) {
		if (isRunning.value) return;
		isRunning.value = true;
		try {
			await runWorkflow(wf, unref(workflowComponentId), branchId);
		} finally {
			isRunning.value = false;
		}
	}

	return { isRunning: readonly(isRunning), run };
}

export type WorkflowsRunListItem = { workflowId: string; branchId: string };
type MaybeRef<T> = T | Ref<T>;

export function useWorkflowsRun(
	wf: ReturnType<typeof generateCore>,
	workflowComponentIds: MaybeRef<WorkflowsRunListItem[]>,
) {
	const runningWorkflowIds = ref<string[]>([]);

	async function handleRunWorkflow({
		workflowId,
		branchId,
	}: WorkflowsRunListItem) {
		if (runningWorkflowIds.value.includes(workflowId)) return;

		try {
			runningWorkflowIds.value = [
				workflowId,
				...runningWorkflowIds.value,
			];
			await runWorkflow(wf, workflowId, branchId);
		} finally {
			runningWorkflowIds.value = runningWorkflowIds.value.filter(
				(id) => id !== workflowId,
			);
		}
	}
	async function run() {
		await Promise.all(unref(workflowComponentIds).map(handleRunWorkflow));
	}

	const isRunning = computed(() => runningWorkflowIds.value.length > 0);

	return {
		run,
		isRunning,
		runningWorkflowIds: readonly(runningWorkflowIds),
	};
}
