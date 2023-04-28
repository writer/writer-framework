<template>
	<div
		class="BuilderSettingsHandlers"
		v-if="ssbm.isSelectionActive() && isNotEmpty"
	>
		<div class="sectionTitle">
			<i class="ri-flashlight-line ri-xl"></i>
			<h3>Events</h3>
		</div>
		<div class="list">
			<div
				class="fieldWrapper"
				v-for="(eventInfo, eventType) in supportedEvents"
			>
				<div class="columns">
					<div class="fieldWrapperMain">
						<span class="name">{{ eventType }}</span>
						<select
							class="content"
							:value="component.handlers?.[eventType]"
							v-on:input="handleHandlerChange($event, eventType)"
						>
							<option
								value=""
								:selected="!component.handlers?.[eventType]"
								key="No handler"
							>
								(No handler)
							</option>
							<option
								:key="userFunction"
								:value="userFunction"
								v-for="userFunction in userFunctions"
							>
								{{ userFunction }}
							</option>
							<option
								:key="`$goToPage_${pageKey}`"
								:value="`$goToPage_${pageKey}`"
								v-for="pageKey in pageKeys"
							>
								Go to page "{{ pageKey }}"
							</option>
							<template v-if="isHandlerInvalid(eventType)">
								<option
									:value="component.handlers?.[eventType]"
								>
									{{ component.handlers?.[eventType] }} (Not
									Found)
								</option>
							</template>
						</select>
					</div>
					<div class="fieldActions">
						<button
							v-if="getStubCode(eventType)"
							v-on:click="showStub(eventType)"
							variant="subtle"
							title="Show event handler stub"
						>
							<i class="ri-question-line ri-lg"></i>
						</button>
						<BuilderModal
							v-if="stubModal"
							:close-action="stubCloseAction"
							icon="question"
							:title="`&quot;${eventType}&quot; Event`"
						>
							<div class="stubMessage">
								You can use the following stub code as a
								starting point for your event handler.
							</div>
							<div class="codeContainer">
								<code
									v-dompurify-html="
										stubModal.highlightedCodeHtml
									"
								>
								</code>
							</div>
							<button
								v-on:click="copyToClipboard(stubModal.code)"
							>
								<i class="ri-file-copy-line ri-lg"></i>
								Copy code to clipboard
							</button>
						</BuilderModal>
					</div>
				</div>
				<div class="desc">{{ eventInfo.desc }}</div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import * as monaco from "monaco-editor";

import { computed, inject, Ref, ref } from "vue";
import { useComponentActions } from "./useComponentActions";
import injectionKeys from "../injectionKeys";
import BuilderModal, { ModalAction } from "./BuilderModal.vue";

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const { setHandlerValue } = useComponentActions(ss, ssbm);
const component = computed(() => ss.getComponentById(ssbm.getSelectedId()));

const supportedEvents = computed(() => {
	const { type } = component.value;
	const { events } = ss.getComponentDefinition(type);
	return events;
});

const isNotEmpty = computed((): boolean => {
	return Object.keys(supportedEvents.value ?? {}).length > 0;
});

const userFunctions = computed(() => ss.getUserFunctions());
const pageKeys = computed(() => ss.getPageKeys());

const isHandlerInvalid = (eventType: string) => {
	const userFunction = component.value.handlers?.[eventType];
	if (!userFunction) return false;

	// $ is reserved for frontend internal use, such as page change

	if (userFunction.startsWith("$")) {
		return false;
	}
	if (userFunctions.value.includes(userFunction)) return false;
	return true;
};

const handleHandlerChange = (ev: Event, eventType: string) => {
	const userFunction = (ev.target as HTMLInputElement).value;
	setHandlerValue(component.value.id, eventType, userFunction);
};

type StubModal = {
	code: string;
	highlightedCodeHtml: string;
};

const stubModal: Ref<StubModal> = ref(null);

const getStubCode = (eventType: string) => {
	const { type } = component.value;
	const { events } = ss.getComponentDefinition(type);
	const event = events[eventType];
	return event?.stub;
};

const showStub = async (eventType: string) => {
	const code = getStubCode(eventType);
	const highlightedCodeHtml = await monaco.editor.colorize(
		code,
		"python",
		{}
	);
	stubModal.value = {
		code,
		highlightedCodeHtml,
	};
};

const stubCloseAction: ModalAction = {
	desc: "Close",
	fn: () => {
		stubModal.value = null;
	},
};

const copyToClipboard = (text: string) => {
	navigator.clipboard.writeText(text);
};
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderSettingsHandlers {
	padding: 24px;
}
.list {
	border-radius: 4px;
	overflow: hidden;
}

.fieldWrapper .columns {
	display: flex;
	gap: 12px;
	align-items: center;
	max-width: 100%;
}

.fieldWrapper .content {
	padding: 16px 8px 12px 8px;
	width: 100%;
}

.fieldActions > button {
	border-radius: 16px;
}

.addHandler .fields {
	display: flex;
	gap: 16px;
	margin-bottom: 16px;
}

.stubMessage {
	font-size: 0.8rem;
}

.codeContainer {
	white-space: pre-wrap;
	background: var(--builderSubtleHighlightColorSolid);
	padding: 16px;
	border-radius: 4px;
	font-family: Consolas, monospace;
	font-size: 0.85rem;
	margin-top: 12px;
	margin-bottom: 12px;
	overflow: hidden;
	text-overflow: ellipsis;
}

.codeContainer code {
	white-space: pre-wrap;
}
</style>
