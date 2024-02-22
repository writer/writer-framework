<template>
	<div ref="rootEl" class="CorePDF">
		<div class="controls">
			<i class="ri-arrow-up-s-line" @click="() => gotoPage(page - 1)"></i>
			<i
				class="ri-arrow-down-s-line"
				@click="() => gotoPage(page + 1)"
			></i>
			<span :key="page">{{ page }} / {{ pages }}</span>
			<i class="ri-zoom-in-line" @click="incrementScale"></i>
			<i class="ri-zoom-out-line" @click="decrementScale"></i>
			<span>{{ Math.round(scale * 100) }}%</span>
			<span class="separator" />
			<i
				v-if="matches.length"
				class="ri-arrow-up-s-line"
				@click="decrementMatchIdx"
			></i>
			<i
				v-if="matches.length"
				class="ri-arrow-down-s-line"
				@click="incrementMatchIdx"
			></i>
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
					:highlight-text="highlightText"
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
import { FieldType } from "../../streamsyncTypes";
import { cssClasses } from "../../renderer/sharedStyleFields";

const description = "A component to embed a PDF document.";

export default {
	streamsync: {
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
			cssClasses,
		},
		events: {
			"pdf-load": {
				desc: "",
			},
		},
	},
};
</script>

<script setup lang="ts">
import { inject, ref, watch, computed } from "vue";
import { VuePDF, usePDF } from "@tato30/vue-pdf";
import injectionKeys from "../../injectionKeys";
import "@tato30/vue-pdf/style.css";

type MatchType = { str: string; page: number; index: number };

const fields = inject(injectionKeys.evaluatedFields);

const { pdf, pages } = usePDF(fields.source);

const highlightText = computed(() => {
	return fields.highlights.value
		? fields.highlights.value
				.map((v: string) => v.replaceAll("|", "\\|"))
				.join("|")
		: "";
});
const highlightOptions = ref({
	completeWords: false,
	ignoreCase: true,
});
const scale = ref(1);
const page = ref(1);
const matches = ref<MatchType[]>([]);
const currentMatch = ref(0);
const rootEl = ref(null);
const viewerEl = ref(null);

const onHighlight = (value) => {
	matches.value = [
		...matches.value,
		...value.matches.map((m: MatchType, idx: number) => ({
			page: value.page,
			str: m.str,
			index: idx,
		})),
	];
	// sort by page and index
	matches.value.sort((a, b) => {
		if (a.page === b.page) {
			return a.index - b.index;
		}
		return a.page - b.page;
	});
	if (currentMatch.value > 0) {
		gotoHighlight(currentMatch.value);
	}
};

const scroll = (event) => {
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
};

const calcScrollPosition = (targetEl: HTMLElement, parentEl: HTMLElement) => {
	let offsetTop = 0;
	let el = targetEl;
	while (el && el !== parentEl) {
		offsetTop += el.offsetTop;
		el = el.offsetParent as HTMLElement;
	}
	return offsetTop;
};

const gotoHighlight = (matchIdx: number) => {
	if (matchIdx < 1 || matchIdx > matches.value.length) {
		return;
	}
	const match = matches.value[matchIdx - 1];
	console.log(match);
	const matchEls = rootEl.value.querySelectorAll(
		`div[page='${match.page}'] span.highlight`,
	);
	const matchEl = matchEls[match.index];
	// scrollIntoView is breaking pdf viewer
	viewerEl.value.scrollTop = calcScrollPosition(matchEl, viewerEl.value);
};

const gotoPage = (page: number) => {
	if (page < 1 || page > pages.value) {
		return;
	}
	const pageEl = rootEl.value.querySelector("div[page='" + page + "']");
	viewerEl.value.scrollTop = calcScrollPosition(pageEl, viewerEl.value);
};

const onLoaded = () => {
	if (fields.page.value) {
		gotoPage(fields.page.value);
	}
	if (fields.selectedMatch.value) {
		currentMatch.value = fields.selectedMatch.value;
	}
};

const incrementMatchIdx = () => {
	if (currentMatch.value < matches.value.length) {
		currentMatch.value = currentMatch.value + 1;
	} else {
		currentMatch.value = 1;
	}
};

const decrementMatchIdx = () => {
	if (currentMatch.value > 1) {
		currentMatch.value = currentMatch.value - 1;
	} else {
		currentMatch.value = matches.value.length;
	}
};

const incrementScale = () => {
	scale.value = scale.value < 2 ? scale.value + 0.1 : scale.value;
};

const decrementScale = () => {
	scale.value = scale.value > 0.25 ? scale.value - 0.1 : scale.value;
};

watch(fields.source, () => {
	matches.value = [];
});

watch(fields.highlights, () => {
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
@import "../../renderer/sharedStyles.css";

.CorePDF {
	position: relative;
	display: flex;
	flex-direction: column;
	width: 100%;
	height: 80vh;
}

.CorePDF .controls {
	flex: 0 0 40px;
	display: flex;
	flex-direction: row;
	justify-content: space-between;
	align-items: center;
	background-color: var(--backgroundColor);
	border-bottom: 1px solid var(--separatorColor);
	padding: 0;
}

.CorePDF .controls span {
	flex: 0 0 fit-content;
	text-align: left;
	padding: 0 10px;
}

.CorePDF .controls i {
	display: block;
	height: 40px;
	width: 40px;
	line-height: 40px;
	text-align: center;
	border-radius: 4px;
	flex: 0 0 40px;
}

.CorePDF .controls i:hover {
	cursor: pointer;
	background: var(--builderSubtleSeparatorColor);
}

.CorePDF .controls > .separator {
	flex: 1;
}

.CorePDF .viewer {
	flex: 1;
	overflow: auto;
	position: relative;
	background-color: var(--separatorColor);
}

.CorePDF .viewer .page {
	border-bottom: 3px solid var(--separatorColor);
	overflow: hidden;
}

.CorePDF .viewer .page > div {
	width: fit-content;
	margin: 0 auto;
}

.CorePDF.beingEdited:not(.selected) object {
	pointer-events: none;
}

.CorePDF .pdf {
	width: 100%;
	height: 100%;
	display: block;
	margin: auto;
	border: 1px solid var(--separatorColor);
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
