# -*- coding: utf-8 -*-
"""
Class for preprocessing the Europarl corpus as well as additional functions for preprocessing the Wikipedia corpus,
generating a test corpus and extracting a list of prepositions from a file.
@author: Yoalli Garcia
"""
import codecs
import os
from nltk import word_tokenize
from nltk import pos_tag_sents
from treetaggerwrapper import TreeTagger


class PreprocessData:
    def __init__(self):
        self.lines_en = []
        self.lines_es =[]
        self.tokenizedLines_en = []
        self.tokenizedLines_es = []
        self.f_a_sents = []
        self.aligned_sents = []
        self.pos_tagged_sents_en = []
        self.pos_tagged_sents_es = []

    def read_file(self, fn_en, fn_es):
        # reads the file containing a sentence in each line 
        # creates a list of sentences
        print("Reading the files...")
        f = codecs.open(fn_en, "r", "utf-8")
        self.lines_en=f.readlines()
        f = codecs.open(fn_es, "r", "utf-8")
        self.lines_es=f.readlines()

    def tokenize_lines(self):
        # goes through the list of sentences and tokenizes each sentence
        # stores the resulting list of lists of words/tokens into "tokenizedLines"
        print("Tokenizing the sentences...")
        for sent in self.lines_en:
            self.tokenizedLines_en.append(word_tokenize(sent))
        for sent in self.lines_es:
            self.tokenizedLines_es.append(word_tokenize(sent))

    def read_tokenized(self, en_file, es_file):
        # read and store an already tokenized file
        sentsen = []
        sentses = []
        with open(en_file, "r") as enf:
            enlines = enf.readlines()
        for enl in enlines:
            splt = enl.split()
            sentsen.append(splt)
        with open(es_file, "r") as esf:
            eslines = esf.readlines()
        for esl in eslines:
            splt = esl.split()
            sentses.append(splt)
        self.tokenizedLines_en = sentsen
        self.tokenizedLines_es = sentses

    def add_pos_tags(self,treetaggerlocation, taglang="es"):
        # POS-tag the tokenized sentences according to language
        print("Adding POS-Tags...")
        pos_tagged_sents = pos_tag_sents(self.tokenizedLines_en)
        # pos_tagged_sents = [[(w1,tag1),(w2,tag2)],[(w1,t2),(w2,t2),...]...]
        for sent in pos_tagged_sents:
            fo = []
            for word in sent:
                temp = word[0] + word[1]
                fo.append(temp)
            self.pos_tagged_sents_en.append(fo)  # -> [["w1t1","w2t2",...],["w1t1",...],...]
        if taglang == "fi":
            tagger = TreeTagger(TAGLANG=taglang, TAGDIR = treetaggerlocation, TAGPARFILE="Preprocessing/fi_en/finnish.par")
        if taglang == "es":
            tagger = TreeTagger(TAGLANG=taglang, TAGDIR = treetaggerlocation, TAGPARFILE="Preprocessing/es_en/spanish.par")
        if taglang == "de":
            tagger = TreeTagger(TAGLANG=taglang, TAGDIR = treetaggerlocation, TAGPARFILE="Preprocessing/de_en/german.par")
        if taglang == "pl":
            tagger = TreeTagger(TAGLANG=taglang, TAGDIR = treetaggerlocation, TAGPARFILE="Preprocessing/pl_en/polish.par")
        pos_tagged_sents = []
        for line in self.tokenizedLines_es:
            if "EE.UU" in line:
                line_t = []
                for w in line:
                    if w == "EE.UU":
                        line_t.append("EEUU")
                    else:
                        line_t.append(w)
                line = line_t
            tags = tagger.tag_text(line)
            pos_tagged_sents.append(tags)
            # -> [['Esto\tDM\teste','es\tVSfin\tser', 'un\tART\tun','texto\tNC\ttexto',],[...],...]
        for i in range(len(pos_tagged_sents)):
            fo = []
            for word in pos_tagged_sents[i]:
                temp = word.split('\t')  # 'esto\tDM\teste' => ['esto', 'DM', 'este']
                word_n_tag = temp[0] + temp[1]  # ['esto', 'DM', 'este'] => 'estoDM'
                fo.append(word_n_tag)
            self.pos_tagged_sents_es.append(fo)

    def read_file_and_tokenize_lines(self, fn_en, fn_es):
        self.read_file(fn_en, fn_es)
        self.tokenize_lines()

    def prepare_lines_for_fast_align(self, pos_tags):
        # adjusts the lines to the fast_align input format
        # example output: 
        # This is an example . ||| Esto es un ejemplo . \n
        print("Preparing the sentences for fast_align...")
        temp_en_list = []
        temp_es_list = []
        if pos_tags:
            self.tokenizedLines_en = self.pos_tagged_sents_en
            self.tokenizedLines_es = self.pos_tagged_sents_es
        for sent in self.tokenizedLines_en:
            temp_sent = " ".join(sent)
            temp_en_list.append(temp_sent)
            
        for sent in self.tokenizedLines_es:
            temp_sent = " ".join(sent)
            temp_es_list.append(temp_sent)

        for i in range(temp_en_list.__len__()):
            try:
                self.f_a_sents.append(temp_en_list[i] + " ||| " + temp_es_list[i] + "\n")
            except IndexError:
                print("IndexError at i: " + str(i))

    def create_fast_align_file(self, input_for_fast_align):
        # creates a file that matches the fast_align input format
        print("Creating a file fit for fast_align...")
        with codecs.open(input_for_fast_align, "w", "utf-8") as out:
            for sent in self.f_a_sents:
                out.write(sent)

    def use_fast_align(self, input_for_fast_align, output_fast_align, path_fast_align):
        # executes fast_align via os
        print("Aligning via fast_align...")
        command = path_fast_align + " -i " + input_for_fast_align + " > " + output_fast_align
        os.system(command)
        with codecs.open(output_fast_align, "r", "utf-8") as af:
            self.aligned_sents = af.readlines()
    
    def fast_align_sentences(self, path_fast_align, input_for_fast_align, output_fast_align, use_pos_tags):
        # combine all the actions needed to fast align the sentences
        # input_for_fast_align  == file with input format "<sentence1> ||| <sentence2>"
        # output_fast_align     == aligned positions of the sentences, e.g.: "0-0 1-1 2-1"
        # path_fast_align       == path to where fast align was installed
        # use_pos_tags          == True if POS-tags should be used for alignment, False if not
        self.prepare_lines_for_fast_align(use_pos_tags)
        self.create_fast_align_file(input_for_fast_align)
        self.use_fast_align(input_for_fast_align, output_fast_align, path_fast_align)

    def save_tokenized_file(self, filename, lang="en"):
        # save the tokenized file to respective file name
        with codecs.open(filename, "w", "utf-8") as te:
            if lang == "en":
                for line in self.tokenizedLines_en:
                    te.write(" ".join(line))
                    te.write("\n")
                te.close()
            else:
                for line in self.tokenizedLines_es:
                    te.write(" ".join(line))
                    te.write("\n")
                te.close()

    def preprocess_data(self, taglang, use_pos_tags, treetaggerlocation, path_fast_align):
        # preprocess Europarl corpus: read file, tokenize lines, POS-tag sentences, and fast_align them
        en_data = "Preprocessing/%s_en/input_en" % taglang
        es_data = "Preprocessing/%s_en/input_%s" % (taglang, taglang)
        tokenized_file_en = "src/tokenized_en"
        tokenized_file_es = "src/tokenized_" + taglang
        output_fast_align = "src/aligned_file"
        temp_file_for_fast_align = "Preprocessing/file_for_fast_align"
        self.read_file_and_tokenize_lines(en_data, es_data)
        self.save_tokenized_file(tokenized_file_en, "en")
        self.save_tokenized_file(tokenized_file_es, taglang)
        self.add_pos_tags(treetaggerlocation, taglang=taglang)
        self.fast_align_sentences(path_fast_align,temp_file_for_fast_align, output_fast_align, use_pos_tags=use_pos_tags)


