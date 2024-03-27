<script setup>
	import { componentByName, generateLowCodeUsage, generateEventHandler, highlightCode, values } from "../core";
	import { withBase } from 'vitepress'

	const component = componentByName("@{component_name}");
</script>

<h1>{{ component.name }}</h1>

{{ component.description }}

<div class="imageContainer">
	<img :src="withBase(`/components/${component.type}.png`)">
</div>

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

This component can be used in python

<div class="language-py vp-adaptive-theme">
	<button title="Copy Code" class="copy"></button>
	<span class="lang">python</span>
	<pre><code class="codeblock" v-html="generateLowCodeUsage(component.name)"></code></pre>
</div>

<div v-if="component.events">
	<div>The function <code>handle_event</code> should be implemented in your code to handle events.</div>
	<div class="language-py vp-adaptive-theme">
		<button title="Copy Code" class="copy"></button>
		<span class="lang">python</span>
		<pre><code class="codeblock" v-html="generateEventHandler()"></code></pre>
	</div>
</div>


<h2>Reference</h2>

* [Learn more about building Streamsync UI using low code](../modifying-app-ui-through-backend)
* <a :href="`https://github.com/streamsync-cloud/streamsync/blob/dev/${component.source_link}`" target="_blank" >Explore the source on GitHub</a>


<style>

.imageContainer {
	display: flex;
	justify-content: center;
	margin: 16px 0;
}

.imageContainer img {
    background: #E9EEF1;
    border-top: 1px solid #E9EEF1;
    border-bottom: 1px solid #E9EEF1;
    height: auto;
	max-width: 50%;
	min-width: 30%;
    padding: 8px;
}

.codeblock {
	padding: 8px;
	font-size: 14px !important;
}
</style>
