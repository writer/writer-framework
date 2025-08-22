<docs lang="md">
Connect it to an LLM by handling the \`wf-chatbot-message\` event, which is triggered every time the user sends a message.

You can add \`actions\` to messages, which are buttons that trigger the \`wf-chatbot-action-click\`.

See the stubs for more details.
</docs>
<template>
	<div ref="rootEl" class="CoreChatbot">
		<div ref="messageAreaEl" class="messageArea">
			<div ref="messagesEl" class="messages">
				<CoreChatbotMessage
					v-for="(message, messageId) in messages"
					:key="messageId"
					:message="message"
					:use-markdown="fields.useMarkdown.value"
					:assistant-role-color="fields.assistantRoleColor.value"
					:initials="
						message.role === 'assistant'
							? fields.assistantInitials.value
							: fields.userInitials.value
					"
					@action-click="handleActionClick($event)"
				/>
				<CoreChatbotMessage
					v-if="displayExtraLoader"
					is-loading
					:initials="fields.assistantInitials.value"
				/>
			</div>
		</div>
		<template v-if="files.length > 0">
			<div class="filesArea">
				<template v-if="isUploadingFiles"> Uploading... </template>
				<div v-else class="list">
					<div v-for="uiFile in files" :key="uiFile.id" class="file">
						<div>
							<div class="name" :title="uiFile.name">
								{{ uiFile.name }}
							</div>
							<div class="size">
								{{ prettyBytes(uiFile.size) }}
							</div>
						</div>
						<WdsControl @click="removeFile(uiFile.id)">
							<WdsIcon name="trash-2" />
						</WdsControl>
					</div>
				</div>
			</div>
			<div class="filesButtons">
				<div v-if="isUploadSizeExceeded" class="sizeExceededMessage">
					<WdsIcon name="triangle-alert" />
					<span>
						Size limit of
						{{ prettyBytes(MAX_FILE_SIZE) }} exceeded.
					</span>
				</div>
				<WdsControl
					v-else-if="!isUploadingFiles"
					title="Upload"
					@click="handleUploadFiles"
				>
					<WdsIcon name="upload" />
				</WdsControl>
			</div>
		</template>
		<template
			v-if="
				pastedImages.length > 0 &&
				fields.enableImagePaste.value === true
			"
		>
			<div class="pastedImagesArea">
				<div class="pastedImagesList">
					<div
						v-for="(image, imageIndex) in pastedImages"
						:key="imageIndex"
						class="pastedImage"
						:class="{
							processing:
								processingImages &&
								image.includes('data:image/svg+xml'),
						}"
					>
						<img :src="image" alt="Pasted image" />
						<WdsControl
							class="removeImage"
							@click="handleRemovePastedImage(imageIndex)"
						>
							<WdsIcon name="x" />
						</WdsControl>
					</div>
				</div>
			</div>
		</template>
		<div class="inputArea">
			<WdsTextareaInput
				v-model="outgoingMessage"
				:placeholder="fields.placeholder.value"
				@keydown.prevent.enter="handleMessageSent"
				@paste="handlePaste"
			>
			</WdsTextareaInput>
		</div>
		<div class="inputButtons">
			<WdsControl
				class="send action"
				title="Send message"
				@click="handleMessageSent"
			>
				<WdsIcon name="wds-send" />
			</WdsControl>
			<WdsControl
				v-if="fields.enableFileUpload.value != 'no'"
				class="action"
				title="Attach files"
				@click="handleAttachFiles"
			>
				<WdsIcon name="paperclip" />
			</WdsControl>
		</div>
	</div>
</template>

<script lang="ts">
import { FieldCategory, FieldType } from "@/writerTypes";
import {
	accentColor,
	createBooleanField,
	buttonColor,
	buttonTextColor,
	containerBackgroundColor,
	cssClasses,
	primaryTextColor,
	secondaryTextColor,
	separatorColor,
} from "@/renderer/sharedStyleFields";
import prettyBytes from "pretty-bytes";
import WdsTextareaInput from "@/wds/WdsTextareaInput.vue";
import WdsControl from "@/wds/WdsControl.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import { WdsColor } from "@/wds/tokens";
import { validatorChatBotMessages } from "@/constants/validators";

const description = "A chatbot component to build human-to-AI interactions.";

const chatbotMessageStub = `
def handle_message_simple(payload, state):

	# payload contains a dict in the form { "role": "user", "message": "hello"}

	state["conversation"] += [payload]
    state["conversation"] += [{
        "role": "assistant",
        "content": "Hello human" if payload == "Hello" else "I don't understand"
    }]

    # Handle streaming by appending to the last message

    import time
    for i in range(10):
        conv = state["conversation"]
        conv[-1]["content"] += f" {i}"
        state["conversation"] = conv
        time.sleep(0.5)
