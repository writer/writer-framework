<template>
	<div ref="rootEl" class="CoreDataframe">
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
				<i class="material-symbols-outlined"> download </i>
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
						class="icon"
						:style="{
							visibility:
								orderSetting?.columnName == columnName
									? 'visible'
									: 'hidden',
						}"
					>
						<span
							v-show="!orderSetting?.descending"
							class="material-symbols-outlined"
						>
							arrow_downward
						</span>
						<span
							v-show="orderSetting?.descending"
							class="material-symbols-outlined"
						>
							arrow_upward
						</span>
					</div>
					<div class="widthAdjuster"></div>
				</div>
				<template
					v-for="(row, rowNumber) in slicedTable?.data"
					:key="rowNumber"
				>
					<div v-if="isIndexShown" class="cell indexCell">
						<template v-if="tableIndex.length == 0">
							{{ slicedTable.indices[rowNumber] }}
						</template>
						<template v-else>
							{{ indexColumnNames.map((c) => row[c]).join(", ") }}
						</template>
					</div>
					<div
						v-for="columnName in shownColumnNames"
						:key="columnName"
						class="cell"
					>
						<BaseMarkdown
							v-if="fields.useMarkdown.value == 'yes'"
							:raw-text="row[columnName]"
						>
						</BaseMarkdown>
						<template v-else>
							{{ row[columnName] }}
						</template>
					</div>
				</template>
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
import { Ref, computed, inject, ref } from "vue";
import { FieldCategory, FieldType } from "@/writerTypes";
import {
	cssClasses,
	primaryTextColor,
	secondaryTextColor,
	separatorColor,
} from "@/renderer/sharedStyleFields";
import { onMounted } from "vue";
import { watch } from "vue";
import { nextTick } from "vue";
import { ComputedRef } from "vue";
import { onUnmounted } from "vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";
import WdsControl from "@/wds/WdsControl.vue";
import BaseMarkdown from "../base/BaseMarkdown.vue";
import { WdsColor } from "@/wds/tokens";
import { useLogger } from "@/composables/useLogger";
import { validatorPositiveNumber } from "@/constants/validators";

