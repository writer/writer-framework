import WdsSkeletonLoader from "@/wds/WdsSkeletonLoader.vue";
import { h } from "vue";
import { AsyncComponentOptions, defineAsyncComponent } from "vue";

function errorComponent() {
	return h(
		"div",
		{
			style: {
				display: "flex",
				alignItems: "center",
				justifyContent: "center",
			},
		},
		h(
			"p",
			{
				style: {
					background: "var(--wdsColorOrange2)",
					padding: "8px",
					borderRadius: "4px",
				},
			},
			"Could not load the component",
		),
	);
}

function loadingComponent() {
	return h(
		"div",
		{
			style: {
				display: "flex",
				alignItems: "center",
				justifyContent: "center",
				height: "100%",
				width: "100%",
				padding: "8px",
			},
		},
		h(WdsSkeletonLoader),
	);
}

export function defineAsyncComponentWithLoader(options: AsyncComponentOptions) {
	return defineAsyncComponent({
		loadingComponent,
		errorComponent,
		delay: 300,
		...options,
	});
}
