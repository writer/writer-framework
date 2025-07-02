<script setup lang="ts">
import Fuse from "fuse.js";
import { computed, inject } from "vue";
import {
	DynamicUserState,
	useDynamicUserState,
} from "../useDynamicUserStateV2";
import injectionKeys from "@/injectionKeys";
import BuilderStateSelectorDropdownComponent from "./BuilderStateSelectorDropdownComponent.vue";
import { WdsDropdownMenuOption } from "@/wds/WdsDropdownMenu.vue";
import { extractObjectPaths } from "@/utils/object";
import WdsDropdownMenuItem from "@/wds/WdsDropdownMenuItem.vue";
import { WdsColor } from "@/wds/tokens";

const wf = inject(injectionKeys.core)!;
const secretsManager = inject(injectionKeys.secretsManager)!;

const props = defineProps({
	componentId: { type: String, required: false, default: undefined },
	query: { type: String, required: false, default: "" },
	allowCreate: { type: Boolean, required: false },
	hideSecrets: { type: Boolean, required: false },
	hideBlueprintResults: { type: Boolean, required: false },
});

const model = defineModel({ type: String });

const dynamicState = useDynamicUserState(wf);

const userState = computed<WdsDropdownMenuOption[]>(() => {
	const options: WdsDropdownMenuOption[] = [];
	for (const path of extractObjectPaths(wf.userStateInitial.value)) {
		if (props.query && !path.includes(props.query)) continue;
		options.push({
			value: path,
			label: path,
			icon: "code",
			iconBgColor: WdsColor.Green2,
		});
	}
	return options.sort((a, b) => a.label.localeCompare(b.label));
});

const secrets = computed<WdsDropdownMenuOption[]>(() => {
	if (props.hideSecrets) return [];

	const options: WdsDropdownMenuOption[] = [];
	for (const path of extractObjectPaths(secretsManager.secrets.value)) {
		const value = `vault.${path}`;
		if (props.query && !value.includes(props.query)) continue;
		options.push({
			value: `vault.${path}`,
			label: path,
			icon: "key",
			iconBgColor: WdsColor.Yellow2,
		});
	}
	options.sort((a, b) => a.label.localeCompare(b.label));
	return filterOptions(options);
});

const bindingsUserState = computed(() =>
	computeOptionsFromDynamicState(dynamicState.bindingsUserState.value),
);
const blueprintsUserState = computed(() =>
	computeOptionsFromDynamicState(dynamicState.blueprintsUserState.value),
);
const blueprintsResults = computed(() => {
	if (props.hideBlueprintResults) return [];
	return computeOptionsFromDynamicState(dynamicState.blueprintsResults.value);
});

function filterOptions(options: WdsDropdownMenuOption[]) {
	if (!props.query) return options;

	const fuse = new Fuse(options, {
		findAllMatches: true,
		includeMatches: true,
		keys: ["value"],
	});

	return fuse.search(props.query).map((res) => res.item);
}

function computeOptionsFromDynamicState(dynamicState: DynamicUserState) {
	return Object.entries(dynamicState).flatMap(([path, { components }]) => {
		if (props.query && !path.includes(props.query)) return [];

		const options = components
			.filter((component) => component.id !== props.componentId)
			.map((component) => ({
				componentId: component.id,
				path,
			}));

		if (!props.query) return options;

		const fuse = new Fuse(options, {
			findAllMatches: true,
			includeMatches: true,
			keys: ["path"],
		});

		return fuse.search(props.query).map((res) => res.item);
	});
}

const hasExactMatch = computed(() => {
	return (
		userState.value.some((i) => i.value === props.query) ||
		secrets.value.some((i) => i.value === props.query) ||
		blueprintsResults.value.some((i) => i.path === props.query) ||
		bindingsUserState.value.some((i) => i.path === props.query)
	);
});

