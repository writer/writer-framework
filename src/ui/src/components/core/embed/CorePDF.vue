<template>
	<div ref="rootEl" class="CorePDF">
		<div v-if="fields.controls.value" class="controls">
			<WdsControl @click="() => gotoPage(page - 1)">
				<WdsIcon name="arrow-up" />
			</WdsControl>
			<WdsControl @click="() => gotoPage(page + 1)">
				<WdsIcon name="arrow-down" />
			</WdsControl>
			<span :key="page">{{ page }} / {{ pages }}</span>
			<WdsControl :disabled="loading" @click="incrementScale">
				<WdsIcon name="zoom-in" />
			</WdsControl>
			<WdsControl :disabled="loading" @click="decrementScale">
				<WdsIcon name="zoom-out" />
			</WdsControl>
			<span>{{ Math.round(scale * 100) }}%</span>
			<span class="separator" />
			<WdsControl v-if="matches.length" @click="decrementMatchIdx">
				<WdsIcon name="chevron-left" />
			</WdsControl>
			<WdsControl v-if="matches.length" @click="incrementMatchIdx">
				<WdsIcon name="chevron-right" />
			</WdsControl>
			<span v-if="matches.length"
				>Matches {{ currentMatch }} / {{ matches.length }}</span
			>
		</div>
		<div ref="viewerEl" class="viewer" @scroll="scroll">
			<div v-for="p in pages" :key="p" :page="p" class="page">
				<VuePDF
					:scale="scale"
					:pdf="pdf"
					:page="p"
					text-layer
					:highlight-text="highlights"
					:highlight-options="highlightOptions"
					@highlight="onHighlight"
					@loaded="onLoaded"
				/>
			</div>
		</div>
		<div class="mask" />
	</div>
</template>

<script lang="ts">
import { FieldType } from "@/writerTypes";
import {
	cssClasses,
	separatorColor,
	primaryTextColor,
	containerBackgroundColor,
	createBooleanField,
} from "@/renderer/sharedStyleFields";
import WdsControl from "@/wds/WdsControl.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import { validatorArrayOfString } from "@/constants/validators";
import type { PDFSrc } from "@tato30/vue-pdf";
import { dataURLToArrayBuffer } from "@/utils/base64";
import type { EncodedFile } from "@/composables/useFilesEncoder/useFilesEncoder";
import { isPlainObject } from "@/utils/object";

const description = "A component to embed PDF documents.";

export default {
	writer: {
		name: "PDF",
		description,
		category: "Embed",
		fields: {
			source: {
				name: "PDF source",
				type: FieldType.Text,
				desc: "A valid URL. Alternatively, you can provide a state reference to a packed PDF file.",
			},
			highlights: {
				name: "Highlights",
				default: JSON.stringify([]),
				desc: "A list of highlights to be applied to the PDF as a JSON array of strings.",
				type: FieldType.Object,
				validator: validatorArrayOfString,
			},
			selectedMatch: {
				name: "Selected highlight match",
				default: null,
				desc: "The index of the selected highlight match.",
				type: FieldType.Number,
			},
			page: {
				name: "Page",
				type: FieldType.Number,
				desc: "The page to be displayed.",
			},
			controls: createBooleanField({
				name: "Enable controls",
				desc: "Show controls to navigate the PDF.",
				default: "yes",
			}),
			containerBackgroundColor,
			separatorColor,
			primaryTextColor,
			cssClasses,
		},
	},
};
</script>

<script setup lang="ts">
import {
	inject,
	ref,
	watch,
	computed,
	onMounted,
	useTemplateRef,
	shallowRef,
} from "vue";
import injectionKeys from "@/injectionKeys";
import "@tato30/vue-pdf/style.css";
import type { HighlightEventPayload, HighlightOptions } from "@tato30/vue-pdf";

type MatchType = { str: string; page: number; index: number };

const fields = inject(injectionKeys.evaluatedFields, {});

let pdf, pages, VuePDF;