const description = "A component to display Pandas DataFrames.";
const defaultDataframe = `data:application/vnd.apache.arrow.file;base64,QVJST1cxAAD/////iAMAABAAAAAAAAoADgAGAAUACAAKAAAAAAEEABAAAAAAAAoADAAAAAQACAAKAAAAlAIAAAQAAAABAAAADAAAAAgADAAEAAgACAAAAGwCAAAEAAAAXwIAAHsiaW5kZXhfY29sdW1ucyI6IFsiX19pbmRleF9sZXZlbF8wX18iXSwgImNvbHVtbl9pbmRleGVzIjogW3sibmFtZSI6IG51bGwsICJmaWVsZF9uYW1lIjogbnVsbCwgInBhbmRhc190eXBlIjogInVuaWNvZGUiLCAibnVtcHlfdHlwZSI6ICJvYmplY3QiLCAibWV0YWRhdGEiOiB7ImVuY29kaW5nIjogIlVURi04In19XSwgImNvbHVtbnMiOiBbeyJuYW1lIjogImNvbF9hIiwgImZpZWxkX25hbWUiOiAiY29sX2EiLCAicGFuZGFzX3R5cGUiOiAiaW50NjQiLCAibnVtcHlfdHlwZSI6ICJpbnQ2NCIsICJtZXRhZGF0YSI6IG51bGx9LCB7Im5hbWUiOiAiY29sX2IiLCAiZmllbGRfbmFtZSI6ICJjb2xfYiIsICJwYW5kYXNfdHlwZSI6ICJpbnQ2NCIsICJudW1weV90eXBlIjogImludDY0IiwgIm1ldGFkYXRhIjogbnVsbH0sIHsibmFtZSI6IG51bGwsICJmaWVsZF9uYW1lIjogIl9faW5kZXhfbGV2ZWxfMF9fIiwgInBhbmRhc190eXBlIjogImludDY0IiwgIm51bXB5X3R5cGUiOiAiaW50NjQiLCAibWV0YWRhdGEiOiBudWxsfV0sICJjcmVhdG9yIjogeyJsaWJyYXJ5IjogInB5YXJyb3ciLCAidmVyc2lvbiI6ICIxMi4wLjAifSwgInBhbmRhc192ZXJzaW9uIjogIjEuNS4zIn0ABgAAAHBhbmRhcwAAAwAAAIgAAABEAAAABAAAAJT///8AAAECEAAAACQAAAAEAAAAAAAAABEAAABfX2luZGV4X2xldmVsXzBfXwAAAJD///8AAAABQAAAAND///8AAAECEAAAABgAAAAEAAAAAAAAAAUAAABjb2xfYgAAAMD///8AAAABQAAAABAAFAAIAAYABwAMAAAAEAAQAAAAAAABAhAAAAAgAAAABAAAAAAAAAAFAAAAY29sX2EAAAAIAAwACAAHAAgAAAAAAAABQAAAAAAAAAD/////6AAAABQAAAAAAAAADAAWAAYABQAIAAwADAAAAAADBAAYAAAAMAAAAAAAAAAAAAoAGAAMAAQACAAKAAAAfAAAABAAAAACAAAAAAAAAAAAAAAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAQAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAABAAAAAAAAAAAAAAAAMAAAACAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAIAAAAAAAAAAwAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAD/////AAAAABAAAAAMABQABgAIAAwAEAAMAAAAAAAEADwAAAAoAAAABAAAAAEAAACYAwAAAAAAAPAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAACgAMAAAABAAIAAoAAACUAgAABAAAAAEAAAAMAAAACAAMAAQACAAIAAAAbAIAAAQAAABfAgAAeyJpbmRleF9jb2x1bW5zIjogWyJfX2luZGV4X2xldmVsXzBfXyJdLCAiY29sdW1uX2luZGV4ZXMiOiBbeyJuYW1lIjogbnVsbCwgImZpZWxkX25hbWUiOiBudWxsLCAicGFuZGFzX3R5cGUiOiAidW5pY29kZSIsICJudW1weV90eXBlIjogIm9iamVjdCIsICJtZXRhZGF0YSI6IHsiZW5jb2RpbmciOiAiVVRGLTgifX1dLCAiY29sdW1ucyI6IFt7Im5hbWUiOiAiY29sX2EiLCAiZmllbGRfbmFtZSI6ICJjb2xfYSIsICJwYW5kYXNfdHlwZSI6ICJpbnQ2NCIsICJudW1weV90eXBlIjogImludDY0IiwgIm1ldGFkYXRhIjogbnVsbH0sIHsibmFtZSI6ICJjb2xfYiIsICJmaWVsZF9uYW1lIjogImNvbF9iIiwgInBhbmRhc190eXBlIjogImludDY0IiwgIm51bXB5X3R5cGUiOiAiaW50NjQiLCAibWV0YWRhdGEiOiBudWxsfSwgeyJuYW1lIjogbnVsbCwgImZpZWxkX25hbWUiOiAiX19pbmRleF9sZXZlbF8wX18iLCAicGFuZGFzX3R5cGUiOiAiaW50NjQiLCAibnVtcHlfdHlwZSI6ICJpbnQ2NCIsICJtZXRhZGF0YSI6IG51bGx9XSwgImNyZWF0b3IiOiB7ImxpYnJhcnkiOiAicHlhcnJvdyIsICJ2ZXJzaW9uIjogIjEyLjAuMCJ9LCAicGFuZGFzX3ZlcnNpb24iOiAiMS41LjMifQAGAAAAcGFuZGFzAAADAAAAiAAAAEQAAAAEAAAAlP///wAAAQIQAAAAJAAAAAQAAAAAAAAAEQAAAF9faW5kZXhfbGV2ZWxfMF9fAAAAkP///wAAAAFAAAAA0P///wAAAQIQAAAAGAAAAAQAAAAAAAAABQAAAGNvbF9iAAAAwP///wAAAAFAAAAAEAAUAAgABgAHAAwAAAAQABAAAAAAAAECEAAAACAAAAAEAAAAAAAAAAUAAABjb2xfYQAAAAgADAAIAAcACAAAAAAAAAFAAAAAsAMAAEFSUk9XMQ==`;

