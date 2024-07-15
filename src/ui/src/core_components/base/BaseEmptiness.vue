<template>
	<div v-if="displayEmpty" class="BaseEmptiness">
		<div class="content">
			<div class="title">
				<h3>Empty {{ definition.name }}</h3>
			</div>
			<div v-if="message" class="message">
				{{ message }}
			</div>
		</div>
	</div>
	<slot v-else-if="displayContent" />
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import injectionKeys from "../../injectionKeys";

const props = defineProps({
	componentId: { type: String, required: true },
	message: { type: String, required: false, default: undefined },
	isEmpty: { type: Boolean },
});

const wf = inject(injectionKeys.core);
const component = computed(() => wf.getComponentById(props.componentId));
const definition = computed(() =>
	wf.getComponentDefinition(component.value.type),
);

const isBeingEdited = inject(injectionKeys.isBeingEdited);

const displayEmpty = computed(() => isBeingEdited.value && props.isEmpty);
const displayContent = computed(() => !displayEmpty.value && !props.isEmpty);
</script>
<style scoped>
@import "../../renderer/sharedStyles.css";

.BaseEmptiness {
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