const highlights = computed<string[]>(() =>
	fields.highlights.value.filter(Boolean),
);
const highlightOptions = shallowRef<HighlightOptions>({
	completeWords: false,

	ignoreCase: true,
});
const scale = ref(1);
const page = ref(1);
const matches = shallowRef<MatchType[]>([]);
const currentMatch = ref(0);
const rootEl = useTemplateRef("rootEl");
const viewerEl = useTemplateRef("viewerEl");
const loading = ref(false);

const pagesLoaded = ref(0);
const highlightsList = shallowRef<
	Pick<HighlightEventPayload, "matches" | "page">[]
>([]);

function isEncodedFile(input: unknown): input is EncodedFile {
	return (
		isPlainObject(input) &&
		"name" in input &&
		"type" in input &&
		"data" in input &&
		typeof input.data === "string" &&
		input.data.startsWith("data:")
	);
}

function extractDataURLFromSource(source: unknown): string | undefined {
	if (typeof source !== "string" || !source.trim()) {
		return undefined;
	}

	// Try to parse as JSON array (file upload format)
	try {
		const parsed = JSON.parse(source);
		if (Array.isArray(parsed) && parsed.length > 0) {
			const firstFile = parsed[0];
			if (isEncodedFile(firstFile)) {
				return firstFile.data;
			}
		}
	} catch {
		// Not valid JSON or not in expected format, continue to use source directly
	}

	// Return source as-is (could be a direct URL or data URL)
	return source;
}

const pdfData = computed(() => {
	if (!fields.source?.value) return undefined;

	const dataURL = extractDataURLFromSource(fields.source.value);
	if (!dataURL) return undefined;

	try {
		return dataURLToArrayBuffer(dataURL);
	} catch {
		return undefined;
	}
});

const pdfSource = computed<PDFSrc>(() => {
	return pdfData.value === undefined
		? {
				url: fields.source.value,
				isEvalSupported: false,
			}
		: {
				data: pdfData.value, // convert source to binary data to avoid fetching DataURL (which is forbidden by some CSP rules)
				isEvalSupported: false,
			};
});

onMounted(async () => {
	if (import.meta.env.SSR) return;
	const VuePDFLib = await import("@tato30/vue-pdf");

	// setup the worker URL ourself to avoid importing the module from a DataURL (which is forbidden by some CSP rules)
	const PDFJS = await import("pdfjs-dist");
	PDFJS.GlobalWorkerOptions.workerSrc = new URL(
		"pdfjs-dist/build/pdf.worker.min.mjs",
		import.meta.url,
	).toString();

	VuePDF = VuePDFLib.VuePDF;
	const usePDF = VuePDFLib.usePDF;
	({ pdf, pages } = usePDF(pdfSource));
	reload();
});

function reload() {
	loading.value = true;
	pagesLoaded.value = 0;
	highlightsList.value = [];
	matches.value = [];
}

function onHighlight(value: HighlightEventPayload) {
	highlightsList.value = [
		...highlightsList.value,
		{ matches: value.matches, page: value.page },
	];
}

function onLoaded(e) {
	pagesLoaded.value++;
}

function buildMatches() {
	matches.value = highlightsList.value
		.reduce<MatchType[]>((acc, item) => {
			const items = item.matches.map((m, idx: number) => ({
				page: item.page,
				str: m.str,
				index: idx,
			}));
			acc.push(...items);

			return acc;
		}, [])
		.sort((a, b) =>
			a.page === b.page ? a.index - b.index : a.page - b.page,
		);
}

function renderingComplete() {
	buildMatches();
	if (currentMatch.value) {
		gotoHighlight(currentMatch.value);
	}
	if (fields.selectedMatch.value) {
		currentMatch.value = fields.selectedMatch.value;
	}
}

function scroll(event) {
	const c = event.target.getBoundingClientRect();
	const r = [...event.target.children]
		.filter((child) => child.className.includes("page"))
		.find((child) => {
			const e = child.getBoundingClientRect();
			const relativeY = e.y - c.y;
			return (
				relativeY < c.height / 2 && relativeY + e.height > c.height / 2
			);
		});
	if (r) {
		page.value = Number(r.getAttribute("page"));
	}
}

