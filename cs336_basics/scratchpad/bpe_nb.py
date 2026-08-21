import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import importlib

    import logging

    logging.basicConfig(
        level=logging.INFO,
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
    return chunks, num_processes


@app.cell
def _():
    return


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

        return tuple(new_tokens)

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
def _(Counter, chunks, logger, num_processes, pairwise):
    from collections import defaultdict
    import regex as re

    from concurrent.futures import ProcessPoolExecutor

    from cs336_basics.pretokenization import count_pre_tokens

    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        chunk_counters = executor.map(
            count_pre_tokens,
            chunks
        )

    counts = Counter()
    for chunk_counts in chunk_counters:
        counts.update(chunk_counts)

    logger.debug(f"Counts:\t{counts}")

    id_to_pre_token = {}
    pre_token_counts = {}
    token_pair_counts = Counter()
    pair_to_pre_token_id = defaultdict(set)
    for pre_token_id, (pre_token, count) in enumerate(counts.items()):
        # first create byte tokens from encoded pre_token
        byte_tokens = tuple(bytes([b]) for b in pre_token.encode("utf-8"))

        # assign id to the byte tokens just generated
        id_to_pre_token[pre_token_id] = byte_tokens

        # assign count to that id
        pre_token_counts[pre_token_id] = count

        for token_pair in pairwise(byte_tokens):
            # count pairwise tokens for bpe algorithm
            token_pair_counts[token_pair] += count
            # keep a lookup dict of which token pairs appear in which word
            pair_to_pre_token_id[token_pair].add(pre_token_id)

    logger.debug(f"ID to pre token:\t{id_to_pre_token}")
    logger.debug(f"Pre token counts:\t{pre_token_counts}")
    logger.debug(f"Token pair counts:\t{token_pair_counts}")
    logger.debug(f"Token pair usage:\t{pair_to_pre_token_id}")
    return (
        id_to_pre_token,
        pair_to_pre_token_id,
        pre_token_counts,
        token_pair_counts,
    )


@app.cell
def _(
    Counter,
    id_to_pre_token,
    logger,
    pair_to_pre_token_id,
    pairwise,
    pre_token_counts,
    token_pair_counts,
    token_pass,
):
    from copy import deepcopy

    endoftext_token_bytes = "<|endoftext|>".encode("utf-8")
    vocabulary = [] + [bytes([i]) for i in range(256)]

    id_to_pre_token_train = deepcopy(id_to_pre_token)
    token_pair_counts_train = deepcopy(token_pair_counts)
    pair_to_pre_token_id_train = deepcopy(pair_to_pre_token_id)

    EPOCHS = 1000
    for train_iteration in range(EPOCHS):

        max_pair = max(token_pair_counts_train, key=lambda pair: (token_pair_counts_train[pair], pair)) # gives the larger or lexicographically larger
        logger.debug(f"Largest pair:\t{max_pair}") # largest count pair

        new_token = max_pair[0] + max_pair[1]
        logger.debug(f"Merging new token:\t{max_pair[0]} {max_pair[1]}")

        vocabulary.append(new_token)
        logger.info(f"Appending {new_token} to vocabulary.")

        pairs_to_check_for_deletion = set()
        affected_pre_token_ids = list(pair_to_pre_token_id_train[max_pair]) # to avoid changing the set while we are iterating over it
        for affected_pre_token_id in affected_pre_token_ids:
            affected_pre_token = id_to_pre_token_train[affected_pre_token_id]
            # logger.debug(f"Affected pre token:\t{affected_pre_token}")

            new_token_representation = token_pass(affected_pre_token, max_pair)
            # logger.debug(f"New representation:\t{new_token_representation}")
            id_to_pre_token_train[affected_pre_token_id] = new_token_representation

            old_pair_counts = Counter(pairwise(affected_pre_token))
            new_pair_counts = Counter(pairwise(new_token_representation))

            removed_pairs = old_pair_counts - new_pair_counts
            added_pairs = new_pair_counts - old_pair_counts

            # logger.debug(f"Old pair counts:\t{old_pair_counts}")
            # logger.debug(f"New pair counts:\t{new_pair_counts}")

            # logger.debug(f"Removed pairs:\t{removed_pairs}")
            # logger.debug(f"Added pairs:\t{added_pairs}")

            for removed_pair, delta in removed_pairs.items():
                if new_pair_counts[removed_pair] == 0:
                    pair_to_pre_token_id_train[removed_pair].remove(affected_pre_token_id)

                token_pair_counts_train[removed_pair] -= delta * pre_token_counts[affected_pre_token_id]
                pairs_to_check_for_deletion.add(removed_pair)

            for added_pair, delta in added_pairs.items():
                token_pair_counts_train[added_pair] += delta * pre_token_counts[affected_pre_token_id]
                pair_to_pre_token_id_train[added_pair].add(affected_pre_token_id)

        for pair in pairs_to_check_for_deletion:
            if token_pair_counts_train[pair] == 0:
                del token_pair_counts_train[pair]

            if pair in pair_to_pre_token_id_train and not pair_to_pre_token_id_train[pair]: # check for empty sets
                del pair_to_pre_token_id_train[pair] # remove empty set

        # # 1. Every pre-token representation must be non-empty
        # for pt_id, tokens in id_to_pre_token_train.items():
        #     assert len(tokens) > 0

        # # 2. Pair counts must never be negative
        # for pair, c in token_pair_counts_train.items():
        #     assert c > 0, f"Non-positive pair count: {pair} -> {c}"

        # # 3. Every ID in pair_to_pre_token_id must actually contain that pair
        # for pair, pre_token_ids in pair_to_pre_token_id_train.items():
        #     for pt_id in pre_token_ids:
        #         tokens = id_to_pre_token_train[pt_id]
        #         assert pair in set(pairwise(tokens)), (
        #             f"Stale usage mapping: {pair} claims to occur in "
        #             f"{pt_id} -> {tokens}"
        #         )

        # # 4. Every pair that actually occurs must have that pre-token ID in the usage map
        # for pt_id, tokens in id_to_pre_token_train.items():
        #     for pair in set(pairwise(tokens)):
        #         assert pt_id in pair_to_pre_token_id_train[pair], (
        #             f"Missing usage mapping: {pair} occurs in "
        #             f"{pt_id} -> {tokens}"
        #         )
    
    logger.info(f"New vocabulary:\t{vocabulary}")
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
