<script setup lang="ts">
import { BUILDER_MANAGER_MODE_ICONS } from "@/constants/icons";
import { useKeyValueEditor } from "./settings/composables/useKeyValueEditor";
import BuilderTemplateInput from "./settings/BuilderTemplateInput.vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import WdsButton from "@/wds/WdsButton.vue";

const {
	assistedEntries,
	getAssistedEntryError,
	updateAssistedEntryKey,
	updateAssistedEntryValue,
	removeAssistedEntry,
	addAssistedEntry,
} = useKeyValueEditor({});
</script>

<template>
	<div class="BuilderVault">
		<h1>
			<span class="material-symbols-outlined">
				{{ BUILDER_MANAGER_MODE_ICONS.vault }}
			</span>
			Secrets vault
		</h1>
		<p>
			Save the key value pairs for all of your integrations and secrets
			here, then reference them with <code>@{}</code> from any block in
			your blueprint.
		</p>

		<div class="BuilderVault__editor">
			<div class="BuilderVault__editor__form">
				<p class="BuilderVault__editor__form__labelKey">Key</p>
				<p class="BuilderVault__editor__form__labelValue">Value</p>
				<template v-for="(entry, id) of assistedEntries" :key="id">
					<WdsFieldWrapper :error="getAssistedEntryError(id)">
						<BuilderTemplateInput
							placeholder="Type a key..."
							:value="entry.key"
							:error="getAssistedEntryError(id)"
							@update:value="updateAssistedEntryKey(id, $event)"
						/>
					</WdsFieldWrapper>
					<WdsFieldWrapper>
						<BuilderTemplateInput
							placeholder="Type a value..."
							:value="entry.value"
							@update:value="updateAssistedEntryValue(id, $event)"
						/>
					</WdsFieldWrapper>
					<div>
						<WdsButton
							variant="neutral"
							size="smallIcon"
							class="BuilderVault__editor__form__deleteBtn"
							@click="removeAssistedEntry(id)"
						>
							<span class="material-symbols-outlined"
								>delete</span
							>
						</WdsButton>
					</div>
				</template>
			</div>

			<WdsButton variant="special" size="small" @click="addAssistedEntry"
				><span class="material-symbols-outlined">add</span>Add a
				pair</WdsButton
			>
		</div>
	</div>
</template>

<style lang="css" scoped>
.BuilderVault {
	max-width: 500px;
	margin-left: auto;
	margin-right: auto;
	padding: 40px;

	display: flex;
	flex-direction: column;
	gap: 24px;
}

.BuilderVault h1 {
	display: flex;
	gap: 12px;
	align-items: center;
	font-weight: 500;
	font-size: 20px;
}

.BuilderVault__editor__form {
	display: grid;
	grid-template-columns: 1fr 1fr auto;
	align-items: flex-start;
	gap: 10px;
	margin-bottom: 22px;
}

.BuilderVault__editor__form__deleteBtn {
	margin-top: 4px;
}
.BuilderVault__editor__form__labelKey {
	grid-column-start: 1;
}
.BuilderVault__editor__form__labelValue {
	grid-column-start: 2;
	grid-column-end: -1;
}
</style>
