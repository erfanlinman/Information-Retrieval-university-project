# Information-Retrieval-university-project
A university-related project, Build an Inverted Index search according to the [documentation specifications](https://github.com/erfanlinman/Information-Retrieval-university-project/blob/master/documents/IR-Hmwrk1-9697-02.pdf)

## Implemented sections
* normal search 
* wildcard search
* spell checking

## Project description
This project uses some of easiest NLP techniques for preprocessing level. First of all, read all data-set files and parsing them to the JSON file according to a year that comment left. Next use some NLP technique in preprocessing JSON files. Finally, make an inverted index from preprocessed files. An inverted index read and used for normal search, wildcard search, and spell checking.

* For wildcard search [pyahocorasick](https://github.com/WojciechMula/pyahocorasick) library is used.
* For spell checking [pyspellchecker](https://github.com/barrust/pyspellchecker) library is used.

> NOTICE:This project use some of easiest NLP techniques for preprocessing level like: lemmatizing, stemming, word position detection from NLTK

## How to use
First make Virtualenv with python 2.7, next run following command
```bash
pip install -r requirment.txt
```
```bash
 python search.py -h
 ```

## Data-set description
[OpinRank Dataset](http://kavita-ganesan.com/entity-ranking-data/)

## LICENSE
[MIT](https://github.com/erfanlinman/Information-Retrieval-university-project/blob/master/LICENSE)