"""
Code completion handler using Writer Palmyra.

This module provides AI-powered code completions for Monaco Editor instances
via the monacopilot library.
"""
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class CodeCompletionHandler:
    """
    Handles code completion requests using Writer Palmyra.
    
    Environment Variables:
        WRITER_COPILOT_ENABLED: Set to "true" to enable completions
        WRITER_API_KEY: API key for Writer AI (Palmyra models)
        WRITER_COPILOT_MODEL: Model to use (default: "palmyra-x5")
    """
    
    def __init__(self):
        """Initialize the completion handler with Writer Palmyra."""
        self.enabled = os.getenv("WRITER_COPILOT_ENABLED", "true").lower() == "true"
        self.client = None
        self.model = None
        
        if not self.enabled:
            return
            
        # Initialize Writer provider
        writer_key = os.getenv("WRITER_API_KEY")
        
        if writer_key:
            self._init_writer(writer_key)
        else:
            logger.warning(
                "WRITER_COPILOT_ENABLED is true but WRITER_API_KEY is not set. "
                "Code completions will be disabled."
            )
            self.enabled = False
    
    def _init_writer(self, api_key: str):
        """Initialize Writer client."""
        try:
            from writerai import Writer
            self.client = Writer(api_key=api_key)
            self.model = os.getenv("WRITER_COPILOT_MODEL", "palmyra-x5")
            logger.info(f"Code completion handler initialized with Writer {self.model}")
        except ImportError:
            logger.error(
                "writer-sdk not properly installed. "
                "Install it with: pip install writer-sdk"
            )
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize Writer client: {e}")
            self.enabled = False
    
    async def get_completion(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get code completion from Writer Palmyra.
        
        Args:
            request_body: Request body from monacopilot containing:
                - completionMetadata: Metadata about the completion request
                    - filename: Name of the file being edited
                    - language: Programming language
                    - textBeforeCursor: Text before cursor position
                    - textAfterCursor: Text after cursor position
        
        Returns:
            Dictionary with completion result:
                - completion: The suggested code completion text
        """
        # Return empty completion if disabled or not initialized
        if not self.enabled or not self.client:
            return {"completion": ""}
        
        # Extract the actual completion metadata
        completion_data = request_body.get("completionMetadata", request_body)
        
        # Get completion from Writer
        return await self._get_writer_completion(completion_data)
    
    async def _get_writer_completion(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Get completion from Writer Palmyra."""
        try:
            # Extract context from request
            language = request_body.get("language", "")
            text_before = request_body.get("textBeforeCursor", "")
            text_after = request_body.get("textAfterCursor", "")
            filename = request_body.get("filename", "untitled")
            
            # Build prompt for Writer
            prompt = self._build_completion_prompt(
                language=language,
                text_before=text_before,
                text_after=text_after,
                filename=filename
            )
            
            # Call Writer Chat API
            response = self.client.chat.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=0.3,
            )
            
            # Extract completion text
            if response.choices and len(response.choices) > 0:
                completion_text = response.choices[0].message.content.strip()
                completion_text = self._clean_completion(completion_text)
                return {"completion": completion_text}
            else:
                return {"completion": ""}
                
        except Exception as e:
            logger.error(f"Error getting completion from Writer: {e}")
            return {"completion": ""}
    
    def _build_completion_prompt(
        self,
        language: str,
        text_before: str,
        text_after: str,
        filename: str
    ) -> str:
        """
        Build the prompt for Claude to generate code completion.
        
        Args:
            language: Programming language
            text_before: Code before cursor
            text_after: Code after cursor
            filename: Name of the file
        
        Returns:
            Formatted prompt string
        """
        return f"""You are an expert code completion assistant. Your task is to provide a short, relevant code completion that continues from the cursor position.

File: {filename}
Language: {language}

Code before cursor:
```{language}
{text_before}
```

Code after cursor:
```{language}
{text_after}
```

Provide ONLY the completion text that should be inserted at the cursor position. Do not include any explanations, markdown formatting, or code blocks. Just output the exact text that should be inserted.

The completion should:
- Be contextually relevant to the code before and after
- Follow the existing code style and conventions
- Be concise (typically 1-3 lines)
- NOT repeat code that already exists before the cursor
- Complete the current statement, expression, or block naturally if it makes sense, otherwise use next line as a starting point

Completion:"""

    def _clean_completion(self, completion: str) -> str:
        """
        Clean up the completion text from Writer Palmyra.
        
        Args:
            completion: Raw completion from Writer
        
        Returns:
            Cleaned completion text
        """
        # Remove markdown code blocks if present
        if completion.startswith("```"):
            lines = completion.split("\n")
            # Remove first line (```language)
            lines = lines[1:]
            # Remove last line if it's ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            completion = "\n".join(lines)
        
        # Trim excessive whitespace but preserve intentional indentation
        completion = completion.rstrip()
        
        return completion


# Global instance
_completion_handler: Optional[CodeCompletionHandler] = None


def get_completion_handler() -> CodeCompletionHandler:
    """
    Get or create the global completion handler instance.
    
    Returns:
        CodeCompletionHandler instance
    """
    global _completion_handler
    if _completion_handler is None:
        _completion_handler = CodeCompletionHandler()
    return _completion_handler

