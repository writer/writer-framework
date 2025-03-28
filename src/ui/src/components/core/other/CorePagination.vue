<template>
	<div ref="rootEl" class="CorePagination">
		<div class="pagination-left">
			<div v-show="pagesizeEnabled" class="pagination-pagesize">
				<select class="pagesize-select" @change="onPageSizeChange">
					<option
						v-for="(o, key) in pageSizeOptions"
						:key="key"
						:value="o.value"
						:selected="o.value == fields.pageSize.value"
					>
						{{ o.label }}
					</option>
				</select>
			</div>
			<div class="pagination-description">
				Showing <span class="bold">{{ firstItem }}</span> to
				<span class="bold">{{ lastItem }}</span> of
				<span class="bold">{{ totalItem }}</span> results
			</div>
		</div>
		<div class="pagination-right">
			<div class="pagination-picker">
				<div
					class="paginationpicker-block"
					:class="{
						'paginationpicker-disabled': pagePreviousDisabled,
					}"
					@click="jumpTo(fields.page.value - 1)"
				>
					<i class="material-symbols-outlined"> navigate_before </i>
				</div>
				<template v-for="(l, index) in links" :key="index">
					<div
						v-if="l == '...'"
						class="paginationpicker-block paginationpicker-neutral"
					>
						{{ l }}
					</div>
					<div
						v-if="l != '...' && l != fields.page.value"
						class="paginationpicker-block"
						@click="jumpTo(l)"
					>
						{{ l }}
					</div>
					<div
						v-if="l == fields.page.value"
						class="paginationpicker-block paginationpicker-currentpage"
					>
						{{ l }}
					</div>
				</template>
				<div
					class="paginationpicker-block"
					:class="{ 'paginationpicker-disabled': pageNextDisabled }"
					@click="jumpTo(fields.page.value + 1)"
				>
					<i class="material-symbols-outlined"> navigate_next </i>
				</div>
			</div>
			<div v-show="jumptoEnabled" class="pagination-jump">
				<label>Jump to</label>
				<input
					type="text"
					:value="fields.page.value"
					@input="onJumpTo"
				/>
			</div>
		</div>
	</div>
</template>

<script lang="ts">
import { FieldType } from "@/writerTypes";
import { validatorPositiveNumber } from "@/constants/validators";
import { baseYesNoField } from "@/renderer/sharedStyleFields";

const pageChangeStub = `
def handle_page_change(state, payload):
    page = payload
    state["page"] = page

    records = _load_records_from_db(start = state["page"] * state["pageSize"], limit = state["pageSize"])
    # update a repeater
    state["highlighted_members"] = {r.id: r for r in records}
`;

const onPageSizeChangeStub = `
def handle_page_size_change(state, payload):
    state['pageSize'] = payload

    records = _load_records_from_db(start = state["page"] * state["pageSize"], limit = state["pageSize"])
    # update a repeater
    state["highlighted_members"] = {r.id: r for r in records}
`;

export default {
	writer: {
		name: "Pagination",
		category: "Other",
		description:
			"A component that can help you paginate records, for example from a Repeater or a DataFrame.",
		fields: {
			page: {
				name: "Page",
				init: "1",
				default: "1",
				type: FieldType.Number,
				desc: "The current page number.",
				validator: validatorPositiveNumber,
			},
			pageSize: {
				name: "Page Size",
				default: "10",
				type: FieldType.Number,
				desc: "The number of items per page.",
				validator: validatorPositiveNumber,
			},
			totalItems: {
				name: "Total Items",
				default: "10",
				type: FieldType.Number,
				desc: "The total number of items",
				validator: validatorPositiveNumber,
			},
			pageSizeOptions: {
				name: "Page Size Options",
				init: "",
				default: "",
				type: FieldType.Text,
				desc: "A comma-separated list of page size options. If it's empty, the user can't change the page size. Set your default page size as the first option.",
			},
			pageSizeShowAll: {
				...baseYesNoField,
				name: "Show All Option",
				default: "no",
				desc: "Show an option to show all records.",
			},
			jumpTo: {
				...baseYesNoField,
				name: "Jump To",
				default: "no",
				desc: "Show an option to jump to a specific page.",
			},
		},
		events: {
			"wf-change-page": {
				desc: "Fires when the user pick a page",
				stub: pageChangeStub.trim(),
				eventPayloadExample: 2,
			},
			"wf-change-page-size": {
				desc: "Fires when the user change the page size.",
				stub: onPageSizeChangeStub.trim(),
				eventPayloadExample: 10,
			},
		},
	},
};
</script>

<script setup lang="ts">
import { inject, computed, useTemplateRef } from "vue";
import injectionKeys from "@/injectionKeys";
import { useFormValueBroker } from "@/renderer/useFormValueBroker";

const fields = inject(injectionKeys.evaluatedFields);
const wf = inject(injectionKeys.core);
const rootEl = useTemplateRef("rootEl");
const instancePath = inject(injectionKeys.instancePath);

const { handleInput: handlePageInput } = useFormValueBroker(
	wf,
	instancePath,
	rootEl,
);
const { handleInput: handlePageSizeInput } = useFormValueBroker(
	wf,
	instancePath,
	rootEl,
);
const pagesizeEnabled = computed(
	() => fields.pageSizeOptions.value !== "" || fields.pageSizeShowAll.value,
);
const jumptoEnabled = computed(() => fields.jumpTo.value);

