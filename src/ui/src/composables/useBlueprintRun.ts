import { computed, readonly, Ref, ref, unref } from "vue";
import { useWriterTracking } from "./useWriterTracking";
import type { BuilderManager, Core } from "@/writerTypes";
import { inject } from "vue";
import injectionKeys from "@/injectionKeys";

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
	wf: Core,
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
			branchId
				? new CustomEvent("wf-run-blueprint-branch", {
						detail: {
							callback,
							handler: "run_blueprint_branch",
							payload: { branch_id: branchId },
						},
					})
				: new CustomEvent("wf-run-blueprint", {
						detail: {
							callback,
							handler: "run_blueprint_by_id",
							payload: { blueprint_id: blueprintComponentId },
						},
					}),
			null,
			true,
		).catch((err) => {
			tracking.track("blueprints_run_failed", { error: String(err) });
			rej(err);
		});
	});
}

function stopBlueprintRun(wf: Core, runId: string) {
	return new Promise<void>((res, rej) => {
		const tracking = useWriterTracking(wf);
		tracking.track("blueprints_run_stopped");

		wf.forwardEvent(
			new CustomEvent("wf-stop-blueprint", {
				detail: {
					handler: "stop_blueprint_run",
					payload: { run_id: runId },
				},
			}),
			null,
			true,
		)
			.then(() => res())
			.catch((err) => {
				tracking.track("blueprints_run_stop_failed", {
					error: String(err),
				});
				rej(err);
			});
	});
}

export function useBlueprintRun(
	wf: Core,
	wfbm: BuilderManager,
	blueprintComponentId: string | Ref<string>,
) {
	const isRunning = ref(false);
	const socketTimeout = inject(injectionKeys.socketTimeout);

	async function run(branchId?: string) {
		if (isRunning.value) return;
		isRunning.value = true;
		if (socketTimeout) socketTimeout.prevent.value = true;
		try {
			await runBlueprint(wf, unref(blueprintComponentId), branchId);
		} finally {
			isRunning.value = false;
			if (socketTimeout) socketTimeout.prevent.value = false;
		}
	}

	async function stop() {
		const activeRunId = wfbm.activeBlueprintRunId.value;
		if (!activeRunId) return;
		await stopBlueprintRun(wf, activeRunId);
	}

	return { isRunning: readonly(isRunning), run, stop };
}

export type BlueprintsRunListItem = { blueprintId: string; branchId: string };
type MaybeRef<T> = T | Ref<T>;

export function useBlueprintsRun(
	wf: Core,
	blueprintComponentIds: MaybeRef<BlueprintsRunListItem[]>,
) {
	const runningBlueprintIds = ref<string[]>([]);
	const socketTimeout = inject(injectionKeys.socketTimeout);

	async function handleRunBlueprint({
		blueprintId,
		branchId,
	}: BlueprintsRunListItem) {
		if (runningBlueprintIds.value.includes(blueprintId)) return;

		try {
			if (socketTimeout) socketTimeout.prevent.value = true;
			runningBlueprintIds.value = [
				blueprintId,
				...runningBlueprintIds.value,
			];
			await runBlueprint(wf, blueprintId, branchId);
		} finally {
			runningBlueprintIds.value = runningBlueprintIds.value.filter(
				(id) => id !== blueprintId,
			);
			if (socketTimeout) socketTimeout.prevent.value = false;
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
