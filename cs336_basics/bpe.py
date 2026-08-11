from collections import Counter
from itertools import pairwise
import logging

logger = logging.getLogger(__name__)

def init_frequency_mapping(corpus):
    pre_tokenized_corpus = corpus.split(" ")
    frequency_mapping = Counter(pre_tokenized_corpus)
    processed_frequency_mapping = {}
    for word, count in frequency_mapping.items():
        encoded_word = word.encode("utf-8") # one list of bytes
        tokens = []
        for b in encoded_word: # will give ints on iteration
            token = bytes([b]) # simply using b won't work
            tokens.append(token) # careful, it's still a list
        processed_frequency_mapping[tuple(tokens)] = count # insert into new dict
    logger.debug(f"Initialized frequency mapping to:\n{processed_frequency_mapping}")
    return processed_frequency_mapping
    



def count_token_pairs(frequency_mapping):
    counted_pairs = Counter()
    # Counts the occurences of pairwise tokens
    for tokens, count in frequency_mapping.items():
        pairs = pairwise(tokens)
        naive_count = {p: count for p in pairs}
        real_count = Counter(naive_count)
        counted_pairs.update(real_count)
    return counted_pairs


def token_pass(tokens, max_pair, new_token):
    new_tokens = []
    just_matched = False
    for token, next_token in pairwise(tokens):
        logger.debug(f"Checking ({token}, {next_token})")
        if (token, next_token) == max_pair:
            logger.debug(f"Found match! {max_pair}")
            new_tokens.append(new_token)
            just_matched = True
        elif just_matched:
            just_matched = False
            continue
        else:
            just_matched = False
            new_tokens.append(token)

    if not just_matched: new_tokens.append(tokens[-1])
    return new_tokens

