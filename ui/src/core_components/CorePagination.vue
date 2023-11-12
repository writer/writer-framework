<template>
	<div></div>
</template>

<script lang="ts">
import { FieldCategory, FieldType } from "../streamsyncTypes";

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
				init: "25,50,100",
				type: FieldType.Text,
				desc: "A comma-separated list of page size options.",
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
		events: {}
	}
};
</script>

<style scoped>

</style>