export default {
	writer: {
		name: "DataFrame",
		description,
		category: "Content",
		fields: {
			dataframe: {
				name: "Data",
				desc: "Must be a state reference to a Pandas dataframe or PyArrow table. Alternatively, a URL for an Arrow IPC file.",
				type: FieldType.Text,
				default: defaultDataframe,
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
				validator: validatorPositiveNumber,
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
			separatorColor,
			dataframeBackgroundColor: {
				name: "Background",
				type: FieldType.Color,
				category: FieldCategory.Style,
				default: WdsColor.White,
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
const MIN_COLUMN_WIDTH_PX = 80;
const MAX_COLUMN_AUTO_WIDTH_PX = 300;
const UNNAMED_INDEX_COLUMN_PATTERN = /^__index_level_[0-9]+__$/;

type OrderSetting = {
	columnName: string;
	descending: boolean;
};

const fields = inject(injectionKeys.evaluatedFields);
const rootEl: Ref<HTMLElement> = ref();
const toolsEl: Ref<HTMLElement> = ref();
const gridContainerEl: Ref<HTMLElement> = ref();
let baseTable: aq.internal.ColumnTable = null;
const table: Ref<aq.internal.ColumnTable> = ref(null);
const tableIndex = ref([]);
const isIndexShown = computed(() => fields.showIndex.value == "yes");
const orderSetting: Ref<OrderSetting> = ref(null);
const relativePosition: Ref<number> = ref(0);
const columnWidths: Ref<number[]> = ref([]);
let columnBeingWidthAdjusted: number = null;

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
	const data = table.value.objects({
		offset,
		limit,
	});
	const indices = table.value
		.indices()
		.slice(rowOffset.value, rowOffset.value + displayRowCount.value);
	return {
		data,
		indices,
	};
});

const gridStyle = computed(() => {
	const fontStyle = fields.fontStyle.value;
	let templateColumns: string;

	if (columnWidths.value.length == 0) {
		templateColumns = `repeat(${columnCount.value}, minmax(min-content, 1fr))`;
	} else {
		templateColumns = columnWidths.value
			.map((cw) => `${Math.max(cw, MIN_COLUMN_WIDTH_PX)}px`)
			.join(" ");
	}

	return {
		"min-height": `${ROW_HEIGHT_PX * (1 + fields.displayRowCount.value)}px`,
		"max-height": `${(displayRowCount.value + 1) * ROW_HEIGHT_PX}px`,
		"font-family": fontStyle == "monospace" ? "monospace" : undefined,
		"grid-template-columns": templateColumns,
		"grid-template-rows": `${ROW_HEIGHT_PX}px repeat(${displayRowCount.value}, min-content)`,
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

async function loadData() {
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
		table.value = baseTable;
	} catch (e) {
		useLogger().error("Couldn't load dataframe from Arrow URL.", e);
	}
}

function download() {
	const csv = table.value.toCSV();
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
		table.value = baseTable.params({ pattern, filterS }).filter(filterS);
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

/* remove the background if the dataframe is being selected in builder mode */
.CoreDataframe.selected .gridContainer {
	background: unset;
}

.grid {
	margin-bottom: -1px;
	position: v-bind("isRowCountMassive ? 'sticky': 'unset'");
	top: 0;
	display: grid;
}

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

.endpoint {
	position: absolute;
	height: 1px;
	width: 1px;
	background: red;
}
</style>
