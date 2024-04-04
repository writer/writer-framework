import type { Meta, StoryObj } from "@storybook/vue3";
import { provide, ref, computed } from "vue";
import HTMLElement from "../../../core_components/other/CoreHtml.vue";
import injectionKeys from "../../../injectionKeys";
import "remixicon/fonts/remixicon.css";
import { generateCore } from "../../fakeCore";

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
	title: "core-components/other/HTMLElement",
	component: HTMLElement,
	// This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
	tags: ["autodocs"],
	argTypes: {
		element: { control: "text" },
		styles: { control: "text" },
		attrs: { control: "text" },
		htmlInside: { control: "text" },
		cssClasses: { control: "text" },
	},
} satisfies Meta<typeof HTMLElement>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Sample: Story = {
	render: (args) => ({
		components: { HTMLElement },
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
				element: computed(() => args.element),
				styles: computed(() => args.styles),
				attrs: computed(() => args.attrs),
				htmlInside: computed(() => args.htmlInside),
				cssClasses: computed(() => args.cssClasses),
			});
			provide(injectionKeys.isDisabled, ref(false));
			provide(injectionKeys.core, ss as any);
			return { args };
		},
		template:
			'<HTMLElement :style="args.rootStyle" :prop-name="args.propName" />',
	}),
};
	