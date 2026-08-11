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
        level=logging.INFO,
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
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
