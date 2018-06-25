#!/usr/bin/env python
# -*- encoding: utf8 -*-
"""make inverted index by preprocessed file which made by tokenizer_normalizer
    __author__ = "Erfan Rahnemoon"
    __version__ = "0.0.1"
    __maintainer__ = "Erfan Rahnemoon"
    __email__ = "erfan@rahnemoon.name"
"""


import json
import os


def read_json(file_name):
    """read json by path

    Arguments:
        file_name {str} -- path to json

    Returns:
        dictionary -- content of json
    """

    with open(file_name, 'r') as reader:
        return json.load(reader)


def write_json(dic_content, file_name):
    """write dictionary-data in file by json style

    Arguments:
        dic_content {str} -- dictionary for writing in file
        file_name {str} -- path to write a file
    """
    with open('data-files/'+file_name+'.json', 'w+') as writer:
        json.dump(dic_content, writer)
        writer.close()


def make_inverted_index(path_preproc='data-files/json_data/cars/preprocessed/'):
    """read preprocessed file which made by tokenizer_normalizer and make
    inverted index

    Arguments:
        path_preproc {dictionary} -- inverted index
    """

    inverted_index = {}
    token_id = 0
    for preprocessed_data in os.listdir(path_preproc):
        list_docs_dic = read_json(path_preproc + preprocessed_data)
        for dic_doc in list_docs_dic:
            doc_id = dic_doc['doc_id']
            list_of_tokens = dic_doc['list_of_token']
            root_file = dic_doc['root']
            for token, pos in list_of_tokens:
                if token not in inverted_index:
                    inverted_index[token] = {
                        'token_id': token_id,
                        'number_of_doc': 0,
                        'frequncy_token': 0,
                        'posting_list': {}
                    }
                    token_id += 1
                if root_file not in inverted_index[token]['posting_list']:
                    inverted_index[token]['posting_list'][root_file] = {}
                if doc_id not in inverted_index[token]['posting_list'][root_file]:
                    inverted_index[token]['posting_list'][root_file][doc_id] = {
                        'number_of_frequncy': 0,
                        'list_pos': []
                    }
                    inverted_index[token]['number_of_doc'] += 1
                inverted_index[token]['posting_list'][root_file][doc_id]['list_pos'].append(pos)
                inverted_index[token]['posting_list'][root_file][doc_id]['number_of_frequncy'] += 1
                inverted_index[token]['frequncy_token'] += 1
    write_json(inverted_index, 'inverted-index')


def main():
    make_inverted_index()

if __name__ == '__main__':
    main()
