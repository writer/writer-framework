<template>
	<div>
		<BuilderTree
			v-for="[key, node] of sourceFilesEntries"
			:key="key"
			:name="key"
			matched
			:has-children="isSourceFilesDirectory(node)"
			:selected="isSelected(key)"
			:right-click-options="rightClickDropdownOptions"
			:dropdown-options="
				isSourceFilesDirectory(node) || isSourceFilesBinary(node)
					? rightClickDropdownOptions
					: undefined
			"
			@select="handleSelect(key)"
			@dropdown-select="handleDropdownSelect($event, key)"
		>
			<template v-if="isDraft(key)" #nameLeft>
				<WdsStateDot state="newDraft" />
			</template>
			<template #children>
				<BuilderCodePanelSourceFilesTree
					:source-files="node"
					:path-active="pathActive"
					:paths-unsaved="pathsUnsaved"
					:path="[...path, key]"
					@select="$emit('select', $event)"
					@delete="$emit('delete', $event)"
				/>
			</template>
		</BuilderTree>
	</div>
</template>

<script lang="ts">
import type { WdsDropdownMenuOption } from "@/wds/WdsDropdownMenu.vue";

const rightClickDropdownOptions: WdsDropdownMenuOption[] = [
	{ label: "Delete", value: "delete", icon: "delete" },
];
</script>

<script setup lang="ts">
import { SourceFiles } from "@/writerTypes";
import { computed, PropType } from "vue";
import BuilderTree from "../BuilderTree.vue";
import BuilderCodePanelSourceFilesTree from "./BuilderCodePanelSourceFilesTree.vue";
import {
	isSourceFilesDirectory,
	isSourceFilesBinary,
} from "@/core/sourceFiles";
import WdsStateDot from "@/wds/WdsStateDot.vue";

const props = defineProps({
	sourceFiles: {
		type: Object as PropType<SourceFiles>,
		required: true,
	},
	path: { type: Array as PropType<string[]>, default: () => [] },
	pathActive: { type: Array as PropType<string[]>, default: () => [] },
	pathsUnsaved: { type: Array as PropType<string[][]>, default: () => [] },
	displayAddFileButton: { type: Boolean },
});

const emits = defineEmits({
	select: (path: string[]) => Array.isArray(path),
	delete: (path: string[]) => Array.isArray(path),
	addFile: () => true,
});

function pathToStr(path: string[]) {
	return path.join("/");
}

const pathActiveStr = computed(() => pathToStr(props.pathActive));

const pathsUnsavedStr = computed(() => props.pathsUnsaved.map(pathToStr));

const sourceFilesEntries = computed(() => {
	if (!isSourceFilesDirectory(props.sourceFiles)) return [];

	return Object.entries(props.sourceFiles.children).sort((a, b) =>
		a[0].localeCompare(b[0]),
	);
});

function isDraft(key: string) {
	const path = pathToStr([...props.path, key]);
	return pathsUnsavedStr.value.includes(path);
}

function isSelected(key: string) {
	return pathToStr([...props.path, key]) === pathActiveStr.value;
}

function handleSelect(key: string) {
	if (!isSourceFilesDirectory(props.sourceFiles)) return;

	// only allow files to be selected
	const node = props.sourceFiles.children[key];
	if (isSourceFilesDirectory(node)) return;

	emits("select", [...props.path, key]);
}

function handleDropdownSelect(action: string, key: string) {
	if (action === "delete") emits("delete", [...props.path, key]);
}
</script>

<style lang="css" scoped>
:deep(.BuilderTree__main__name) {
	text-overflow: ellipsis;
	overflow: hidden;
}
</style>
