<script setup>
	import { componentByName, generateLowCodeUsage, generateEventHandler, highlightCode, values, markdownToHtml } from "../core";
	import { withBase } from 'vitepress'

	const component = componentByName("@{component_name}");
</script>

<h1>{{ component.name }}</h1>

{{ component.description }}

<div class="expandedImageContainer">
	<div class="expandedImageContainerInner">
		<img :src="withBase(`/components/${component.type}.png`)">
	</div>
</div>

<div v-html="`${ markdownToHtml(component.docs) }`"></div>

<div v-if="component.fields">
	<h2>Fields</h2>
	<table>
		<thead>
			<td>Name</td>
			<td>Type</td>
			<td>Description</td>
			<td>Options</td>
		</thead>
		<tr v-for="field in component.fields">
			<td>{{ field.name }}</td>
			<td>{{ field.type }}</td>
			<td>{{ field.desc }}</td>
			<td>
                <ul>
                    <li v-for="option in values(field.options)">{{ option }}</li>
                </ul>
			</td>
		</tr>
	</table>
</div>

<div v-if="component.events">
	<h2>Events</h2>
	<table>
		<thead>
			<td>Name</td>
			<td>Description</td>
			<td>Usage</td>
		</thead>
		<tr v-for="[event, eventInfo] in Object.entries(component.events)">
			<td>{{ event }}</td>
			<td>{{ eventInfo.desc }}</td>
			<td class="language-py">
				<pre><code class="codeblock" v-html="highlightCode(eventInfo.stub)"></code></pre>
			</td>
		</tr>
	</table>
</div>

<h2>Low code usage</h2>

This component can be declared directly in Python, using [backend-driven UI](../backend-driven-ui).

<div class="language-py vp-adaptive-theme">
	<button title="Copy Code" class="copy"></button>
	<span class="lang">python</span>
	<pre><code class="codeblock" v-html="generateLowCodeUsage(component.name)"></code></pre>
</div>

<div v-if="component.events">
	<div>A function, in this example <code>handle_event</code>, should be implemented in your code to handle events.</div>
	<div class="language-py vp-adaptive-theme">
		<button title="Copy Code" class="copy"></button>
		<span class="lang">python</span>
		<pre><code class="codeblock" v-html="generateEventHandler()"></code></pre>
	</div>
</div>


<h2>Reference</h2>

* <a :href="`https://github.com/streamsync-cloud/streamsync/blob/dev/src/ui/${component.fileRef}`" target="_blank" >Explore this component's source code on GitHub</a>


<style>

.expandedImageContainer {
	padding: 16px;
	border-radius: 16px;
    background: #E9EEF1;
	overflow: hidden;
	display: flex;
	justify-content: center;
}

.expandedImageContainerInner {
    display: flex;
    align-items: flex-start;
	max-width: 300px;
    max-height: 210px;
}

.expandedImageContainer img {
    max-height: 210px;
}

thead {
	font-weight: bold;
}

.codeblock {
	padding: 8px;
	font-size: 14px !important;
}
</style>