def generate_test_corpus(filename="tokenized_en", eval_data="SCWS/ratings.txt", new_file="TEST_corpus_en"):
    # Experiment: generate a corpus that only contains sentences that contain at least one word from the eval file
    words = []
    with open(eval_data) as scws:
        lines = scws.readlines()
    for line in lines:
        sline = line.split("\t")
        words.append(sline[1])
        words.append(sline[3])
    words = set(words)
    print(words)
    new_lines = []
    with open(filename) as corpus:
        lines = corpus.readlines()
    print("lines read!")
    for i in range(len(lines)):
        if any(word in lines[i] for word in words):
            open(new_file, "a").write(lines[i])
    return new_file


def preprocess_wiki_corpus(file_in, file_out, trim=1000000):
    # preprocess the wikipedia corpus line by line
    f = codecs.open(file_in, "r", "utf-8")
    lines = [next(f) for x in range(trim)]
    print(lines[-1])
    tok_lines = []
    for line in lines:
        if line == "---END.OF.DOCUMENT---\n":
            continue
        else:
            tok_lines.append(word_tokenize(line))
    with codecs.open(file_out, "w", "utf-8") as f_out:
        for line in tok_lines:
            f_out.write(" ".join(line))
            f_out.write("\n")
        f_out.close()


def get_prepositions(filename):
    # extract prepositions from file containing one preposition per line
    prepositions = []
    with open(filename, "r") as prepos:
        lines = prepos.readlines()
        for p in lines:
            p = p.lower().strip()
            prepositions.append(p)
    return prepositions


def preprocess_europarl(config):
    # extract parameters from config and initiate preprocessing
    params = config["Preprocessing"]
    path_fast_align = params["fast_align location"]
    treetaggerlocation = params["TreeTagger location"]
    pD = PreprocessData()
    pD.preprocess_data(params["language"], params["use pos tags"], treetaggerlocation, path_fast_align)


if __name__ == '__main__':
    # preprocess_wiki_corpus("TEST_en", "TEST_OUT", 1000)
    # generate_test_corpus()
    pass
    
