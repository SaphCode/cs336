# %%
ord('n')

# %%
chr(0)

# %%
chr(0).__repr__()

# %%
print(chr(0))


# %%
"this is a test" + chr(0) + "string"
# %%
print("this is a test" + chr(0) + "string")

# %%
test_string = "hello! ö ä ß"
utf_8_encoded = test_string.encode("utf-8")
print(utf_8_encoded)
# %%
print(type(utf_8_encoded))
# %%
list(utf_8_encoded)
# %%
print(len(test_string))
# %%
print(len(utf_8_encoded))
# %%
print(utf_8_encoded.decode("utf-8"))

# %%
test_string = "hello! ö ä ß"
utf_16_encoded = test_string.encode("utf-16")
print(utf_16_encoded)
# %%
print(type(utf_16_encoded))
# %%
list(utf_16_encoded)
# %%
print(len(test_string))
# %%
print(len(utf_16_encoded))
# %%
print(utf_16_encoded.decode("utf-16"))


# %%
test_string = "hello! ö ä ß"
utf_32_encoded = test_string.encode("utf-32")
print(utf_32_encoded)
# %%
print(type(utf_32_encoded))
# %%
list(utf_32_encoded)
# %%
print(len(test_string))
# %%
print(len(utf_32_encoded))
# %%
print(utf_32_encoded.decode("utf-32"))


# %%
def decode_utf8_bytes_to_str_wrong(bytestring: bytes):
    decoded_unicode_chars = []
    print(bytestring)
    print(list(bytestring))
    for b in bytestring:
        print(b)
        print([b])
        print(bytes([b]))
        print(bytes([b]).__repr__())
        print(str(bytes([b])))
        decoded_unicode_char = bytes([b]).decode("utf-8") 
        print(decoded_unicode_char)
        decoded_unicode_chars.append(decoded_unicode_char)

    print(decoded_unicode_chars)
    joined_decoded_chars = "".join(decoded_unicode_chars) # this uses "", which character is this?

    return joined_decoded_chars
decode_utf8_bytes_to_str_wrong("Hällo".encode("utf-8"))

# %%
list("".encode("utf-8"))


# %%
"".encode("utf-8")

# %%
b'\xC3\xC3'.decode("utf-8")
# %%
print('hello')
# %%
PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
# %%
import regex as re
re.findall(PAT, "some text that i'll pre-tokenize")
# %%
re.findall(PAT, "Hällo! mein; name-ist wursc!tl'nt i have a big apple, and _i_ need **a** lot *of* drinks to get/ through t6his 89.")
# %%
from collections import Counter
doc = """low low low low low lower lower widest widest widest newest newest newest newest newest newest"""
pre_tokenized_corpus = doc.split(" ")
frequency_mapping = Counter(pre_tokenized_corpus)
processed_frequency_mapping = {}
for word, count in frequency_mapping.items():
    encoded_word = word.encode("utf-8") # one list of bytes
    tokens = []
    for b in encoded_word: # will give ints on iteration
        token = bytes([b]) # simply using b won't work
        tokens.append(token) # careful, it's still a list
    processed_frequency_mapping[tuple(tokens)] = count # insert into new dict

# %%
from itertools import pairwise

for i in range(6):
    counted_pairs = Counter()
    for tokens, count in processed_frequency_mapping.items():
        pairs = pairwise(tokens)
        naive_count = {p: count for p in pairs}
        real_count = Counter(naive_count)
        counted_pairs.update(real_count)
    max_pair = max(counted_pairs, key=lambda token: (counted_pairs[token], token))
    new_token = max_pair[0] + max_pair[1]

    new_processed_frequency_mapping = {}
    for tokens in processed_frequency_mapping:
        new_tokens = []
        just_matched = False
        for token, next_token in pairwise(tokens):
            if (token, next_token) == max_pair:
                new_tokens.append(new_token)
                just_matched = True
            elif just_matched:
                just_matched = False
                continue
            else:
                just_matched = False
                new_tokens.append(token)       
        new_processed_frequency_mapping[new_tokens] = processed_frequency_mapping[tokens]
        
    print(processed_frequency_mapping)


    

# %%
max_pair = (b'a', b'a')
new_token = max_pair[0] + max_pair[1]
processed_frequency_mapping = {(b'a',): 3}
new_processed_frequency_mapping = {}
for tokens in processed_frequency_mapping:
    new_tokens = []
    just_matched = False
    for token, next_token in pairwise(tokens):
        if not just_matched and (token, next_token) == max_pair:
            new_tokens.append(new_token)
            just_matched = True
        elif just_matched:
            just_matched = False
            continue
        else:
            just_matched = False
            new_tokens.append(token)  
    
    if not just_matched: new_tokens.append(tokens[-1])
    new_processed_frequency_mapping[tuple(new_tokens)] = processed_frequency_mapping[tokens]
print(new_processed_frequency_mapping)

# %%
for t in test:
    print(bytes([t]))
# %%
