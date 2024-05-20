---
outline: [2, 2]
---

<script setup>
    import defs from "writer-ui/components.codegen.json";
	import { categories, categoryDescription } from "../core";
	import { withBase } from 'vitepress'
</script>

# Component list

This list is automatically generated from the framework's source code.

<div v-for="categoryKey in categories()" class="componentCategory">
    <h2 :id="categoryKey">{{categoryKey}}</h2>
    {{ categoryDescription(categoryKey) }}
    <div class="boxContainer">
        <div v-for="def in defs.filter(d => d.category == categoryKey)" class="box">
			<a :href="withBase(`/components/${def.type}.html`)" class="componentLink">
				<h3 :id="def.type">{{def.name}}</h3>
				<div class="imageContainer">
					<div class="imageContainerInner">
						<img :src="withBase(`/components/${def.type}.png`)" />
					</div>
				</div>
			</a>
        </div>
    </div>
</div>

<style>

.componentCategory .secondaryText {
    color: #909090;
}

.componentCategory .boxContainer {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    margin-top: 16px;
}

.componentCategory .box {
    border: 1px solid var(--vp-c-divider);
    border-radius: 8px;
}

.componentCategory .box h3 {
    margin: 16px;
    font-size: 1rem;
    font-weight: normal;
}

.componentCategory .box .imageContainer {
    background: #E9EEF1;
    border-top: 1px solid #E9EEF1;
    border-bottom: 1px solid #E9EEF1;
    width: 100%;
    height: 160px;
    overflow: hidden;
    padding: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.componentCategory .box .imageContainerInner {
    display: flex;
    align-items: flex-start;
    max-height: 144px;
}

.componentCategory .box img {
    max-height: 144px;
}

.componentCategory .box summary {
    margin-bottom: 0;
}

.componentCategory .box .descriptionContainer {
    padding: 16px;
}

.componentLink h3 {
	color: var(--vp-c-text-1);
}

.vp-doc a {
	text-decoration: none;
}

</style>
