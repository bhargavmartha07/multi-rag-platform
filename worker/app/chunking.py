import re


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[str]:

    if not text or not text.strip():

        return []

    text = re.sub(r"\n{3,}", "\n\n", text)

    sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks: list[str] = []
    current_chunk: list[str] = []
    current_length = 0

    for sentence in sentences:

        sentence_length = len(sentence)

        if (
            current_length + sentence_length > chunk_size
            and current_chunk
        ):

            chunks.append(" ".join(current_chunk))

            overlap_text = " ".join(current_chunk)

            overlap_words = overlap_text.split()[
                -chunk_overlap // 5:
            ]

            current_chunk = overlap_words
            current_length = len(" ".join(overlap_words))

        current_chunk.append(sentence)
        current_length += sentence_length

    if current_chunk:

        chunks.append(" ".join(current_chunk))

    return [
        chunk.strip()
        for chunk in chunks
        if chunk.strip()
    ]
