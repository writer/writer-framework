<docs lang="md">
Connect it to an LLM by handling the \`ss-chatbot-message\` event, which is triggered every time the user sends a message.

You can add \`actions\` to messages, which are buttons that trigger the \`ss-chatbot-action-click\`.

See the stubs for more details.
</docs>
<template>
	<div ref="rootEl" class="CoreChatbot">
		<div ref="messageAreaEl" class="messageArea">
			<div ref="messagesEl" class="messages">
				<div
					v-for="(message, messageId) in messages"
					:key="messageId"
					class="message"
					:class="message.role"
				>
					<div class="avatar">
						{{
							message.role == "assistant"
								? fields.assistantInitials.value
								: fields.userInitials.value
						}}
					</div>
					<div class="content">
						<div class="text">
							<BaseMarkdown
								v-if="fields.useMarkdown.value == 'yes'"
								:raw-text="message.content?.trim()"
							>
							</BaseMarkdown>
							<template v-else>
								{{ message.content?.trim() }}
							</template>
						</div>
						<div v-if="message.actions" class="actions">
							<button
								v-for="(action, actionIndex) in message.actions"
								:key="actionIndex"
								class="action"
								@click="handleActionClick(action)"
							>
								<div
									v-if="action.subheading"
									class="subheading"
								>
									{{ action.subheading }}
								</div>
								<h3 class="name">{{ action.name }}</h3>
								<div v-if="action.desc" class="desc">
									{{ action.desc }}
								</div>
							</button>
						</div>
					</div>
				</div>
				<div v-if="isResponsePending" class="loadingContainer">
					<LoadingSymbol class="loadingSymbol"></LoadingSymbol
					>Loading...
				</div>
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
				<svg
					width="15"
					height="12"
					viewBox="0 0 15 12"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						d="M14.0712 4.50295C14.2882 4.72002 14.2882 5.07197 14.0712 5.28905L10.5337 8.8265C10.3166 9.04357 9.96468 9.04357 9.7476 8.8265C9.53052 8.60942 9.53052 8.25747 9.7476 8.0404L12.892 4.896L9.7476 1.7516C9.53052 1.53452 9.53052 1.18257 9.7476 0.965495C9.96467 0.74842 10.3166 0.74842 10.5337 0.965495L14.0712 4.50295ZM13.6781 5.45185L3.67268 5.45185L3.67268 4.34014L13.6781 4.34014L13.6781 5.45185ZM2.00511 7.11942L2.00511 8.23114L0.893394 8.23114L0.893394 7.11942L2.00511 7.11942ZM3.67268 9.89871L5.52553 9.89871L5.52553 11.0104L3.67268 11.0104L3.67268 9.89871ZM2.00511 8.23114C2.00511 9.15211 2.7517 9.89871 3.67268 9.89871L3.67268 11.0104C2.13772 11.0104 0.893394 9.76609 0.893394 8.23114L2.00511 8.23114ZM3.67268 5.45185C2.7517 5.45185 2.00511 6.19845 2.00511 7.11942L0.893394 7.11942C0.893394 5.58447 2.13772 4.34014 3.67268 4.34014L3.67268 5.45185Z"
						fill="currentColor"
					/>
				</svg>
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
import LoadingSymbol from "../../renderer/LoadingSymbol.vue";
import BaseMarkdown from "../base/BaseMarkdown.vue";
import { FieldCategory, FieldType } from "../../streamsyncTypes";
import {
	accentColor,
	buttonColor,
	buttonTextColor,
	containerBackgroundColor,
	cssClasses,
	primaryTextColor,
	secondaryTextColor,
	separatorColor,
} from "../../renderer/sharedStyleFields";
import prettyBytes from "pretty-bytes";
import WdsTextareaInput from "../../wds/WdsTextareaInput.vue";
import WdsControl from "../../wds/WdsControl.vue";

const MAX_FILE_SIZE = 200 * 1024 * 1024;

const description = "A chatbot component to build human-to-AI interactions.";

const defaultConversation = `[
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
	streamsync: {
		name: "Chatbot",
		description,
		category: "Content",
		fields: {
			conversation: {
				name: "Conversation",
				default: defaultConversation,
				desc: "An array with messages or a writer.ai.Conversation object.",
				type: FieldType.Object,
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
				name: "Use Markdown",
				desc: "If active, the output will be sanitized; unsafe elements will be removed.",
				default: "no",
				type: FieldType.Text,
				options: {
					yes: "Yes",
					no: "No",
				},
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
				default: "#F5F5F9",
				type: FieldType.Color,
				category: FieldCategory.Style,
				applyStyleVariable: true,
			},
			avatarBackgroundColor: {
				name: "Avatar",
				default: "#2C2D30",
				type: FieldType.Color,
				category: FieldCategory.Style,
				applyStyleVariable: true,
			},
			avatarTextColor: {
				name: "Avatar text",
				default: "#FFFFFF",
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
				default: "#000000",
			},
			buttonTextColor: {
				...buttonTextColor,
				default: "#ffffff",
			},
			cssClasses,
		},
		events: {
			"ss-chatbot-message": {
				desc: "Triggered when the user sends a message.",
				stub: chatbotMessageStub,
			},
			"ss-chatbot-action-click": {
				desc: "Handle clicks on actions.",
				stub: chatbotActionClickStub,
			},
			"ss-file-change": {
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
} from "vue";
import injectionKeys from "../../injectionKeys";

type Action = {
	subheading?: string;
	name: string;
	desc?: string;
	data?: string;
};

type Message = {
	role: string;
	pending: boolean;
	content: string;
	actions?: Action[];
};

const rootEl: Ref<HTMLElement> = ref(null);
const messageAreaEl: Ref<HTMLElement> = ref(null);
const messagesEl: Ref<HTMLElement> = ref(null);
const isResponsePending: Ref<boolean> = ref(false);
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

function handleMessageSent() {
	isResponsePending.value = true;
	const event = new CustomEvent("ss-chatbot-message", {
		detail: {
			payload: {
				role: "user",
				content: outgoingMessage.value,
			},
			callback: () => {
				isResponsePending.value = false;
			},
		},
	});
	rootEl.value.dispatchEvent(event);
	outgoingMessage.value = "";
}

function handleActionClick(action: Message["actions"][number]) {
	const { data } = action;
	const event = new CustomEvent("ss-chatbot-action-click", {
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
	var reader = new FileReader();
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

	const event = new CustomEvent("ss-file-change", {
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
@import "../../renderer/sharedStyles.css";
@import "../../renderer/colorTransformations.css";

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

.message {
	display: flex;
	gap: 8px;
}

.message .avatar {
	border-radius: 50%;
	background: var(--avatarBackgroundColor);
	color: var(--avatarTextColor);
	margin-top: 6px;
	height: 32px;
	width: 32px;
	flex: 0 0 32px;
	display: flex;
	font-weight: 500;
	font-size: 0.75rem;
	align-items: center;
	justify-content: center;
	overflow: hidden;
	text-transform: uppercase;
}

.message .content {
	border-radius: 8px;
	width: fit-content;
	flex: 0 1 auto;
	color: var(--primaryTextColor);
	white-space: pre-wrap;
}

.message.assistant .content {
	background: v-bind(
		"fields.assistantRoleColor.value ? fields.assistantRoleColor.value : 'linear-gradient(264deg, #f5ebff 0.71%, #eef1ff 100%)'"
	);
}

.message.user .content {
	background: var(--userRoleColor);
}

.content .text {
	line-height: 2;
	padding: 12px 16px 12px 16px;
}

.content .actions {
	padding: 16px;
	background: rgba(0, 0, 0, 0.02);
	display: flex;
	gap: 12px;
	flex-wrap: wrap;
}

.content .actions .action {
	padding: 12px;
	border-radius: 4px;
	background: var(--containerBackgroundColor);
	overflow: hidden;
	line-height: normal;
	display: flex;
	gap: 4px;
	flex-direction: column;
	box-shadow: 0 2px 2px 0px rgba(0, 0, 0, 0.1);
	cursor: pointer;
	border: 0;
}

.action .subheading {
	color: var(--secondaryTextColor);
	font-size: 0.7rem;
}

.action .desc {
	font-size: 0.7rem;
}

.loadingContainer {
	padding: 16px;
	display: flex;
	gap: 16px;
	align-items: center;
	justify-content: center;
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
