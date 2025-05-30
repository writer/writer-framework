import { JSONValue } from "@/builder/settings/BuilderFieldsKeyValue.vue";
import { shallowRef, ref, computed } from "vue";

export function useSecretsManager() {
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
