<template>
	<div class="BuilderBlueprintLibraryItem">
		<div class="BuilderBlueprintLibraryItem__header">
			<h3 class="BuilderBlueprintLibraryItem__title">
				{{ block.title }}
			</h3>
			<span class="BuilderBlueprintLibraryItem__version"
				>v{{ block.version_number }}</span
			>
		</div>
		<p class="BuilderBlueprintLibraryItem__description">
			{{ block.description }}
		</p>
		<div class="BuilderBlueprintLibraryItem__actions">
			<WdsButton
				v-if="showDeleteButton"
				variant="neutral"
				size="small"
				:disabled="isDeleting"
				@click="handleDelete"
			>
				<WdsIcon name="trash-2" />
				{{ isDeleting ? "Deleting..." : "Delete" }}
			</WdsButton>
			<WdsButton
				variant="primary"
				size="small"
				:disabled="isInstalling"
				@click="handleInstall"
			>
				<WdsIcon name="download" />
				{{ isInstalling ? "Installing..." : "Install" }}
			</WdsButton>
		</div>
	</div>
</template>

<script setup lang="ts">
import { ref, inject, computed, onMounted } from "vue";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import { useToasts } from "../useToast";
import { useWriterTracking } from "@/composables/useWriterTracking";
import injectionKeys from "@/injectionKeys";
import { useWriterApi } from "@/composables/useWriterApi";
import { useComponentActions } from "@/builder/useComponentActions";
import {
	DEFAULT_ORG_ID,
	LOCAL_DEV_USER_ID,
} from "@/constants/sharedBlueprints";
import { fetchWriterApiCurrentUserProfile } from "@/composables/useWriterApiUser";
import type { Component } from "@/writerTypes";

const props = defineProps<{
	block: {
		id: string;
		title: string;
		description: string;
		version_number: number;
		createdBy: number;
	};
}>();

const emit = defineEmits<{
	installed: [];
	deleted: [];
}>();

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const { pushToast } = useToasts();
const tracking = useWriterTracking(wf);
const { writerApi } = useWriterApi();
const { installSharedBlueprint } = useComponentActions(wf, wfbm);
const isInstalling = ref(false);
const isDeleting = ref(false);
const currentUserId = ref<number | null>(null);

// Check if current user is the creator
const showDeleteButton = computed(() => {
	return (
		currentUserId.value !== null &&
		props.block.createdBy === currentUserId.value
	);
});

onMounted(async () => {
	try {
		const user = await fetchWriterApiCurrentUserProfile();
		currentUserId.value = user.id;
	} catch {
		// In local dev, backend uses LOCAL_DEV_USER_ID
		// Fallback to constant if we can't fetch the user profile
		currentUserId.value = LOCAL_DEV_USER_ID;
	}
});

async function handleInstall() {
	// Use default orgId for local development when writerOrgId is not available
	const orgId = wf.writerOrgId.value || DEFAULT_ORG_ID;

	isInstalling.value = true;
	try {
		// Fetch blueprint from be.agent-storage
		const blueprint = await writerApi.getSharedBlueprint(
			orgId,
			props.block.id,
		);

		// Install blueprint
		const components = blueprint.version.components as Component[];

		const _blueprintId = installSharedBlueprint({
			id: blueprint.id,
			title: blueprint.title,
			version: blueprint.version.version,
			description: blueprint.version.description || undefined,
			components,
		});

		pushToast({
			type: "success",
			message: `Blueprint "${props.block.title}" installed successfully`,
		});

		emit("installed");
	} catch (error) {
		pushToast({
			type: "error",
			message: `Failed to install blueprint: ${error instanceof Error ? error.message : String(error)}`,
		});
	} finally {
		isInstalling.value = false;
	}
}

async function handleDelete() {
	const confirmed = confirm(
		`Are you sure you want to delete "${props.block.title}"? This will permanently remove it from the shared blueprint library.`,
	);
	if (!confirmed) return;

	isDeleting.value = true;
	try {
		const orgId = wf.writerOrgId.value || DEFAULT_ORG_ID;
		await writerApi.deleteSharedBlueprint(orgId, props.block.id);

		pushToast({
			type: "success",
			message: `Blueprint "${props.block.title}" deleted successfully`,
		});

		tracking.track("blueprints_block_deleted", {
			blueprintId: props.block.id,
		});

		emit("deleted");
	} catch (error) {
		pushToast({
			type: "error",
			message: `Failed to delete blueprint: ${error instanceof Error ? error.message : String(error)}`,
		});
	} finally {
		isDeleting.value = false;
	}
}
</script>

<style scoped>
.BuilderBlueprintLibraryItem {
	display: flex;
	flex-direction: column;
	gap: 12px;
	padding: 16px;
	border: 1px solid var(--builderSeparatorColor);
	border-radius: 8px;
	background: var(--builderBackgroundColor);
	transition: border-color 0.2s;
}

.BuilderBlueprintLibraryItem:hover {
	border-color: var(--builderPrimaryColor);
}

.BuilderBlueprintLibraryItem__header {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	gap: 12px;
}

.BuilderBlueprintLibraryItem__title {
	font-size: 16px;
	font-weight: 600;
	margin: 0;
	flex: 1;
}

.BuilderBlueprintLibraryItem__version {
	font-size: 12px;
	color: var(--builderSecondaryTextColor);
	white-space: nowrap;
}

.BuilderBlueprintLibraryItem__description {
	font-size: 14px;
	color: var(--builderSecondaryTextColor);
	margin: 0;
	line-height: 1.5;
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	overflow: hidden;
}

.BuilderBlueprintLibraryItem__actions {
	display: flex;
	justify-content: flex-end;
	margin-top: auto;
}
</style>
