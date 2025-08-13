<template>
	<div class="BuilderSettingsArtifactAPITriggerDetails">
		<WdsTitle2>Test your trigger</WdsTitle2>
		<WdsTabs
			v-model="tab"
			class="BuilderSettingsArtifactAPITriggerDetails__tabs"
			:tabs="tabs"
		/>
		<div
			v-if="tab === 'builder'"
			class="BuilderSettingsArtifactAPITriggerDetails__builder"
		>
			<div
				v-for="[fieldKey, fieldValue] in artifactFields"
				:key="fieldKey"
				class="BuilderSettingsArtifactAPITriggerDetails__field"
			>
				<!-- Only one field expected in this artifact -->
				<WdsFieldWrapper
					:label="fieldValue.name ?? fieldKey"
					:hint="fieldValue.desc"
					:is-expansible="true"
				>
					<BuilderFieldsCode
						v-if="fieldValue.type == FieldType.Code"
						:field-key="fieldKey"
						:component-id="component?.id ?? ''"
						:is-expanded="false"
						input-language="json"
					/>
				</WdsFieldWrapper>
			</div>
		</div>

		<div v-else class="BuilderSettingsArtifactAPITriggerDetails__api">
			<ol class="BuilderSettingsArtifactAPITriggerDetails__steps">
				<li
					id="stepCreate"
					class="BuilderSettingsArtifactAPITriggerDetails__step"
				>
					<p
						class="BuilderSettingsArtifactAPITriggerDetails__step__hint"
					>
						Paste the CURL command into your terminal
					</p>
					<WdsButton
						variant="tertiary"
						size="small"
						@click="copyCreate()"
					>
						<WdsIcon
							:name="isCreateCopied ? 'check' : 'clipboard'"
						/>

						Copy cURL command
					</WdsButton>
				</li>
				<li
					id="stepPaste"
					class="BuilderSettingsArtifactAPITriggerDetails__step"
				>
					<p
						class="BuilderSettingsArtifactAPITriggerDetails__step__hint"
					>
						Once the job has run, paste the result here:
					</p>
					<WdsTextareaInput
						v-model="apiOutput"
						placeholder="Paste cURL output here"
					/>
				</li>
				<li
					id="stepPoll"
					class="BuilderSettingsArtifactAPITriggerDetails__step"
				>
					<p
						class="BuilderSettingsArtifactAPITriggerDetails__step__hint"
					>
						Lastly, paste the poll async into your terminal to
						retrieve your artifact
					</p>
					<WdsButton
						variant="tertiary"
						size="small"
						:disabled="isPollDisabled"
						@click="copyPoll()"
					>
						<WdsIcon :name="isPollCopied ? 'check' : 'clipboard'" />
						Copy poll async
					</WdsButton>
				</li>
			</ol>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, ref } from "vue";
import injectionKeys from "@/injectionKeys";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import WdsTabs, { WdsTabOptions } from "@/wds/WdsTabs.vue";
import WdsTextareaInput from "@/wds/WdsTextareaInput.vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import BuilderFieldsCode from "./BuilderFieldsCode.vue";
import { useClipboard } from "@vueuse/core";
import WdsTitle2 from "@/wds/WdsTitle2.vue";
import { FieldType } from "@/writerTypes";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const component = computed(() =>
	wf.getComponentById(ssbm.firstSelectedId.value),
);
const blueprintId = computed(() => component.value?.parentId ?? "");

const componentDefinition = computed(() => {
	if (!component.value) return null;
	return wf.getComponentDefinition(component.value.type);
});

const artifactFields = computed(() => {
	const allFields = componentDefinition.value?.fields ?? {};
	return Object.entries(allFields).filter(([, f]) => f.isArtifactField);
});

const baseURL = (wf.writerBaseUrl.value ?? "https://api.writer.com").replace(
	/\/+$/,
	"",
);

const curlCreate = computed(
	() =>
		`curl --location --request POST '${baseURL}/v1/agents/${wf.writerAppId.value}/blueprints/${blueprintId.value}/jobs' \\` +
		`\n--header 'Authorization: Bearer ${wf.writerApiKey.value}' \\` +
		`\n--header 'Content-Type: application/json' --data '{"inputs": []}'`,
);

type TabMode = "builder" | "api";
const tabs: WdsTabOptions<TabMode>[] = [
	{ label: "Run in Agent Builder", value: "builder" },
	{ label: "Run via API", value: "api" },
];
const tab = ref<TabMode>("builder");

const apiOutput = ref("");
const parsedOutput = computed(() => {
	try {
		return JSON.parse(apiOutput.value);
	} catch {
		return null;
	}
});

const { copy: copyCreate, copied: isCreateCopied } = useClipboard({
	source: curlCreate,
});

const isPollDisabled = computed(() => {
	return !parsedOutput.value?.poll_url?.trim();
});

const curlPoll = computed(() => {
	const pollUrl = parsedOutput.value?.poll_url ?? "/v1/agents/jobs/JOB_ID";
	return (
		`curl --location --request GET '${baseURL}${pollUrl}' \\` +
		`\n--header 'Authorization: Bearer ${wf.writerApiKey.value}'`
	);
});

const { copy: copyPoll, copied: isPollCopied } = useClipboard({
	source: curlPoll,
});
</script>

<style scoped>
.WdsTitle2 {
	padding-bottom: 8px;
}
.BuilderSettingsArtifactAPITriggerDetails {
	display: flex;
	flex-direction: column;
	gap: 8px;
	padding: 24px;
}
.BuilderSettingsArtifactAPITriggerDetails__tabs {
	gap: 10px;
}
.BuilderSettingsArtifactAPITriggerDetails__builder,
.BuilderSettingsArtifactAPITriggerDetails__api {
	display: flex;
	flex-direction: column;
	gap: 8px;
	margin-top: 8px;
}
.BuilderSettingsArtifactAPITriggerDetails__steps {
	display: flex;
	flex-direction: column;
	gap: 8px;
	list-style-type: decimal;
	padding-left: 16px;
}
.BuilderSettingsArtifactAPITriggerDetails__step:first-of-type
	> .BuilderSettingsArtifactAPITriggerDetails__step__hint {
	margin-top: 0;
}
.BuilderSettingsArtifactAPITriggerDetails__step__hint {
	margin: 12px 0;
}
</style>
<style>
.BuilderSettingsArtifactAPITriggerDetails__tabs > .WdsTab {
	font-size: 12px;
	padding: 2px 8px;
}
</style>
