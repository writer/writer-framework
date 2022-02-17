<template>
	<div class="App">

		<div class="header">
			<img src="./assets/sslogo.png" alt="Streamsync" />
			<h1>Hot drinks demo</h1>
		</div>

		<div class="section">
			<h2>Gato</h2>
			Gato means cat in Spanish
		</div>

		<div v-for="component, componentId in streamsync.components" :key="componentId" class="componentShell">

			<!--<h3 class="sectionHeading">Heading</h3>-->

			<h1 v-if="component.type == 'heading'" :ref="(el) => { registerComponent(el, componentId, component) }">
				{{ getContent("text", component) }}
			</h1>

			<h3 v-if="component.type == 'label'" :ref="(el) => { registerComponent(el, componentId, component) }">
				{{ getContent("text", component) }}
			</h3>

			<input v-if="component.type == 'slider'" type="range" :value="getContent('value', component)" :ref="(el) => { registerComponent(el, componentId, component) }">

			<button v-if="component.type == 'button'" :ref="(el) => { registerComponent(el, componentId, component) }">{{ getContent("text", component) }}</button>

			<p v-if="component.type == 'text'" :ref="(el) => { registerComponent(el, componentId, component) }">{{ getContent("text", component) }}</p>


		</div>

		<img :src="streamsync.state.plot" />


	</div>
</template>

<script>
export default {
	inject: [ "streamsync" ],

	methods: {
		registerComponent: function (el, componentId, component) {
			if (el.dataset.streamsyncId) return;
			el.dataset.streamsyncId = componentId;

			if (!component.handlers) return;

			Object.keys(component.handlers).forEach(eventType => {
				el.addEventListener(eventType, (event) => { this.forwardEvent(event); });
			});
		},

		getContent: function (key, component) {
			if (!component.content) return null;
			const s = component.content[key];
			if (s.charAt(0) != "@") return s; // String literal
			const stateKey = s.substring(1); // Not a string literal, get from state

			return this.streamsync.state[stateKey];
		},

		forwardEvent: function (event) {
			this.streamsync.startTime = performance.now();
			this.streamsync.forward(event)
		}
	}

}
</script>

<style>

body {
	margin: 0;
	font-family: sans-serif;
	color: #202020;
	font-size: 0.75rem;
	--separator: rgba(0, 0, 0, 0.1);
}

.header {
	padding: 16px 24px 16px 24px;
	border-bottom: 1px solid var(--separator);
	display: flex;
	align-items: center;
}

.header img {
	height: 32px;
	margin-right: 24px;
}

h1 {
	margin: 0;
	font-weight: normal;
	font-size: 1.2rem;
}

h2 {
	font-size: 0.9rem;
	letter-spacing: 0.03rem;
	font-weight: bold;
	margin: 0;
	margin-bottom: 8px;
}

h3 {
	margin: 0;
	font-weight: bold;
	font-size: 1rem;
}

.section {
	padding: 24px;
	display: block;
	border-bottom: 1px solid var(--separator);
}

p {
	margin: 0;
}

.componentShell {
	margin: 16px;
	padding: 16px;
	position: relative;
	display: block;
	z-index: 1;
/*	border: 1px solid #f0f0f0;*/
	border-radius: 4px;
}

.componentShell .sectionHeading {
	padding-bottom: 16px;
	margin-bottom: 16px;
	border-bottom: 1px solid #f0f0f0;
}

</style>
