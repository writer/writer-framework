<template>
	<div ref="rootEl" class="CoreDataframe" :aria-busy="isBusy">
		<div ref="toolsEl" class="tools">
			<div v-if="fields.enableSearch.value === 'yes'">
				<WdsTextInput
					class="search"
					placeholder="Search"
					left-icon="search"
					@change="handleSearchChange"
				/>
			</div>
			<WdsControl
				v-if="fields.enableDownload.value === 'yes'"
				title="Download"
				class="download"
				@click="download"
			>
				<i class="material-symbols-outlined">download</i>
			</WdsControl>
		</div>
		<div ref="gridContainerEl" class="gridContainer" @scroll="handleScroll">
			<div
				class="grid"
				:style="gridStyle"
				:class="{
					scrolled: rowOffset > 0,
					wrapText: fields.wrapText.value === 'yes',
				}"
			>
				<div
					:style="{
						display: 'grid',
						'grid-template-columns': gridTemplateColumns,
					}"
				>
					<div v-if="hasActions"></div>

					<div
						v-if="isIndexShown"
						data-writer-grid-col="0"
						class="cell headerCell indexCell"
					>
						<div class="name"></div>
						<div class="widthAdjuster"></div>
					</div>
					<div
						v-for="(columnName, columnPosition) in shownColumnNames"
						:key="columnName"
						:data-writer-grid-col="
							columnPosition + (isIndexShown ? 1 : 0)
						"
						class="cell headerCell"
						@click="handleSetOrder($event, columnName)"
					>
						<div class="name">
							{{ columnName }}
						</div>
						<div
							v-show="orderSetting?.columnName == columnName"
							class="icon"
						>
							<span class="material-symbols-outlined">{{
								orderSetting?.descending
									? "arrow_upward"
									: "arrow_downward"
							}}</span>
						</div>
						<div class="widthAdjuster"></div>
					</div>
				</div>

				<CoreDataframeRow
					v-for="(row, rowNumber) in slicedTable?.data"
					:key="rowNumber"
					:style="{
						'grid-template-columns': gridTemplateColumns,
					}"
					:row="row"
					:actions="actions"
					:use-markdown="useMarkdown"
					:editable="enableRecordUpdate && !isBusy"
					:columns="shownColumnNames"
					:show-index="isIndexShown"
					:index-text="
						slicedTable.indices[rowNumber] ??
						indexColumnNames.map((c) => row[c]).join(', ')
					"
					@action="handleActionRow"
					@change="handleUpdateCell"
				/>
				<div v-if="enableRecordAdd" class="CoreDataframe__newRow cell">
					<WdsButton
						aria-label="Create a new row at the end"
						size="small"
						variant="tertiary"
						@click="handleAddRow"
					>
						<i class="material-symbols-outlined">add</i>
						Add a row
					</WdsButton>
				</div>
			</div>
			<div
				v-if="isRowCountMassive"
				class="endpoint"
				:style="endpointStyle"
			></div>
		</div>
	</div>
</template>

<script lang="ts">
import { computed, inject, ref, shallowRef } from "vue";
import { FieldCategory, FieldType } from "@/writerTypes";
import CoreDataframeRow from "./CoreDataframe/CoreDataframeRow.vue";
import {
	cssClasses,
	primaryTextColor,
	secondaryTextColor,
	accentColor,
	separatorColor,
} from "@/renderer/sharedStyleFields";
import { onMounted } from "vue";
import { watch } from "vue";
import { nextTick } from "vue";
import { ComputedRef } from "vue";
import { onUnmounted } from "vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";
import WdsControl from "@/wds/WdsControl.vue";
import { useDataFrameValueBroker } from "./CoreDataframe/useDataframeValueBroker";
import {
	ARQUERO_INTERNAL_ID,
	DEFAULT_DATA_FRAME,
	UNNAMED_INDEX_COLUMN_PATTERN,
} from "./CoreDataframe/constants";
import WdsButton from "@/wds/WdsButton.vue";

const description = "A component to display Pandas DataFrames.";

const dataFrameUpdateHandlerStub = `
# Subscribe this event handler to the \`wf-dataframe-update\` event
#
# more on : https://dev.writer.com/framework/dataframe
def on_record_change(state, payload):
    state['mydf'].record_update(payload) # should contain an EditableDataFrame instance`;

