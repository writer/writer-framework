<script setup lang="ts">
import {
	computed,
	inject,
	MaybeRef,
	onMounted,
	PropType,
	readonly,
	ref,
	shallowRef,
	toRef,
	toValue,
	watch,
} from "vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import { Component, Core } from "@/writerTypes";
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
import WdsSkeletonLoader from "@/wds/WdsSkeletonLoader.vue";

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

function useAsyncResource<T>(
	func: () => Promise<T>,
	defaultData: T | undefined,
) {
	const data = shallowRef<T | undefined>(defaultData);
	const isLoading = ref(false);
	const error = shallowRef();

	async function load() {
		isLoading.value = true;
		error.value = undefined;
		try {
			data.value = await func();
		} catch (e) {
			error.value = e;
			data.value = undefined;
		} finally {
			isLoading.value = false;
		}
	}

	return { data: readonly(data), isLoading, error, load };
}

function useMcpProject(wf: Core) {
	const { data, error, isLoading, load } = useAsyncResource<WriterMcpProject>(
		async () => {
			if (!wf.isWriterCloudApp.value || !wf.writerOrgId.value) return;
			const projects = await writerApi.mcpFetchProjects(
				wf.writerOrgId.value,
			);
			return projects.at(0);
		},
		undefined,
	);

	return { project: data, isLoading, error, load };
}

function useMcpApps(projectId: MaybeRef<string | undefined>) {
	const appConfigurations = shallowRef([]);
	const functionsByAppId = shallowRef<
		Record<string, { data: WriterMcpAppFunction[]; loading?: boolean }>
	>({});

	async function loadAppFunction(c: WriterMcpAppConfiguration) {
		functionsByAppId.value = {
			...functionsByAppId.value,
			[c.appId]: { loading: true, data: [] },
		};

		const functionsRes = await writerApi.mcpFetchAppFunctions(c.appId);

		functionsByAppId.value = {
			...functionsByAppId.value,
			[c.appId]: { loading: false, data: functionsRes },
		};
	}

	async function load() {
		const pId = toValue(projectId);
		if (
			!wf.isWriterCloudApp.value ||
			!wf.writerOrgId.value ||
			pId === undefined
		)
			return;

		const allAppConfigurations: WriterMcpAppConfiguration[] = [];

		const limit = 10;

		// eslint-disable-next-line no-constant-condition
		while (true) {
			const configurationRes = await writerApi.mcpFetchAppConfigurations(
				wf.writerOrgId.value,
				pId,
				{ limit, offset: allAppConfigurations.length },
			);

			allAppConfigurations.push(...configurationRes.result);

			if (configurationRes.result.length < limit) break;
		}

		appConfigurations.value = allAppConfigurations;

		await Promise.allSettled(appConfigurations.value.map(loadAppFunction));
	}

	return { appConfigurations, functionsByAppId, load };
}

function getActivatedToolCount(conf: WriterMcpAppConfiguration) {
	const allFunctions = functionsByAppId.value[conf.appId]?.data ?? [];
	const availableFunctions = conf.allFunctionsEnabled
		? allFunctions
		: allFunctions.filter((f) => conf.enabledFunctions.includes(f.name));

	const activatedFunctionIds = activatedFunctions.value.map((f) => f.id);

	const activatedFunctionsForThisApp = availableFunctions.filter((c) =>
		activatedFunctionIds.includes(c.id),
	);

	return `${activatedFunctionsForThisApp.length} / ${availableFunctions.length}`;
}

const {
	project,
	load: loadProject,
	isLoading: isProjectLoading,
} = useMcpProject(wf);

const projectId = computed(() => project.value?.id);

onMounted(loadProject);

const {
	appConfigurations,
	functionsByAppId,
	load: loadProjectApps,
} = useMcpApps(projectId);

watch(projectId, async () => {
	await loadProjectApps();
});

const activatedFunctions = computed<WriterMcpAppFunction[]>(() => {
	try {
		const data = JSON.parse(fieldViewModel.value);
		return Array.isArray(data) ? data : [];
	} catch {
		return [];
	}
});

function toggleFunctionActivated(funcId: string) {
	if (activatedFunctions.value.some((f) => f.id === funcId)) {
		const newValue = activatedFunctions.value.filter(
			(f) => f.id !== funcId,
		);
		fieldViewModel.value = JSON.stringify(newValue);
	} else {
		fieldViewModel.value = JSON.stringify([
			...activatedFunctions.value,
			funcId,
		]);
	}
}
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
			<WdsSkeletonLoader v-if="isProjectLoading" />
			<SharedCollapsible
				v-for="conf of appConfigurations"
				v-else
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
						<WdsSkeletonLoader
							v-if="functionsByAppId[conf.appId].loading"
						/>
						<li
							v-for="func of functionsByAppId[conf.appId].data"
							v-else
							:key="func.id"
						>
							<WdsCheckbox
								:label="func.name"
								:detail="func.description"
								:disabled="
									!conf.allFunctionsEnabled &&
									!conf.enabledFunctions.includes(func.name)
								"
								:model-value="
									activatedFunctions.includes(func.id)
								"
								@update:model-value="
									toggleFunctionActivated(func.id)
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
	padding-top: 8px;
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
	display: flex;
	flex-direction: column;
	gap: 4px;
}
</style>
