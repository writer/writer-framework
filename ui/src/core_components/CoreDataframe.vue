<template>
	<div class="CoreDataframe" :style="rootStyle">
		<table v-if="!isEmpty">
			<thead>
				<tr>
					<th v-if="isShowIndex"></th>
					<th v-for="columnIndex in columnIndexes" :key="columnIndex">
						{{ columnIndex }}
					</th>
				</tr>
			</thead>
			<tbody>
				<tr v-for="rowIndex in rowIndexes" :key="rowIndex">
					<td v-if="isShowIndex" class="rowIndex">
						{{ rowIndex }}
					</td>
					<td v-for="columnName in columnIndexes" :key="columnName">
						{{ dfData[columnName][rowIndex] }}
					</td>
				</tr>
			</tbody>
		</table>
		<div class="empty" v-else>Empty dataframe.</div>
	</div>
</template>

<script lang="ts">
import { computed, inject } from "vue";
import { FieldCategory, FieldType } from "../streamsyncTypes";
import {
	primaryTextColor,
	secondaryTextColor,
	separatorColor,
} from "../renderer/sharedStyleFields";

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
			primaryTextColor,
			secondaryTextColor,
			separatorColor,
			dataframeBackgroundColor: {
				name: "Background",
				type: FieldType.Color,
				category: FieldCategory.Style,
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

const fields = inject(injectionKeys.evaluatedFields);

const dfData = computed(() => fields.value?.dataframe?.data);

const isShowIndex = computed(() => fields.value?.showIndex == "yes");

const columnIndexes = computed(() => {
	return Object.keys(dfData.value ?? {});
});

const isEmpty = computed(() => {
	const e = !dfData.value || columnIndexes.value.length == 0;
	return e;
});

const rowIndexes = computed(() => {
	const firstColumn = dfData.value[columnIndexes.value[0]];
	const rowIndexes = Object.keys(firstColumn);
	return rowIndexes;
});

const rootStyle = computed(() => {
	const fontStyle = fields.value.fontStyle;

	return {
		"font-family": fontStyle == "monospace" ? "monospace" : undefined,
	};
});
</script>

<style scoped>
@import "../renderer/sharedStyles.css";

.CoreDataframe {
	background: var(--dataframeBackgroundColor);
	font-size: 0.8rem;
	width: fit-content;
	max-width: 100%;
	max-height: 80vh;
	overflow: auto;
	border: 1px solid var(--separatorColor);
	width: 100%;
}

table {
	width: 100%;
	border-spacing: 0;
	border-collapse: separate;
}

th {
	position: sticky;
	top: 0;
	padding: 8px;
	color: var(--primaryTextColor);
	background-color: var(--dataframeHeaderRowBackgroundColor);
	border: 0.5px solid var(--separatorColor);
}

td {
	border: 0.5px solid var(--separatorColor);
	padding: 8px;
	color: var(--primaryTextColor);
}

td.rowIndex {
	color: var(--secondaryTextColor);
}
</style>
