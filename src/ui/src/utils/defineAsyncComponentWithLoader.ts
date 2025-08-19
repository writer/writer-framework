import { useLogger } from "@/composables/useLogger";
import WdsSkeletonLoader from "@/wds/WdsSkeletonLoader.vue";
import { CSSProperties, h } from "vue";
import { AsyncComponentOptions, defineAsyncComponent } from "vue";

type LoadingComponentProps = Pick<CSSProperties, "height" | "width">;

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

function loadingComponent(props: LoadingComponentProps) {
	return h(
		"div",
		{
			style: {
				display: "flex",
				alignItems: "center",
				justifyContent: "center",
				height: props.height ?? "100%",
				width: props.width ?? "100%",
				padding: "8px",
			},
		},
		h(WdsSkeletonLoader),
	);
}

const ASYNC_COMP_MAX_RETRIES = 5;

export function defineAsyncComponentWithLoader(
	options: AsyncComponentOptions & {
		loadingComponentProps?: LoadingComponentProps;
	},
) {
	return defineAsyncComponent({
		loadingComponent: () =>
			loadingComponent(options.loadingComponentProps ?? {}),
		errorComponent,
		delay: 300,
		onError(error, retry, fail, attempts) {
			const logger = useLogger();
			if (attempts <= ASYNC_COMP_MAX_RETRIES) {
				const msg = `Failed to load async component (retry ${attempts}/${ASYNC_COMP_MAX_RETRIES})`;
				logger.warn(msg, error);
				setTimeout(retry, 1_000);
			} else {
				const msg = `Failed to load async component after ${ASYNC_COMP_MAX_RETRIES} attempts`;
				logger.error(msg, error);
				fail();
			}
		},
		...options,
	});
}