const firstItem = computed(() => {
	if (fields.totalItems.value == 0) {
		return 0;
	}
	return (fields.page.value - 1) * fields.pageSize.value + 1;
});
const lastItem = computed(() =>
	Math.min(
		fields.page.value * fields.pageSize.value,
		fields.totalItems.value,
	),
);
const totalItem = computed(() => fields.totalItems.value);
const totalPage = computed(() =>
	Math.ceil(
		parseInt(fields.totalItems.value) / parseInt(fields.pageSize.value),
	),
);

const pageSizeOptions = computed(() => {
	let options = [];
	const inputs = fields.pageSizeOptions.value.split(",");
	for (const o in inputs) {
		const n = parseInt(inputs[o], 10);
		options.push({ value: n, label: `${n} items` });
	}
	if (fields.pageSizeShowAll.value) {
		options.push({ value: totalItem.value, label: "All items" });
	}

	return options;
});

/**
 * Calculate the links to show in the pagination
 */
const links = computed(() => {
	const links = [];
	const page = parseInt(fields.page.value);

	if (totalPage.value <= 7) {
		for (let i = 0; i < totalPage.value; i++) {
			links.push(i + 1);
		}
	} else if (page == 1 || page == 2) {
		links.push(1);
		links.push(2);
		links.push(3);
		links.push("...");
		links.push(totalPage.value - 2);
		links.push(totalPage.value - 1);
		links.push(totalPage.value);
	} else if (page == 3) {
		links.push(1);
		links.push(2);
		links.push(3);
		links.push(4);
		links.push("...");
		// links.push(totalPage.value - 2)
		links.push(totalPage.value - 1);
		links.push(totalPage.value);
	} else if (page == 4) {
		links.push(1);
		links.push(2);
		links.push(3);
		links.push(4);
		links.push(5);
		links.push("...");
		links.push(totalPage.value);
	} else if (page == totalPage.value || page == totalPage.value - 1) {
		links.push(1);
		links.push(2);
		links.push(3);
		links.push("...");
		links.push(totalPage.value - 2);
		links.push(totalPage.value - 1);
		links.push(totalPage.value);
	} else if (page == totalPage.value - 2) {
		links.push(1);
		links.push(2);
		links.push("...");
		links.push(totalPage.value - 3);
		links.push(totalPage.value - 2);
		links.push(totalPage.value - 1);
		links.push(totalPage.value);
	} else {
		links.push(1);
		links.push("...");
		links.push(page - 1);
		links.push(page);
		links.push(page + 1);
		links.push("...");
		links.push(totalPage.value);
	}

	return links;
});

/**
 * Disable the previous page button if the current page is the first page.
 */
const pagePreviousDisabled = computed(() => {
	const previousPage = parseInt(fields.page.value) - 1;
	return previousPage < 1;
});

/**
 * Disable the next page button if the current page is the last page.
 */
const pageNextDisabled = computed(() => {
	const nextPage = parseInt(fields.page.value) + 1;
	return nextPage > totalPage.value;
});

const onJumpTo = (event) => {
	if (event.target.value === "") {
		return;
	}

	let page = parseInt(event.target.value);
	if (page > totalPage.value) {
		page = totalPage.value;
	}

	handlePageInput(page, "wf-change-page");
};

const jumpTo = (page: number) => {
	handlePageInput(page, "wf-change-page");
};

const onPageSizeChange = (event) => {
	let pageSize = parseInt(event.target.value);
	handlePageSizeInput(pageSize, "wf-change-page-size");
};
</script>

<style scoped>
.CorePagination {
	display: flex;
	align-items: center;
	flex-wrap: wrap;

	width: 100%;
}

.pagination-left {
	display: flex;
	justify-content: start;
	align-items: center;
	gap: 16px;
	padding: 8px 0;
}

.pagination-right {
	display: flex;
	align-items: center;
	justify-content: end;
	gap: 16px;
	flex-grow: 1;
	padding: 8px 0;
}

.pagination-picker {
	display: flex;
	align-items: center;
	gap: 0;
	border-radius: 8px;
	overflow: hidden;
	border: 1px solid var(--separatorColor);
}

.pagination-jump {
	display: flex;
	align-items: center;
	gap: 8px;
}

.pagination-jump input {
	width: 32px;
	height: 30px;
	border: 1px solid var(--separatorColor);
	background-color: transparent;
}

.paginationpicker-block {
	display: flex;
	align-items: center;
	justify-content: center;

	height: 32px;
	width: 32px;
	border-collapse: collapse;

	margin-top: -1px;
	margin-left: -1px;
	cursor: pointer;
}

.paginationpicker-block:not(:last-of-type) {
	border-right: 1px solid var(--separatorColor);
}

.paginationpicker-currentpage {
	background-color: var(--accentColor);
	color: var(--emptinessColor);
}

.paginationpicker-disabled {
	cursor: default;
	pointer-events: none;
}

.paginationpicker-neutral {
	cursor: default;
}

select {
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	height: 32px;
	padding: 0 8px 0 8px;
	font-size: 0.75rem;
	max-width: 100%;
	width: fit-content;
	outline: none;
}

.bold {
	font-weight: bold;
}
</style>
