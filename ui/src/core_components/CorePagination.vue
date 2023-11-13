<template>
	<div class="pagination" ref="rootEl">
		<div class="pagination-left">
			<div class="pagination-pagesize" v-show="pagesizeEnabled">
				<select class="pagesize-select" @change="onPageSizeChange">
					<option v-for="o in pageSizeOptions" :value="o.value">{{ o.label }}</option>
				</select>
			</div>
			<div class="pagination-description">
				Showing <span class="bold">{{ firstItem }}</span> to <span class="bold">{{ lastItem }}</span> of <span class="bold">{{ totalItem }}</span> results
			</div>
		</div>
		<div class="pagination-right">
			<div class="pagination-picker">

				<div class="paginationpicker-block ri-arrow-left-s-line"></div>
				<template v-for="l in links">
					<div v-if="l == '...'" class="paginationpicker-block paginationpicker-neutral">
						{{ l }}
					</div>
					<div v-if="l != '...' && l != pageValue" class="paginationpicker-block" @click="jumpTo(l)">
						{{ l }}
					</div>
					<div v-if="l == pageValue" class="paginationpicker-block paginationpicker-currentpage">
						{{ l }}
					</div>
				</template>
				<div class="paginationpicker-block ri-arrow-right-s-line"></div>
			</div>
			<div class="pagination-jump" v-show="jumptoEnabled">
				<label>Jump to</label>
				<input type="text" :value="pageValue" @input="onJumpTo"/>
			</div>

		</div>
	</div>
</template>

<script lang="ts">
import { FieldType } from "../streamsyncTypes";

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
`

export default {
	streamsync: {
		name: "Pagination",
		category: "Other",
		description: "paginates records from a repeater or dataframe",
		fields: {
			page: {
				name: "Page",
				init: "1",
				type: FieldType.Number,
				desc: "The current page number.",
			},
			pageSize: {
				name: "Page Size",
				init: "25",
				type: FieldType.Number,
				desc: "The number of items per page.",
			},
			totalItems: {
				name: "Total Items",
				init: "0",
				type: FieldType.Number,
				desc: "The total number of items",
			},
			pageSizeOptions: {
				name: "Page Size Options",
				init: "",
				type: FieldType.Text,
				desc: "A comma-separated list of page size options. If it's empty, the user can't change the page size.",
			},
			pageSizeShowAll: {
				name: "Show All Option",
				init: "no",
				type: FieldType.Text,
				options: {
					yes: "Yes",
					no: "No",
				},
				desc: "Show an option to show all records.",
			},
			jumpTo: {
				name: "Jump To",
				init: "no",
				type: FieldType.Text,
				options: {
					yes: "Yes",
					no: "No",
				},
				desc: "Show an option to jump to a specific page.",
			},
			urlParam: {
				name: "URL Param",
				init: "",
				type: FieldType.Text,
				desc: "The URL parameter to use for the page number. If it's empty, the page is not saved on the url.",
			},
		},
		events: {
			"page-changed": {
				desc: "Fires when the user pick a page",
				stub: pageChangeStub.trim(),
			},
			"page-size-changed": {
				desc: "Fires when the user change the page size.",
				stub: onPageSizeChangeStub.trim()
			}
		}
	}
};
</script>

<script setup lang="ts">
import {Ref, inject, ref, computed} from "vue";
import injectionKeys from "../injectionKeys";
import {useFormValueBroker} from "../renderer/useFormValueBroker";

const fields = inject(injectionKeys.evaluatedFields);
const ss = inject(injectionKeys.core);
const rootEl = ref(null);
const instancePath = inject(injectionKeys.instancePath);

const {formValue: pageValue, handleInput: handlePageInput } = useFormValueBroker(ss, instancePath, rootEl);
const {formValue: pageSizeValue, handleInput: handlePageSizeInput } = useFormValueBroker(ss, instancePath, rootEl);
const pagesizeEnabled = computed(() => fields.pageSizeOptions.value !== "" || fields.pageSizeShowAll.value === "yes");
const jumptoEnabled = computed(() => fields.jumpTo.value === "yes");

const firstItem = computed(() => {
	return (pageValue.value - 1) * (fields.pageSize.value) + 1
});
const lastItem = computed(() => Math.min((pageValue.value) * fields.pageSize.value, fields.totalItems.value));
const totalItem = computed(() => fields.totalItems.value);
const totalPage = computed(() => Math.ceil(parseInt(fields.totalItems.value) / parseInt(fields.pageSize.value)) - 1);

const pageSizeOptions = computed(() => {
	let options = []
	const inputs = fields.pageSizeOptions.value.split(",")
	for (const o in inputs) {
		const n = parseInt(inputs[o], 10)
		options.push({value: n, label:`${n} items`})

	}
	if (fields.pageSizeShowAll.value === "yes") {
		options.push({value: -1, label: "All items"})
	}

	return options;
});

const links = computed(() => {
	const links = [];
	const page = parseInt(pageValue.value);

	if (totalPage.value < 3) {
		for (let i = 0; i <= totalPage.value; i++) {
			links.push(i + 1);
		}
	} else if (page == 1 || page == 2) {
		links.push(1);
		links.push(2);
		links.push(3);
		links.push("...")
		links.push(totalPage.value)
	} else if (page == 3) {
		links.push(1);
		links.push(2);
		links.push(3);
		links.push(4);
		links.push("...");
		links.push(totalPage.value)
	} else if (page == totalPage.value || page == totalPage.value - 1) {
		links.push(1);
		links.push("...");
		links.push(totalPage.value - 2)
		links.push(totalPage.value - 1)
		links.push(totalPage.value)
	} else if (page == totalPage.value - 2) {
		links.push(1);
		links.push("...");
		links.push(totalPage.value - 3)
		links.push(totalPage.value - 2)
		links.push(totalPage.value - 1)
		links.push(totalPage.value)
	} else {
		links.push(1)
		links.push("...")
		links.push(page - 1);
		links.push(page);
		links.push(page + 1);
		links.push("...");
		links.push(totalPage.value)
	}

	return links;
})


const onJumpTo = (event) => {
	if (event.target.value === "") {
		return;
	}


	let page = parseInt(event.target.value);
	if (page > totalPage.value) {
		page = totalPage.value;
	}

	handlePageInput(page, 'page-changed')
};

const jumpTo = (page: number) => {
	handlePageInput(page, 'page-changed')
}

const onPageSizeChange = (event) => {
	let pageSize = parseInt(event.target.value);
	handlePageSizeInput(pageSize, 'page-size-changed')
};

</script>

<style scoped>
.pagination {
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
	border: 1px solid var(--separatorColor);
	border-collapse: collapse;

	margin-top: -1px;
	margin-left: -1px;
	cursor: pointer;
}

.paginationpicker-neutral {
	cursor: default;
}

.pagesize-select {
	height: 30px;
	border: 1px solid var(--separatorColor);
	background-color: transparent;
}

.bold {
	font-weight: bold;
}

.paginationpicker-currentpage {
	background-color: var(--accentColor);
	color: var(--emptinessColor);
}
</style>