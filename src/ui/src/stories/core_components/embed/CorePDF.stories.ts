import type { Meta, StoryObj } from "@storybook/vue3";
import { provide, ref, computed } from "vue";
import PDF from "../../../core_components/embed/CorePDF.vue";
import injectionKeys from "../../../injectionKeys";
import "remixicon/fonts/remixicon.css";
import { generateCore } from "../../fakeCore";

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
	title: "core-components/embed/PDF",
	component: PDF,
	// This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
	tags: ["autodocs"],
	argTypes: {
		source: { control: "text" },
		highlights: { control: "text" },
		selectedMatch: { control: "text" },
		page: { control: "text" },
		controls: { control: "text" },
		containerBackgroundColor: { control: "text" },
		separatorColor: { control: "text" },
		primaryTextColor: { control: "text" },
		cssClasses: { control: "text" },
	},
} satisfies Meta<typeof PDF>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Sample: Story = {
	render: (args) => ({
		components: { PDF },
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
				source: computed(() => args.source),
				highlights: computed(() => args.highlights),
				selectedMatch: computed(() => args.selectedMatch),
				page: computed(() => args.page),
				controls: computed(() => args.controls),
				containerBackgroundColor: computed(() => args.containerBackgroundColor),
				separatorColor: computed(() => args.separatorColor),
				primaryTextColor: computed(() => args.primaryTextColor),
				cssClasses: computed(() => args.cssClasses),
			});
			provide(injectionKeys.isDisabled, ref(false));
			provide(injectionKeys.core, ss as any);
			return { args };
		},
		template:
			'<PDF :style="args.rootStyle" :prop-name="args.propName" />',
	}),
};
	