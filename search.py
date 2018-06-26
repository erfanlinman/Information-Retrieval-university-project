#!/usr/bin/env python
# -*- encoding: utf8 -*-
"""search in inverted index by word and wild card
    if inverted index not exit make it
    and module has spell checking

    __author__ = "Erfan Rahnemoon"
    __version__ = "0.0.1"
    __maintainer__ = "Erfan Rahnemoon"
    __email__ = "erfan@rahnemoon.name"
"""
import errno
import getopt
import json
import os
import parser
import pprint
import sys

import ahocorasick
import beautifultable
import spellchecker
import inverted_index_maker
import tokenizers_normalizer


def read_json(path):
    """read json file

    Arguments:
        path {str} -- path to json file

    Returns:
        dictionary -- content of json
    """

    with open(path, 'r+') as reader:
        return json.load(reader)


def write_in_file(content, path):
    """write content in file

    Arguments:
        content {str} -- content to write in file
        path {str} -- path to file
    """

    with open(path, 'w+') as writer:
        writer.write(content)
        writer.close()


def spell_checking(spell, input_word):
    """spell checking word in query

    Arguments:
        spell {obj} -- object from spell checker
        input_word {str} -- query word

    Returns:
        (str, list) -- corrected word and list of suggested word
    """

    return spell.correction(input_word), list(spell.candidates(input_word))


def make_wild_cart(list_of_word):
    """make ahocorasick tree for wildcard search

    Arguments:
        list_of_word {list} -- list of all token in inverted index

    Returns:
        obj -- object of ahocorasick tree
    """

    tree = ahocorasick.Automaton()
    for idx, key in enumerate(list_of_word):
        tree.add_word(str(key), (idx, str(key)))

    return tree


def make_inverted_index():
    """make inverted index file from other files
    """

    parser.parsing()
    tokenizers_normalizer.make_preprocessed_file()
    inverted_index_maker.make_inverted_index()


def wild_card_search(tree, wild_card):
    """wildcard search in ahocorasick tree

    Arguments:
        tree {obj} -- object of ahocorasick
        wild_card {str} -- wild card query

    Returns:
        (list,list,list) -- list of all match with diffrent rule for wildcard
    """

    exact_length_match = list(tree.keys(wild_card, '*',
                                        ahocorasick.MATCH_EXACT_LENGTH))
    most_prefix = list(tree.keys(wild_card, '*',
                                 ahocorasick.MATCH_AT_MOST_PREFIX))
    least_prefix = list(tree.keys(wild_card, '*',
                                  ahocorasick.MATCH_AT_LEAST_PREFIX))

    return exact_length_match, most_prefix, least_prefix


def wild_card_find_doc(inverted_index, wild_card_tokens):
    """search in inverted index and find posting lists of all words which find
    them related to the wildcars

    Arguments:
        inverted_index {dictionary} -- dictionary of tokens and posting-lists
        wild_card_tokens {list} -- all words find them by tree which related to
        wildcard

    Returns:
        dictionary, list -- dictionary of tokens and posting-lists which those
        token found it in inverted index, list of all tokens not found in
        inverted index
    """

    search_wild_card = {}
    list_not_found_token = []
    if inverted_index is not None:
        for token in list(wild_card_tokens):
            if token in inverted_index:
                search_wild_card[token] = inverted_index[token]
            else:
                list_not_found_token.append(token)

    return search_wild_card, list_not_found_token


def init():
    """check essential directories and files if can not find them make them and
    read inverted index, make spell checker instance and config it, make
    wildcard tree

    Returns:
        dictionary, obj, obj -- dictionary of tokens and posting-lists, object
        of spell checker and object of wildcards tree
    """

    print "please wait ..."
    if not os.path.exists('data-files/json_data'):
        try:
            os.makedirs('data-files/json_data')
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    if not os.path.exists('data-files/json_data/cars'):
        try:
            os.makedirs('data-files/json_data/cars')
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    spell = spellchecker.SpellChecker(language=None,
                                      local_dictionary='spell_checker/en.json.gz')
    if os.path.isfile('data-files/inverted-index.json'):
        inverted_index = read_json('data-files/inverted-index.json')
        list_tokens = inverted_index.keys()
        spell.word_frequency.load_words(list_tokens)
        wild_card_tree = make_wild_cart(list_tokens)
    else:
        # if make option not used before so make inverted index, next to other
        # thing
        print 'inverted index not available'
        print 'making inverted index'
        make_inverted_index()
        print 'inverted index was made'

    return inverted_index, spell, wild_card_tree


