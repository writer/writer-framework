<template>
	<div></div>
</template>

<script lang="ts">
import { FieldType } from "../streamsyncTypes";

const pageChangeStub = `
def handle_page_change(state):

	# load only requested records from database
	records = _load_records_from_db(start = state["page"] * state["pageSize"], limit = state["pageSize"])

	# update a repeater
	state["highlighted_members"] = {r.id: r for r in records}`;

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
				desc: "The number of records per page.",
			},
			totalItems: {
				name: "Total Items",
				init: "0",
				type: FieldType.Number,
				desc: "The total number of records",
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
				desc: "Fires when the user pick a page or change the page size.",
				stub: pageChangeStub.trim()
			}
		}
	}
};
</script>

<style scoped>

</style>