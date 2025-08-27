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
						:key="imageIds[imageIndex]"
						class="pastedImage"
					>
						<WdsSkeletonLoader
							v-if="imageProcessingState[imageIndex]"
							class="imageSkeletonLoader"
						/>
						<img
							v-if="!imageProcessingState[imageIndex] && image"
							:src="image"
							alt="Pasted image"
						/>
						<WdsControl
							class="removeImage"
							:aria-label="`Remove pasted image ${imageIndex + 1}`"
							@click="handleRemovePastedImage(imageIndex)"
						>
							<WdsIcon name="x" />
						</WdsControl>
					</div>
				</div>
			</div>
		</template>
		<template v-if="errorMessage">
			<div class="errorMessage" :class="{ 'fade-out': isErrorFadingOut }">
				<WdsIcon name="alert-circle" />
				<span>{{ errorMessage }}</span>
			</div>
		</template>
		<div class="inputArea">
			<WdsTextareaInput
				v-model="outgoingMessage"
				:placeholder="fields.placeholder.value"
				@keydown.enter.exact.prevent="handleMessageSent"
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
import WdsSkeletonLoader from "@/wds/WdsSkeletonLoader.vue";

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
import { optimizeImage } from "@/utils/img";

const rootEl = useTemplateRef("rootEl");
const messageAreaEl = useTemplateRef("messageAreaEl");
const messagesEl = useTemplateRef("messagesEl");
const messageIndexLoading: Ref<number | undefined> = ref(undefined);
const fields = inject(injectionKeys.evaluatedFields);
const logger = useLogger();
const pastedImages = shallowRef<(string | null)[]>([]);
const imageProcessingState = shallowRef<boolean[]>([]);
const imageIds = shallowRef<string[]>([]);
let nextImageId = 0;
const processingImages = ref(false);
const errorMessage: Ref<string | null> = ref(null);
const isErrorFadingOut = ref(false);
const isUploadingFiles = ref(false);
let resizeObserver: ResizeObserver;
let errorTimeout: number | undefined;

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

