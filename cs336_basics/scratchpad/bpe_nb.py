import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import importlib

    import logging

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s | %(name)s | %(message)s",
        force=True,
    )

    logger = logging.getLogger(__name__)
    return (logger,)


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
def _():
    from itertools import pairwise
    from collections import Counter

    def count_token_pairs(frequency_mapping):
        counted_pairs = Counter()
        # Counts the occurences of pairwise tokens
        for tokens, c in frequency_mapping.items():
            for pair in pairwise(tokens):
                counted_pairs[pair] += c
        return counted_pairs


    def test_count_token_pairs():
        case_1 = {
            'hello': 10
        }
        expected_case_1 = Counter({('h', 'e'): 10, ('e', 'l'): 10, ('l', 'l'): 10, ('l', 'o'): 10})
        print(expected_case_1 == count_token_pairs(case_1))
        case_2 = {
            'aaaa': 10
        }
        expected_case_2 = Counter({('a', 'a'): 30})
        print(expected_case_2 == count_token_pairs(case_2))

    test_count_token_pairs()

    def token_pass(tokens, max_pair):
        new_token = max_pair[0] + max_pair[1]
        new_tokens = []
        i=0
        while i < len(tokens):
            if (i+1 < len(tokens) and (tokens[i], tokens[i+1]) == max_pair):
                new_tokens.append(new_token)
                i+=2
            else:
                new_tokens.append(tokens[i])
                i+=1

        return new_tokens

    def test_token_pass():
        tokens_1 = (b'a', b'a', b'a', b'a', b'a')
        max_pair_1 = (b'a', b'a')
        new_tokens_1 = token_pass(tokens_1, max_pair_1)
        print(new_tokens_1)
        tokens_2 = (b'h', b'e', b'l', b'l', b'o')
        max_pair_2 = (b'e', b'l')
        new_tokens_2 = token_pass(tokens_2, max_pair_2)
        print(new_tokens_2)

    test_token_pass()



    return Counter, pairwise, token_pass


@app.cell
def _(Counter, chunks, logger, pairwise, special_tokens):
    import regex as re
    from collections import defaultdict

    PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""

    escaped_special_tokens = [re.escape(st) for st in special_tokens]
    split_pattern = "|".join(escaped_special_tokens)
    logger.debug(f"Using split pattern: {split_pattern} (| is regex or)")

    matches = re.findall(split_pattern, chunks[0])
    logger.debug(f"First 5 matches:\t{matches[:5]}")
    logger.debug(f"Last 5 matches:\t{matches[-5:]}")

    split_docs = re.split(split_pattern, chunks[0])
    logger.debug(f"First 3 docs, first 20 chars:\t{split_docs[0][:20]}, {split_docs[1][:20]}, {split_docs[2][:20]}")

    counts = Counter()
    for i, d in enumerate(split_docs):
        counts.update(m.group() for m in re.finditer(PAT, d))
        if i > 10: break # TODO: remove
    logger.debug(f"Counts:\t{counts}")

    id_to_pre_token = {}
    pre_token_counts = {}
    token_pair_counts = Counter()
    pair_to_pre_token_id = defaultdict(set)
    for word_id, (pre_token, count) in enumerate(counts.items()):
        # first create byte tokens from encoded pre_token
        byte_tokens = tuple(bytes([b]) for b in pre_token.encode("utf-8"))

        # assign id to the byte tokens just generated
        id_to_pre_token[word_id] = byte_tokens

        # assign count to that id
        pre_token_counts[word_id] = count

        for token_pair in pairwise(byte_tokens):
            # count pairwise tokens for bpe algorithm
            token_pair_counts[token_pair] += count
            # keep a lookup dict of which token pairs appear in which word
            pair_to_pre_token_id[token_pair].add(word_id)
        
    logger.debug(f"ID to pre token:\t{id_to_pre_token}")
    logger.debug(f"Pre token counts:\t{pre_token_counts}")
    logger.debug(f"Token pair counts:\t{token_pair_counts}")
    logger.debug(f"Token pair usage:\t{pair_to_pre_token_id}")
    return (token_pair_counts,)


@app.cell
def _(byte_token_counts, logger, token_pair_counts, token_pass):
    # TODO: WEAVE IN THE PAIRING INTO THE INITIALIZATION IN THE CELL BEFORE, AND THEN SEE WHERE EVERY PAIR OCCURS AND KEEP A LIST. UPDATE THE NEW PAIRS AS SUCH:
    # - first token count -= count
    # - second token count -= count
    # - new pair count += count
    # THEN UPDATE ONLY THE OCCURENCES OF THESE WORDS BY TAKING YOUR LIST (THAT YOU DON'T HAVE YET) AND GOING EVERYWHERE THAT PAIR OCCURS

    endoftext_token_bytes = "<|endoftext|>".encode("utf-8")
    print(endoftext_token_bytes)
    vocabulary = [] + [bytes([i]) for i in range(256)]

    trained_byte_token_counts = byte_token_counts.copy()
    for train_iteration in range(3):

        max_pair = max(token_pair_counts, key=lambda pair: (token_pair_counts[pair], pair)) # gives the larger or lexicographically larger
        logger.debug(f"Largest pair:\t{max_pair}") # largest count pair

        new_token = max_pair[0] + max_pair[1]
        logger.info(f"Merging new token:\t{max_pair[0]} {max_pair[1]}")

        vocabulary.append(new_token)
        logger.debug(f"Appending {new_token} to vocabulary.")

        new_byte_token_counts = {}
        for tokens in trained_byte_token_counts:
            new_tokens = token_pass(tokens, max_pair)
   
            new_byte_token_counts[tuple(new_tokens)] = trained_byte_token_counts[tokens]
            logger.debug(f"Updated mapping at {tuple(new_tokens)} to value {trained_byte_token_counts[tokens]}.")

        trained_byte_token_counts = new_byte_token_counts
        logger.info(f"New mapping: {new_byte_token_counts}")

    logger.info(f"New vocabulary after BPE:\t{vocabulary}")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