const dataFrameAddHandlerStub = `
# Subscribe this event handler to the \`wf-dataframe-add\` event
#
# more on : https://dev.writer.com/framework/dataframe
def on_record_add(state, payload):
	payload['record']['sales'] = 0 # default value inside the dataframe
	state['mydf'].record_add(payload) # should contain an EditableDataFrame instance`;

const dataFrameActionHandlerStub = `
# Subscribe this event handler to the \`wf-dataframe-action\` event
#
# more on : https://dev.writer.com/framework/dataframe
def on_record_action(state, payload):
	# state['mydf'] should contains an EditableDataFrame instance
	record_index = payload['record_index']
	if payload['action'] == 'remove':
		state['mydf'].record_remove(payload) # should contain an EditableDataFrame instance
	if payload['action'] == 'open':
		state['record'] = state['mydf'].record(record_index) # dict representation of record`;

export default {
	writer: {
		name: "DataFrame",
		description,
		category: "Content",
		events: {
			"wf-dataframe-add": {
				desc: "Capture adding a row.",
				stub: dataFrameAddHandlerStub.trim(),
			},
			"wf-dataframe-update": {
				desc: "Capture a cell change.",
				stub: dataFrameUpdateHandlerStub.trim(),
			},
			"wf-dataframe-action": {
				desc: "Remove or open a row.",
				stub: dataFrameActionHandlerStub.trim(),
			},
		},
		fields: {
			dataframe: {
				name: "Data",
				desc: "Must be a state reference to a Pandas dataframe or PyArrow table. Alternatively, a URL for an Arrow IPC file.",
				type: FieldType.Text,
				default: DEFAULT_DATA_FRAME,
			},
			showIndex: {
				name: "Show index",
				desc: "Shows the dataframe's index. If an Arrow table is used, shows the zero-based integer index.",
				type: FieldType.Text,
				default: "yes",
				options: {
					yes: "yes",
					no: "no",
				},
			},
			enableSearch: {
				name: "Enable search",
				type: FieldType.Text,
				default: "no",
				options: {
					yes: "yes",
					no: "no",
				},
			},
			enableRecordAdd: {
				name: "Enable adding a record",
				type: FieldType.Text,
				default: "no",
				options: {
					yes: "yes",
					no: "no",
				},
			},
			enableRecordUpdate: {
				name: "Enable updating a record",
				type: FieldType.Text,
				default: "no",
				options: {
					yes: "yes",
					no: "no",
				},
			},
			enableDownload: {
				name: "Enable download",
				desc: "Allows the user to download the data as CSV.",
				type: FieldType.Text,
				default: "no",
				options: {
					yes: "yes",
					no: "no",
				},
			},
			actions: {
				name: "Actions",
				desc: "Define rows actions",
				type: FieldType.KeyValue,
				default: JSON.stringify({ remove: "Remove", open: "Open" }),
			},
			useMarkdown: {
				name: "Use Markdown",
				type: FieldType.Text,
				desc: "If active, the output will be sanitized; unsafe elements will be removed.",
				options: {
					yes: "yes",
					no: "no",
				},
				default: "no",
			},
			displayRowCount: {
				name: "Display row count",
				desc: "Specifies how many rows to show simultaneously.",
				type: FieldType.Number,
				category: FieldCategory.Style,
				default: "10",
			},
			wrapText: {
				name: "Wrap text",
				type: FieldType.Text,
				category: FieldCategory.Style,
				desc: "Not wrapping text allows for an uniform grid, but may be inconvenient if your data contains longer text fields.",
				options: {
					yes: "yes",
					no: "no",
				},
				default: "no",
			},
			primaryTextColor,
			secondaryTextColor,
			accentColor,
			separatorColor,
			dataframeBackgroundColor: {
				name: "Background",
				type: FieldType.Color,
				category: FieldCategory.Style,
				default: "#ffffff",
				applyStyleVariable: true,
			},
			fontStyle: {
				name: "Font style",
				type: FieldType.Text,
				category: FieldCategory.Style,
				options: {
					normal: "normal",
					monospace: "monospace",
				},
				default: "normal",
			},
			cssClasses,
		},
	},
};
</script>

<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import type * as aq from "arquero";
import type { Table } from "apache-arrow";

/**
 * If the table is massive, only a certain amount of rows is rendered at a time,
 * to prevent filling the DOM with unnecessary rows.
 */
const MASSIVE_ROW_COUNT = 1000;
const ROW_HEIGHT_PX = 36; // Must match CSS
const ROW_ADD_RECORD_HEIGHT_PX = 58;
const MIN_COLUMN_WIDTH_PX = 80;
const MAX_COLUMN_AUTO_WIDTH_PX = 300;

