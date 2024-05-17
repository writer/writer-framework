<template>
	<div class="ChildlessPlaceholder">
		<div class="content">
			<div class="title">
				<h3>Empty {{ definition.name }}</h3>
			</div>
			<div v-if="message" class="message">
				{{ message }}
			</div>
		</div>
	</div>
</template>
<script setup lang="ts">
import { computed, inject, toRefs } from "vue";
import { Component } from "../writerTypes";
import injectionKeys from "../injectionKeys";

const ALLOWED_LIST_MAX_LENGTH = 10;
const wf = inject(injectionKeys.core);

interface Props {
	componentId: Component["id"];
}
const props = defineProps<Props>();
const { componentId } = toRefs(props);
const component = computed(() => wf.getComponentById(componentId.value));
const definition = computed(() =>
	wf.getComponentDefinition(component.value.type),
);

const typesToMessage = (
	types: Component["type"][],
	lastJoiner: "or" | "and",
) => {
	const definitions = types.map((type) => wf.getComponentDefinition(type));
	const names = definitions.map((def) => def?.name);
	const message = `${names.slice(0, -1).join(", ")} ${
		names.length > 1 ? lastJoiner : ""
	} ${names.at(-1)}`;
	return message;
};

const message = computed(() => {
	const containableTypes = wf.getContainableTypes(componentId.value);
	let message: string;

	if (containableTypes.length <= ALLOWED_LIST_MAX_LENGTH) {
		const typesMessage = typesToMessage(containableTypes, "and");
		message = `You can add ${typesMessage} components`;
	}

	return message;
});
</script>
<style scoped>
@import "./sharedStyles.css";

.ChildlessPlaceholder {
	background: #e4e7ed;
	color: #4f4f4f;
	padding: 16px;
	display: flex;
	align-items: center;
	justify-content: center;
	width: 100%;
	min-height: 100%;
}

.content {
	text-align: center;
}

.title > h3 {
	color: #4f4f4f;
}

.message {
	opacity: 0.5;
	margin-top: 8px;
}
</style>
