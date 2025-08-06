<script setup lang="ts">
import { computed, inject } from "vue";
import injectionKeys from "@/injectionKeys";
import { useComponentInformation } from "@/composables/useComponentInformation";
import { useBlueprintComponentResultId } from "@/composables/useBlueprintComponentResultId";
import { useButtonClipboard } from "@/builder/useButtonClipboard";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import SharedMoreDropdown from "@/components/shared/SharedMoreDropdown.vue";
import { useWriterTracking } from "@/composables/useWriterTracking";
import {
	BuilderSettingsDropdownActions,
	isBuilderSettingsDropdownAction,
	useBuilderSettingsActions,
} from "@/builder/settings/useBuilderSettingsActions";
import { flattenInstancePath } from "@/renderer/instancePath";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const componentId = inject(injectionKeys.componentId);
const instancePath = inject(injectionKeys.instancePath);

const props = defineProps({
	showDisplayErrorOption: { type: Boolean },
});

const emits = defineEmits({
	showError: () => true,
});

const { component, definition: def } = useComponentInformation(wf, componentId);

const resultId = useBlueprintComponentResultId(component, def);
const tracking = useWriterTracking(wf);

const { copyText: copyComponentId, isCopied: isComponentIdCopied } =
	useButtonClipboard(resultId);

const settingsActions = useBuilderSettingsActions(
	wf,
	wfbm,
	tracking,
	{},
	{
		instancePath: flattenInstancePath(instancePath),
		componentId,
	},
);

function handleDropdownSelect(value: string) {
	if (isBuilderSettingsDropdownAction(value)) {
		settingsActions.handleDropdownSelect(value);
	}

	switch (value) {
		case "showError":
			emits("showError");
			break;
	}
}

const dropdownActionsHidden = new Set([
	BuilderSettingsDropdownActions.Add,
	BuilderSettingsDropdownActions.MoveUp,
	BuilderSettingsDropdownActions.MoveDown,
	BuilderSettingsDropdownActions.Paste,
]);

const dropdownOptions = computed(() => {
	const options = settingsActions.dropdownOptions.value
		.filter(
			(o) =>
				!dropdownActionsHidden.has(
					o.value as BuilderSettingsDropdownActions,
				),
		)
		.map((o) => {
			delete o.shortcut;
			return o;
		});

	if (props.showDisplayErrorOption) {
		options.unshift({
			value: "showError",
			label: "Add error path",
			icon: "split",
		});
	}

	return options;
});
</script>

<template>
	<div class="BlueprintsNodeActions">
		<WdsButton
			v-if="resultId"
			size="smallIcon"
			variant="neutral"
			data-writer-tooltip-placement="bottom"
			:data-writer-unselectable="true"
			:data-writer-tooltip="
				isComponentIdCopied ? 'Copied!' : 'Copy result variable'
			"
			@click.prevent="copyComponentId"
		>
			<WdsIcon name="at-sign" />
		</WdsButton>
		<SharedMoreDropdown
			data-automation-action="node-actions-dropdown"
			:options="dropdownOptions"
			:data-writer-unselectable="true"
			trigger-custom-size="32px"
			trigger-icon="ellipsis-vertical"
			@select="handleDropdownSelect"
		/>
	</div>
</template>

<style scoped>
.BlueprintsNodeActions {
	display: flex;
	gap: 4px;
	justify-content: flex-end;
}
</style>
