import re

from writer.abstract import register_abstract_template
from writer.blocks.base_block import WriterBlock
from writer.ss_types import AbstractTemplate

DEFAULT_MODEL = "palmyra-vision"


class WriterVision(WriterBlock):
    @classmethod
    def register(cls, type: str):
        super(WriterVision, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "Analyze images",
                    "description": "Submit images and a prompt to the Writer Vision model to analyze the images and generate a response.",
                    "category": "Writer",
                    "fields": {
                        "prompt": {"name": "Prompt", "type": "Text", "control": "Textarea", "desc": "The prompt to use for the image analysis."},

                        # Keep this commented out for now,
                        # as `palmyra-vision` is the only model available
                        # for image analysis at the moment.
                        # Uncomment when more models are available.

                        # "modelId": {
                        #     "name": "Model",
                        #     "type": "Model Id",
                        #     "default": DEFAULT_MODEL,
                        #     "desc": "The model to use for image analysis."
                        # },
                        "images": {
                            "name": "Images",
                            "type": "Object",
                            "default": "[]",
                            "validator": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "description": "The name of the image file.",
                                        },
                                        "file_id": {
                                            "type": "string",
                                            "description": "The ID of the image file in Writer cloud.",
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "outs": {
                        "success": {
                            "name": "Success",
                            "description": "If the function doesn't raise an Exception.",
                            "style": "success",
                        },
                        "error": {
                            "name": "Error",
                            "description": "If the function raises an Exception.",
                            "style": "error",
                        },
                    },
                    "featureFlags": [
                        "vision_block"
                    ]
                },
            ),
        )

    def run(self):
        try:
            prompt = self._get_field("prompt")
            if not prompt:
                raise ValueError("Prompt cannot be empty. Please provide a valid prompt for image analysis.")
            if "{{" not in prompt or "}}" not in prompt:
                raise ValueError(
                    "Prompt must include image names in the format {{image_name}}. "
                    "Please ensure the prompt contains placeholders for the images."
                )

            # Currently, only 'palmyra-vision' is supported.
            model_id = DEFAULT_MODEL
            # model_id = self._get_field("modelId", False, default_field_value=DEFAULT_MODEL)

            images = self._get_field("images", as_json=True, required=True)

            # Validate images input
            if not isinstance(images, list):
                raise ValueError(
                    f"Images must be a list: received {type(images)}."
                    )
            if not images:
                raise ValueError(
                    "Images list cannot be empty. Please provide "
                    "at least one image."
                    )
            placeholders = set(re.findall(r"\{\{(\w+)\}\}", prompt))
            for image in images:
                if not isinstance(image, dict):
                    raise ValueError(
                        "Image definitions must be dictionaries and contain "
                        f"`name` and `file_id` attributes: received {type(image)}."
                        )
                if "name" not in image or "file_id" not in image:
                    raise ValueError(
                        f"Invalid image definition: {image}. "
                        "An image specified as a dictionary must contain "
                        "`name` and `file_id` attributes."
                        )
                if image["name"] not in placeholders:
                    raise ValueError(
                        f"Image name '{image['name']}' not found in the prompt. "
                        "Please ensure the prompt includes the image name in the format {{image_name}}."
                        )

            client = self.writer_sdk_client
            response = client.vision.analyze(
                prompt=prompt,
                model=model_id,
                variables=images
            )

            if not response:
                self.outcome = "error"
                raise RuntimeError(
                    "No response returned from the model. "
                    "Please validate the prompt and model configuration."
                    )

            self.result = response.data
            self.outcome = "success"
        except BaseException as e:
            self.outcome = "error"
            raise e
