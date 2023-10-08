<template>
	<div class="LeafletMap" ref="rootEl"></div>
</template>

<script>
</script>

<script lang="ts">
import { computed, inject, Ref } from "vue";
import { ref } from "vue";
import { cssClasses } from "../renderer/sharedStyleFields";

import { FieldCategory, FieldType } from "../streamsyncTypes";
const defaultData = {
	markers: [
		{data: [50, 50], title: "This is a marker", group:"red"},
		{data: [40, 50], title: "This is a marker", group:"red"},
		{data: [50, 40], title: "This is a marker", group:"blue"},
	],
	circle_markers: [
		{data: [50, 50], title: "This is a marker", group:"red"},
		{data: [40, 50], title: "This is a marker", group:"red"},
		{data: [50, 40], title: "This is a marker", group:"blue"},
	],
	circles: [
		{data: [50, 50], title: "This is a circle", group:"red"},
		{data: [40, 50], title: "This is a circle", group:"red"},
		{data: [50, 40], title: "This is a circle", group:"blue"},
	],
	polylines: [
		{data: [[45.51, -122.68],[37.77, -122.43],[34.04, -118.2]], title: "this is a polyline", group:"yellow"}
	],
	polygons: [
		{data: [
  			[[37, -109.05],[41, -109.03],[41, -102.05],[37, -102.04]], // outer ring
  			[[37.29, -108.58],[40.71, -108.58],[40.71, -102.50],[37.29, -102.50]] // hole
			],
			options: {color: "black"},
			title: "this is a polyline", group:"green"
		}
	]

};
const defaultBasemaps = [
		{name: "OpenStreetMap", url:'https://tile.openstreetmap.org/{z}/{x}/{y}.png', options: {}},
		{name: "OpenStreetMap.HOT", url:'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', options: {}},
		{name: "OpenTopoMap", url: "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", options: {}}
	];

const defaultView = {
	center: [0, 0],
	zoom: 1
}

export default {    
    streamsync: {
		name: "Leaflet",
		description: "Shows a message in the shape of a speech bubble.",
		category: "Content",
		
        // Fields will be editable via Streamsync Builder
        
        fields: {
			text: {
				name: "Text",
				type: FieldType.Text,
			},
			view: {
				name: "View",
				type:FieldType.KeyValue,
				default: JSON.stringify(defaultView, null, 2),
			},
			basemaps: {
				name: "Basemap",
				type: FieldType.KeyValue,
				default: JSON.stringify(defaultBasemaps, null, 2),
			},
			data: {
				name: "Data",
				type: FieldType.KeyValue,
				default: JSON.stringify(defaultData, null, 2),
			},
		},

        // Preview field is used in the Component Tree

		previewField: "text",
	},
};
</script>
<script setup lang="ts">
import "leaflet/dist/leaflet.css";

import { FieldType } from "../streamsyncTypes";
import injectionKeys from "../injectionKeys";
import { inject } from "vue";
import { useFormValueBroker } from "../renderer/useFormValueBroker";
import { computed, onMounted, Ref, ref, watch } from "vue";
import { makeVector } from "@apache-arrow/ts";

const rootEl: Ref<HTMLElement> = ref(null);
const fields = inject(injectionKeys.evaluatedFields);
const ss = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);
const flattenedInstancePath = inject(injectionKeys.flattenedInstancePath);

onMounted(async () => {
	const L = await import("leaflet");
	
	var map = L.map(
		rootEl.value, {})
		.setView(fields.view.value.center, fields.view.value.zoom);

	var myBasemaps = Object.fromEntries(
		fields.basemaps.value.map((basemap, i) => { 
			return [basemap.name, L.tileLayer(basemap.url, basemap.options).addTo(map)]
		})
	);

	let vector_layers = {
		"rectangles": L.rectangle,
		"polygons": L.polygon,
		"polylines": L.polyline,
		"circles": L.circle, 
		"markers": L.marker,
		"circle_markers": L.circleMarker
	};

	var myOverlays = {}
	Object.entries(vector_layers).map((item) => {
		let [vectorLayer, callback] = item;
		if (vectorLayer in fields.data.value) {
			for (var vector of fields.data.value[vectorLayer]) {
				var m = callback(vector.data, vector.options? vector.options : {}).addTo(map)
				if (vector.title)
					m.bindPopup(vector.title)
				if (vector.group) {
					if (vector.group in myOverlays)
						myOverlays[vector.group].push(m);	
					else
						myOverlays[vector.group] = [m]
				}
			};
		}
	})

	var layers = {}
	for (let k in myOverlays) 
		layers[k] = L.layerGroup(myOverlays[k])

	L.control.layers(myBasemaps, layers, {}).addTo(map);
});
</script>

<style scoped>
@import "../renderer/sharedStyles.css";

.LeafletMap {
	height: 400px;
	width: 100%;
}

</style>
