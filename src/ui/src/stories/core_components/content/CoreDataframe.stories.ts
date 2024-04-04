import type { Meta, StoryObj } from "@storybook/vue3";
import { provide, ref, computed } from "vue";
import DataFrame from "../../../core_components/content/CoreDataframe.vue";
import injectionKeys from "../../../injectionKeys";
import "remixicon/fonts/remixicon.css";
import { generateCore } from "../../fakeCore";

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
	title: "core-components/content/DataFrame",
	component: DataFrame,
	// This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
	tags: ["autodocs"],
	argTypes: {
		dataframe: { control: "text" },
		showIndex: { control: "text" },
		enableSearch: { control: "text" },
		enableDownload: { control: "text" },
		displayRowCount: { control: "text" },
		wrapText: { control: "text" },
		primaryTextColor: { control: "text" },
		secondaryTextColor: { control: "text" },
		separatorColor: { control: "text" },
		dataframeBackgroundColor: { control: "text" },
		dataframeHeaderRowBackgroundColor: { control: "text" },
		fontStyle: { control: "text" },
		cssClasses: { control: "text" },
	},
} satisfies Meta<typeof DataFrame>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Sample: Story = {
	render: (args) => ({
		components: { DataFrame },
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
				dataframe: computed(() => args.dataframe),
				showIndex: computed(() => args.showIndex),
				enableSearch: computed(() => args.enableSearch),
				enableDownload: computed(() => args.enableDownload),
				displayRowCount: computed(() => args.displayRowCount),
				wrapText: computed(() => args.wrapText),
				primaryTextColor: computed(() => args.primaryTextColor),
				secondaryTextColor: computed(() => args.secondaryTextColor),
				separatorColor: computed(() => args.separatorColor),
				dataframeBackgroundColor: computed(() => args.dataframeBackgroundColor),
				dataframeHeaderRowBackgroundColor: computed(() => args.dataframeHeaderRowBackgroundColor),
				fontStyle: computed(() => args.fontStyle),
				cssClasses: computed(() => args.cssClasses),
			});
			provide(injectionKeys.isDisabled, ref(false));
			provide(injectionKeys.core, ss as any);
			return { args };
		},
		template:
			'<DataFrame :style="args.rootStyle" :prop-name="args.propName" />',
	}),
};
	