type OrderSetting = {
	columnName: string;
	descending: boolean;
};

const fields = inject(injectionKeys.evaluatedFields);
const rootEl = ref<HTMLElement>();
const toolsEl = ref<HTMLElement>();
const gridContainerEl = ref<HTMLElement>();
let baseTable: aq.internal.ColumnTable = null;
const table = shallowRef<aq.internal.ColumnTable | null>(null);
const tableIndex = shallowRef([]);
const isIndexShown = computed(() => fields.showIndex.value == "yes");
const actions = computed<Record<string, string>>(() => fields.actions.value);
const orderSetting = shallowRef<OrderSetting | null>(null);
const relativePosition = ref(0);
const columnWidths = ref<number[]>([]);
let columnBeingWidthAdjusted: number = null;

const wf = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);

const {
	handleUpdateCell,
	handleAddRow,
	handleActionRow,
	isBusy: isUpdatingBusy,
} = useDataFrameValueBroker(wf, instancePath, rootEl, table);

const isBusy = computed(() => isLoadingData.value || isUpdatingBusy.value);

const columnNames: ComputedRef<string[]> = computed(() => {
	if (!table.value) {
		return [];
	}
	return table.value?.columnNames();
});
const indexColumnNames = computed(() =>
	columnNames.value.filter((c) => tableIndex.value.includes(c)),
);
const shownColumnNames = computed(() => {
	const cols = columnNames.value.filter((c) => {
		if (c === ARQUERO_INTERNAL_ID) return false;
		const isIndex = tableIndex.value.includes(c);
		const isUnnamed = UNNAMED_INDEX_COLUMN_PATTERN.test(c);
		return !(isIndex && isUnnamed);
	});
	return cols;
});

const columnCount = computed(
	() => (isIndexShown.value ? 1 : 0) + shownColumnNames.value.length,
);
const rowCount = computed(() => table.value?.numRows() ?? 0);
const isRowCountMassive = computed(() => rowCount.value > MASSIVE_ROW_COUNT);
const displayRowCount = computed(() =>
	Math.min(fields.displayRowCount.value, rowCount.value),
);

const hasActions = computed(
	() => Object.keys(fields.actions.value || {}).length > 0,
);
const useMarkdown = computed(() => fields.useMarkdown.value == "yes");
const enableRecordUpdate = computed(
	() => fields.enableRecordUpdate.value == "yes",
);
const enableRecordAdd = computed(() => fields.enableRecordAdd.value == "yes");

const rowOffset = computed(() => {
	let maxOffset: number;
	if (fields.wrapText.value == "yes") {
		maxOffset = rowCount.value - 1;
	} else {
		maxOffset = rowCount.value - displayRowCount.value;
	}
	const newOffset = Math.min(
		Math.ceil(relativePosition.value * maxOffset),
		maxOffset,
	);
	return newOffset;
});

const slicedTable = computed(() => {
	if (!table.value) return null;
	const offset = isRowCountMassive.value ? rowOffset.value : 0;
	const limit = isRowCountMassive.value
		? displayRowCount.value
		: MASSIVE_ROW_COUNT;
	const data = table.value.objects({ offset, limit });
	const indices = table.value
		.indices()
		.slice(rowOffset.value, rowOffset.value + displayRowCount.value);

	return { data, indices };
});

const gridTemplateColumns = computed(() => {
	let columns = hasActions.value ? "16px " : "";

	if (columnWidths.value.length == 0) {
		columns += `repeat(${columnCount.value}, minmax(min-content, 1fr))`;
	} else {
		columns += columnWidths.value
			.map((cw) => `${Math.max(cw, MIN_COLUMN_WIDTH_PX)}px`)
			.join(" ");
	}

	return columns;
});

const gridStyle = computed(() => {
	const fontStyle = fields.fontStyle.value;

	return {
		"min-height": `${(1 + fields.displayRowCount.value + Number(enableRecordAdd.value ?? false)) * ROW_HEIGHT_PX}px`,
		"max-height": `${(displayRowCount.value + 1 + Number(enableRecordAdd.value ?? false)) * ROW_HEIGHT_PX}px`,
		"font-family": fontStyle == "monospace" ? "monospace" : undefined,
		"grid-template-rows": `${ROW_HEIGHT_PX}px repeat(${displayRowCount.value}, min-content) ${ROW_ADD_RECORD_HEIGHT_PX}px`,
	};
});

