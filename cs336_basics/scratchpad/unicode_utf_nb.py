import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
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



    return


if __name__ == "__main__":
    app.run()
