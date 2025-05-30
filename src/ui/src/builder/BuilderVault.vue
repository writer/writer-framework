<script setup lang="ts">
import { BUILDER_MANAGER_MODE_ICONS } from "@/constants/icons";
import { useKeyValueEditor } from "./settings/composables/useKeyValueEditor";
import BuilderTemplateInput from "./settings/BuilderTemplateInput.vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import WdsButton from "@/wds/WdsButton.vue";
import { computed, onMounted, ref, shallowRef } from "vue";
import WdsSkeletonLoader from "@/wds/WdsSkeletonLoader.vue";
import { JSONValue } from "./settings/BuilderFieldsKeyValue.vue";

function useSecretsManager() {
	const secrets = shallowRef<JSONValue>({});
	const isLoading = ref(false);
	const isSaving = ref(false);
	const errror = ref(false);

	async function load() {
		isLoading.value = true;
		errror.value = false;

		try {
			await new Promise((res) => setTimeout(res, 500));
			// TODO: real implementation
			secrets.value = {
				GOOGLE_SECRET: "foo",
				WRITER_API_KEY: "foo",
			};
		} catch (e) {
			errror.value = e;
			secrets.value = {};
		} finally {
			isLoading.value = false;
		}
	}

	async function update(newSecrets: JSONValue) {
		isSaving.value = true;
		errror.value = false;

		try {
			await new Promise((res) => setTimeout(res, 500));
			// TODO: real implementation
			secrets.value = newSecrets;
		} catch (e) {
			errror.value = e;
		} finally {
			isSaving.value = false;
		}
	}

	return {
		secrets,
		load,
		readonly: computed(() => isLoading.value || isSaving.value),
		isLoading,
		update,
	};
}

const {
	secrets,
	load: loadSecrets,
	readonly,
	isLoading: isSecretsLoading,
	update: updateSecrets,
} = useSecretsManager();

const {
	currentValue,
	assistedEntries,
	getAssistedEntryError,
	updateAssistedEntryKey,
	updateAssistedEntryValue,
	updateAssistedEntries,
	removeAssistedEntry,
	addAssistedEntry,
} = useKeyValueEditor({});

function save() {
	if (typeof currentValue.value !== "object" || currentValue.value === null)
		return;
	updateSecrets(currentValue.value);
}

onMounted(async () => {
	await loadSecrets();
	if (typeof secrets.value !== "object" || secrets.value === null) return;
	updateAssistedEntries(secrets.value);
});
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
				<template v-if="isSecretsLoading">
					<WdsSkeletonLoader style="height: 40px" />
					<WdsSkeletonLoader style="height: 40px" />
					<WdsSkeletonLoader style="height: 40px" />
					<WdsSkeletonLoader style="height: 40px" />
					<WdsSkeletonLoader style="height: 40px" />
				</template>
				<template
					v-for="(entry, id) of assistedEntries"
					v-else
					:key="id"
				>
					<WdsFieldWrapper :error="getAssistedEntryError(id)">
						<BuilderTemplateInput
							placeholder="Type a key..."
							:value="entry.key"
							:error="getAssistedEntryError(id)"
							:readonly="readonly"
							@update:value="updateAssistedEntryKey(id, $event)"
						/>
					</WdsFieldWrapper>
					<WdsFieldWrapper>
						<BuilderTemplateInput
							placeholder="Type a value..."
							:value="entry.value"
							:readonly="readonly"
							@update:value="updateAssistedEntryValue(id, $event)"
						/>
					</WdsFieldWrapper>
					<div>
						<WdsButton
							variant="neutral"
							size="smallIcon"
							class="BuilderVault__editor__form__deleteBtn"
							:disabled="readonly"
							@click="removeAssistedEntry(id)"
						>
							<span class="material-symbols-outlined"
								>delete</span
							>
						</WdsButton>
					</div>
				</template>
			</div>
			<div class="BuilderVault__editor__toolbar">
				<WdsButton
					variant="tertiary"
					size="small"
					:disabled="readonly"
					@click="addAssistedEntry"
					><span class="material-symbols-outlined">add</span>Add a
					pair</WdsButton
				>
				<WdsButton
					variant="primary"
					size="small"
					:disabled="readonly"
					@click="save"
					>Save</WdsButton
				>
			</div>
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
.BuilderVault__editor__toolbar {
	display: flex;
	gap: 8px;
	justify-content: space-between;
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
