<template>
	<div
		class="CoreDataframe"
		:style="rootStyle"
		v-on:scroll="handleScroll"
		ref="rootEl"
	>
		<div class="dfGrid" :style="gridStyle" v-if="rowCount > 0">
			<div
				v-if="isIndexShown"
				data-streamsync-grid-col="0"
				class="dfCell dfIndexCell"
				:style="gridHeadStyle"
				title="Index"
				v-on:dblclick="recalculateColumnWidths"
			></div>
			<div
				v-for="(columnName, columnPosition) in columnNames.filter(c => !dfIndex.includes(c))"
				:data-streamsync-grid-col="
					columnPosition + (isIndexShown ? 1 : 0)
				"
				:key="columnName"
				class="dfCell"
				:style="gridHeadStyle"
				:title="columnName"
				v-on:dblclick="recalculateColumnWidths"
			>
				{{ columnName }}
			</div>
			<template v-for="(row, rowIndex) in slicedData" :key="rowIndex">
				<div v-if="isIndexShown" class="dfCell dfIndexCell">
					<template v-if="typeof dfIndex === 'undefined'">
						{{ (rowIndex+rowOffset) }}
					</template>
					<template v-else>
						{{ columnNames.filter(c => dfIndex.includes(c)).map(c => row[c]).join(", ") }}
					</template>
				</div>
				<div
					class="dfCell"
					v-for="(columnName, columnPosition) in columnNames.filter(c => !dfIndex.includes(c))"
					:key="columnName"
				>
					{{ row[columnName] }}
				</div>
			</template>
		</div>

		<div class="empty" v-else>Empty dataframe.</div>
		<div class="endpoint" :style="endpointStyle"></div>
	</div>
</template>

<script lang="ts">
import { Ref, computed, inject, ref } from "vue";
import { FieldCategory, FieldType } from "../streamsyncTypes";
import {
	primaryTextColor,
	secondaryTextColor,
	separatorColor,
} from "../renderer/sharedStyleFields";
import { onMounted } from "vue";
import { watch } from "vue";
import { nextTick } from "vue";
import { ComputedRef } from "vue";

const description = "A component to display Pandas DataFrames.";

const defaultDataframe = `
{
  "data": {
    "col_a": {"a": 1, "b": 2, "c": 3},
    "col_b": {"a": 4, "b": 5, "c": 6}
  },
  "metadata": {}
}`.trim();

export default {
	streamsync: {
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
			displayRowCount: {
				name: "Display row count",
				desc: "Specifies how many rows to show simultaneously.",
				type: FieldType.Number,
				category: FieldCategory.Style,
				default: "10",
			},
			primaryTextColor,
			secondaryTextColor,
			separatorColor,
			dataframeBackgroundColor: {
				name: "Background",
				type: FieldType.Color,
				category: FieldCategory.Style,
				default: "#ffffff",
				applyStyleVariable: true,
			},
			dataframeHeaderRowBackgroundColor: {
				name: "Header row background",
				type: FieldType.Color,
				category: FieldCategory.Style,
				default: "#f0f0f0",
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
			showIndex: {
				name: "Show index",
				type: FieldType.Text,
				default: "yes",
				options: {
					yes: "yes",
					no: "no",
				},
			},
		},
	},
};
</script>
<script setup lang="ts">
import injectionKeys from "../injectionKeys";
import * as aq from "arquero";
import { tableFromIPC, Table } from 'apache-arrow';

/**
 * Only a certain amount of rows is rendered at a time (MAX_ROWS_RENDERED),
 * to prevent filling the DOM with unnecessary rows.
 */
const ROW_HEIGHT_PX = 36; // Must match CSS
const MIN_COLUMN_WIDTH_PX = 80;

const fields = inject(injectionKeys.evaluatedFields);
const rootEl: Ref<HTMLElement> = ref();
const dfData = ref(null);
const dfIndex = ref([]);
const isIndexShown = computed(() => fields.showIndex.value == "yes");
const relativePosition: Ref<number> = ref(0);
const columnWidths: Ref<number[]> = ref([]);

const columnNames: ComputedRef<string[]> = computed(() => {
	if (!dfData.value) {
		return [];
	}
	return dfData.value?.columnNames();
});

