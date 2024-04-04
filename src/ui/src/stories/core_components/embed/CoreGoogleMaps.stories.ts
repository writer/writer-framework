import type { Meta, StoryObj } from "@storybook/vue3";
import { provide, ref, computed } from "vue";
import GoogleMaps from "../../../core_components/embed/CoreGoogleMaps.vue";
import injectionKeys from "../../../injectionKeys";
import "remixicon/fonts/remixicon.css";
import { generateCore } from "../../fakeCore";

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
	title: "core-components/embed/GoogleMaps",
	component: GoogleMaps,
	// This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
	tags: ["autodocs"],
	argTypes: {
		apiKey: { control: "text" },
		mapId: { control: "text" },
		mapType: { control: "text" },
		zoom: { control: "text" },
		lat: { control: "text" },
		lng: { control: "text" },
		markers: { control: "text" },
		cssClasses: { control: "text" },
	},
} satisfies Meta<typeof GoogleMaps>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Sample: Story = {
	render: (args) => ({
		components: { GoogleMaps },
		setup() {
			const ss = generateCore();
			args.rootStyle = computed(() => {
				return {
					"--accentColor": "#29cf00",
					"--buttonColor": "#ffffff",
					"--emptinessColor": "#e9eef1",
					"--separatorColor": "rgba(0, 0, 0, 0.07)",
					"--primaryTextColor": "#202829",
					"--buttonTextColor": "#202829",
					"--secondaryTextColor": "#5d7275",
					"--containerBackgroundColor": "#ffffff",
				};
			});
			provide(injectionKeys.evaluatedFields, {
				apiKey: computed(() => args.apiKey),
				mapId: computed(() => args.mapId),
				mapType: computed(() => args.mapType),
				zoom: computed(() => args.zoom),
				lat: computed(() => args.lat),
				lng: computed(() => args.lng),
				markers: computed(() => args.markers),
				cssClasses: computed(() => args.cssClasses),
			});
			provide(injectionKeys.isDisabled, ref(false));
			provide(injectionKeys.core, ss as any);
			return { args };
		},
		template:
			'<GoogleMaps :style="args.rootStyle" :prop-name="args.propName" />',
	}),
};
	