#!/usr/bin/env python
# -*- encoding: utf8 -*-
"""read json file stored by parser and tokenized and normalized them and write
in preprocessed directory
module run thread to number of json file
    __author__ = "Erfan Rahnemoon"
    __version__ = "0.0.1"
    __maintainer__ = "Erfan Rahnemoon"
    __email__ = "erfan@rahnemoon.name"

"""


import json
import os
import sys
from threading import Thread

import nltk
from json_autoarray import JSONAutoArray
from nltk import pos_tag
from nltk.corpus import wordnet
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer


def read_json(path_base):
    """read json file

    Arguments:
        path_base {str} -- path to json file

    Returns:
        dictionary -- content of file in json style
    """

    with open(path_base) as reader:
        return json.load(reader)


def read_stop_word(path_to_file):
    """read stop word and convert to list and retun them

    Arguments:
        path_to_file {str} -- path to file contain stop word

    Returns:
        list -- list of stop word
    """

    with open(path_to_file) as reader:
        content = reader.read()

    return content.splitlines()


def lemmatizer_fun(lemmatizer, token, token_tag=None):
    """lemmatize token with tag of token in sentence
    if token has not tag lemmatized With no tag method

    Arguments:
        lemmatizer {obj} -- instance of WordNetLemmatizer
        token {str} -- token

    Keyword Arguments:
        token_tag {str} -- tag of token in sentence (default: {None})

    Returns:
        str -- lemmatized token
    """

    if token_tag is None:
        return lemmatizer.lemmatize(token)

    return lemmatizer.lemmatize(token, pos=token_tag)


def stemmer_fun(stemmer, token):
    """stemming token by porter one algoritm

    Arguments:
        stemmer {obj} -- instance of PorterStemmer
        token {str} -- token

    Returns:
        str -- stemmed token
    """

    return stemmer.stem(token)


def get_wordnet_pos(treebank_tag):
    """convert universal tag to wordnet tag

    Arguments:
        treebank_tag {str} -- tag in universal set

    Returns:
        str -- tag in wordnet set
    """

    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    return None


def add_position_to_list_token(list_tokens):
    """add postion of each token in list of token

    Arguments:
        list_tokens {list} -- list of token

    Returns:
        list -- list of token with postion of each token
    """

    list_tokens_pos = []
    postion = 0
    for token in list_tokens:
        list_tokens_pos.append((token, postion))
        postion += 1
    return list_tokens_pos


def add_postion_tag_to_token(list_tokens_pos):
    """add tag of each token in list of token

    Arguments:
        list_tokens_pos {list} -- list of token and position

    Returns:
        list -- list of token, postion, and tag for each token
    """

    list_tokens_pos_tag = []
    for token, pos in list_tokens_pos:
        list_tokens_pos_tag.append((token,
                                    get_wordnet_pos(pos_tag([token])[0][1]),
                                    pos))
    return list_tokens_pos_tag


def remove_stop_word(list_of_token, list_of_stop_word):
    """remove stop word from list of token

    Arguments:
        list_of_token {list} -- list of tokens
        list_of_stop_word {list} -- list of all stop words

    Returns:
        list -- list of token without stopwords
    """

    filtered_tokens = []
    for token in list_of_token:
        if token[0] not in list_of_stop_word:
            filtered_tokens.append(token)
    return filtered_tokens


def tokenizer(doc, ignore_keys):
    """tokeize text by regex tokenizer

    Arguments:
        doc {dictionary} -- dictionary of all part of document
        ignore_keys {list} -- keys must be ignored from dictionary of document

    Returns:
        list -- list of tokens
    """

    list_of_token = []
    for key, item in doc.iteritems():
        if key not in ignore_keys and item is not None:
            tokenizer_engine = RegexpTokenizer(r'[a-zA-Z]+')
            list_of_token.extend(tokenizer_engine.tokenize(item.lower()))

    return list_of_token