const columnCount = computed(() => {
	const nonIndexColumns = columnNames.value.filter(c => !dfIndex.value.includes(c));
	const count = (isIndexShown.value ? 1 : 0) + nonIndexColumns.length;
	return count;
});
const rowCount = computed(() => dfData.value?.numRows() ?? 0);
const displayRowCount = computed(() =>
	Math.min(fields.displayRowCount.value, rowCount.value),
);
const rowOffset = computed(() =>
	Math.min(
		Math.floor(relativePosition.value * rowCount.value),
		rowCount.value - displayRowCount.value,
	),
);

const isEmpty = computed(() => {
	const e = !dfData.value;
	return e;
});

const slicedData = computed(() => {
	if (!dfData.value) return null;
	const sliced = dfData.value.objects({
		offset: rowOffset.value,
		limit: displayRowCount.value,
	});
	return sliced;
})

const rootStyle = computed(() => {
	const fontStyle = fields.fontStyle.value;
	return {
		"font-family": fontStyle == "monospace" ? "monospace" : undefined,
	};
});

const gridHeadStyle = computed(() => {
	return {
		"background-color": fields.dataframeHeaderRowBackgroundColor.value,
	};
});

const gridStyle = computed(() => {
	let templateColumns: string;

	if (columnWidths.value.length == 0) {
		templateColumns = `repeat(${columnCount.value}, minmax(min-content, 1fr))`;
		console.log(templateColumns);
	} else {
		templateColumns = columnWidths.value
			.map((cw) => `${Math.max(cw, MIN_COLUMN_WIDTH_PX)}px`)
			.join(" ");
	}

	return {
		"grid-template-columns": templateColumns,
		"grid-template-rows": `repeat(${displayRowCount.value}, 36px)`,
	};
});

const endpointStyle = computed(() => {
	const totalCount = ROW_HEIGHT_PX * rowCount.value;
	return {
		top: `${totalCount}px`,
	};
});

function handleScroll(ev: Event) {
	const scrollTop = rootEl.value.scrollTop;
	relativePosition.value =
		(scrollTop + ROW_HEIGHT_PX) / rootEl.value.scrollHeight;
}

async function recalculateColumnWidths() {
	columnWidths.value = [];
	await nextTick();
	const columnHeadersEls = rootEl.value?.querySelectorAll(
		"[data-streamsync-grid-col]",
	);
	columnHeadersEls?.forEach((headerEl) => {
		const headerHTMLEl = headerEl as HTMLElement;
		const columnPosition = headerHTMLEl.dataset.streamsyncGridCol;
		const { width } = headerHTMLEl.getBoundingClientRect();
		columnWidths.value[columnPosition] = width;
	});
}

function getIndexFromArrowTable(table: Table<any>) {
	const pandasMetadataJSON = table.schema.metadata.get("pandas");
	if (!pandasMetadataJSON) return;
	const pandasMetadata = JSON.parse(pandasMetadataJSON);
	return pandasMetadata.index_columns;
}

async function loadData () {
	const url = fields.dataframe.value;

	try {
		const res = await fetch(url);
		const blob = await res.blob();
		const buffer = await blob.arrayBuffer();
		const arrowTable = tableFromIPC(buffer);
		dfIndex.value = getIndexFromArrowTable(arrowTable);
		const aqTable = aq.fromArrow(arrowTable);
		dfData.value = aqTable;
		console.log("index", dfIndex.value);
	} catch (e) {
		console.error("Couldn't load dataframe from Arrow URL.", e);
	}
}

watch(
	fields.dataframe,
	() => {
		loadData();
	}
);

watch(columnCount, () => {
	recalculateColumnWidths();
});

onMounted(async () => {
	await loadData();
	new ResizeObserver(recalculateColumnWidths).observe(rootEl.value, {
		box: "border-box",
	});
});
</script>

<style scoped>
@import "../renderer/sharedStyles.css";

.CoreDataframe {
	background: var(--dataframeBackgroundColor);
	font-size: 0.8rem;
	width: fit-content;
	max-width: 100%;
	max-height: 90vh;
	overflow: auto;
	border: 1px solid var(--separatorColor);
	width: 100%;
	display: block;
	position: relative;
}

.dfGrid {
	position: sticky;
	top: 0;
	display: grid;
}

.dfCell {
	padding: 8px;
	height: 36px;
	display: flex;
	align-items: center;
	overflow: hidden;
	white-space: nowrap;
	color: var(--primaryTextColor);
	border-bottom: 1px solid var(--separatorColor);
}

.dfCell:not(.dfIndexCell) {
	border-left: 1px solid var(--separatorColor);
}

.dfIndexCell {
	color: var(--secondaryTextColor);
}

.endpoint {
	position: absolute;
	height: 1px;
	width: 1px;
}
</style>
