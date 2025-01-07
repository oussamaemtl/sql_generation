from langchain.llms.base import LLM
from typing import Optional, List
from pydantic import PrivateAttr
from groq import Groq  # Ensure the Groq SDK is installed
from langchain.schema import ChatMessage
from langchain_core.output_parsers.base import BaseOutputParser
from langchain.schema import ChatMessage


def truncate_prompt(prompt: str, max_tokens: int = 15000) -> str:
    tokens = prompt.split()
    if len(tokens) > max_tokens:
        truncated_prompt = " ".join(tokens[-max_tokens:])
        return truncated_prompt
    return prompt


class GroqLLM(LLM):
    _client: Groq = PrivateAttr()
    _model: str = PrivateAttr()

    def __init__(self, api_key: str, model: str):
        super().__init__()
        self._client = Groq(api_key=api_key)
        self._model = model

    def _call(
        self, prompt: str, stop: Optional[List[str]] = None, **kwargs
    ) -> str:
        """
        Handle LLM calls and ensure the response adheres to LangChain's expected format.
        """
        try:
            truncated_prompt = truncate_prompt(prompt)

            # Call Groq API
            chat_completion = self._client.chat.completions.create(
                messages=[{"role": "user", "content": truncated_prompt}],
                model=self._model,
            )
            response = chat_completion.choices[0].message.content.strip()

            # Post-process response to conform to LangChain format
            if not response.startswith("Thought:") and not response.startswith(
                "Action:"
            ):
                # Wrap response in the expected structure if not provided
                response = (
                    f"Thought: Let's analyze the request.\n"
                    f"Action: none\n"
                    f"Action Input: {prompt}\n"
                    f"Observation: {response}\n"
                    f"Final Answer: {response}"
                )

            return response
        except Exception as e:
            raise ValueError(f"Error during Groq API call: {e}")

    def generate_chat_message(self, prompt: str) -> ChatMessage:
        """
        Generate a response in a format compatible with LangChain's Chat models.
        """
        content = self._call(prompt)
        return ChatMessage(role="assistant", content=content)

    @property
    def _llm_type(self) -> str:
        return "groq"


class GroqOutputParser(BaseOutputParser):
    def parse(self, result: List[ChatMessage]) -> str:
        if not isinstance(result, list) or not result[0].content:
            raise ValueError("Invalid result format.")
        return result[0].content

    def get_format_instructions(self) -> str:
        return "Please provide a valid SQL response."
