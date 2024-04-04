/* eslint-disable @typescript-eslint/no-var-requires */
import { promises as fs, existsSync } from "fs";
import path from "path";
import { fileURLToPath } from "url";

import * as core from "./core.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const srcFile = (...args) => path.resolve(__dirname, "..", "src", ...args);

const storyFile = (...args) => srcFile("stories", "core_components", ...args);

const relPath = (from, to) => path.relative(path.dirname(from), to);

async function loadComponents() {
	const rawComponents = await core.loadComponents();
	// eslint-disable-next-line no-console
	return rawComponents.map((component) => {
		return {
			nameTrim: component.name.replaceAll(/\s/g, ""),
			...component,
		};
	});
}

function generateImports(component, { filePath, srcPath }) {
	return `import type { Meta, StoryObj } from "@storybook/vue3";
import { provide, ref, computed } from "vue";
import ${component.nameTrim} from "${relPath(filePath, component.fileRef)}";
import injectionKeys from "${srcPath("injectionKeys")}";
import "remixicon/fonts/remixicon.css";
import { generateCore } from "${srcPath("stories", "fakeCore")}";`;
}

function generateArgTypes(component) {
	return Object.entries(component.fields)
		.map(([key, field]) => {
			return `		${key}: { control: "text" },`;
		})
		.join("\n");
}

function generateArgWrap(component) {
	return Object.entries(component.fields)
		.map(([key]) => {
			return `				${key}: computed(() => args.${key}),`;
		})
		.join("\n");
}

function generateMeta(component, { module }) {
	return `

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
	title: "core-components/${module}/${component.nameTrim}",
	component: ${component.nameTrim},
	// This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
	tags: ["autodocs"],
	argTypes: {
${generateArgTypes(component)}
	},
} satisfies Meta<typeof ${component.nameTrim}>;

export default meta;
type Story = StoryObj<typeof meta>;`;
}

function generateStory(component) {
	return `

export const Sample: Story = {
	render: (args) => ({
		components: { ${component.nameTrim} },
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
${generateArgWrap(component)}
			});
			provide(injectionKeys.isDisabled, ref(false));
			provide(injectionKeys.core, ss as any);
			return { args };
		},
		template:
			'<${component.nameTrim} :style="args.rootStyle" :prop-name="args.propName" />',
	}),
};
	`;
}

export async function generate() {
	const components = await loadComponents();

	for (const component of components) {
		component.nameTrim = component.name.replaceAll(/\s/g, "");
		const name = path.basename(component.fileRef, ".vue");
		const mod = component.fileRef.split("/").slice(-2, -1)[0];
		// eslint-disable-next-line no-console
		console.log("Generating ", storyFile(mod, name + ".stories.ts"));
		if (!existsSync(storyFile(mod))) {
			await fs.mkdir(storyFile(mod), { recursive: true });
		}
		const filePath = storyFile(mod, name + ".stories.ts");
	
		await fs.writeFile(
			filePath,
			generateImports(component, {
				filePath,
				srcPath: (...path) => relPath(filePath, srcFile(...path)),
			}) +
				generateMeta(component, { module: mod }) +
				generateStory(component),
			{
				flag: "w+",
			},
		);
	}
}
