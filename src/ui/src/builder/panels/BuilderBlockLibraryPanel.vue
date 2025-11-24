<template>
	<WdsModal
		v-if="isOpen && isCustomBlocksEnabled"
		title="Block Library"
		size="wide"
		display-close-button
		@close="handleClose"
	>
		<div class="BuilderBlockLibraryPanel">
			<div class="BuilderBlockLibraryPanel__header">
				<div class="BuilderBlockLibraryPanel__search">
					<WdsTextInput
						v-model="searchQuery"
						placeholder="Search blocks..."
						left-icon="search"
					/>
				</div>
				<div class="BuilderBlockLibraryPanel__filters">
					<WdsDropdownInput
						v-model="selectedCategory"
						placeholder="All categories"
					>
						<option value="">All categories</option>
						<option value="Logic">Logic</option>
						<option value="File Processing">File Processing</option>
						<option value="Data Transformation">
							Data Transformation
						</option>
						<option value="API Integration">API Integration</option>
						<option value="Text Processing">Text Processing</option>
						<option value="Utilities">Utilities</option>
						<option value="Other">Other</option>
					</WdsDropdownInput>
				</div>
				<WdsButton
					variant="primary"
					size="small"
					@click.stop="showCreateModal"
				>
					<WdsIcon name="plus" />
					Create Block
				</WdsButton>
			</div>

			<div class="BuilderBlockLibraryPanel__content">
				<div v-if="isLoading" class="BuilderBlockLibraryPanel__loading">
					<p>Loading blocks...</p>
				</div>

				<div
					v-else-if="blocks.length === 0"
					class="BuilderBlockLibraryPanel__empty"
				>
					<p>No blocks found</p>
					<p
						v-if="searchQuery || selectedCategory"
						class="BuilderBlockLibraryPanel__empty__hint"
					>
						Try adjusting your search or filters
					</p>
				</div>

				<div v-else class="BuilderBlockLibraryPanel__grid">
					<BuilderBlockLibraryItem
						v-for="block in blocks"
						:key="block.id"
						:block="block"
						@installed="handleBlockInstalled"
					/>
				</div>
			</div>
		</div>
	</WdsModal>

	<BuilderSettingsBlockLibrary
		v-if="isCreateModalShown"
		v-model="isCreateModalShown"
		@created="handleBlockCreated"
	/>
</template>

<script setup lang="ts">
import { ref, computed, watch, inject, nextTick } from "vue";
import WdsModal from "@/wds/WdsModal.vue";
import BuilderBlockLibraryItem from "./BuilderBlockLibraryItem.vue";
import BuilderSettingsBlockLibrary from "../settings/BuilderSettingsBlockLibrary.vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";
import WdsDropdownInput from "@/wds/WdsDropdownInput.vue";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import injectionKeys from "@/injectionKeys";
import { useToasts } from "../useToast";
import { useDebouncer } from "@/composables/useDebouncer";

const props = defineProps<{
	modelValue: boolean;
}>();

const emit = defineEmits<{
	"update:modelValue": [value: boolean];
}>();

const wf = inject(injectionKeys.core);
const { pushToast } = useToasts();

const isOpen = computed({
	get: () => props.modelValue,
	set: (value) => emit("update:modelValue", value),
});

const isCustomBlocksEnabled = computed(
	() =>
		Array.isArray(wf.featureFlags.value) &&
		wf.featureFlags.value.includes("custom_blocks"),
);

const searchQuery = ref("");
const selectedCategory = ref("");
const blocks = ref<
	Array<{
		id: string;
		title: string;
		description: string;
		category: string;
		version_number: number;
	}>
>([]);
const isLoading = ref(false);
const isCreateModalShown = ref(false);

async function loadBlocks() {
	if (!isCustomBlocksEnabled.value) return;

	isLoading.value = true;
	try {
		const params = new URLSearchParams();
		if (searchQuery.value) {
			params.append("search", searchQuery.value);
		}
		if (selectedCategory.value) {
			params.append("category", selectedCategory.value);
		}

		const response = await fetch(
			`/api/block-library/blocks?${params.toString()}`,
		);
		if (!response.ok) {
			throw new Error("Failed to load blocks");
		}

		blocks.value = await response.json();
	} catch (error) {
		pushToast({
			type: "error",
			message: `Failed to load blocks: ${error instanceof Error ? error.message : String(error)}`,
		});
	} finally {
		isLoading.value = false;
	}
}

async function showCreateModal() {
	// Close the Block Library modal temporarily to avoid z-index issues
	isOpen.value = false;
	// Use nextTick to ensure the modal closes before opening the create modal
	await nextTick();
	isCreateModalShown.value = true;
}

async function handleBlockCreated() {
	isCreateModalShown.value = false;
	await loadBlocks();
	// Reopen the Block Library modal after the block is created
	await nextTick();
	isOpen.value = true;
}

function handleBlockInstalled() {
	// Block will reinitialize the session, so no need to do anything here
}

// Debounced load function
const debouncedLoadBlocks = useDebouncer(loadBlocks, 300);

// Load blocks on mount and when filters change
watch([searchQuery, selectedCategory], () => {
	debouncedLoadBlocks();
});

function handleClose() {
	isOpen.value = false;
}

// Load blocks when modal opens
watch(isOpen, (newValue) => {
	if (newValue && isCustomBlocksEnabled.value) {
		loadBlocks();
	}
});
</script>

<style scoped>
.BuilderBlockLibraryPanel {
	display: flex;
	flex-direction: column;
	height: 100%;
	max-height: 80vh;
}

.BuilderBlockLibraryPanel__header {
	display: flex;
	gap: 12px;
	padding: 16px;
	border-bottom: 1px solid var(--builderSeparatorColor);
	align-items: center;
	flex-shrink: 0;
}

.BuilderBlockLibraryPanel__search {
	flex: 1;
}

.BuilderBlockLibraryPanel__filters {
	min-width: 200px;
}

.BuilderBlockLibraryPanel__content {
	flex: 1;
	overflow-y: auto;
	min-height: 0;
}

.BuilderBlockLibraryPanel__grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
	gap: 16px;
	padding: 16px;
}

.BuilderBlockLibraryPanel__loading,
.BuilderBlockLibraryPanel__empty {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 48px;
	color: var(--builderSecondaryTextColor);
	text-align: center;
}

.BuilderBlockLibraryPanel__empty__hint {
	font-size: 12px;
	margin-top: 8px;
}
</style>
