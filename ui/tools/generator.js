/* eslint-disable @typescript-eslint/no-var-requires */
const fs = require("fs").promises;
const { createServer } = require("vite");

const getPyType = (type) => {
	switch (type) {
		case "Number":
			return "Union[float, str]";
		case "Object":
			return "Union[Dict, str]";
		case "Key-Value":
			return "Union[Dict, str]";
		default:
			return "str";
	}
}

async function loadComponents() {
	const vite = await createServer({
		server: {
			middlewareMode: true,
		},
		appType: "custom",
	});

	const { data } = await vite.ssrLoadModule("./tools/getComponents.ts");
	// eslint-disable-next-line no-console
	console.log("Writing components JSON to", process.argv[3]);
	await fs.writeFile(process.argv[3], JSON.stringify(data, null, 2));
	await vite.close();
	return data.map((component) => {
		return {
			nameTrim: component.name.replaceAll(/\s/g, ""),
			...component,
		};
	});
}

function generateImports() {
	return `from typing import TypedDict, Union, Optional, Dict, Callable
from streamsync.ui_manager import StreamsyncUI
from streamsync.core_ui import Component
  `;
}

function generateTypes(data) {
	const types = data.map((component) => {
		let type = `

${component.nameTrim}Props = TypedDict('${component.nameTrim}Props', {`;
		type += Object.entries(component.fields)
			.map(([key, field]) => {
				return `
    "${key}": ${getPyType(field.type)}`;
			})
			.join(",");
		type += `
}, total=False)`;

		type += `

${component.nameTrim}EventHandlers = TypedDict('${component.nameTrim}EventHandlers', {`;
		type += Object.entries(component.events || {})
			.map(([key]) => {
				return `
    "${key}": Union[str, Callable]`;
			})
			.join(",");
		type += `
}, total=False)`;
		return type;
	});
	return types.join("");
}

function generateClass() {
	return `

class StreamsyncUIManager(StreamsyncUI):
    """The StreamsyncUIManager class is intended to include dynamically-
    generated methods corresponding to UI components defined in the Vue
    frontend during the build process.

    This class serves as a bridge for programmatically interacting with the
    frontend, allowing methods to adapt to changes in the UI components without
    manual updates.
    """

    # Hardcoded classes for proof-of-concept purposes
  `;
}

function generateComponentDefaults(component) {
	return Object.entries(component.fields)
		.filter(([, field]) => typeof field.default !== "undefined")
		.map(([key, field]) => {
			const defaultValue = ("" + (field?.default || ""))
				?.replaceAll('"', '\\"')
				?.replaceAll("\n", "\\n");
			return `            "${key}": "${defaultValue}",`;
		})
		.join("\n");

	//`  content = { defaultContent, content }`
}

function generateMethods(data) {
	const methods = data.map((component) => {
		return `
    def ${component.nameTrim}(self, 
            content: ${component.nameTrim}Props = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[${component.nameTrim}EventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        ${component.description}
        """
        defaultContent: ${component.nameTrim}Props = {
${generateComponentDefaults(component)}
        }
        content = defaultContent | content
        component = self.${component.allowedChildrenTypes?.length ? "create_container_component" : "create_component"}(
            '${component.type}',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    `;
	});
	return methods.join("");
}

loadComponents().then((data) => {
	// eslint-disable-next-line no-console
	console.log("Writing ui.py to", process.argv[2]);
	return fs.writeFile(
		process.argv[2],
		generateImports() +
			generateTypes(data) +
			generateClass() +
			generateMethods(data),
	);
});
