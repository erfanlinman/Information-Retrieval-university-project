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
import getopt
import json
import sys
import pprint

import ahocorasick

from spell_checker import spellchecker


def read_json(path):
    """read json file

    Arguments:
        path {str} -- path to json file

    Returns:
        dictionary -- content of json
    """

    with open(path, 'r+') as reader:
        return json.load(reader)


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


def wild_card_search(tree, wild_card, inverted_index=None):
    """wildcard search in ahocorasick tree

    Arguments:
        tree {obj} -- object of ahocorasick
        wild_card {str} -- wild card query

    Keyword Arguments:
        inverted_index {dictionary} -- inverted index for search in it
        (default: {None})

    Returns:
        (list,list,list) -- list of all match with diffrent rule for wildcard
    """

    exat_length_match = list(tree.keys(wild_card, '*',
                                       ahocorasick.MATCH_EXACT_LENGTH))
    most_prefix = list(tree.keys(wild_card, '*',
                                 ahocorasick.MATCH_AT_MOST_PREFIX))
    least_prefix = list(tree.keys(wild_card, '*',
                                  ahocorasick.MATCH_AT_LEAST_PREFIX))
    if inverted_index:
        pass
    return exat_length_match, most_prefix, least_prefix
    # set_search_wild_card = set()
    # for token in exat_length_match:
    #     set_search_wild_card.add(token)
    # for token in most_prefix:
    #     set_search_wild_card.add(token)
    # for token in least_prefix:
    #     set_search_wild_card.add(token)
    # list_doc_id_search = []
    # for token in list(set_search_wild_card):
    #     for value in inverted_index[token]['posting_list'].itervalues():
    #         list_doc_id_search.append(value.keys())
    # # set_result = set(list_doc_id_search[0][0])
    # # print list_doc_id_search[0][0]
    # # for list_ in list_doc_id_search:
    # #     for item in list_:
    # #         set_result.intersection_update(item)
    # set_result = set.intersection(*map(set, list_doc_id_search))
    # print set_result


def main(argv):
    """main method of project make inverted index and read it and make
    available wilcard search, search, make inverted index,print inverted index
    option for user

    Arguments:
        argv {list} -- argument read from terminal
    """

    print "please wait ..."
    inverted_index = read_json('data-files/inverted-index.json')
    list_tokens = inverted_index.keys()
    spell = spellchecker.SpellChecker()
    spell._word_frequency.load_words(list_tokens)
    wild_card_tree = make_wild_cart(list_tokens)
    try:
        opts, args = getopt.getopt(argv, "hw:m:s:p:", ["help", "wildcard=",
                                                       "make_index=", "search=",
                                                       "print="])
    except getopt.GetoptError:
        print "search.py -h"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "search.py -w <wildcard> for wildcard search"
            print "search.py -s <wildcard> for normal search"
            print "search.py -m for making inverted index"
            sys.exit()
        elif opt in ("-w", "--wildcard"):
            exat, most, least = wild_card_search(wild_card_tree,
                                                 arg)
            print '\n'
            print 'Exact length match:\n{}\n'.format('     '.join(exat))
            print 'Most prefix match:\n{}\n'.format('     '.join(most))
            print 'Least prefix match:\n{}\n'.format('     '.join(least))

        elif opt in ("-m", "--make_index"):
            pass
        elif opt in ("-s", "--search"):
            if arg in inverted_index:
                pprint.pprint(inverted_index[arg]['posting_list'])
            else:
                corrected, suggested = spell_checking(spell, arg)
                print 'did you mean :   \n\n{}\n'.format(corrected)
                print 'suggested words: \n\n{}\n'.format('    '.join(suggested))
        elif opt in ("-p", "--print"):
            pass


if __name__ == '__main__':
    main(sys.argv[1:])
