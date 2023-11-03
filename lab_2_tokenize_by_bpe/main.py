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
        if prepared_word not in dict_of_frequencies:
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
                word_as_list[i+1] = ''
            if '' in word_as_list:
                word_as_list.remove('')
        new_dict[tuple(word_as_list)] = word_frequencies[word]
    return new_dict


def train(
    word_frequencies: dict[tuple[str, ...], int] | None, num_merges: int
) -> dict[tuple[str, ...], int] | None:
    """
    Creates required number of new tokens by merging existing ones
    :param word_frequencies: dictionary of a kind <preprocessed word: number of occurrences>
    :param num_merges: required number of new tokens
    :return: dictionary in the form of <preprocessed word: number of occurrences>
    """
    if not isinstance(word_frequencies, dict) or not isinstance(num_merges, int):
        return None
    if word_frequencies is None:
        return None
    while num_merges > 0:
        dict_of_token_pairs = count_tokens_pairs(word_frequencies)
        if dict_of_token_pairs is None:
            return None
        num_merges = min(num_merges, len(dict_of_token_pairs))
        temp_list_of_max_token_pairs = []
        list_of_max_token_pairs = []
        max_token_pair = max(dict_of_token_pairs.values())
        for token_pair in dict_of_token_pairs:
            if dict_of_token_pairs[token_pair] == max_token_pair:
                temp_list_of_max_token_pairs.append(token_pair)
        max_token_pair_length = max(len(str(token_pair)) for token_pair in temp_list_of_max_token_pairs)
        for token_pair in temp_list_of_max_token_pairs:
            if len(str(token_pair)) == max_token_pair_length:
                list_of_max_token_pairs.append(token_pair)
        list_of_max_token_pairs.sort(key=lambda x: (-len(x), x))
        word_frequencies = merge_tokens(word_frequencies, list_of_max_token_pairs[0])
        num_merges -= 1
        if word_frequencies is None:
            return None
    return word_frequencies


def get_vocabulary(
    word_frequencies: dict[tuple[str, ...], int], unknown_token: str
) -> dict[str, int] | None:
    """
    Establishes correspondence between tokens and its integer identifier
    :param word_frequencies: dictionary in the form of <preprocessed word: number of occurrences>
    :param unknown_token: a token to signify an unknown token
    :return: dictionary in the form of <token: identifier>
    """
    if not isinstance(word_frequencies, dict) or not isinstance(unknown_token, str):
        return None
    if word_frequencies is None:
        return None
    new_dict = {}
    list_of_tokens = set()
    for word in word_frequencies:
        for token in word:
            list_of_tokens.add(token)
            for letter in token:
                list_of_tokens.add(letter)
    list_of_tokens.add(unknown_token)
    sorted_list_of_tokens = sorted(list_of_tokens)
    sorted_list_of_tokens_2 = sorted(sorted_list_of_tokens, key=len, reverse=True)
    for i, token in enumerate(sorted_list_of_tokens_2):
        if token not in new_dict:
            new_dict[token] = i
    return new_dict


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
    if (not isinstance(encoded_text, list) or not isinstance(vocabulary, dict)
            or not (isinstance(end_of_word_token, str) or (end_of_word_token is None))):
        return None
    list_of_tokens = []
    new_dict = []
    for i in encoded_text:
        for token, value in vocabulary.items():
            if value == i:
                list_of_tokens.append(token)
        for token in list_of_tokens:
            if end_of_word_token is not None and end_of_word_token == token:
                list_of_tokens[list_of_tokens.index(token)] = ' '
            else:
                new_dict.append(token)
    return ''.join(list_of_tokens)


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
