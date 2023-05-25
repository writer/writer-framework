<template>
	<div
		class="CoreDataframe"
		:style="rootStyle"
		v-on:scroll="handleScroll"
		ref="rootEl"
	>
		<div class="dfGrid" :style="gridStyle">
			<div
				v-if="isIndexShown"
				data-streamsync-grid-col="0"
				class="dfCell dfIndexCell"
				:style="gridHeadStyle"
				title="Index"
				v-on:dblclick="recalculateColumnWidths"
			></div>
			<div
				v-for="(columnName, columnPosition) in columnIndexes"
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

			<template v-for="rowIndex in slicedRowIndexes" :key="rowIndex">
				<div v-if="isIndexShown" class="dfCell dfIndexCell">
					{{ rowIndex }}
				</div>
				<div
					class="dfCell"
					v-for="(columnName, columnPosition) in columnIndexes"
					:key="columnName"
				>
					{{ dfData[columnName][rowIndex] }}
				</div>
			</template>
		</div>

		<!-- <div class="empty" v-else>Empty dataframe.</div> -->
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
				desc: "Must be a JSON object or a state reference to a Pandas dataframe.",
				type: FieldType.Object,
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

/**
 * Only a certain amount of rows is rendered at a time (MAX_ROWS_RENDERED),
 * to prevent filling the DOM with unnecessary rows.
 */
const ROW_HEIGHT_PX = 36; // Must match CSS
const MIN_COLUMN_WIDTH_PX = 80;

const fields = inject(injectionKeys.evaluatedFields);
const rootEl: Ref<HTMLElement> = ref();

const dfData = computed(() => fields.dataframe.value?.data);
const isIndexShown = computed(() => fields.showIndex.value == "yes");
const relativePosition: Ref<number> = ref(0);

const columnIndexes = computed(() => {
	return Object.keys(dfData.value ?? {});
});

const columnCount = computed(
	() => columnIndexes.value.length + (isIndexShown.value ? 1 : 0),
);
const rowCount = computed(() => rowIndexes.value.length);
const displayRowCount = computed(() => Math.min(fields.displayRowCount.value, rowCount.value));
const startRow = computed(() =>
	Math.min(
		Math.floor(relativePosition.value * rowCount.value),
		rowCount.value - displayRowCount.value,
	),
);

const columnWidths: Ref<number[]> = ref([]);
watch(columnCount, () => {
	recalculateColumnWidths();
});

const isEmpty = computed(() => {
	const e = !dfData.value || columnCount.value == 0;
	return e;
});

const rowIndexes = computed(() => {
	const firstColumn = dfData.value[columnIndexes.value[0]];
	const rowIndexes = Object.keys(firstColumn);
	return rowIndexes;
});

const slicedRowIndexes = computed(() => {
	const sliced = rowIndexes.value.slice(
		startRow.value,
		startRow.value + displayRowCount.value,
	);
	return sliced;
});

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
	const rowCount = rowIndexes.value.length;
	const totalCount = ROW_HEIGHT_PX * rowCount;
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

onMounted(() => {
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
