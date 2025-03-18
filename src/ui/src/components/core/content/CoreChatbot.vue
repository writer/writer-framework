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
				<div v-if="!isUploadingFiles" class="list">
					<div
						v-for="(file, fileIndex) in files"
						:key="fileIndex"
						class="file"
					>
						<div>
							<div class="name" :title="file.name">
								{{ file.name }}
							</div>
							<div class="size">
								{{ prettyBytes(file.size) }}
							</div>
						</div>
						<WdsControl @click="handleRemoveFile(fileIndex)">
							<i class="material-symbols-outlined"> delete </i>
						</WdsControl>
					</div>
				</div>
			</div>
			<div class="filesButtons">
				<WdsControl
					v-if="!isUploadSizeExceeded && !isUploadingFiles"
					title="Upload"
					@click="handleUploadFiles"
				>
					<i class="material-symbols-outlined">upload</i>
				</WdsControl>
				<div v-if="isUploadSizeExceeded" class="sizeExceededMessage">
					<i class="material-symbols-outlined">warning</i>
					Size limit of
					{{ prettyBytes(MAX_FILE_SIZE) }} exceeded.
				</div>
			</div>
		</template>
		<div class="inputArea">
			<WdsTextareaInput
				v-model="outgoingMessage"
				:placeholder="fields.placeholder.value"
				@keydown.prevent.enter="handleMessageSent"
			>
			</WdsTextareaInput>
		</div>
		<div class="inputButtons">
			<WdsControl
				class="send action"
				title="Send message"
				@click="handleMessageSent"
			>
				<CoreChatbotSentMessageIcon />
			</WdsControl>
			<WdsControl
				v-if="fields.enableFileUpload.value != 'no'"
				class="action"
				title="Attach files"
				@click="handleAttachFiles"
			>
				<i class="material-symbols-outlined">attach_file</i>
			</WdsControl>
		</div>
	</div>
</template>

<script lang="ts">
import {
	FieldCategory,
	FieldType,
	WriterComponentDefinition,
} from "@/writerTypes";
import {
	accentColor,
	baseYesNoField,
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
import { WdsColor } from "@/wds/tokens";
import { validatorChatBotMessages } from "@/constants/validators";

const MAX_FILE_SIZE = 200 * 1024 * 1024;

const description = "A chatbot component to build human-to-AI interactions.";

const initConversation = `[
  {
  "role": "assistant",
  "content": "How can I help you?"
  },
  {
  "role": "user",
  "content": "I'm building a Chatbot"
  }
]`;

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
				init: initConversation,
				desc: "An array with messages or a writer.ai.Conversation object.",
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
			useMarkdown: {
				...baseYesNoField,
				name: "Use Markdown",
				desc: "If active, the output will be sanitized; unsafe elements will be removed.",
				default: "no",
			},
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
	shallowRef,
	inject,
	ref,
	computed,
	ComputedRef,
	useTemplateRef,
} from "vue";
import injectionKeys from "@/injectionKeys";
import CoreChatbotSentMessageIcon from "./CoreChatBot/CoreChatbotSentMessageIcon.vue";
import CoreChatbotMessage from "./CoreChatBot/CoreChatbotMessage.vue";
import type { Message } from "./CoreChatBot/CoreChatbotMessage.vue";

const rootEl = useTemplateRef("rootEl");
const messageAreaEl = useTemplateRef("messageAreaEl");
const messagesEl = useTemplateRef("messagesEl");
const messageIndexLoading: Ref<number | undefined> = ref(undefined);
const fields = inject(injectionKeys.evaluatedFields);
const files: Ref<File[]> = shallowRef([]);
const isUploadingFiles = ref(false);
let resizeObserver: ResizeObserver;

const messages: ComputedRef<Message[]> = computed(() => {
	return fields.conversation?.value ?? [];
});

const outgoingMessage: Ref<string> = ref("");

const isUploadSizeExceeded = computed(() => {
	let filesSize = 0;
	Array.from(files.value).forEach((file) => {
		filesSize += file.size;
	});
	return filesSize >= MAX_FILE_SIZE;
});

const displayExtraLoader = computed(() => {
	if (messageIndexLoading.value === undefined) return false;
	return messageIndexLoading.value >= messages.value.length;
});

function handleMessageSent() {
	if (messageIndexLoading.value) return;
	messageIndexLoading.value = messages.value.length + 1;
	const event = new CustomEvent("wf-chatbot-message", {
		detail: {
			payload: {
				role: "user",
				content: outgoingMessage.value,
			},
			callback: () => {
				messageIndexLoading.value = undefined;
			},
		},
	});
	rootEl.value.dispatchEvent(event);
	outgoingMessage.value = "";
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
	if (fields.enableFileUpload.value == "multiple") {
		el.multiple = true;
	}
	el.addEventListener("change", () => {
		// A new list is created to allow shallowRef to detect the change

		let newList: File[];
		if (fields.enableFileUpload.value == "multiple") {
			newList = [...files.value];
		} else {
			newList = [];
		}
		Array.from(el.files).forEach((file) => {
			newList.push(file);
		});
		files.value = newList;
	});
	el.dispatchEvent(new MouseEvent("click"));
}

function handleRemoveFile(index: number) {
	const newList = files.value.toSpliced(index, 1);
	files.value = newList;
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

	isUploadingFiles.value = true;

	const getPayload = async () => {
		let accumSize = 0;
		const encodedFiles = Promise.all(
			Array.from(files.value).map(async (f) => {
				accumSize += f.size;
				const fileItem = {
					name: f.name,
					type: f.type,
					data: await encodeFile(f),
				};
				return fileItem;
			}),
		);
		if (accumSize > MAX_FILE_SIZE) {
			alert("Size limit exceeded.");
			return;
		}
		return encodedFiles;
	};

	const payload = await getPayload();
	if (!payload) {
		isUploadingFiles.value = false;
		return;
	}

	const event = new CustomEvent("wf-file-change", {
		detail: {
			payload,
			callback: () => {
				isUploadingFiles.value = false;
				files.value = [];
			},
		},
	});

	rootEl.value.dispatchEvent(event);
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
	grid-template-rows: 1fr fit-content(20%) 20%;
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

.inputArea {
	grid-column: 1 / 3;
	grid-row: 3;
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
	grid-row: 3;
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
</style>
