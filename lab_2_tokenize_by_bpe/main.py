"""
Lab 2
BPE and machine translation evaluation
"""


def prepare_word(
    raw_word: str, start_of_word: str | None, end_of_word: str | None
) -> tuple[str, ...] | None:
    """
    Tokenizes word into unigrams and appends end-of-word token
    :param raw_word: original word
    :param start_of_word: a token that signifies the start of word
    :param end_of_word: a token that signifies the end of word
    :return: preprocessed word
    """
    if (not isinstance(raw_word, str) or not (isinstance(start_of_word, str) or start_of_word is None)
            or not (isinstance(end_of_word, str) or end_of_word is None)):
        return None
    list_of_tokens = []
    if start_of_word is not None:
        list_of_tokens.append(start_of_word)
    for token in raw_word:
        list_of_tokens.append(token)
    if end_of_word is not None:
        list_of_tokens.append(end_of_word)
    return tuple(list_of_tokens)


def collect_frequencies(
    text: str, start_of_word: str | None, end_of_word: str
) -> dict[tuple[str, ...], int] | None:
    """
    Counts number of occurrences of each word
    :param text: original text with no preprocessing
    :param start_of_word: a token that signifies the start of word
    :param end_of_word: a token that signifies the end of word
    :return: dictionary in the form of <preprocessed word: number of occurrences>
    """
    if (not isinstance(text, str) or (not isinstance(start_of_word, str) and start_of_word is not None)
            or not isinstance(end_of_word, str)):
        return None
    dict_of_frequencies = {}
    tuple_of_words = text.split()
    for word in tuple_of_words:
        prepared_word = prepare_word(word, start_of_word, end_of_word)
        if prepared_word is None:
            return None
        dict_of_frequencies[prepared_word] = tuple_of_words.count(word)
    return dict_of_frequencies


def count_tokens_pairs(
    word_frequencies: dict[tuple[str, ...], int]
) -> dict[tuple[str, str], int] | None:
    """
    Counts number of occurrences of each pair of subsequent tokens
    :param word_frequencies: dictionary in the form of <preprocessed word: number of occurrences>
    :return: dictionary in the form of <token pair: number of occurrences>
    """
    if not isinstance(word_frequencies, dict):
        return None
    dict_of_token_pairs = {}
    for key in word_frequencies.keys():
        for i in range(len(key)-1):
            pair_as_tuple = (key[i], key[i+1])
            if pair_as_tuple not in dict_of_token_pairs.keys():
                dict_of_token_pairs[pair_as_tuple] = word_frequencies[key]
            else:
                dict_of_token_pairs[pair_as_tuple] += word_frequencies[key]
    return dict_of_token_pairs


def merge_tokens(
    word_frequencies: dict[tuple[str, ...], int], pair: tuple[str, str]
) -> dict[tuple[str, ...], int] | None:
    """
    Updates word frequency dictionary by replacing a pair of token with a merged one
    :param word_frequencies: dictionary in the form of <preprocessed word: number of occurrences>
    :param pair: a pair of tokens to be merged
    :return: dictionary in the form of <preprocessed word: number of occurrences>
    """
    if not isinstance(word_frequencies, dict) or not isinstance(pair, tuple):
        return None
    new_dict = {}
    for word in word_frequencies.keys():
        word_as_list = list(word)
        for i in range(len(word)-1):
            current_pair = tuple([word[i], word[i+1]])
            if current_pair == pair:
                word_as_list[i] = pair[0]+pair[1]
                word_as_list.remove(word[i+1])
        word_as_tuple = tuple(word_as_list)
        new_dict[word_as_tuple] = word_frequencies[word]
    return new_dict


print(merge_tokens({
    ('I', 't', "'", 's', '</s>'): 1,
    ('f', 'a', 'r', ',', '</s>'): 1,
    ('f', 'a', 'r', 't', 'h', 'e', 'r', ',', '</s>'): 1,
    ('f', 'a', 'r', 't', 'h', 'e', 's', 't', '</s>'): 1,
    ('a', 'n', 'd', '</s>'): 1,
    ('o', 'l', 'd', ',', '</s>'): 1,
    ('o', 'l', 'd', 'e', 'r', ',', '</s>'): 1,
    ('o', 'l', 'd', 'e', 's', 't', '</s>'): 1
}, (',', '</s>')))