`.trim();

const chatbotActionClickStub = `
def handle_action_simple(payload, state):

    # payload contains the "data" property of the action

    if payload == "change_title":
        state["app_background_color"] = "red"

# Make an action available when adding a message

def handle_message_with_action(payload, state):
    state["conversation"] += [payload]
    state["conversation"] += [{
        "role": "assistant",
        "content": "I don't know, but check this out.",
        "actions": [{
            "subheading": "Resource",
            "name": "Surprise",
            "desc": "Click to be surprised",
            "data": "change_title"
        }]
    }]
`.trim();

const fileChangeStub = `
def handle_file_upload(state, payload):

	# An array of dictionaries is provided in the payload
	# The dictionaries have the properties name, type and data
    # The data property is a file-like object

    uploaded_files = payload
    for i, uploaded_file in enumerate(uploaded_files):
        name = uploaded_file.get("name")
        file_data = uploaded_file.get("data")
        with open(f"{name}-{i}.jpeg", "wb") as file_handle:
            file_handle.write(file_data)
`.trim();

export default {
	writer: {
		name: "Chatbot",
		description,
		category: "Content",
		fields: {
			conversation: {
				name: "Conversation",
				init: "@{chat}",
				desc: "An array with messages or a variable that contains your conversation as an object.",
				type: FieldType.Object,
				validator: validatorChatBotMessages,
			},
			assistantInitials: {
				name: "Assistant initials",
				default: "AI",
				type: FieldType.Text,
			},
			userInitials: {
				name: "User initials",
				default: "YOU",
				type: FieldType.Text,
			},
			useMarkdown: createBooleanField({
				name: "Enable markdown",
				desc: "If active, the output will be sanitized; unsafe elements will be removed.",
				default: "no",
			}),
			enableFileUpload: {
				name: "Enable file upload",
				default: "no",
				type: FieldType.Text,
				options: {
					single: "Single file",
					multiple: "Multiple files",
					no: "No",
				},
			},
			enableImagePaste: createBooleanField({
				name: "Enable image paste",
				desc: "Allow users to paste images directly into the chat input using Ctrl/Cmd+V.",
				default: "yes",
			}),
			placeholder: {
				name: "Placeholder",
				default: "What do you need?",
				type: FieldType.Text,
			},
			assistantRoleColor: {
				name: "Assistant role",
				type: FieldType.Color,
				category: FieldCategory.Style,
				applyStyleVariable: true,
			},
			userRoleColor: {
				name: "User role",
				default: WdsColor.Gray1,
				type: FieldType.Color,
				category: FieldCategory.Style,
				applyStyleVariable: true,
			},
			avatarBackgroundColor: {
				name: "Avatar",
				default: WdsColor.Gray6,
				type: FieldType.Color,
				category: FieldCategory.Style,
				applyStyleVariable: true,
			},
			avatarTextColor: {
				name: "Avatar text",
				default: WdsColor.White,
				type: FieldType.Color,
				category: FieldCategory.Style,
				applyStyleVariable: true,
			},
			accentColor,
			containerBackgroundColor,
			primaryTextColor,
			secondaryTextColor,
			separatorColor,
			buttonColor: {
				...buttonColor,
				default: WdsColor.Black,
			},
			buttonTextColor: {
				...buttonTextColor,
				default: WdsColor.White,
			},
			cssClasses,
		},
		events: {
			"wf-chatbot-message": {
				desc: "Triggered when the user sends a message.",
				stub: chatbotMessageStub,
				eventPayloadExample: {
					role: "user",
					content: "I'm building a Chatbot",
				},
			},
			"wf-chatbot-action-click": {
				desc: "Handle clicks on actions.",
				stub: chatbotActionClickStub,
			},
			"wf-file-change": {
				desc: "Triggered when files are uploaded",
				stub: fileChangeStub,
			},
		},
	},
};
</script>
<script setup lang="ts">
import {
	type Ref,
	onMounted,
	onBeforeUnmount,
	inject,
	ref,
	computed,
	ComputedRef,
	useTemplateRef,
	shallowRef,
} from "vue";
import injectionKeys from "@/injectionKeys";
import { useFilesEncoder } from "@/composables/useFilesEncoder/useFilesEncoder";
import CoreChatbotMessage from "./CoreChatBot/CoreChatbotMessage.vue";
import type {
	Message,
	ContentFragment,
} from "./CoreChatBot/CoreChatbotMessage.vue";
import { useLogger } from "@/composables/useLogger";

const rootEl = useTemplateRef("rootEl");
const messageAreaEl = useTemplateRef("messageAreaEl");
const messagesEl = useTemplateRef("messagesEl");
const messageIndexLoading: Ref<number | undefined> = ref(undefined);
const fields = inject(injectionKeys.evaluatedFields);
const logger = useLogger();
let resizeObserver: ResizeObserver;

const messages: ComputedRef<Message[]> = computed(() => {
	return fields.conversation?.value ?? [];
});

const outgoingMessage: Ref<string> = ref("");

const isMultipleFilesAllowed = computed<boolean>(
	() => fields.enableFileUpload.value === "multiple",
);

const { files, calcTotalSize, addFiles, removeFile, clearFiles, encodeFiles } =
	useFilesEncoder({
		multiple: isMultipleFilesAllowed,
	});

const MAX_FILE_SIZE = 200 * 1024 * 1024;

const isUploadSizeExceeded = computed(
	() => calcTotalSize(files.value) > MAX_FILE_SIZE,
);

const displayExtraLoader = computed(() => {
	if (messageIndexLoading.value === undefined) return false;
	return messageIndexLoading.value >= messages.value.length;
});

function handleMessageSent(e: KeyboardEvent) {
	if (e.shiftKey) return;

	e.preventDefault();
	if (messageIndexLoading.value) return;
	if (!outgoingMessage.value && pastedImages.value.length === 0) return;

	messageIndexLoading.value = messages.value.length + 1;

	// Create payload based on whether we have images or just text
	type MessagePayload = {
		role: string;
		content: string | ContentFragment[];
	};
	let payload: MessagePayload;
	if (pastedImages.value.length > 0) {
		// Create multimodal content
		const contentFragments: ContentFragment[] = [];

		// Add text fragment if there's text
		if (outgoingMessage.value.trim()) {
			contentFragments.push({
				type: "text",
				text: outgoingMessage.value,
			});
		}

		// Add image fragments
		pastedImages.value.forEach((imageUrl) => {
			contentFragments.push({
				type: "image_url",
				image_url: {
					url: imageUrl,
				},
			});
		});

		payload = {
			role: "user",
			content: contentFragments,
		};
	} else {
		// Simple text message
		payload = {
			role: "user",
			content: outgoingMessage.value,
		};
	}

	const event = new CustomEvent("wf-chatbot-message", {
		detail: {
			payload,
			callback: () => {
				messageIndexLoading.value = undefined;
			},
		},
	});
	rootEl.value.dispatchEvent(event);
	outgoingMessage.value = "";
	pastedImages.value = [];
}

function handleActionClick(action: Message["actions"][number]) {
	const { data } = action;
	const event = new CustomEvent("wf-chatbot-action-click", {
		detail: {
			payload: data,
		},
	});
	rootEl.value.dispatchEvent(event);
}

function handleAttachFiles() {
	const el: HTMLInputElement = document.createElement("input");
	el.type = "file";
	if (isMultipleFilesAllowed.value) {
		el.multiple = true;
	}
	el.addEventListener("change", () => {
		addFiles(Array.from(el.files || []));
	});
	el.dispatchEvent(new MouseEvent("click"));
}

async function handlePaste(event: ClipboardEvent) {
	// Check if image pasting is enabled
	if (fields.enableImagePaste.value !== true) return;

	const items = event.clipboardData?.items;
	if (!items) return;

	const imageItems = [];
	for (let i = 0; i < items.length; i++) {
		const item = items[i];
		if (item.type.startsWith("image/")) {
			const file = item.getAsFile();
			if (file) {
				imageItems.push(file);
			}
		}
	}

	if (imageItems.length === 0) return;

	// Prevent default paste for images
	event.preventDefault();

	// Show immediate visual feedback with placeholder URLs
	const placeholderImages = imageItems.map(
		() =>
			"data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIwIiBoZWlnaHQ9IjgwIiB2aWV3Qm94PSIwIDAgMTIwIDgwIiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIxMjAiIGhlaWdodD0iODAiIGZpbGw9IiNmM2Y0ZjYiLz48Y2lyY2xlIGN4PSI2MCIgY3k9IjQwIiByPSIxNiIgZmlsbD0iIzlca2E0YWYiPjxhbmltYXRlIGF0dHJpYnV0ZU5hbWU9Im9wYWNpdHkiIHZhbHVlcz0iMC4yOzE7MC4yIiBkdXI9IjEuNXMiIHJlcGVhdENvdW50PSJpbmRlZmluaXRlIi8+PC9jaXJjbGU+PC9zdmc+",
	);
	pastedImages.value = [...pastedImages.value, ...placeholderImages];
	processingImages.value = true;

	// Process images in the background
	try {
		await Promise.all(
			imageItems.map(async (file, index) => {
				try {
					// Optimize image if it's too large
					const optimizedFile = await optimizeImage(file);
					const dataUrl = await encodeFile(optimizedFile);

					// Replace placeholder with actual image
					const currentImages = [...pastedImages.value];
					const placeholderIndex =
						currentImages.length - imageItems.length + index;
					currentImages[placeholderIndex] = dataUrl as string;
					pastedImages.value = currentImages;

					return dataUrl as string;
				} catch (error) {
					logger.error("Failed to process pasted image:", error);
					// Remove the placeholder if processing fails
					const currentImages = [...pastedImages.value];
					const placeholderIndex =
						currentImages.length - imageItems.length + index;
					currentImages.splice(placeholderIndex, 1);
					pastedImages.value = currentImages;
					return null;
				}
			}),
		);
	} catch (error) {
		logger.error("Error processing pasted images:", error);
	} finally {
		processingImages.value = false;
	}
}

function handleRemovePastedImage(index: number) {
	const newList = [...pastedImages.value];
	newList.splice(index, 1);
	pastedImages.value = newList;
}

function scrollToBottom() {
	messageAreaEl.value.scrollTo({
		top: messageAreaEl.value.scrollHeight,
		left: 0,
	});
}

const pastedImages: Ref<string[]> = shallowRef([]);
const processingImages: Ref<boolean> = ref(false);
const isUploadingFiles = ref(false);

const optimizeImage = async (file: File): Promise<File> => {
	// Only optimize if file is larger than 2MB
	if (file.size <= 2 * 1024 * 1024) {
		return file;
	}

	return new Promise((resolve) => {
		const canvas = document.createElement("canvas");
		const ctx = canvas.getContext("2d")!;
		const img = new Image();

		img.onload = () => {
			// Calculate new dimensions (max 1920x1080)
			const maxWidth = 1920;
			const maxHeight = 1080;
			let { width, height } = img;

			if (width > maxWidth || height > maxHeight) {
				const ratio = Math.min(maxWidth / width, maxHeight / height);
				width = Math.floor(width * ratio);
				height = Math.floor(height * ratio);
			}

			canvas.width = width;
			canvas.height = height;

			// Draw and compress
			ctx.drawImage(img, 0, 0, width, height);
			canvas.toBlob(
				(blob) => {
					if (blob) {
						resolve(
							new File([blob], file.name, { type: "image/jpeg" }),
						);
					} else {
						resolve(file);
					}
				},
				"image/jpeg",
				0.85,
			);
		};

		img.onerror = () => resolve(file);
		img.src = URL.createObjectURL(file);
	});
};

const encodeFile = async (file: File) => {
	const reader = new FileReader();
	reader.readAsDataURL(file);

	return new Promise((resolve, reject) => {
		reader.onload = () => resolve(reader.result);
		reader.onerror = () => reject(reader.error);
	});
};

async function handleUploadFiles() {
	if (files.value.length == 0) return;
	if (isUploadingFiles.value) return;
	if (isUploadSizeExceeded.value) return;

	isUploadingFiles.value = true;

	const { encodedFiles } = await encodeFiles();

	if (encodedFiles.length === 0) {
		isUploadingFiles.value = false;
		return;
	}

	rootEl.value.dispatchEvent(
		new CustomEvent("wf-file-change", {
			detail: {
				payload: encodedFiles,
				callback: () => {
					isUploadingFiles.value = false;
					clearFiles();
				},
			},
		}),
	);
}

onMounted(() => {
	/**
	 * A ResizeObserver allows the component to scroll to the bottom when a
	 * new message is added or grows in size. For example, after markdown rendering is finished.
	 *
	 * CSS overflow-anchor wasn't used due to problematic support in Safari.
	 */

	resizeObserver = new ResizeObserver(() => {
		scrollToBottom();
	});

	/**
	 * ResizeObserver only watches the client height, not the scroll height.
	 * So it's the element inside that needs to be watched to detect changes.
	 */

	resizeObserver.observe(messagesEl.value);
});

onBeforeUnmount(() => {
	resizeObserver.unobserve(messagesEl.value);
});
</script>
<style scoped>
@import "@/renderer/sharedStyles.css";
@import "@/renderer/colorTransformations.css";

.CoreChatbot {
	display: grid;
	grid-template-columns: 1fr 20%;
	grid-template-rows: 1fr fit-content(20%) fit-content(150px) 20%;
	height: 80vh;
	gap: 16px;
}

.messageArea {
	overflow-y: auto;
	overflow-x: hidden;
	grid-column: 1 / 3;
	grid-row: 1;
	padding-right: 16px;
}

.messages {
	display: flex;
	gap: 16px;
	flex-direction: column;
}

.filesArea {
	grid-column: 1;
	grid-row: 2;
	overflow-y: auto;
}

.filesArea .list {
	flex: 1 1 auto;
	display: flex;
	flex-wrap: wrap;
	align-items: flex-start;
	gap: 16px;
}

.file {
	background: var(--softenedSeparatorColor);
	border-radius: 8px;
	display: flex;
	gap: 16px;
	align-items: center;
	padding: 12px;
	font-size: 0.7rem;
}

.file .name {
	min-width: 5ch;
	max-width: 20ch;
	text-overflow: ellipsis;
	white-space: nowrap;
	overflow: hidden;
}

.file .size {
	margin-top: 4px;
	color: var(--secondaryTextColor);
}

.filesButtons {
	grid-column: 2;
	grid-row: 2;
	display: flex;
	flex-direction: column;
	align-items: end;
	justify-content: center;
	padding-right: 14px;
}

.pastedImagesArea {
	grid-column: 1 / 3;
	grid-row: 3;
	overflow-x: auto;
	padding: 8px 0;
}

.inputArea {
	grid-column: 1 / 3;
	grid-row: 4;
	text-align: right;
	display: flex;
	align-items: top;
}

.inputArea textarea {
	width: 100%;
	height: 100%;
	resize: none;
	border-radius: 12px;
	padding: 14px 20% 14px 14px;
	background: transparent;
}

.inputButtons {
	grid-column: 2;
	grid-row: 4;
	display: flex;
	padding: 14px;
	flex-direction: column;
	gap: 8px;
	align-items: flex-end;
}

.inputButtons .action {
	color: var(--buttonTextColor);
	background-color: var(--buttonColor);
}

.pastedImagesList {
	display: flex;
	gap: 12px;
	align-items: center;
}

.pastedImage {
	position: relative;
	flex-shrink: 0;
}

.pastedImage img {
	width: 120px;
	height: 80px;
	object-fit: cover;
	border-radius: 8px;
	box-shadow: var(--wdsShadowMd);
	display: block;
}

.pastedImage .removeImage {
	position: absolute;
	top: -8px;
	right: -8px;
	width: 32px;
	height: 32px;
}

.pastedImage.processing {
	opacity: 0.7;
	position: relative;
}

.pastedImage.processing::after {
	content: "";
	position: absolute;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
	width: 16px;
	height: 16px;
	border: 2px solid var(--wdsColorPrimary);
	border-top: 2px solid transparent;
	border-radius: 50%;
	animation: spin 1s linear infinite;
}

@keyframes spin {
	0% {
		transform: translate(-50%, -50%) rotate(0deg);
	}
	100% {
		transform: translate(-50%, -50%) rotate(360deg);
	}
}
</style>
