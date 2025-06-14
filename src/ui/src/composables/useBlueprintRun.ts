import type { generateCore } from "@/core";
import { computed, readonly, Ref, ref, unref } from "vue";
import { useWriterTracking } from "./useWriterTracking";

interface RunBlueprintResponse {
	ok: boolean;
	payload: {
		mail: {
			payload: {
				type: "info" | "error";
				title: string;
			};
		}[];
		result: {
			ok: boolean;
		};
	};
}

function runBlueprint(
	wf: ReturnType<typeof generateCore>,
	blueprintComponentId: string,
	branchId?: string,
) {
	return new Promise<void>((res, rej) => {
		const tracking = useWriterTracking(wf);
		tracking.track("blueprints_run_started");
		const startedAt = new Date().getTime();

		function callback(result: RunBlueprintResponse) {
			const hasError = result.payload?.mail?.some(
				(m) => m.payload?.type === "error",
			);
			const trackPayload = {
				durationMs: new Date().getTime() - startedAt,
			};
			if (hasError) {
				tracking.track("blueprints_run_failed", trackPayload);
			} else {
				tracking.track("blueprints_run_succeeded", trackPayload);
			}
			res(undefined);
		}

		wf.forwardEvent(
			branchId ?
			new CustomEvent(
				"wf-run-blueprint-branch", 
				{
					detail: {
						callback,
						handler: "run_blueprint_branch",
						payload: { "branch_id": branchId }
					},
				}
			) :
			new CustomEvent(
				"wf-run-blueprint", 
				{
					detail: {
						callback,
						handler: "run_blueprint_by_id",
						payload: { blueprint_id: blueprintComponentId },
					},
				}
			),
			null,
			true,
		).catch((err) => {
			tracking.track("blueprints_run_failed", { error: String(err) });
			rej(err);
		});
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
