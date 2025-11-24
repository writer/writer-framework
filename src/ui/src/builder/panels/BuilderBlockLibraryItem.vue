<template>
	<div class="BuilderBlockLibraryItem">
		<div class="BuilderBlockLibraryItem__header">
			<h3 class="BuilderBlockLibraryItem__title">{{ block.title }}</h3>
			<span class="BuilderBlockLibraryItem__version"
				>v{{ block.version_number }}</span
			>
		</div>
		<p class="BuilderBlockLibraryItem__description">
			{{ block.description }}
		</p>
		<div class="BuilderBlockLibraryItem__actions">
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
const { pushToast } = useToasts();
const isInstalling = ref(false);

async function handleInstall() {
	isInstalling.value = true;
	try {
		const response = await fetch(
			`/api/block-library/blocks/${props.block.id}/install`,
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
			},
		);

		if (!response.ok) {
			const error = await response.json();
			throw new Error(error.detail || "Failed to install block");
		}

		pushToast({
			type: "success",
			message: `Block "${props.block.title}" installed successfully`,
		});

		emit("installed");

		// Reinitialize session to pick up the new block (similar to file save)
		try {
			await wf.init();
		} catch (error) {
			pushToast({
				type: "error",
				message:
					"Block installed but failed to reload. Please refresh the page.",
			});
		}
	} catch (error) {
		pushToast({
			type: "error",
			message: `Failed to install block: ${error instanceof Error ? error.message : String(error)}`,
		});
	} finally {
		isInstalling.value = false;
	}
}
</script>

<style scoped>
.BuilderBlockLibraryItem {
	display: flex;
	flex-direction: column;
	gap: 12px;
	padding: 16px;
	border: 1px solid var(--builderSeparatorColor);
	border-radius: 8px;
	background: var(--builderBackgroundColor);
	transition: border-color 0.2s;
}

.BuilderBlockLibraryItem:hover {
	border-color: var(--builderPrimaryColor);
}

.BuilderBlockLibraryItem__header {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	gap: 12px;
}

.BuilderBlockLibraryItem__title {
	font-size: 16px;
	font-weight: 600;
	margin: 0;
	flex: 1;
}

.BuilderBlockLibraryItem__version {
	font-size: 12px;
	color: var(--builderSecondaryTextColor);
	white-space: nowrap;
}

.BuilderBlockLibraryItem__description {
	font-size: 14px;
	color: var(--builderSecondaryTextColor);
	margin: 0;
	line-height: 1.5;
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	overflow: hidden;
}

.BuilderBlockLibraryItem__actions {
	display: flex;
	justify-content: flex-end;
	margin-top: auto;
}
</style>
