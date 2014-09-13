"""
Tests for the document vectorization module.

"""
import unittest
import string
from api import doctovec


class TestCleanWord(unittest.TestCase):
    """Test word cleaning and filtering."""

    def test_whitespace_stripping(self):
        leading = u'  test'
        trailing = u'test  '
        expected = u'test'
        stripped_leading = doctovec.clean_word(leading)
        stripped_trailing = doctovec.clean_word(trailing)

        self.assertEqual(stripped_leading, expected)
        self.assertEqual(stripped_trailing, expected)

    def test_removes_punctuation(self):
        punctuation = doctovec.PUNCT
        for char in punctuation:
            self.assertEqual(doctovec.clean_word(unicode(char)), u'')

    def test_lowercases_words(self):
        uppercase = u'TEST'
        expected = u'test'
        self.assertEqual(doctovec.clean_word(uppercase), expected)


class TestWordIsNotJunk(unittest.TestCase):
    """Test word validation."""

    def test_dont_keep_empty_words(self):
        empty = ''
        self.assertFalse(doctovec.word_is_not_junk(empty))

    def test_dont_keep_stopwords(self):
        for word in doctovec.STOPWORDS:
            self.assertFalse(doctovec.word_is_not_junk(word))

    def test_dont_keep_all_digit_words(self):
        test = '1209358172305'
        self.assertFalse(doctovec.word_is_not_junk(test))

    def test_dont_keep_words_starting_with_digits(self):
        test = '1hello'
        self.assertFalse(doctovec.word_is_not_junk(test))

    def test_dont_keep_single_character_words(self):
        english_chars = [char for char in string.lowercase]
        for char in english_chars:
            self.assertFalse(doctovec.word_is_not_junk(char))

    def test_keeps_some_valid_words(self):
        valid_words = [
            'computation',
            'robotics',
            'algorithm',
            'artificial',
            'intelligence',
            'research',
            'undergraduate',
            'graduate',
            'dr'
        ]

        for word in valid_words:
            self.assertTrue(doctovec.word_is_not_junk(word))

