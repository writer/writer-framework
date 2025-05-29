import type { CSSProperties } from "vue";

/**
 * Colors from [Writer's design system](https://www.figma.com/design/jgLDtwVwg3hReC1t4Vw20D/.WDS-Writer-Design-System?node-id=1-2)
 */
export enum WdsColor {
	White = "#ffffff",
	Black = "#000000",

	Blue1 = "#f3f5ff",
	Blue2 = "#e4e9ff",
	Blue3 = "#bfcbff",
	Blue4 = "#6985ff",
	Blue5 = "#5551ff",
	Blue6 = "#4a46da",

	Gray0 = "#fbfbfd",
	Gray1 = "#f5f5f9",
	Gray2 = "#e4e7ed",
	Gray3 = "#d2d4d7",
	Gray4 = "#828282",
	Gray5 = "#4f4f4f",
	Gray6 = "#333333",

	Purple1 = "#f6effd",
	Purple2 = "#ede2ff",
	Purple3 = "#d4b2f7",
	Purple4 = "#a95ef8",
	Purple5 = "#721cc9",

	Orange1 = "#fff4f1",
	Orange2 = "#ffcfc2",
	Orange4 = "#ff8866",
	Orange5 = "#ff643c",

	Green1 = "#f2fffb",
	Green2 = "#d4fff2",
	Green3 = "#a9f9e1",
	Green5 = "#3bdcab",
	Green6 = "#078660",

	Puprple3 = "#E4C9FF",
}

/**
 * Shadows from [Writer's design system](https://www.figma.com/design/jgLDtwVwg3hReC1t4Vw20D/.WDS-Writer-Design-System?node-id=1-14)
 */
export enum WdsShadow {
	Box = "0px 2px 0px 0px #f3f3f3",
	Menu = "0px 1px 8px 0px #bfcbff40",
	Large = "0px 3px 40px 0px #acb9dc66",
}

export const WDS_CSS_PROPERTIES = Object.freeze<CSSProperties>(
	Object.fromEntries([
		...Object.entries(WdsColor).map(([key, value]) => [
			`--wdsColor${key}`,
			value,
		]),
		...Object.entries(WdsShadow).map(([key, value]) => [
			`--wdsShadow${key}`,
			value,
		]),
	]),
);
