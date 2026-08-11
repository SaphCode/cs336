import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import importlib
    import cs336_basics.bpe as bpe

    importlib.reload(bpe)

    import logging

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s | %(name)s | %(message)s",
        force=True,
    )

    logger = logging.getLogger(__name__)
    return bpe, logger


@app.cell
def _(bpe, logger):
    doc = """low low low low low lower lower widest widest widest newest newest newest newest newest newest"""
    processed_frequency_mapping = bpe.init_frequency_mapping(doc)

    endoftext_token = "<|endoftext|>".encode("utf-8")
    vocabulary = [endoftext_token] + [bytes([i]) for i in range(256)]
    for i in range(12):
        counted_pairs = bpe.count_token_pairs(processed_frequency_mapping)
        logger.debug(f"Count of pairwise tokens:\t{counted_pairs}") # count of pairwise tokens

        max_pair = max(counted_pairs, key=lambda pair: (counted_pairs[pair], pair)) # gives the larger or lexicographically larger
        logger.debug(f"Largest pair:\t{max_pair}") # largest count pair

        new_token = max_pair[0] + max_pair[1]
        logger.info(f"Merging new token:\t{max_pair[0]} {max_pair[1]}")

        vocabulary.append(new_token)
        logger.debug(f"Appending {new_token} to vocabulary.")

        new_processed_frequency_mapping = {}
        for tokens in processed_frequency_mapping:
            new_tokens = bpe.token_pass(tokens, max_pair, new_token)
   
            new_processed_frequency_mapping[tuple(new_tokens)] = processed_frequency_mapping[tokens]
            logger.debug(f"Updated mapping at {tuple(new_tokens)} to value {processed_frequency_mapping[tokens]}.")

        processed_frequency_mapping = new_processed_frequency_mapping
        logger.info(f"New mapping: {new_processed_frequency_mapping}")

    logger.info(f"New vocabulary after BPE:\t{vocabulary}")
    return


@app.cell
def _(logger):
    from cs336_basics.pretokenization import find_chunk_boundaries
    from pathlib import Path

    test_file = Path("data/TinyStoriesV2-GPT4-valid.txt")

    chunks = []
    with open(test_file, 'rb') as f:
        num_processes = 4
        boundaries = find_chunk_boundaries(f, num_processes, b"<|endoftext|>")

        # The following is a serial implementation, but you can parallelize this
        # by sending each start/end pair to a set of processes.
        for start, end in zip(boundaries[:-1], boundaries[1:]):
            logger.debug(f"start:\t{start}, end:\t{end}, length [chars]: {(end-start)/1e6} M")
            f.seek(start)
            chunk = f.read(end - start).decode("utf-8", errors="ignore")
            chunks.append(chunk)
            logger.debug(f"Chunked text, first and last 100 chars:\n{chunk[:100]}\n...\n{chunk[-100:]}")
            # Run pre-tokenization on your chunk and store the counts for each pre-token
    return (chunks,)


@app.cell
def _():
    special_tokens = ["<|endoftext|>", "<|testtoken|>"]
    "|".join(special_tokens)
    return (special_tokens,)


@app.cell
def _(chunks, logger, special_tokens):
    import regex as re
    escaped_special_tokens = [re.escape(st) for st in special_tokens]
    split_pattern = "|".join(escaped_special_tokens)
    logger.debug(f"Using split pattern: {split_pattern} (| is regex or)")

    matches = re.findall(split_pattern, chunks[0])
    logger.debug(f"First 5 matches:\t{matches[:5]}")
    logger.debug(f"Last 5 matches:\t{matches[-5:]}")

    split_docs = re.split(split_pattern, chunks[0])
    logger.debug(f"First 3 docs, first 20 chars:\t{split_docs[0][:20]}, {split_docs[1][:20]}, {split_docs[2][:20]}")

    pretokenized_split_docs = []
    PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
    for d in split_docs:
        logger.debug(f"Pre-tokenizing:\t{d}")
        pat_matches = re.findall(PAT, d)
        logger.debug(pat_matches)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
