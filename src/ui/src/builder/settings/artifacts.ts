import { defineAsyncComponent } from "vue";
import BuilderAsyncLoader from "../BuilderAsyncLoader.vue";

export const artifactRegistry = {
    apiTriggerDetails: defineAsyncComponent({
        loader: () => import("./BuilderSettingsArtifactAPITriggerDetails.vue"),
        loadingComponent: BuilderAsyncLoader,
    })
};

export type ArtifactKey = keyof typeof artifactRegistry;
