from __future__ import annotations

import logging
from functools import partial
from typing import Any

import numpy as np
import tqdm

from mteb.model_meta import ModelMeta
from mteb.models.wrapper import Wrapper
from mteb.requires_package import requires_package

logger = logging.getLogger(__name__)


class OpenAIWrapper(Wrapper):
    default_embed_dims = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }

    def __init__(
        self,
        model_name: str,
        max_tokens: int,
        tokenizer_name: str = "cl100k_base",
        embed_dim: int | None = None,
        client: Any | None = None,  # OpenAI
        **kwargs,
    ) -> None:
        """Wrapper for OpenAIs embedding API.
        To handle documents larger than 8191 tokens, we truncate the document to the specified sequence length. If the docuement is empty we return a
        zero vector.
        """
        requires_package(
            self,
            "openai",
            model_name,
            install_instruction="pip install 'mteb[openai]'",
        )
        from openai import OpenAI

        requires_package(
            self,
            "tiktoken",
            model_name,
            install_instruction="pip install 'mteb[openai]'",
        )
        import tiktoken

        self._client = OpenAI() if client is None else client

        self._model_name = model_name
        if embed_dim is None:
            if model_name not in self.default_embed_dims:
                raise ValueError(
                    f"Model {model_name} does not have a default embed_dim. Please provide an embedding dimension."
                )
            self._embed_dim = self.default_embed_dims[model_name]
        else:
            self._embed_dim = embed_dim

        self._max_tokens = max_tokens
        self._encoding = tiktoken.get_encoding(tokenizer_name)

    def truncate_text_tokens(self, text):
        """Truncate a string to have `max_tokens` according to the given encoding."""
        truncated_sentence = self._encoding.encode(text)[: self._max_tokens]
        return self._encoding.decode(truncated_sentence)

    def encode(self, sentences: list[str], **kwargs: Any) -> np.ndarray:
        requires_package(self, "openai", "Openai text embedding")

        from openai import NotGiven

        if self._model_name == "text-embedding-ada-002" and self._embed_dim is not None:
            logger.warning(
                "Reducing embedding size available only for text-embedding-3-* models"
            )

        mask_sents = [(i, t) for i, t in enumerate(sentences) if t.strip()]
        mask, no_empty_sent = list(zip(*mask_sents)) if mask_sents else ([], [])
        trimmed_sentences = []
        for sentence in no_empty_sent:
            encoded_sentence = self._encoding.encode(sentence)
            if len(encoded_sentence) > self._max_tokens:
                truncated_sentence = self.truncate_text_tokens(sentence)
                trimmed_sentences.append(truncated_sentence)
            else:
                trimmed_sentences.append(sentence)

        max_batch_size = kwargs.get("batch_size", 2048)
        sublists = [
            trimmed_sentences[i : i + max_batch_size]
            for i in range(0, len(trimmed_sentences), max_batch_size)
        ]

        show_progress_bar = (
            False
            if "show_progress_bar" not in kwargs
            else kwargs.pop("show_progress_bar")
        )

        no_empty_embeddings = []

        for sublist in tqdm.tqdm(sublists, leave=False, disable=not show_progress_bar):
            try:
                response = self._client.embeddings.create(
                    input=sublist,
                    model=self._model_name,
                    encoding_format="float",
                    dimensions=self._embed_dim or NotGiven(),
                )
            except Exception as e:
                # Sleep due to too many requests
                logger.info("Sleeping for 10 seconds due to error", e)
                import time

                time.sleep(10)
                try:
                    response = self._client.embeddings.create(
                        input=sublist,
                        model=self._model_name,
                        encoding_format="float",
                        dimensions=self._embed_dim or NotGiven(),
                    )
                except Exception as e:
                    logger.info("Sleeping for 60 seconds due to error", e)
                    time.sleep(60)
                    response = self._client.embeddings.create(
                        input=sublist,
                        model=self._model_name,
                        encoding_format="float",
                        dimensions=self._embed_dim or NotGiven(),
                    )
            no_empty_embeddings.extend(self._to_numpy(response))

        no_empty_embeddings = np.array(no_empty_embeddings)

        all_embeddings = np.zeros((len(sentences), self._embed_dim), dtype=np.float32)
        if len(mask) > 0:
            mask = np.array(mask, dtype=int)
            all_embeddings[mask] = no_empty_embeddings
        return all_embeddings

    def _to_numpy(self, embedding_response) -> np.ndarray:
        return np.array([e.embedding for e in embedding_response.data])


text_embedding_3_small = ModelMeta(
    name="openai/text-embedding-3-small",
    revision="3",
    release_date="2024-01-25",
    languages=None,  # supported languages not specified
    loader=partial(  # type: ignore
        OpenAIWrapper,
        model_name="text-embedding-3-small",
        tokenizer_name="cl100k_base",
        max_tokens=8191,
    ),
    max_tokens=8191,
    embed_dim=1536,
    open_weights=False,
    n_parameters=None,
    memory_usage_mb=None,
    license=None,
    reference="https://openai.com/index/new-embedding-models-and-api-updates/",
    similarity_fn_name="cosine",
    framework=["API"],
    use_instructions=False,
    public_training_code=None,
    public_training_data=None,  # assumed
    training_datasets=None,
)
text_embedding_3_large = ModelMeta(
    name="openai/text-embedding-3-large",
    revision="3",
    release_date="2024-01-25",
    languages=None,  # supported languages not specified
    loader=partial(  # type: ignore
        OpenAIWrapper,
        model_name="text-embedding-3-large",
        tokenizer_name="cl100k_base",
        max_tokens=8191,
    ),
    max_tokens=8191,
    embed_dim=3072,
    open_weights=False,
    reference="https://openai.com/index/new-embedding-models-and-api-updates/",
    framework=["API"],
    use_instructions=False,
    n_parameters=None,
    memory_usage_mb=None,
    public_training_code=None,
    public_training_data=None,  # assumed
    training_datasets=None,
    license=None,
    similarity_fn_name=None,
)
text_embedding_ada_002 = ModelMeta(
    name="openai/text-embedding-ada-002",
    revision="3",
    release_date="2022-12-15",
    languages=None,  # supported languages not specified
    loader=partial(  # type: ignore
        OpenAIWrapper,
        model_name="text-embedding-ada-002",
        tokenizer_name="cl100k_base",
        max_tokens=8191,
    ),
    reference="https://openai.com/index/new-and-improved-embedding-model/",
    max_tokens=8191,
    embed_dim=1536,
    open_weights=False,
    framework=["API"],
    use_instructions=False,
    n_parameters=None,
    memory_usage_mb=None,
    public_training_code=None,
    public_training_data=None,  # assumed
    training_datasets=None,
    license=None,
    similarity_fn_name=None,
)
