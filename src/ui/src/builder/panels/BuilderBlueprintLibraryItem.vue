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
import { ref, inject } from "vue";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import { useToasts } from "../useToast";
import injectionKeys from "@/injectionKeys";
import { useWriterApi } from "@/composables/useWriterApi";
import { useComponentActions } from "@/builder/useComponentActions";
import type { Component } from "@/writerTypes";

const props = defineProps<{
	block: {
		id: string;
		title: string;
		description: string;
		version_number: number;
	};
}>();

const emit = defineEmits<{
	installed: [];
}>();

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const { pushToast } = useToasts();
const { writerApi } = useWriterApi();
const { installSharedBlueprint } = useComponentActions(wf, wfbm);
const isInstalling = ref(false);

async function handleInstall() {
	const orgId = wf.writerOrgId.value;
	if (!orgId) {
		pushToast({
			type: "error",
			message:
				"Organization ID is required. Please set up your environment variable.",
		});
		return;
	}

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
