import { App } from "vue";

export function setCaptureTabsDirective(app: App<Element>) {
	app.directive("capture-tabs", {
		mounted: (el: HTMLTextAreaElement) => {
			el.addEventListener("keydown", (ev) => {
				if (ev.key != "Tab") return;
				ev.preventDefault();
				el.setRangeText(
					"  ",
					el.selectionStart,
					el.selectionStart,
					"end",
				);
			});
		},
	});
}