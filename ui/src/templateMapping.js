
// Maps Streamsync component types to renderable Vue components

import CoreText from "./core_components/CoreText.vue";
import CoreButton from "./core_components/CoreButton.vue";
import CoreSection from "./core_components/CoreSection.vue";
import CoreWhen from "./core_components/CoreWhen.vue";
import CoreSlider from "./core_components/CoreSlider.vue";
import CorePyplot from "./core_components/CorePyplot.vue";
import CoreHeading from "./core_components/CoreHeading.vue";

export default {
    "button": CoreButton,
    "text": CoreText,
    "section": CoreSection,
    "when": CoreWhen,
    "slider": CoreSlider,
    "pyplot": CorePyplot,
    "heading": CoreHeading
}