def train(
    word_frequencies: dict[tuple[str, ...], int] | None, num_merges: int
) -> dict[tuple[str, ...], int] | None:
    """
    Creates required number of new tokens by merging existing ones
    :param word_frequencies: dictionary of a kind <preprocessed word: number of occurrences>
    :param num_merges: required number of new tokens
    :return: dictionary in the form of <preprocessed word: number of occurrences>
    """
    if (not isinstance(word_frequencies, dict) and word_frequencies is not None) or not isinstance(num_merges, int):
        return None
    if word_frequencies is None:
        return None
    dict_of_token_pairs = count_tokens_pairs(word_frequencies)
    list_of_max_token_pairs = []
    while len(list_of_max_token_pairs) < num_merges:
        if dict_of_token_pairs is None:
            return None
        if len(dict_of_token_pairs) == 0:
            break
        temp_list_of_max_token_pairs = []
        max_token_pair = max(dict_of_token_pairs.values())
        for token_pair in dict_of_token_pairs:
            if dict_of_token_pairs[token_pair] == max_token_pair:
                temp_list_of_max_token_pairs.append(token_pair)
        temp_list_of_max_token_pairs.sort(key=lambda x: (-len(x), x))
        for temp_token_pair in temp_list_of_max_token_pairs:
            if len(list_of_max_token_pairs) < num_merges:
                list_of_max_token_pairs.append(temp_token_pair)
                del dict_of_token_pairs[temp_token_pair]
    new_dict = word_frequencies
    for new_token_pair in list_of_max_token_pairs:
        new_dict = merge_tokens(new_dict, new_token_pair)
    if new_dict is None:
        return None
    return new_dict


def get_vocabulary(
    word_frequencies: dict[tuple[str, ...], int], unknown_token: str
) -> dict[str, int] | None:
    """
    Establishes correspondence between tokens and its integer identifier
    :param word_frequencies: dictionary in the form of <preprocessed word: number of occurrences>
    :param unknown_token: a token to signify an unknown token
    :return: dictionary in the form of <token: identifier>
    """


def decode(
    encoded_text: list[int] | None, vocabulary: dict[str, int] | None, end_of_word_token: str | None
) -> str | None:
    """
    Translates encoded sequence into decoded one
    :param encoded_text: a sequence of token identifiers
    :param vocabulary: dictionary in the form of <token: identifier>
    :param end_of_word_token: an end-of-word token
    :return: decoded sequence
    """


def tokenize_word(
    word: tuple[str, ...], vocabulary: dict[str, int], end_of_word: str | None, unknown_token: str
) -> list[int] | None:
    """
    Splits word into tokens
    :param word: preprocessed word
    :param vocabulary: dictionary in the form of <token: identifier>
    :param end_of_word: an end-of-word token
    :param unknown_token: token that signifies unknown sequence
    :return: list of token identifiers
    """


def load_vocabulary(vocab_path: str) -> dict[str, int] | None:
    """
    Reads and retrieves dictionary of type <token: identifier>
    :param vocab_path: path to the saved vocabulary
    :return: dictionary in the form of <token: identifier>
    """


def encode(
    original_text: str,
    vocabulary: dict[str, int] | None,
    start_of_word_token: str | None,
    end_of_word_token: str | None,
    unknown_token: str,
) -> list[int] | None:
    """
    Translates decoded sequence into encoded one
    :param original_text: original text
    :param vocabulary: dictionary in the form of <token: identifier>
    :param start_of_word_token: a start-of-word token
    :param end_of_word_token: an end-of-word token
    :param unknown_token: token that signifies unknown sequence
    :return: list of token identifiers
    """


def collect_ngrams(text: str, order: int) -> list[tuple[str, ...]] | None:
    """
    Extracts n-grams from the given sequence
    :param text: original text
    :param order: required number of elements in a single n-gram
    :return: sequence of n-grams
    """


def calculate_precision(
    actual: list[tuple[str, ...]], reference: list[tuple[str, ...]]
) -> float | None:
    """
    Compares two sequences by virtue of Precision metric
    :param actual: predicted sequence of n-grams
    :param reference: expected sequence of n-grams
    :return: value of Precision metric
    """


def geo_mean(precisions: list[float], max_order: int) -> float | None:
    """
    Computes geometric mean of sequence of values
    :param precisions: sequence of Precision values
    :param max_order: maximum length of n-gram considered
    :return: value of geometric mean of Precision metric
    """


def calculate_bleu(actual: str | None, reference: str, max_order: int = 3) -> float | None:
    """
    Compares two sequences by virtue of BLEU metric
    :param actual: predicted sequence
    :param reference: expected sequence
    :param max_order: max length of n-gram to consider for comparison
    :return: value of BLEU metric
    """
