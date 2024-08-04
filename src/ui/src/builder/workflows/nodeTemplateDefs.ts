import { FieldType } from "../../writerTypes";

const httpcall = {
	name: "HTTP call",
	description: "Helps you make HTTP calls",
	category: "Content",
	fields: {
		conversation: {
			name: "Conversation",
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
	},
	outs: {
		success: {
			name: "Success",
			description: "If the HTTP call succeeds.",
			style: "success",
		},
		exception: {
			name: "Error",
			description: "If the HTTP call doesn't succeed.",
			style: "error",
		},
	},
};

const pythonfunc = {
	name: "Python function",
	description: "Run Python functions",
	category: "Content",
	fields: {
		conversation: {
			name: "Conversation",
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
	},
	outs: {
		success: {
			name: "Success",
			description: "If the function doesn't raise an Exception.",
			style: "success",
		},
		exception: {
			name: "Exception",
			description: "If the function raises an Exception.",
			style: "error",
		},
	},
};

export default {
	httpcall,
	pythonfunc,
};
