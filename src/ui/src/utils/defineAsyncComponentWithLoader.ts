import WdsSkeletonLoader from "@/wds/WdsSkeletonLoader.vue";
import { defineComponent, h } from "vue";
import { AsyncComponentOptions, defineAsyncComponent } from "vue";

const ErrorComponent = defineComponent({
	render: () =>
		h(
			"p",
			{
				style: {
					background: "var(--wdsColorOrange2)",
					padding: "8px",
				},
			},
			"Could not load the component",
		),
});

export function defineAsyncComponentWithLoader(options: AsyncComponentOptions) {
	return defineAsyncComponent({
		loadingComponent: WdsSkeletonLoader,
		errorComponent: ErrorComponent,
		...options,
	});
}
