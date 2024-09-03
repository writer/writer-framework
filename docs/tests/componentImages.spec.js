const fs = require('fs');
const components = require('writer-ui/components.codegen.json');

describe('Components docs', () => {
	for (const component of components) {
		if (component.toolkit && component.toolkit !== "core") return;
		it(`${component.name} - should have an image`, () => {
			expect(() => {
				fs.accessSync(`./framework/public/components/${component.type}.png`);
			}).not.toThrow();
		});
	}
});

