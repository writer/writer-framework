<template>
	<div ref="rootEl" class="CoreRoot" data-writer-container>
		<template v-for="vnode in getChildrenVNodes()" :key="vnode.key">
			<component
				:is="vnode"
				v-if="vnode.key === `${displayedPageId}:0`"
			></component>
		</template>
	</div>
</template>

<script lang="ts">
import { FieldType } from "@/writerTypes";
import * as sharedStyleFields from "@/renderer/sharedStyleFields";
import { useEvaluator } from "@/renderer/useEvaluator";

const ssHashChangeStub = `
def handle_hashchange(state, payload):
	# The payload is a dictionary with the page key and all the route variables in the URL hash.
	# For example, if the current URL is http://localhost:3000/#main/animal=duck&colour=yellow
	# you will get the following dictionary
	# {
	#	  "page_key": "main",
	#	  "route_vars": {
	#		  "animal": "duck",
	#		  "colour": "yellow"
	#	  }
	# }

	page_key = payload.get("page_key")
	route_vars = payload.get("route_vars")

	if not route_vars:
		return

	if route_vars.get("animal") == "duck":
		state["message"] = "You've navigated to the Duck zone."
	else:
		state["message"] = "You're not in the Duck zone.`.trim();

const wfAppOpenStub = `
def handle_app_open(state):
	# The payload is a dictionary with the page key and all the route variables in the URL hash.
	# For example, if the current URL is http://localhost:3000/#/animal=duck&colour=yellow
	# you will get the following dictionary
	# {
	#   "page_key": "main",
	#	  "route_vars": {
	#		  "animal": "duck",
	#		  "colour": "yellow"
	#	  }
	# }

	page_key = payload.get("page_key")
	route_vars = payload.get("route_vars")
`.trim();

const description =
	"The root component of the application, which serves as the starting point of the component hierarchy.";

export default {
	writer: {
		name: "Root",
		category: "Root",
		description,
		allowedChildrenTypes: ["page"],
		fields: {
			appName: {
				name: "App name",
				type: FieldType.Text,
				desc: "The app name will be shown in the browser's title bar.",
			},
			...sharedStyleFields,
		},
		events: {
			"wf-app-open": {
				desc: "Captures the first application load, including page key and route vars.",
				stub: wfAppOpenStub,
			},
			"wf-hashchange": {
				desc: "Capture changes to the URL hash, including page key and route vars.",
				stub: ssHashChangeStub,
			},
		},
	},
};
</script>
<script setup lang="ts">
import {
	computed,
	inject,
	watch,
	nextTick,
	onBeforeMount,
	useTemplateRef,
} from "vue";
import injectionKeys from "@/injectionKeys";
import { changePageInHash, serializeParsedHash } from "@/core/navigation";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const getChildrenVNodes = inject(injectionKeys.getChildrenVNodes);
const rootEl = useTemplateRef("rootEl");
const { isComponentVisible } = useEvaluator(wf);

const displayedPageId = computed(() => {
	const activePageId = wf.activePageId.value;
	const activePageExists = Boolean(wf.getComponentById(activePageId));
	if (activePageExists && wf.isChildOf("root", activePageId))
		return activePageId;

	const pageComponents = wf.getComponents("root", {
		includeBMC: true,
		includeCMC: true,
		sortedByPosition: true,
	});
	if (pageComponents.length == 0) return null;
	const visiblePages = pageComponents.filter((c) => isComponentVisible(c.id));
	if (visiblePages.length == 0) return null;
	return visiblePages[0].id;
});

function handleHashChange() {
	const parsedHash = serializeParsedHash();
	const event = new CustomEvent("wf-hashchange", {
		detail: {
			payload: parsedHash,
		},
	});
	rootEl.value?.dispatchEvent(event);
	if (!parsedHash.pageKey) return;
	wf.setActivePageFromKey(parsedHash.pageKey);
}

watch(displayedPageId, (newPageId) => {
	const page = wf.getComponentById(newPageId);
	const pageKey = page.content?.["key"];
	if (ssbm && !ssbm.isComponentIdSelected(newPageId)) {
		ssbm.setSelection(null);
	}
	nextTick().then(() => {
		window.scrollTo(0, 0);
		document
			.querySelector(".ComponentRenderer")
			?.parentElement?.scrollTo(0, 0);
	});
	changePageInHash(pageKey);
});

onBeforeMount(() => {
	window.addEventListener("hashchange", () => {
		handleHashChange();
	});
	handleHashChange();
});
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.CoreRoot {
	background: var(--emptinessColor);
	min-height: 100%;
	display: flex;
	width: 100%;
}

.CoreRoot.selected {
	background-color: var(--emptinessColor);
}
</style>