function calcScrollPosition(targetEl: HTMLElement, parentEl: HTMLElement) {
	let offsetTop = 0;
	let el = targetEl;
	while (el && el !== parentEl) {
		offsetTop += el.offsetTop;
		el = el.offsetParent as HTMLElement;
	}
	return offsetTop;
}

function gotoHighlight(matchIdx: number) {
	if (matchIdx < 1 || matchIdx > matches.value.length) {
		return;
	}
	const match = matches.value[matchIdx - 1];
	if (!match) return;
	const matchEls = rootEl.value.querySelectorAll(
		`div[page='${match.page}'] span.highlight`,
	);
	const matchEl = matchEls[match.index];
	if (!(matchEl instanceof HTMLElement)) return;
	// scrollIntoView is breaking pdf viewer
	viewerEl.value.scrollTop = calcScrollPosition(matchEl, viewerEl.value);
}

const gotoPage = (page: number) => {
	if (page < 1 || page > pages?.value) {
		return;
	}
	const pageEl = rootEl.value.querySelector("div[page='" + page + "']");
	if (!(pageEl instanceof HTMLElement)) return;
	viewerEl.value.scrollTop = calcScrollPosition(pageEl, viewerEl.value);
};

function incrementMatchIdx() {
	if (currentMatch.value < matches.value.length) {
		currentMatch.value = currentMatch.value + 1;
	} else {
		currentMatch.value = 1;
	}
}

function decrementMatchIdx() {
	if (currentMatch.value > 1) {
		currentMatch.value = currentMatch.value - 1;
	} else {
		currentMatch.value = matches.value.length;
	}
}

function incrementScale() {
	scale.value = scale.value < 2 ? scale.value + 0.1 : scale.value;
}

function decrementScale() {
	scale.value = scale.value > 0.25 ? scale.value - 0.1 : scale.value;
}

watch(pagesLoaded, () => {
	if (pagesLoaded.value === pages?.value) {
		if (fields.page?.value) {
			gotoPage(fields.page.value);
		}
	}
});

watch([highlightsList, pagesLoaded], () => {
	if (
		(highlights.value.length == 0 ||
			highlightsList.value.length === pages?.value) &&
		pagesLoaded.value === pages?.value
	) {
		renderingComplete();
		loading.value = false;
	}
});

watch([scale, fields.source], reload);

watch(highlights, () => {
	highlightsList.value = [];
	matches.value = [];
});

watch(currentMatch, () => {
	gotoHighlight(currentMatch.value);
});

watch(fields.selectedMatch, () => {
	currentMatch.value = fields.selectedMatch.value;
});

watch(fields.page, () => {
	gotoPage(fields.page.value);
});
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";
@import "@/renderer/colorTransformations.css";

.CorePDF {
	position: relative;
	display: flex;
	flex-direction: column;
	width: 100%;
	height: 80vh;
	color: var(--primaryTextColor);
}

.CorePDF .controls {
	flex: 0 0 40px;
	gap: 8px;
	display: flex;
	flex-direction: row;
	justify-content: space-between;
	align-items: center;
	background-color: var(--backgroundColor);
	padding: 0;
}

.CorePDF .controls span {
	flex: 0 0 fit-content;
	text-align: left;
	padding: 0 10px;
}

.CorePDF .controls > .separator {
	flex: 1;
}

.CorePDF .viewer {
	flex: 1;
	overflow: auto;
	position: relative;
	background-color: var(--containerBackgroundColor);
}

.CorePDF .viewer .page {
	margin-bottom: 3px;
	overflow: hidden;
}

.CorePDF .viewer .page:last-child {
	margin-bottom: 0;
}

.CorePDF .viewer .page > div {
	width: fit-content;
	margin: 0 auto;
}

.CorePDF .mask {
	pointer-events: none;
}

.CorePDF.beingEdited .mask {
	pointer-events: auto;
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background-color: rgba(0, 0, 0, 0);
}

.CorePDF.beingEdited.selected .mask {
	pointer-events: none;
}
</style>