const hasResult = computed(() => {
	if (userState.value.length) return true;
	if (blueprintsUserState.value.length) return true;
	if (bindingsUserState.value.length) return true;
	if (blueprintsResults.value.length) return true;
	if (secrets.value.length) return true;
	return false;
});
</script>

<template>
	<div class="BuilderStateSelectorDropdown">
		<template v-if="allowCreate && query && !hasExactMatch">
			<p class="BuilderStateSelectorDropdown__section__title">
				Add new variable
			</p>
			<WdsDropdownMenuItem
				:option="{
					value: query,
					label: query,
					icon: 'add',
					iconBgColor: WdsColor.Blue4,
					iconColor: WdsColor.White,
				}"
				@click.stop="model = query"
			/>
		</template>
		<div v-else-if="!hasResult" class="BuilderStateSelectorDropdown__empty">
			No result
		</div>
		<div
			v-if="blueprintsUserState.length"
			class="BuilderStateSelectorDropdown__section"
		>
			<p class="BuilderStateSelectorDropdown__section__title">
				Set states
			</p>
			<BuilderStateSelectorDropdownComponent
				v-for="s of blueprintsUserState"
				:key="s.path"
				:path="s.path"
				:component-id="s.componentId"
				:selected="s.path === model"
				@click.stop="model = s.path"
			/>
		</div>
		<div
			v-if="bindingsUserState.length"
			class="BuilderStateSelectorDropdown__section"
		>
			<p class="BuilderStateSelectorDropdown__section__title">
				Interface variables
			</p>
			<BuilderStateSelectorDropdownComponent
				v-for="s of bindingsUserState"
				:key="s.path"
				:path="s.path"
				:component-id="s.componentId"
				:selected="s.path === model"
				@click.stop="model = s.path"
			/>
		</div>
		<div
			v-if="!hideBlueprintResults && blueprintsResults.length"
			class="BuilderStateSelectorDropdown__section"
		>
			<p class="BuilderStateSelectorDropdown__section__title">
				block results
			</p>
			<BuilderStateSelectorDropdownComponent
				v-for="s of blueprintsResults"
				:key="s.path"
				:path="s.path"
				:component-id="s.componentId"
				:selected="s.path === model"
				@click.stop="model = s.path"
			/>
		</div>
		<div
			v-if="!hideSecrets && secrets.length"
			class="BuilderStateSelectorDropdown__section"
		>
			<p class="BuilderStateSelectorDropdown__section__title">Secrets</p>
			<WdsDropdownMenuItem
				v-for="option of secrets"
				:key="option.value"
				:option
				:selected="option.value === model"
				@click.stop="model = option.value"
			/>
		</div>
		<div
			v-if="userState.length"
			class="BuilderStateSelectorDropdown__section"
		>
			<p class="BuilderStateSelectorDropdown__section__title">
				main.py variables
			</p>
			<WdsDropdownMenuItem
				v-for="option of userState"
				:key="option.value"
				:option
				:selected="option.value === model"
				@click.stop="model = option.value"
			/>
		</div>
	</div>
</template>

<style lang="css" scoped>
.BuilderStateSelectorDropdown {
	border: 1px solid var(--wdsColorGray2);
	background: #fff;
	z-index: 2;
	width: 100%;
	max-height: 40vh;
	overflow-y: auto;
	border-radius: 8px;

	padding: 8px 10px;

	box-shadow: var(--wdsShadowMenu);
	box-sizing: border-box;
}
.BuilderStateSelectorDropdown__empty {
	color: var(--wdsColorGray4);
}
.BuilderStateSelectorDropdown__section__title {
	text-transform: uppercase;
	margin: 12px 4px;
	margin-bottom: 0px;
	font-size: 13px;
	font-weight: 500;
}

.BuilderStateSelectorDropdown__section:not(:last-child) {
	border-bottom: 1px solid var(--wdsColorGray2);
	padding-bottom: 8px;
	margin-bottom: 8px;
}
</style>