def help_option():
    """print result for help input option
    """

    print 'search.py -w <wildcard> for wildcard search'
    print 'search.py -s <wildcard> for normal search'
    print 'search.py -m for making inverted index'
    sys.exit()


def wild_card_option(input_token, wild_card_tree, inverted_index):
    """print result for wildcard search input option

    Arguments:
        input_token {str} -- token from standard input
        wild_card_tree {obj} -- instance of wildcard tree
        inverted_index {dic} -- dictionary of tokens and posting-lists
    """

    exact, most, least = wild_card_search(wild_card_tree, input_token)
    print '\n'
    # Exact length match => words, results
    doc_found, not_founds = wild_card_find_doc(inverted_index, exact)
    print 'Exact length match:\n{}\n'.format('\n'.join(exact))
    print 'founded words:\n{}\n'.format(pprint.pformat(doc_found, indent=4))
    print 'nothing found for:\n{}\n'.format('\n'.join(not_founds))
    print '{}'.format('#' * 70)
    # Most prefix match => words, results
    doc_found, not_founds = wild_card_find_doc(inverted_index, most)
    print 'Most prefix match:\n{}\n'.format('\n'.join(most))
    print 'founded words:\n{}\n'.format(pprint.pformat(doc_found, indent=4))
    print 'nothing found for:\n{}'.format('\n'.join(not_founds))
    print '{}'.format('#' * 70)
    # Least prefix match => words, results
    doc_found, not_founds = wild_card_find_doc(inverted_index, least)
    print 'Least prefix match:\n{}\n'.format('\n'.join(least))
    print 'founded words:\n{}\n'.format(pprint.pformat(doc_found, indent=4))
    print 'nothing found for:\n{}'.format('\n'.join(not_founds))
    print '{}'.format('#' * 70)


def search_option(input_token, inverted_index, spell_checker):
    """print result for search option input and if input is wrong make
    suggestion with spell checker

    Arguments:
        input_token {str} -- input token from standard input
        inverted_index {dic} -- dictionary of tokens and posting-lists
        spell_checker {obj} -- instance of spell checker
    """

    if input_token in inverted_index:
        pprint.pprint(inverted_index[input_token]['posting_list'])
    else:
        corrected, suggested = spell_checking(spell_checker, input_token)
        print 'did you mean :   \n\n{}\n'.format(corrected)
        print 'suggested words: \n\n{}\n'.format('\n'.join(suggested))


def print_option(inverted_index):
    """make table of inverted index in TXT file

    Arguments:
        inverted_index {dic} -- dictionary of tokens and posting-lists
    """

    table = beautifultable.BeautifulTable()
    table.column_headers = ['token', 'token ID', 'doc ID',
                            'root file', 'term frequency']
    for token, postinglist in inverted_index.iteritems():
        token_id = postinglist['token_id']

        for root, dic_doc_id in postinglist['posting_list'].iteritems():
            for doc_id, value in dic_doc_id.iteritems():
                table.append_row([token, token_id, doc_id,
                                 root, value['number_of_frequency']])
                write_in_file(str(table), 'table_inverted_index.txt')


def main(argv):
    """main method of project make inverted index and read it and make
    available wildcard search, search, make inverted index,print inverted index
    option for user

    Arguments:
        argv {list} -- argument read from terminal
    """

    inverted_index, spell, wild_card_tree = init()
    try:
        opts, args = getopt.getopt(argv, 'hpmw:s:', ['help', 'wildcard=',
                                                     'make_index', 'search=',
                                                     'print'])
    except getopt.GetoptError:
        print 'search.py -h'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help_option()
        elif opt in ("-w", "--wildcard"):
            wild_card_option(arg, wild_card_tree, inverted_index)
        elif opt in ('-m', '--make_index'):
            make_inverted_index()
        elif opt in ('-s', '--search'):
            search_option(arg, inverted_index, spell)
        elif opt in ("-p", "--print"):
            print_option(inverted_index)

if __name__ == '__main__':
    main(sys.argv[1:])