const endpointStyle = computed(() => {
	const totalHeight = ROW_HEIGHT_PX * rowCount.value;
	return {
		top: `${totalHeight}px`,
	};
});

function handleScroll() {
	const scrollTop = gridContainerEl.value.scrollTop;
	relativePosition.value =
		scrollTop /
		(gridContainerEl.value.scrollHeight -
			gridContainerEl.value.clientHeight);
}

function resetScroll() {
	gridContainerEl.value.scrollTop = 0;
}

async function recalculateColumnWidths() {
	columnWidths.value = [];
	await nextTick();
	const columnHeadersEls = gridContainerEl.value?.querySelectorAll(
		"[data-writer-grid-col]",
	);
	columnHeadersEls?.forEach((headerEl) => {
		const headerHTMLEl = headerEl as HTMLElement;
		const columnPosition = headerHTMLEl.dataset.writerGridCol;
		const { width: autoWidth } = headerHTMLEl.getBoundingClientRect();
		const newWidth = Math.min(autoWidth, MAX_COLUMN_AUTO_WIDTH_PX);
		columnWidths.value[columnPosition] = newWidth;
	});
}

function handleSetOrder(ev: MouseEvent, columnName: string) {
	const targetEl = ev.target as HTMLElement;
	if (targetEl.classList.contains("widthAdjuster")) return;
	const currentColumnName = orderSetting.value?.columnName;

	if (currentColumnName !== columnName) {
		orderSetting.value = {
			columnName,
			descending: false,
		};
		return;
	}

	const currentlyDescending = orderSetting.value?.descending;

	if (currentlyDescending) {
		orderSetting.value = null;
		return;
	}

	orderSetting.value = {
		columnName,
		descending: !orderSetting.value.descending,
	};
}

function getIndexFromArrowTable(table: Table) {
	const pandasMetadataJSON = table.schema.metadata.get("pandas");
	if (!pandasMetadataJSON) return [];
	const pandasMetadata = JSON.parse(pandasMetadataJSON);
	return pandasMetadata.index_columns;
}

const isLoadingData = ref(false);

async function loadData() {
	isLoadingData.value = true;
	const aq = await import("arquero");
	const { tableFromIPC } = await import("apache-arrow");
	const url = fields.dataframe.value;

	try {
		const res = await fetch(url);
		const blob = await res.blob();
		const buffer = await blob.arrayBuffer();
		const arrowTable = tableFromIPC(buffer);
		tableIndex.value = getIndexFromArrowTable(arrowTable);
		const aqTable = aq.fromArrow(arrowTable);
		baseTable = aqTable;
		// add a unique ID to each row to be allow to edit a specific cell
		table.value = baseTable.derive({
			[ARQUERO_INTERNAL_ID]: () => aq.op.row_number(),
		});
	} catch (e) {
		// eslint-disable-next-line no-console
		console.error("Couldn't load dataframe from Arrow URL.", e);
	} finally {
		isLoadingData.value = false;
	}
}

async function download() {
	const aq = await import("arquero");
	const csv = table.value.select(aq.not(ARQUERO_INTERNAL_ID)).toCSV();
	const el = document.createElement("a");

	const blob = new Blob([csv], { type: "text/csv" });
	const url = URL.createObjectURL(blob);

	el.href = url;
	el.download = "data.csv";
	el.click();
	URL.revokeObjectURL(url);
}

async function applyOrder() {
	const aq = await import("arquero");
	if (orderSetting.value === null) {
		table.value = table.value.unorder();
		return;
	}

	let orderCriterion: string | object;

	if (orderSetting.value.descending) {
		orderCriterion = aq.desc(orderSetting.value.columnName);
	} else {
		orderCriterion = orderSetting.value.columnName;
	}
	table.value = table.value.orderby(orderCriterion);
}

async function handleSearchChange(ev: InputEvent) {
	const searchText = (ev.target as HTMLInputElement).value;
	if (!searchText) {
		table.value = baseTable;
	} else {
		const pattern = new RegExp(searchText, "i");
		const columnNames = baseTable.columnNames();
		const filterS =
			"(d, $) => " +
			columnNames
				.map((c) => `aq.op.match(d.${c}, $.pattern) !== null`)
				.join(" || ");

		const aq = await import("arquero");
		table.value = baseTable
			.params({ pattern, filterS })
			.filter(filterS)
			.derive({ [ARQUERO_INTERNAL_ID]: () => aq.op.row_number() });
	}
	await nextTick();
	resetScroll();
}

