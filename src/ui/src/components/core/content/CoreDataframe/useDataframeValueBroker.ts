import { ComponentPublicInstance, computed, Ref, ShallowRef } from "vue";
import { type internal } from "arquero";
import { ARQUERO_INTERNAL_ID, UNNAMED_INDEX_COLUMN_PATTERN } from "./constants";
import { useJobs } from "./useJobs";
import { Core, InstancePath } from "@/writerTypes";
import { useComponentLinkedBlueprints } from "@/composables/useComponentBlueprints";

/**
 * Encapsulates the logic to update an Arquero table and sync it with the backend
 */
export function useDataFrameValueBroker(
	wf: Core,
	instancePath: InstancePath,
	emitterEl: Ref<HTMLElement | ComponentPublicInstance>,
	table: ShallowRef<internal.ColumnTable | null>,
) {
	const componentId = instancePath.at(-1).componentId;
	const component = computed(() => wf.getComponentById(componentId));

	type Job =
		| {
			eventType: "wf-dataframe-add";
			payload: Parameters<typeof handlerAddRow>;
		}
		| {
			eventType: "wf-dataframe-update";
			payload: Parameters<typeof handlerUpdateCell>;
		}
		| {
			eventType: "wf-dataframe-action";
			payload: Parameters<typeof handlerActionRow>;
		};

	const { push: pushJob, isBusy } = useJobs<Job>(handler);

	async function handler(job: Job) {
		switch (job.eventType) {
			case "wf-dataframe-add":
				await handlerAddRow(...job.payload);
				break;
			case "wf-dataframe-update":
				await handlerUpdateCell(...job.payload);
				break;
			case "wf-dataframe-action":
				await handlerActionRow(...job.payload);
				break;
		}
	}

	async function handlerAddRow() {
		const eventType = "wf-dataframe-add";

		const rowIndex = table.value.numRows();

		const aq = await import("arquero");

		const recordFilter = aq.escape(
			(d: Record<string, unknown>) => d[ARQUERO_INTERNAL_ID] === rowIndex,
		);

		// get previous value to format it
		const previousRecord = table.value.filter(recordFilter).object();
		if (!previousRecord) throw Error("Could not find record");

		const newRecord = getDefaultRecord(previousRecord);
		const newRow = aq.from([newRecord]);

		table.value = table.value.concat(newRow).derive({
			[ARQUERO_INTERNAL_ID]: () => aq.op.row_number(),
		});

		if (!isEventUsed(eventType)) return;

		return new Promise((res) => {
			const event = new CustomEvent(eventType, {
				detail: {
					payload: {
						record: newRecord,
						record_index: rowIndex,
					},
					callback: res,
				},
			});
			dispatchEvent(event);
		});
	}

	async function handlerActionRow(action: string, rowIndex: number) {
		const eventType = "wf-dataframe-action";
		if (!table.value) throw Error("Table is not ready");
		if (!isEventUsed(eventType)) return;

		const rowIndexBackend = rowIndex - 1; // 0-based index (arquero is based on 1-based index)

		return new Promise((res) => {
			const event = new CustomEvent(eventType, {
				detail: {
					payload: { action, record_index: rowIndexBackend },
					callback: res,
				},
			});

			dispatchEvent(event);
		});
	}

	async function handlerUpdateCell(
		columnName: string,
		rowIndex: number,
		value: unknown,
	) {
		if (!table.value) throw Error("Table is not ready");
		if (rowIndex === undefined)
			throw Error("Must specify the index to update a row");
		const eventType = "wf-dataframe-update";
		const rowIndexBackend = rowIndex - 1; // 0-based index (arquero is based on 1-based index)

		const aq = await import("arquero");

		const recordFilter = aq.escape(
			(d: Record<string, unknown>) => d[ARQUERO_INTERNAL_ID] === rowIndex,
		);

		// get previous value to format it
		const previousRecord = table.value.filter(recordFilter).object();
		if (!previousRecord) throw Error("Could not find record");
		const previousValue = previousRecord[columnName];

		const valueTyped = formatValue(previousValue, value);

		// update arquero table
		const updater = aq.escape((d: Record<string, unknown>) => {
			return d[ARQUERO_INTERNAL_ID] === rowIndex
				? valueTyped
				: d[columnName];
		});

		table.value = table.value.derive({ [columnName]: updater });

		if (!isEventUsed(eventType)) return;

		const record = cleanRecord(table.value.filter(recordFilter).object());

		return new Promise((res) => {
			const event = new CustomEvent(eventType, {
				detail: {
					payload: { record, record_index: rowIndexBackend },
					callback: res,
				},
			});

			dispatchEvent(event);
		});
	}

	function isEventUsed(eventType: string): boolean {
		const isHandlerSet = component.value.handlers?.[eventType];
		const isBindingSet = component.value.binding?.eventType == eventType;
		const isBlueprintAttached = useComponentLinkedBlueprints(
			wf,
			componentId,
			eventType,
		).isLinked.value;

		return Boolean(isHandlerSet || isBindingSet || isBlueprintAttached);
	}

	function dispatchEvent(event: CustomEvent) {
		if (emitterEl.value instanceof HTMLElement) {
			emitterEl.value.dispatchEvent(event);
		} else {
			emitterEl.value.$el.dispatchEvent(event); // Vue instance (ComponentPublicInstance)
		}
	}

	return {
		isBusy,

		handleUpdateCell: (...args: Parameters<typeof handlerUpdateCell>) =>
			pushJob({
				eventType: "wf-dataframe-update",
				payload: args,
			}),

		handleAddRow: (...args: Parameters<typeof handlerAddRow>) =>
			pushJob({
				eventType: "wf-dataframe-add",
				payload: args,
			}),

		handleActionRow: (...args: Parameters<typeof handlerActionRow>) =>
			pushJob({
				eventType: "wf-dataframe-action",
				payload: args,
			}),
	};
}

function formatValue(previousValue: unknown, value: unknown) {
	switch (typeof previousValue) {
		case "number":
			return Number(value);
		case "string":
			return String(value);
		case "boolean":
			return Boolean(value);
		case "bigint":
			return BigInt(String(value));
		default:
			throw Error(
				`Could not update a field of type ${typeof previousValue}`,
			);
	}
}

function isVirtualColumn(key: string) {
	return (
		key === ARQUERO_INTERNAL_ID || UNNAMED_INDEX_COLUMN_PATTERN.test(key)
	);
}

function cleanRecord(row: object) {
	return Object.entries(row)
		.filter(([key]) => !isVirtualColumn(key))
		.reduce((acc, [key, value]) => {
			acc[key] = value;
			return acc;
		}, {});
}

function getDefaultRecord(row: object) {
	return Object.entries(row)
		.filter(([key]) => !isVirtualColumn(key))
		.reduce((acc, [key, value]) => {
			acc[key] = getDefaultValue(value);
			return acc;
		}, {});
}

function getDefaultValue(value: unknown) {
	switch (typeof value) {
		case "number":
			return 0;
		case "string":
			return "";
		case "boolean":
			return false;
		case "bigint":
			return BigInt(0);
		case "object":
			return {};
		default:
			throw Error(
				`Could not get default value a field of type ${typeof value}`,
			);
	}
}