function handleMessageSent(e?: KeyboardEvent | MouseEvent) {
	// Ignore key events while composing (IME)
	if (e && "isComposing" in e && (e as KeyboardEvent).isComposing) return;
	if (messageIndexLoading.value) return;
	if (processingImages.value) {
		showError("Images are still processing. Please wait a moment…");
		return;
	}
	const trimmedMessage = outgoingMessage.value?.trim();
	if (!trimmedMessage && pastedImages.value.length === 0) return;

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
		pastedImages.value
			.filter((imageUrl): imageUrl is string => imageUrl !== null)
			.forEach((imageUrl) => {
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
			content: trimmedMessage!,
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
	imageProcessingState.value = [];
	imageIds.value = [];
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
	el.click();
}

async function handlePaste(event: ClipboardEvent) {
	// Check if image pasting is enabled
	if (fields.enableImagePaste.value !== true) return;

	const items = event.clipboardData?.items;
	if (!items) return;

	// Define constraints
	const MAX_IMAGES = 10;
	const MAX_TOTAL_SIZE = 50 * 1024 * 1024; // 50MB total
	const MAX_IMAGE_SIZE = 10 * 1024 * 1024; // 10MB per image
	const SUPPORTED_FORMATS = [
		"image/jpeg",
		"image/jpg",
		"image/png",
		"image/webp",
	];

	const imageItems = [];
	let totalSize = 0;
	let skippedLargeImages = 0;
	let skippedUnsupportedFormats = 0;

	for (let i = 0; i < items.length; i++) {
		const item = items[i];
		if (item.type.startsWith("image/")) {
			// Check if format is supported
			if (!SUPPORTED_FORMATS.includes(item.type.toLowerCase())) {
				skippedUnsupportedFormats++;
				continue;
			}

			const file = item.getAsFile();
			if (file) {
				// Check individual image size
				if (file.size > MAX_IMAGE_SIZE) {
					skippedLargeImages++;
					continue;
				}
				totalSize += file.size;
				imageItems.push(file);
			}
		}
	}

	if (imageItems.length === 0) {
		if (skippedUnsupportedFormats > 0 && skippedLargeImages > 0) {
			showError(
				`Images not added: ${skippedUnsupportedFormats} unsupported format(s) (only JPG, JPEG, PNG supported), ${skippedLargeImages} too large (max ${MAX_IMAGE_SIZE / 1024 / 1024}MB each).`,
			);
		} else if (skippedUnsupportedFormats > 0) {
			showError(
				`Unsupported image format(s). Only JPG, JPEG, and PNG images are supported.`,
			);
		} else if (skippedLargeImages > 0) {
			showError(
				`Image too large. Maximum size is ${MAX_IMAGE_SIZE / 1024 / 1024}MB per image.`,
			);
		}
		return;
	}

	// Check total number of images
	const totalImages = pastedImages.value.length + imageItems.length;
	if (totalImages > MAX_IMAGES) {
		const allowedCount = MAX_IMAGES - pastedImages.value.length;
		if (allowedCount <= 0) {
			showError(
				`Maximum ${MAX_IMAGES} images allowed. Please remove some images first.`,
			);
			return;
		}
		// Only take what we can fit
		imageItems.splice(allowedCount);
		showError(
			`Only ${allowedCount} image(s) added. Maximum ${MAX_IMAGES} images allowed.`,
		);
	}

	// Check total size
	if (totalSize > MAX_TOTAL_SIZE) {
		showError(
			`Total size too large (${(totalSize / 1024 / 1024).toFixed(1)}MB). Maximum ${MAX_TOTAL_SIZE / 1024 / 1024}MB total.`,
		);
		return;
	}

	// Show warning for skipped images
	const warnings = [];
	if (skippedLargeImages > 0) {
		warnings.push(
			`${skippedLargeImages} image(s) too large (max ${MAX_IMAGE_SIZE / 1024 / 1024}MB each)`,
		);
	}
	if (skippedUnsupportedFormats > 0) {
		warnings.push(
			`${skippedUnsupportedFormats} unsupported format(s) (only JPG, JPEG, PNG supported)`,
		);
	}
	if (warnings.length > 0) {
		showError(`${warnings.join(", ")} - these images were skipped.`);
	}

	// Prevent default paste for images
	event.preventDefault();

	// Show immediate visual feedback with placeholder URLs and stable IDs
	const newImageSlots = imageItems.map(() => null);
	const newProcessingStates = imageItems.map(() => true);
	const newImageIds = imageItems.map(() => `img-${nextImageId++}`);
	pastedImages.value = [...pastedImages.value, ...newImageSlots];
	imageProcessingState.value = [
		...imageProcessingState.value,
		...newProcessingStates,
	];
	imageIds.value = [...imageIds.value, ...newImageIds];
	processingImages.value = true;

	// Process images in the background
	const failures: number[] = [];
	try {
		await Promise.all(
			imageItems.map(async (file, index) => {
				try {
					// Optimize image if it's too large
					const optimizedFile = await optimizeImage(file, logger);
					if (optimizedFile === file && file.size > 2 * 1024 * 1024) {
						logger.log(
							`Using original file for ${file.name} (optimization failed)`,
						);
					} else if (optimizedFile !== file) {
						logger.log(
							`Successfully optimized ${file.name} from ${(file.size / 1024 / 1024).toFixed(2)}MB to ${(optimizedFile.size / 1024 / 1024).toFixed(2)}MB`,
						);
					}
					const dataUrl = await encodeFile(optimizedFile);

					// Set the processed image and update processing state using stable ID
					const imageId = newImageIds[index];
					const imageIndex = imageIds.value.findIndex(
						(id) => id === imageId,
					);
					if (
						imageIndex !== -1 &&
						imageIndex < pastedImages.value.length
					) {
						const currentImages = [...pastedImages.value];
						const currentProcessingState = [
							...imageProcessingState.value,
						];

						currentImages[imageIndex] = dataUrl as string;
						currentProcessingState[imageIndex] = false;

						pastedImages.value = currentImages;
						imageProcessingState.value = currentProcessingState;
					}

					return dataUrl as string;
				} catch (error) {
					logger.error("Failed to process pasted image:", error);
					// Track failure for later cleanup instead of immediate splice
					failures.push(index);
					return null;
				}
			}),
		);

		// Process failures using stable IDs, in descending order to preserve indices
		failures
			.map((failureIndex) => ({
				failureIndex,
				imageId: newImageIds[failureIndex],
			}))
			.map(({ imageId }) =>
				imageIds.value.findIndex((id) => id === imageId),
			)
			.filter((imageIndex) => imageIndex !== -1)
			.sort((a, b) => b - a)
			.forEach((imageIndex) => {
				if (imageIndex < pastedImages.value.length) {
					const currentImages = [...pastedImages.value];
					const currentProcessingState = [
						...imageProcessingState.value,
					];
					const currentIds = [...imageIds.value];

					currentImages.splice(imageIndex, 1);
					currentProcessingState.splice(imageIndex, 1);
					currentIds.splice(imageIndex, 1);

					pastedImages.value = currentImages;
					imageProcessingState.value = currentProcessingState;
					imageIds.value = currentIds;
				}
			});
	} catch (error) {
		logger.error("Error processing pasted images:", error);
	} finally {
		processingImages.value = false;
	}
}

function handleRemovePastedImage(index: number) {
	const newImageList = [...pastedImages.value];
	const newProcessingList = [...imageProcessingState.value];
	const newIdList = [...imageIds.value];

	newImageList.splice(index, 1);
	newProcessingList.splice(index, 1);
	newIdList.splice(index, 1);

	pastedImages.value = newImageList;
	imageProcessingState.value = newProcessingList;
	imageIds.value = newIdList;
}

function showError(message: string) {
	errorMessage.value = message;
	isErrorFadingOut.value = false;
	// Clear any existing timeout
	if (errorTimeout) {
		clearTimeout(errorTimeout);
	}
	// Auto-hide error after 5 seconds with fade-out animation
	errorTimeout = setTimeout(() => {
		// Start fade-out animation
		isErrorFadingOut.value = true;
		// Remove the message after animation completes
		setTimeout(() => {
			errorMessage.value = null;
			isErrorFadingOut.value = false;
		}, 300); // Match animation duration
	}, 5000) as unknown as number;
}

function scrollToBottom() {
	messageAreaEl.value.scrollTo({
		top: messageAreaEl.value.scrollHeight,
		left: 0,
	});
}

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
	if (errorTimeout) {
		clearTimeout(errorTimeout);
		errorTimeout = undefined;
	}
});
</script>
<style scoped>
@import "@/renderer/sharedStyles.css";
@import "@/renderer/colorTransformations.css";

.CoreChatbot {
	display: grid;
	grid-template-columns: 1fr 20%;
	grid-template-rows:
		1fr fit-content(20%) fit-content(150px) fit-content(60px)
		fit-content(40px);
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

.errorMessage {
	grid-column: 1 / 3;
	grid-row: 5;
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 8px 12px;
	background-color: var(--wdsColorOrange1);
	border: 1px solid var(--wdsColorOrange3);
	color: var(--wdsColorOrange5);
	border-radius: 8px;
	font-size: 14px;
	animation: fadeIn 0.3s ease-out;
}

.errorMessage.fade-out {
	animation: fadeOut 0.3s ease-out forwards;
}

.errorMessage .WdsIcon {
	flex-shrink: 0;
	color: var(--wdsColorOrange5);
}

@keyframes fadeIn {
	from {
		opacity: 0;
	}
	to {
		opacity: 1;
	}
}

@keyframes fadeOut {
	from {
		opacity: 1;
	}
	to {
		opacity: 0;
	}
}

.imageSkeletonLoader {
	width: 120px;
	height: 80px;
	border-radius: 8px;
	position: absolute;
	top: 0;
	left: 0;
}
</style>
