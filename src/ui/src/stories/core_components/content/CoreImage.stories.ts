import type { Meta, StoryObj } from "@storybook/vue3";
import { provide, ref, computed } from "vue";
import Image from "../../../core_components/content/CoreImage.vue";
import injectionKeys from "../../../injectionKeys";
import "remixicon/fonts/remixicon.css";
import { generateCore } from "../../fakeCore";

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
	title: "core-components/content/Image",
	component: Image,
	// This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
	tags: ["autodocs"],
	argTypes: {
		src: { control: "text" },
		caption: { control: "text" },
		maxWidth: { control: "text" },
		maxHeight: { control: "text" },
		secondaryTextColor: { control: "text" },
		cssClasses: { control: "text" },
	},
} satisfies Meta<typeof Image>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Sample: Story = {
	render: (args) => ({
		components: { Image },
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
				src: computed(() => args.src),
				caption: computed(() => args.caption),
				maxWidth: computed(() => args.maxWidth),
				maxHeight: computed(() => args.maxHeight),
				secondaryTextColor: computed(() => args.secondaryTextColor),
				cssClasses: computed(() => args.cssClasses),
			});
			provide(injectionKeys.isDisabled, ref(false));
			provide(injectionKeys.core, ss as any);
			return { args };
		},
		template:
			'<Image :style="args.rootStyle" :prop-name="args.propName" />',
	}),
};
	