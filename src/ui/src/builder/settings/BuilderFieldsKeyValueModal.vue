<template>
	<WdsModal
		title="Category key values"
		display-close-button
		:actions="actions"
		@close="$emit('close')"
	>
		<template #titleActions>
			<WdsTabs
				v-model="mode"
				class="BuilderFieldsKeyValueModal__tabs"
				:tabs="tabs"
			/>
		</template>

		<template #default>
			<BuilderEmbeddedCodeEditor
				v-if="mode === 'freehand'"
				variant="minimal"
				:model-value="draftStr"
				language="json"
			/>
			<BuilderFieldsKeyValueEditor
				v-if="mode === 'assisted'"
				v-model="draft"
			/>
		</template>
	</WdsModal>
</template>

<script setup lang="ts">
import {
	PropType,
	Ref,
	computed,
	defineAsyncComponent,
	ref,
	toRef,
	watch,
} from "vue";
import WdsTabs, { WdsTabOptions } from "@/wds/WdsTabs.vue";
import WdsModal, { ModalAction } from "@/wds/WdsModal.vue";
import BuilderAsyncLoader from "../BuilderAsyncLoader.vue";
import type { JSONValue } from "./BuilderFieldsKeyValue.vue";
import BuilderFieldsKeyValueEditor from "./BuilderFieldsKeyValueEditor.vue";

const BuilderEmbeddedCodeEditor = defineAsyncComponent({
	loader: () => import("../BuilderEmbeddedCodeEditor.vue"),
	loadingComponent: BuilderAsyncLoader,
});

type Mode = "assisted" | "freehand";

const props = defineProps({
	data: {
		type: Object as PropType<JSONValue>,
		required: true,
	},
});

const emits = defineEmits({
	submit: (data: JSONValue) => typeof data === "object" && data !== undefined,
	close: () => true,
});

const draft = ref(props.data);

watch(toRef(props, "data"), (newValue) => (draft.value = newValue));

const draftStr = computed(() => JSON.stringify(draft.value, undefined, 2));

const actions = computed<ModalAction[]>(() => [
	{
		desc: "Save",
		fn: () => emits("submit", draft.value),
		disabled: JSON.stringify(props.data) === draftStr.value,
	},
]);

const mode: Ref<Mode> = ref("assisted");

const tabs: WdsTabOptions<Mode>[] = [
	{ label: "Static List", value: "assisted" },
	{ label: "JSON", value: "freehand" },
];
</script>

<style scoped>
.BuilderFieldsKeyValueModal__assisted {
}
</style>
