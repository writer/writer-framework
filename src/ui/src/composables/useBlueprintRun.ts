import type { generateCore } from "@/core";
import { computed, readonly, Ref, ref, unref } from "vue";

function runBlueprint(
	wf: ReturnType<typeof generateCore>,
	blueprintComponentId: string,
	branchId?: string,
) {
	return new Promise((res, rej) => {
		wf.forwardEvent(
			new CustomEvent("wf-builtin-run", {
				detail: {
					callback: res,
					handler: branchId
						? `$runBlueprintTriggerBranchById_${branchId}`
						: `$runBlueprintById_${blueprintComponentId}`,
				},
			}),
			null,
			true,
		).catch(rej);
	});
}

export function useBlueprintRun(
	wf: ReturnType<typeof generateCore>,
	blueprintComponentId: string | Ref<string>,
) {
	const isRunning = ref(false);

	async function run(branchId?: string) {
		if (isRunning.value) return;
		isRunning.value = true;
		try {
			await runBlueprint(wf, unref(blueprintComponentId), branchId);
		} finally {
			isRunning.value = false;
		}
	}

	return { isRunning: readonly(isRunning), run };
}

export type BlueprintsRunListItem = { blueprintId: string; branchId: string };
type MaybeRef<T> = T | Ref<T>;

export function useBlueprintsRun(
	wf: ReturnType<typeof generateCore>,
	blueprintComponentIds: MaybeRef<BlueprintsRunListItem[]>,
) {
	const runningBlueprintIds = ref<string[]>([]);

	async function handleRunBlueprint({
		blueprintId,
		branchId,
	}: BlueprintsRunListItem) {
		if (runningBlueprintIds.value.includes(blueprintId)) return;

		try {
			runningBlueprintIds.value = [
				blueprintId,
				...runningBlueprintIds.value,
			];
			await runBlueprint(wf, blueprintId, branchId);
		} finally {
			runningBlueprintIds.value = runningBlueprintIds.value.filter(
				(id) => id !== blueprintId,
			);
		}
	}
	async function run() {
		await Promise.all(unref(blueprintComponentIds).map(handleRunBlueprint));
	}

	const isRunning = computed(() => runningBlueprintIds.value.length > 0);

	return {
		run,
		isRunning,
		runningBlueprintIds: readonly(runningBlueprintIds),
	};
}
