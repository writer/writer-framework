<template>
	<WdsModal
		v-if="isOpen && isBlueprintLibraryEnabled"
		title="Blueprint Library"
		size="wide"
		display-close-button
		@close="handleClose"
	>
		<div class="BuilderBlueprintLibraryPanel">
			<div class="BuilderBlueprintLibraryPanel__header">
				<div class="BuilderBlueprintLibraryPanel__search">
					<WdsTextInput
						v-model="searchQuery"
						placeholder="Search blueprints..."
						left-icon="search"
					/>
				</div>
			</div>

			<div class="BuilderBlueprintLibraryPanel__content">
				<WdsSkeletonLoader
					v-if="isLoading"
					class="BuilderBlueprintLibraryPanel__loading"
				/>

				<div
					v-else-if="blueprints.length === 0"
					class="BuilderBlueprintLibraryPanel__empty"
				>
					<p>No blueprints found</p>
					<p
						v-if="searchQuery"
						class="BuilderBlueprintLibraryPanel__empty__hint"
					>
						Try adjusting your search
					</p>
				</div>

				<div v-else class="BuilderBlueprintLibraryPanel__sections">
					<SharedCollapsible
						v-if="globalBlueprints.length > 0"
						class="BuilderBlueprintLibraryPanel__section"
						:open="true"
						:icons="{
							open: 'chevron-down',
							close: 'chevron-right',
						}"
					>
						<template #title>
							<span
								class="BuilderBlueprintLibraryPanel__sectionTitle"
							>
								Agents for everyone
							</span>
						</template>
						<template #content>
							<div class="BuilderBlueprintLibraryPanel__grid">
								<BuilderBlueprintLibraryItem
									v-for="blueprint in globalBlueprints"
									:key="blueprint.id"
									:block="blueprint"
								/>
							</div>
						</template>
					</SharedCollapsible>

					<SharedCollapsible
						v-if="orgBlueprints.length > 0"
						class="BuilderBlueprintLibraryPanel__section"
						:open="true"
						:icons="{
							open: 'chevron-down',
							close: 'chevron-right',
						}"
					>
						<template #title>
							<span
								class="BuilderBlueprintLibraryPanel__sectionTitle"
							>
								Agents for your organization
							</span>
						</template>
						<template #content>
							<div class="BuilderBlueprintLibraryPanel__grid">
								<BuilderBlueprintLibraryItem
									v-for="blueprint in orgBlueprints"
									:key="blueprint.id"
									:block="blueprint"
								/>
							</div>
						</template>
					</SharedCollapsible>
				</div>
			</div>
		</div>
	</WdsModal>
</template>

<script setup lang="ts">
import { ref, computed, watch, inject } from "vue";
import WdsModal from "@/wds/WdsModal.vue";
import BuilderBlueprintLibraryItem from "./BuilderBlueprintLibraryItem.vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";
import WdsSkeletonLoader from "@/wds/WdsSkeletonLoader.vue";
import SharedCollapsible from "@/components/shared/SharedCollapsible.vue";
import injectionKeys from "@/injectionKeys";
import { useToasts } from "../useToast";
import { useDebouncer } from "@/composables/useDebouncer";
import { useWriterApi } from "@/composables/useWriterApi";

const isOpen = defineModel({ type: Boolean });

const wf = inject(injectionKeys.core);
const { pushToast } = useToasts();
const { writerApi } = useWriterApi();

const isBlueprintLibraryEnabled = computed(
	() =>
		Array.isArray(wf.featureFlags.value) &&
		wf.featureFlags.value.includes("blueprint_library"),
);

const searchQuery = ref("");
const blueprints = ref<
	Array<{
		id: string;
		title: string;
		description: string;
		category: string;
		visibility: string;
		createdBy: number;
	}>
>([]);
const isLoading = ref(false);

const globalBlueprints = computed(() =>
	blueprints.value.filter((bp) => bp.visibility === "GLOBAL"),
);
const orgBlueprints = computed(() =>
	blueprints.value.filter((bp) => bp.visibility === "ORG"),
);

async function loadBlueprints() {
	if (!isBlueprintLibraryEnabled.value) return;

	const orgId = wf.writerOrgId.value;
	if (!orgId) {
		pushToast({
			type: "error",
			message:
				"Organization ID is required. Please set up your environment variable.",
		});
		isLoading.value = false;
		return;
	}

	isLoading.value = true;
	try {
		const results = await writerApi.listSharedBlueprints(
			orgId,
			searchQuery.value || undefined,
		);

		// Transform to match frontend format
		blueprints.value = results.map((bp) => ({
			id: bp.id,
			title: bp.title,
			description: bp.description,
			category: bp.category || "Shared Blueprints",
			visibility: bp.visibility,
			createdBy: bp.createdBy,
		}));
	} catch (error) {
		pushToast({
			type: "error",
			message: `Failed to load blueprints: ${error instanceof Error ? error.message : String(error)}`,
		});
	} finally {
		isLoading.value = false;
	}
}

const debouncedLoadBlueprints = useDebouncer(loadBlueprints, 300);

watch(searchQuery, debouncedLoadBlueprints);

function handleClose() {
	isOpen.value = false;
}

watch(isOpen, (newValue) => {
	if (newValue && isBlueprintLibraryEnabled.value) {
		loadBlueprints();
	}
});
</script>

<style scoped>
.BuilderBlueprintLibraryPanel {
	display: flex;
	flex-direction: column;
	height: 100%;
	max-height: 80vh;
}

.BuilderBlueprintLibraryPanel__header {
	display: flex;
	gap: 12px;
	padding: 16px;
	border-bottom: 1px solid var(--builderSeparatorColor);
	align-items: center;
	flex-shrink: 0;
}

.BuilderBlueprintLibraryPanel__search {
	flex: 1;
}

.BuilderBlueprintLibraryPanel__content {
	flex: 1;
	overflow-y: auto;
	min-height: 0;
}

.BuilderBlueprintLibraryPanel__sections {
	display: flex;
	flex-direction: column;
	gap: 24px;
	padding: 16px;
}

.BuilderBlueprintLibraryPanel__section {
	--accentColor: var(--builderSecondaryTextColor);
}

.BuilderBlueprintLibraryPanel__section :deep(.content) {
	padding-top: 12px;
	padding-left: 0;
}

.BuilderBlueprintLibraryPanel__sectionTitle {
	font-size: 14px;
	font-weight: 600;
	color: var(--builderSecondaryTextColor);
	text-transform: uppercase;
	letter-spacing: 0.5px;
}

.BuilderBlueprintLibraryPanel__grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
	gap: 16px;
}

.BuilderBlueprintLibraryPanel__loading,
.BuilderBlueprintLibraryPanel__empty {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 48px;
	color: var(--builderSecondaryTextColor);
	text-align: center;
}

.BuilderBlueprintLibraryPanel__empty__hint {
	font-size: 12px;
	margin-top: 8px;
}
</style>
