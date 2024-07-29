<template>
	<div class="WorkflowsNodeBox">
		<div class="title">{{ def.name }}</div>
		<div class="main">
			<slot></slot>
		</div>
		<div class="outputs">
			<div v-for="(out, outId) in def.outs" :key="outId" class="output">
				{{ out.name }}
				<div
					class="ball"
					:class="out.style"
					:data-writer-socket-id="outId"
					:data-writer-unselectable="true"
					@click.capture="
						(ev: DragEvent) => handleOutClick(ev, outId)
					"
				></div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import { Component } from "../writerTypes";
import injectionKeys from "../injectionKeys";

const wf = inject(injectionKeys.core);

const props = defineProps<{
	component: Component;
}>();

const def = computed(() => {
	return wf?.getComponentDefinition(props.component.type);
});

const emit = defineEmits(["outSelect"]);

function handleOutClick(ev: DragEvent, outId: string) {
	ev.stopPropagation();
	emit("outSelect", outId);
}
</script>

<style scoped>
@import "../renderer/sharedStyles.css";

.WorkflowsNodeBox {
	background: var(--builderBackgroundColor);
	border-radius: 12px;
	width: 240px;
	position: absolute;
	box-shadow: 0px 2px 0px 0px rgba(0, 0, 0, 0.03);
}

.title {
	background: #ede2ff;
	padding: 12px 16px 12px 16px;
	border-radius: 12px 12px 0 0;
	border-top: 1px solid var(--builderSeparatorColor);
	border-left: 1px solid var(--builderSeparatorColor);
	border-right: 1px solid var(--builderSeparatorColor);
}

.main {
	font-size: 12.5px;
	padding: 12px 16px 12px 16px;
	border-left: 1px solid var(--builderSeparatorColor);
	border-right: 1px solid var(--builderSeparatorColor);
}

.outputs {
	border: 1px solid var(--builderSeparatorColor);
	border-radius: 0 0 12px 12px;
	display: flex;
	flex-direction: column;
	gap: 8px;
	padding: 12px 0 12px 16px;
}

.output {
	display: flex;
	gap: 8px;
	align-items: center;
	justify-content: right;
	font-size: 10px;
	font-style: normal;
	font-weight: 500;
	letter-spacing: 1.3px;
	text-transform: uppercase;
}

.output .ball {
	margin-right: -8px;
	height: 16px;
	width: 16px;
	border-radius: 50%;
	border: 1px solid var(--builderBackgroundColor);
	cursor: pointer;
}

.output .ball.success {
	background: var(--builderSuccessColor);
}

.output .ball.error {
	background: var(--builderErrorColor);
}
</style>
