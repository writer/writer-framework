import { JSONValue } from "@/builder/settings/BuilderFieldsKeyValue.vue";
import { useWriterApi } from "@/composables/useWriterApi";
import { Core } from "@/writerTypes";
import { shallowRef, ref, computed } from "vue";

export function useSecretsManager(wf: Core) {
	const SECRET_KEY_NAME = "vault";

	const secrets = shallowRef<JSONValue>({});
	const isLoading = ref(false);
	const isSaving = ref(false);
	const errror = ref(false);

	const { writerApi } = useWriterApi();

	async function fetchExisitingVault() {
		try {
			const res = await writerApi.fetchSecret(
				wf.writerOrgId.value,
				wf.writerAppId.value,
				SECRET_KEY_NAME,
			);
			return res.secret;
		} catch {
			return undefined;
		}
	}

	async function load() {
		if (!wf.isWriterCloudApp.value) return;

		isLoading.value = true;
		errror.value = false;

		try {
			const exisitingVault = await fetchExisitingVault();
			secrets.value = exisitingVault ?? {};
		} finally {
			isLoading.value = false;
		}
	}

	async function update(newSecrets: JSONValue) {
		if (!wf.isWriterCloudApp.value) return;
		isSaving.value = true;
		errror.value = false;

		const exisitingVault = await fetchExisitingVault();

		try {
			if (exisitingVault === undefined) {
				await writerApi.createSecret(
					wf.writerOrgId.value,
					wf.writerAppId.value,
					SECRET_KEY_NAME,
					newSecrets,
				);
			} else {
				await writerApi.updateSecret(
					wf.writerOrgId.value,
					wf.writerAppId.value,
					SECRET_KEY_NAME,
					newSecrets,
				);
			}

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
