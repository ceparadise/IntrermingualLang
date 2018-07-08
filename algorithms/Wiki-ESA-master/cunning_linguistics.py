# -*- coding: utf-8 -*-
'''Small module for computational linguistics applied to Twitter.
The main classes are a TweetHarvester, which gathers data from Twitters' API,
and a SemanticAnalyser, which relies on the previously constructed TFIDF 
matrices.'''

from __future__ import division

import re, json, os

from scipy import sparse as sps
import numpy as np
from collections import Counter
from numpy.linalg import norm

# ==============================================================================
# Defines stuff to analyse text using an already constructed interpretation
# matrix.
# ==============================================================================


extensions = {'content': '.raw',
              'words': '.w',
              'links': '.l',
              'matrix': '.mtx'}


def load(file_handle):
    return json.load(file_handle, object_hook=None)


def reconstruct(d):
    '''Helper method to reconstruct CSR matrix dumped in JSON format'''
    if 'object_type' in d and d['object_type'] == 'csr_matrix':
        data = np.array(d['data'])
        indices = d['indices']
        indptr = d['indptr']
        shape = tuple(d['shape'])
        instance = sps.csr_matrix((data, indices, indptr),
                                  shape)
        return instance


def mload(file_handle):
    '''Loads CSR matrices from JSON dump.'''
    return json.load(file_handle, object_hook=reconstruct)


class SemanticAnalyser(object):
    '''Analyser class using Explicit Semantic Analysis (ESA) to process 
    text fragments. It can compute semantic (pseudo) distance and similarity,
    as well'''

    def load(file_handle):
        return json.load(file_handle, object_hook=None)

    def __init__(self, matrix_dir='matrix', row_chunk_size=10 ** 4):
        # Hashes for word and concept indices
        self.row_chunk_size = row_chunk_size
        with open(os.path.join(matrix_dir, 'word2index.ind'), 'r') as f:
            self.word2index = load(f)
        with open(os.path.join(matrix_dir, 'concept2index.ind'), 'r') as f:
            self.concept2index = load(f)
        self.index2concept = {i: c for c, i in self.concept2index.items()}

        # Count number of words and concepts
        self.n_words = len(self.word2index)
        self.n_concepts = len(self.concept2index)
        self.matrix_dir = matrix_dir

    def clean(self, text):
        text = re.sub('[^\w\s\d\'\-]', '', text)
        text = text.lower()

        return text

    def interpretation_vector(self, text):
        '''Converts a text fragment string into a row vector where the i'th
        entry corresponds to the total TF-IDF score of the text fragment
        for concept i'''

        # Remove mess (quotes, parentheses etc) from text
        text = self.clean(text)

        # Convert string to hash like {'word' : no. of occurrences}
        countmap = Counter(text.split()).items()

        # Interpretation vector to be returned
        result = sps.csr_matrix((1, self.n_concepts), dtype=float)

        # Add word count in the correct position of the vector
        for word, count in countmap:
            try:
                ind = self.word2index[word]
                # Which file to look in
                file_number = int(ind / self.row_chunk_size)
                filename = os.path.join(self.matrix_dir, str(file_number) + extensions['matrix'])

                # And which row to extract
                row_number = ind % self.row_chunk_size

                # Do it! Do it naw!
                with open(filename, 'r') as f:
                    temp = mload(f)
                    result = result + count * temp.getrow(row_number)
            except KeyError:
                pass  # No data on this word -> discard

        # Done. Return row vector as a 1x#concepts CSR matrix
        return result

    def interpret_text(self, text, display_concepts=10):
        '''Attempts to guess the core concepts of the given text fragment'''
        # Compute the interpretation vector for the text fragment
        vec = self.interpretation_vector(text)

        # Magic, don't touch
        top_n = vec.data.argsort()[:len(vec.data) - 1 - display_concepts:-1]

        # List top scoring concepts and their TD-IDF
        concepts = [self.index2concept[vec.indices[i]] for i in top_n]
        return concepts

    #        scores = [vec.data[i] for i in top_n]
    #        #Return as dict {concept : score}
    #        return dict(zip(concepts, scores))

    def interpret_file(self, filename):
        with open(filename, 'r') as f:
            data = self.clean(f.read())
        return self.interpret_text(data)

    def scalar(self, v1, v2):
        # Compute their inner product and make sure it's a scalar
        dot = v1.dot(v2.transpose())
        assert dot.shape == (1, 1)

        if dot.data:
            scal = dot.data[0]
        else:
            scal = 0  # Empty sparse matrix means zero

        # Normalize and return
        sim = scal / (norm(v1.data) * norm(v2.data))
        return sim

    def cosine_similarity(self, text1, text2):
        '''Determines cosine similarity between input texts.
        Returns float in [0,1]'''

        # Determine intepretation vectors
        v1 = self.interpretation_vector(text1)
        v2 = self.interpretation_vector(text2)

        # Compute the normalized dot product and return
        return self.scalar(v1, v2)

    def cosine_distance(self, text1, text2):
        return 1 - self.cosine_similarity(text1, text2)
