import { defineAsyncComponentWithLoader } from "@/utils/defineAsyncComponentWithLoader";

export const artifactRegistry = {
	apiTriggerDetails: defineAsyncComponentWithLoader({
		loader: () => import("./BuilderSettingsArtifactAPITriggerDetails.vue"),
	}),
};

export type ArtifactKey = keyof typeof artifactRegistry;
