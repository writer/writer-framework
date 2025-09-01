<script setup lang="ts">
import { computed, inject, onMounted, PropType, shallowRef, toRef } from "vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import { Component } from "@/writerTypes";
import { useComponentFieldViewModel } from "../useComponentFieldViewModel";
import { useWriterApi } from "@/composables/useWriterApi";
import { useAbortController } from "@/composables/useAbortController";
import injectionKeys from "@/injectionKeys";
import {
	WriterMcpAppConfiguration,
	WriterMcpAppFunction,
	WriterMcpProject,
} from "@/writerApi";
import WdsCheckbox from "@/wds/WdsCheckbox.vue";
import SharedCollapsible from "@/components/shared/SharedCollapsible.vue";

const props = defineProps({
	componentId: { type: String as PropType<Component["id"]>, required: true },
	fieldKey: { type: String, required: true },
	label: { type: String, default: undefined },
	unit: { type: String, default: undefined },
	hint: { type: String, default: undefined },
	error: { type: String, default: undefined },
});

const fieldViewModel = useComponentFieldViewModel({
	componentId: toRef(props, "componentId"),
	fieldKey: toRef(props, "fieldKey"),
});

const wf = inject(injectionKeys.core);

const abort = useAbortController();
const { writerApi } = useWriterApi({ signal: abort.signal });

function useMcp() {
	const project = shallowRef<WriterMcpProject | undefined>();
	const appConfigurations = shallowRef<WriterMcpAppConfiguration[]>([]);
	const functionsByAppId = shallowRef<Record<string, WriterMcpAppFunction[]>>(
		{},
	);

	async function loadAppFunction(c: WriterMcpAppConfiguration) {
		const functionsRes = await writerApi.mcpFetchAppFunctions(c.appId);

		functionsByAppId.value = {
			...functionsByAppId.value,
			[c.appId]: functionsRes,
		};
	}

	onMounted(async () => {
		if (!wf.isWriterCloudApp.value || !wf.writerOrgId.value) return;
		const projects = await writerApi.mcpFetchProjects(wf.writerOrgId.value);
		// TODO: create the project ?
		project.value = projects.at(0);

		const configurationRes = await writerApi.mcpFetchAppConfigurations(
			wf.writerOrgId.value,
			project.value.id,
		);
		appConfigurations.value = configurationRes.result;

		await Promise.allSettled(appConfigurations.value.map(loadAppFunction));
	});

	return { project, appConfigurations, functionsByAppId };
}

function getActivatedToolCount(conf: WriterMcpAppConfiguration) {
	const allToolsCount = functionsByAppId.value[conf.appId]?.length ?? 0;
	const activatedToolsCount = conf.allFunctionsEnabled
		? allToolsCount
		: conf.enabledFunctions.length;
	return `${activatedToolsCount} / ${allToolsCount}`;
}

const { appConfigurations, functionsByAppId } = useMcp();

const model = computed<boolean>({
	get: () => fieldViewModel.value === "yes",
	set: (checked) => {
		fieldViewModel.value = checked ? "yes" : "no";
	},
});
</script>

<template>
	<WdsFieldWrapper
		:label
		:unit
		:hint
		:error
		:data-automation-key="props.fieldKey"
	>
		<div class="BuilderFieldsMCPTools__content">
			<SharedCollapsible
				v-for="conf of appConfigurations"
				:key="conf.id"
				:icons="{ close: 'chevron-down', open: 'chevron-up' }"
			>
				<template #title>
					<div class="BuilderFieldsMCPTools__content__app__title">
						<img
							:src="conf.app.logo"
							:alt="`Logo of app ${conf.app.displayName}`"
						/>

						<span
							class="BuilderFieldsMCPTools__content__app__title__name"
							>{{ conf.app.displayName }}</span
						>
						<span
							class="BuilderFieldsMCPTools__content__app__title__count"
							>{{ getActivatedToolCount(conf) }}</span
						>
					</div>
				</template>

				<template #content>
					<ul
						v-if="functionsByAppId[conf.appId]"
						class="BuilderFieldsMCPTools__content__functions"
					>
						<li
							v-for="func of functionsByAppId[conf.appId]"
							:key="func.id"
						>
							<WdsCheckbox
								:label="func.name"
								:detail="func.description"
								:disabled="
									!conf.allFunctionsEnabled &&
									!conf.enabledFunctions.includes(func.name)
								"
							/>
						</li>
					</ul>
				</template>
			</SharedCollapsible>
		</div>
	</WdsFieldWrapper>
</template>

<style scoped>
.BuilderFieldsMCPTools__content {
	display: flex;
	flex-direction: column;
	gap: 8px;
}
.BuilderFieldsMCPTools__content__app__title {
	display: grid;
	gap: 8px;
	align-items: center;
	grid-template-columns: 24px 1fr auto;
	width: 100%;
}
.BuilderFieldsMCPTools__content__app__title img {
	max-width: 24px;
	max-height: 24px;
}
.BuilderFieldsMCPTools__content__app__title__name {
	font-weight: 500;
}
.BuilderFieldsMCPTools__content__app__title__count {
	color: var(--wdsColorGray4);
}

.BuilderFieldsMCPTools__content__functions {
	list-style: none;
	margin-top: 12px;
}
</style>
