import { defineAsyncComponent } from "vue";
import BuilderAsyncLoader from "../BuilderAsyncLoader.vue";

export const artifactRegistry = {
    apiFieldDefinitions: defineAsyncComponent({
        loader: () => import("./BuilderSettingsArtifactAPIFieldDefinitions.vue"),
        loadingComponent: BuilderAsyncLoader,
    }),
    apiTriggerDetails: defineAsyncComponent({
        loader: () => import("./BuilderSettingsArtifactAPITriggerDetails.vue"),
        loadingComponent: BuilderAsyncLoader,
    })
};

export type ArtifactKey = keyof typeof artifactRegistry;