def normalization(lemmatizer, stemmer,
                  list_token_tag_pos,
                  bool_lemmatizing=True,
                  bool_stemming=False):
    """normalized each token in list of [token, tag, postion] which can be done
    by lemmatization and stemmation

    Arguments:
        lemmatizer {obj} -- instance of WordNetLemmatizer
        stemmer {obj} -- instance of PorterStemmer
        list_token_tag_pos {list} -- list contain token, tag, position

    Keyword Arguments:
        bool_lemmatizing {bool} -- use lemmatizing for normalization
        (default: {True})
        bool_stemming {bool} -- use stemming for normalization
        (default: {False})

    Returns:
        list -- list of token, postion which tokes are normalized
    """

    list_result = []
    if bool_lemmatizing:
        lemmatized_tokens = []
        for token_tag_pos in list_token_tag_pos:
            if token_tag_pos[1] is not None:
                # lemmatizing with token tag
                lemmatized_tokens.append((lemmatizer_fun(lemmatizer,
                                                         token_tag_pos[0],
                                                         token_tag_pos[1]),
                                          token_tag_pos[2]))
            else:
                # lemmatizing without token tag
                lemmatized_tokens.append((lemmatizer_fun(lemmatizer,
                                          token_tag_pos[0]),
                                          token_tag_pos[2]))
        list_result = lemmatized_tokens
        lemmatized_tokens = None
    # stemming
    if bool_stemming:
        stemmed_tokens = []
        for token_tag_pos in list_token_tag_pos:
            stemmed_tokens.append((stemmer_fun(stemmer, token_tag_pos[0]),
                                  token_tag_pos[2]))
        list_result = stemmed_tokens
        stemmed_tokens = None

    return list_result


def tokenizer_normalizer(lemmatizer, stemmer, file_name, list_stop_words):
    """read json file stored by parser and tokenized and normalized them after
    this store each document dictionary in json by serial json writer

    Arguments:
        lemmatizer {obj} -- instance of WordNetLemmatizer
        stemmer {obj} -- instance of PorterStemmer
        file_name {str} -- path to json file which parser stored them
        list_stop_words {list} -- list of all stop words
    """

    print file_name
    base_address = 'data-files/json_data/cars/'
    conten = read_json(base_address+'parsed/'+file_name)
    # if directory does not exist make it
    if not os.path.isdir(base_address+'preprocessed/'):
        os.mkdir(base_address+'preprocessed/')
    address_write_preprocessed = base_address+'preprocessed/'+file_name
    # json sreial writer
    with JSONAutoArray.ArrayWriter(address_write_preprocessed) as json_streamer:
        for dic_document in conten:
            tokens = tokenizer(dic_document, ['docID', 'root', 'date'])
            tokens = add_position_to_list_token(tokens)
            filter_token = remove_stop_word(tokens, list_stop_words)
            token_tag_pos = add_postion_tag_to_token(filter_token)
            dic_doc_tokens = {
                "doc_id": dic_document['docID'],
                "root": file_name,
                "list_of_token": normalization(lemmatizer,
                                               stemmer,
                                               token_tag_pos)
            }
            json_streamer.write(dic_doc_tokens)


def make_preprocessed_file():
    """start tokenizer_normalizer by path of json file and read stop words
    after this for each json file run thread and store preprocessed file
    """

    reload(sys)
    sys.setdefaultencoding('cp1252')
    stop_words = read_stop_word('data-files/stopwords.txt')
    try:
        nltk.data.find('corpora/brown')
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('brown')
        nltk.download('punkt')
        nltk.download('wordnet')
    wordnet_lemmatizer = WordNetLemmatizer()
    porter_stemmer = PorterStemmer()
    wordnet.ensure_loaded()
    list_thread = []
    for data_file in os.listdir('data-files/json_data/cars/parsed'):
        # for each json file run thread
        list_thread.append(Thread(target=tokenizer_normalizer,
                                  args=(wordnet_lemmatizer, porter_stemmer,
                                        data_file, stop_words)))
    for thread in list_thread:
        thread.start()
    for thread in list_thread:
        thread.join()


if __name__ == '__main__':
    make_preprocessed_file()
