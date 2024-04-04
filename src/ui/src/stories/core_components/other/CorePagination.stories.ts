import type { Meta, StoryObj } from "@storybook/vue3";
import { provide, ref, computed } from "vue";
import Pagination from "../../../core_components/other/CorePagination.vue";
import injectionKeys from "../../../injectionKeys";
import "remixicon/fonts/remixicon.css";
import { generateCore } from "../../fakeCore";

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
	title: "core-components/other/Pagination",
	component: Pagination,
	// This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
	tags: ["autodocs"],
	argTypes: {
		page: { control: "text" },
		pageSize: { control: "text" },
		totalItems: { control: "text" },
		pageSizeOptions: { control: "text" },
		pageSizeShowAll: { control: "text" },
		jumpTo: { control: "text" },
	},
} satisfies Meta<typeof Pagination>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Sample: Story = {
	render: (args) => ({
		components: { Pagination },
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
				page: computed(() => args.page),
				pageSize: computed(() => args.pageSize),
				totalItems: computed(() => args.totalItems),
				pageSizeOptions: computed(() => args.pageSizeOptions),
				pageSizeShowAll: computed(() => args.pageSizeShowAll),
				jumpTo: computed(() => args.jumpTo),
			});
			provide(injectionKeys.isDisabled, ref(false));
			provide(injectionKeys.core, ss as any);
			return { args };
		},
		template:
			'<Pagination :style="args.rootStyle" :prop-name="args.propName" />',
	}),
};
	