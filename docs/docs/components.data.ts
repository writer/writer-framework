import defs from "streamsync-ui/components.codegen.json";
import { highlightCode } from "./core";

export default {
	async load() {
		let components = []
		for (let component of defs) {
			// highlight stub in event handler
			for (let event in component.events) {
				let eventInfo = component.events[event];
				eventInfo.code = highlightCode(eventInfo.stub)
			}

			components.push(component)
		}

		return components
	}
}
