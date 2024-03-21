const fs = require('fs');
const components = require('streamsync-ui/components.json');

describe('Components docs', () => {
	for (const component of components) {
		it(`${component.name} - should have an image`, () => {
			expect(() => {
				fs.accessSync(`./docs/public/components/${component.type}.png`);
			}).not.toThrow();
		});
	}
});