async function handleWidthAdjust(ev: MouseEvent) {
	if (ev.buttons !== 1) {
		columnBeingWidthAdjusted = null;
		return;
	}

	const targetEl = ev.target as HTMLElement;

	/*
	Event handlers are document-level. Check that it's the right Dataframe being adjusted.
	*/

	if (!rootEl.value.contains(targetEl)) return;

	if (
		columnBeingWidthAdjusted === null &&
		targetEl.classList.contains("widthAdjuster")
	) {
		const adjustedColEl = targetEl.closest(".cell") as HTMLElement;
		columnBeingWidthAdjusted = parseInt(
			adjustedColEl.dataset.writerGridCol,
		);
	} else if (columnBeingWidthAdjusted === null) {
		return;
	}

	const colEl = gridContainerEl.value.querySelector(
		`[data-writer-grid-col="${columnBeingWidthAdjusted}"]`,
	);
	const adjusterEl = colEl.querySelector(".widthAdjuster");
	const { width: adjusterWidth } = adjusterEl.getBoundingClientRect();
	const { left: colLeft } = colEl.getBoundingClientRect();
	const mouseX = ev.clientX;
	const newWidth = mouseX - colLeft + adjusterWidth / 2;
	columnWidths.value[columnBeingWidthAdjusted] = newWidth;
}

watch(fields.dataframe, () => {
	loadData();
});

watch(orderSetting, async () => {
	await applyOrder();
});

watch(columnCount, () => {
	recalculateColumnWidths();
});

watch(fields.wrapText, () => {
	recalculateColumnWidths();
});

onMounted(async () => {
	await loadData();
	document.addEventListener("mousemove", handleWidthAdjust);
	if (!toolsEl.value) return;
	new ResizeObserver(recalculateColumnWidths).observe(toolsEl.value, {
		box: "border-box",
	});
});

onUnmounted(() => {
	document.removeEventListener("mousemove", handleWidthAdjust);
});
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";
@import "@/renderer/colorTransformations.css";

.CoreDataframe {
	font-size: 0.8rem;
	width: 100%;
}

.CoreDataframe__newRow {
	display: flex;
	align-self: center;
	justify-content: center;
}
.CoreDataframe__newRow__btn {
	cursor: pointer;

	background-color: var(--separatorColor);
	border: 1px solid var(--emptinessColor);
	height: 16px;
	width: 16px;
	border-radius: 4px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.tools {
	display: flex;
	gap: 16px;
	align-items: center;
	color: var(--primaryTextColor);
	justify-content: right;
}

.tools:not(:empty) {
	margin-bottom: 16px;
}

.tools .search {
	display: flex;
	align-items: center;
	gap: 8px;
	border-radius: 8px;
}

.gridContainer {
	background: var(--dataframeBackgroundColor);
	position: relative;
	overflow: auto;
	max-height: 90vh;
}

.grid {
	margin-bottom: -1px;
	position: v-bind("isRowCountMassive ? 'sticky': 'unset'");
	top: 0;
	display: grid;
}

.endpoint {
	position: absolute;
	height: 1px;
	width: 1px;
	background: red;
}
</style>

<style>
.cell {
	min-height: 36px;
	padding: 8px;
	overflow: hidden;
	color: var(--primaryTextColor);
	border-bottom: 1px solid var(--separatorColor);
	display: flex;
	align-items: start;
	white-space: nowrap;
	font-size: 0.75rem;
	text-overflow: ellipsis;
}

.grid.wrapText .cell {
	white-space: pre-wrap;
}

.cell.headerCell {
	padding: 0;
	cursor: pointer;
	gap: 8px;
	user-select: none;
	font-size: 0.875rem;
	font-weight: 400;
	margin-bottom: 12px;
	border-bottom: none;
	top: 0;
	z-index: 1;
}

.grid.scrolled .cell.headerCell {
	box-shadow: 0px 2px 0px 0px rgba(0, 0, 0, 0.05);
}

.cell .name {
	padding: 8px;
	flex: 1 1 auto;
	overflow: hidden;
	text-overflow: ellipsis;
}

.cell .icon {
	flex: 0 0 auto;
	display: flex;
	align-items: center;
	visibility: hidden;
}

.cell .widthAdjuster {
	cursor: col-resize;
	min-width: 16px;
	flex: 0 0 16px;
	height: 100%;
	margin-right: -1px;
}

.cell:hover .widthAdjuster {
	background-color: var(--separatorColor);
}

.indexCell {
	color: var(--secondaryTextColor);
}
</style>
