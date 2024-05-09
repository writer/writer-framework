import functools
import json
import logging
import os
from time import sleep
from typing import Generator, List, Optional, TypedDict, Union

from requests import RequestException, Response
from requests import post as r_post

from streamsync.core import get_app_process


logger = logging.Logger(__name__)


def retry(max_retries=3, backoff_factor=1, status_forcelist=(500, 502, 503, 504)):
    """
    A decorator that retries a function if RequestException occurred.

    :param max_retries: Maximum number of retries.
    :param backoff_factor: Multiplier for calculating delay between retries.
    :param status_forcelist: Tuple of HTTP status codes to force a retry.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            response = None
            while attempts < max_retries:
                try:
                    response = func(*args, **kwargs)
                    if response.status_code in status_forcelist:
                        raise RequestException(f"Retry for status: {response.status_code}")
                    return response
                except RequestException as e:
                    attempts += 1
                    logger.debug(f"Attempt {attempts}: {e}")
                    if attempts >= max_retries or e.response.status_code not in status_forcelist:
                        raise
                    sleep(backoff_factor * (2 ** (attempts - 1)))
        return wrapper
    return decorator


def _process_line(line: str):
    prefix = "data: "
    if line.startswith(prefix):
        line = line[len(prefix):]
        data: dict = json.loads(line)
        text = data.get("value")
        if text:
            return text


class WriterAIManager:
    """
    Manages configuration and authentication data for Writer AI functionalities.

    :ivar url: Base URL for the Writer AI API.
    :ivar token: Authentication token for the Writer AI API.
    :ivar temperature: Generation temperature for controlling randomness.
    :ivar max_tokens: Maximum number of tokens per generation.
    """

    default_temperature: float = 0.7
    default_max_tokens = 2048

    def __init__(self, token: Optional[str] = None, api_url: Optional[str] = None):
        """
        Initializes a WriterAIManager instance.

        This method sets the API URL, authentication token, global temperature setting,
        and global maximum token limit for responses, using environment variables.

        :param token: Optional; the default token for API authentication used if WRITER_API_KEY environment variable is not set up.
        :param token: Optional; API URL to use if WRITER_API_URL environment variable is not set up.
        """
        self.url: Optional[str] = os.environ.get('WRITER_API_URL', api_url)
        self.token: Optional[str] = os.environ.get('WRITER_API_KEY', token)
        self.temperature: float = float(os.environ.get('WRITER_API_TEMPERATURE', self.default_temperature))
        self.max_tokens: int = int(os.environ.get('WRITER_API_MAX_TOKENS', self.default_max_tokens))

        current_process = get_app_process()
        setattr(current_process, 'ai_manager', self)

    @classmethod
    def acquire_instance(cls) -> 'WriterAIManager':
        """
        Retrieve the existing instance of WriterAIManager from the current app process.

        :returns: The current instance of the manager.
        :raises RuntimeWarning: If no instance of WriterAIManager is found in the current process.
        """
        current_process = get_app_process()
        try:
            instance = getattr(current_process, 'ai_manager')
            return instance
        except AttributeError:
            raise RuntimeWarning('No WriterAIManager instance found. Have you initialized it?')

    @classmethod
    def authorize(cls, token: str):
        """
        Authorize the WriterAIManager with a new token.
        This can be done as an alternative to setting up an environment variable, or to override the token that was already provided before.

        :param token: The new token to use for authentication.
        """
        instance = cls.acquire_instance()
        instance.token = token

    @classmethod
    def prepare_headers(cls) -> dict:
        """
        Prepare the authorization headers for HTTP requests.

        :returns: Authorization and content-type headers.
        :raises RuntimeWarning: If the token was not provided through `authorize` method or `WRITER_API_KEY` variable.
        """
        instance = cls.acquire_instance()
        if not instance.token:
            raise RuntimeWarning('No token assigned to WriterAIManager. You can assign WRITER_API_KEY environment variable,  pass a token during manager initialization, or use authorize() method.')
        headers = {
            "Authorization": f"Bearer {instance.token}",
            "Content-Type": "application/json"
        }
        return headers

    @classmethod
    def prepare_config(cls) -> dict:
        """
        Prepare the configuration for AI requests.

        :returns: Configuration dictionary containing `max_tokens` and `temperature`.
        """
        instance = cls.acquire_instance()
        return {
            "max_tokens": instance.max_tokens,
            "temperature": instance.temperature
        }

    @classmethod
    def get_max_tokens(cls) -> int:
        """
        Get a maximum token limit for AI generation.

        :returns max_tokens: The maximum number of tokens from config.
        """
        try:
            instance = cls.acquire_instance()
            return instance.max_tokens
        except RuntimeWarning:
            return cls.default_max_tokens

    @classmethod
    def set_max_tokens(cls, new_max_tokens: int):
        """
        Set a new maximum token limit for AI generation.

        :param new_max_tokens: The new maximum number of tokens to set.
        """
        instance = cls.acquire_instance()
        instance.max_tokens = new_max_tokens

    @classmethod
    def get_temperature(cls) -> float:
        """
        Get a temperature for AI generation.

        :returns temperature: The temperature value from config.
        """
        try:
            instance = cls.acquire_instance()
            return instance.temperature
        except RuntimeWarning:
            return cls.default_temperature

    @classmethod
    def set_temperature(cls, new_temperature: float):
        """
        Set a new temperature for AI generation.

        :param new_temperature: The new temperature value to set.
        """
        instance = cls.acquire_instance()
        instance.temperature = new_temperature

    @classmethod
    def get_api_url(cls) -> str:
        """
        Get the base URL of the API.

        :returns: The base URL of the API.
        :raises RuntimeError: If URL was not provided.
        """
        instance = cls.acquire_instance()
        if not instance.url:
            raise RuntimeError("No URL defined for AI manager")
        return instance.url

    @classmethod
    def get_chat_url(cls) -> str:
        """
        Get the full URL for the chat endpoint.

        :returns: The full URL for the chat API endpoint.
        """
        return cls.get_api_url() + "chat"

    @classmethod
    def get_completion_url(cls) -> str:
        """
        Get the full URL for the completions endpoint.

        :returns: The full URL for the completions API endpoint.
        """
        return cls.get_api_url() + "completions"

    @classmethod
    def use_model(cls, model: str) -> dict:
        """
        Get the configuration for a specific model.

        :param model: The model identifier.
        :returns: Configuration dictionary updated with the model.
        """
        instance = cls.acquire_instance()
        return instance.prepare_config() | {"model": model}

    @classmethod
    def use_chat_model(cls, messages: list, stream: Optional[bool] = False) -> dict:
        """
        Get the configuration for the chat model.

        :returns: Configuration dictionary for the chat model.
        """
        return cls.use_model("palmyra-chat-v2-32k") | {"messages": messages, "stream": stream}

    @classmethod
    def use_completion_model(cls, prompt: str, stream: Optional[bool] = False) -> dict:
        """
        Get the configuration for the completion model.

        :returns: Configuration dictionary for the completion model.
        """
        return cls.use_model("palmyra-x-v2") | {"prompt": prompt, "stream": stream}

    @staticmethod
    @retry(max_retries=3, backoff_factor=1)
    def safe_post(url: str, headers: dict, json_data: dict) -> Response:
        """
        Make a POST request to a URL with retries and exponential backoff.

        :param url: The URL to which the POST request is made.
        :param headers: Headers to include in the request.
        :param json_data: JSON data to send in the request body.
        :returns: The response from the server.
        :raises RequestException: On a non-retryable error or after exceeding max retries.
        """
        with r_post(url, headers=headers, json=json_data) as response:
            response.raise_for_status()
            return response

    @staticmethod
    def safe_post_stream(url: str, headers: dict, json_data: dict) -> Generator[str, None, None]:
        """
        Make a POST request to a URL with the intention to stream the response.

        :param url: The URL to which the POST request is made.
        :param headers: Headers to include in the request.
        :param json_data: JSON data to send in the request body.
        :returns: Yields lines of data from the response as they become available.
        """
        @retry(max_retries=3, backoff_factor=1)
        def call():
            return r_post(url, headers=headers, json=json_data, stream=True)

        with call() as response:
            response.raise_for_status()
            buffer = ""
            for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                buffer += chunk
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        yield line
            if buffer:  # Handle any remaining buffer
                yield buffer
            response.close()

    @staticmethod
    def make_call_to_complete(text: str, data: Optional[dict] = None):
        if not data:
            data = {}

        request_data = WriterAIManager.use_completion_model(text) | data

        url = WriterAIManager.get_completion_url()
        headers = WriterAIManager.prepare_headers()

        response_data = WriterAIManager.safe_post(url, headers, request_data).json()
        return response_data

    @staticmethod
    def make_call_to_stream_complete(text: str, data: Optional[dict] = None):
        if not data:
            data = {}

        request_data = \
            WriterAIManager.use_completion_model(text, stream=True) | data

        url = WriterAIManager.get_completion_url()
        headers = WriterAIManager.prepare_headers()

        response = WriterAIManager.safe_post_stream(url, headers, request_data)
        return response

    @staticmethod
    def make_call_to_chat_complete(messages: list, data: Optional[dict] = None):
        if not data:
            data = {}

        request_data = WriterAIManager.use_chat_model(messages) | data

        url = WriterAIManager.get_chat_url()
        headers = WriterAIManager.prepare_headers()
        response_data = WriterAIManager.safe_post(url, headers, request_data).json()
        return response_data

    @staticmethod
    def make_call_to_stream_chat_complete(messages: list, data: Optional[dict] = None):
        if not data:
            data = {}

        request_data = WriterAIManager.use_chat_model(messages, stream=True) | data

        url = WriterAIManager.get_chat_url()
        headers = WriterAIManager.prepare_headers()
        response = WriterAIManager.safe_post_stream(url, headers, request_data)
        return response


class Conversation:
    class Message(TypedDict):
        role: str
        content: str

    def __init__(self, config: Optional[dict] = None):
        """
        Initializes the Conversation object.

        :param config: Optional dictionary containing initial configuration settings.
        """
        self.messages: List[Conversation.Message] = []
        self.temperature = None
        self.max_tokens = None

        if config:
            self.temperature, self.max_tokens = \
                config.get("temperature"), config.get("max_tokens")

        if self.temperature is None:
            self.temperature = WriterAIManager.get_temperature()
        if self.max_tokens is None:
            self.max_tokens = WriterAIManager.get_max_tokens()

    def __add__(self, chunk_or_message: Union['Conversation.Message', str]):
        """
        Adds a message or appends a chunk of text to the last message in the conversation.

        :param chunk_or_message: Message dictionary or string text to add.
        :raises ValueError: If chunk_or_message is neither a dictionary with "role" and "content" nor a string.
        """
        if isinstance(chunk_or_message, dict):
            # Trying to add a whole message
            message = chunk_or_message
            if not ("role" in message and "content" in message):
                raise ValueError("Improper message format to add to Conversation")
            self.messages.append({"role": message["role"], "content": message["content"]})
        elif isinstance(chunk_or_message, str):
            # Trying to add a chunk of text to the last message
            chunk = chunk_or_message
            self.messages[-1]["content"] = self.messages[-1]["content"] + chunk
        else:
            raise ValueError("Conversation can only be appended with messages (dict) or chunks of text (str)")

    @property
    def json_config(self) -> dict:
        """
        Returns the current configuration settings as a dictionary.

        :return: Configuration settings including temperature and max_tokens.
        """
        return {"temperature": self.temperature, "max_tokens": self.max_tokens}

    def add(self, role: str, message: str):
        """
        Adds a new message to the conversation.

        :param role: The role of the message sender.
        :param message: The content of the message.
        """
        self.__add__({"role": role, "content": message})

    def complete(self, data: Optional[dict] = None) -> str:
        """
        Processes the conversation with the current messages and additional data to generate a response.

        :param data: Optional parameters to pass for processing.
        :return: The content of the generated response.
        :raises RuntimeError: If response data was not properly formatted to retrieve model text.
        """
        if not data:
            data = {}

        response_data = \
            WriterAIManager.make_call_to_chat_complete(
                messages=self.messages,
                data=self.json_config | data
                )

        if "choices" in response_data:
            for entry in response_data["choices"]:
                message = entry.get("message")
                if message:
                    text = message.get("content")
                    self.add("assistant", text)
                    return text
        raise RuntimeError(f"Failed to acquire proper response for completion from data: {response_data}")

    def stream_complete(self, data: Optional[dict] = None) -> Generator[str, None, None]:
        """
        Initiates a stream to receive chunks of the model's reply.
        Note: in contrast with `Conversation.complete`, this method is not adding any messages to the conversation.

        :param data: Optional parameters to pass for processing.
        :yields: Model response chunks as they arrive from the stream.
        """
        if not data:
            data = {}

        response = \
            WriterAIManager.make_call_to_stream_chat_complete(
                messages=self.messages,
                data=self.json_config | data
            )
        for line in response:
            processed_line = _process_line(line)
            if processed_line:
                yield processed_line
        else:
            response.close()

    def to_dict(self) -> list:
        """
        Returns a representation of the conversation, excluding system messages.

        :return: List of messages without system messages.
        """
        # Excluding system messages for privacy & security reasons
        serialized_messages = \
            [message for message in self.messages if message["role"] != "system"]
        return [serialized_messages]


def complete(initial_text: str, data: Optional[dict] = None) -> str:
    """
    Completes the input text using the given data and returns the first resulting text choice.

    :param initial_text: The initial text prompt for the completion.
    :param data: Optional dictionary containing parameters for the completion call.
    :return: The text of the first choice from the completion response.
    :raises RuntimeError: If response data was not properly formatted to retrieve model text.
    """
    response_data = WriterAIManager.make_call_to_complete(initial_text, data)

    if "choices" in response_data:
        for entry in response_data["choices"]:
            text = entry.get("text")
            if text:
                return text

    raise RuntimeError(f"Failed to acquire proper response for completion from data: {response_data}")


def stream_complete(initial_text: str, data: Optional[dict] = None) -> Generator[str, None, None]:
    """
    Streams completion results from an initial text prompt, yielding each piece of text as it is received.

    :param initial_text: The initial text prompt for the stream completion.
    :param data: Optional dictionary containing parameters for the stream completion call.
    :yields: Each text completion as it arrives from the stream.
    """
    response = WriterAIManager.make_call_to_stream_complete(initial_text, data)
    for line in response:
        processed_line = _process_line(line)
        if processed_line:
            yield processed_line
    else:
        response.close()


def init(token: Optional[str] = None, url: Optional[str] = None):
    """
    Initializes the WriterAIManager with an optional token.

    :param token: Optional token for authentication.
    :param url: Optional API URL to use for calls.
    :return: An instance of WriterAIManager.
    """
    return WriterAIManager(token=token, api_url=url)
