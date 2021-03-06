import unittest
import unittest.mock

from programy.extensions.newsapi.newsapi import NewsAPIExtension
from programy.extensions.newsapi.newsapi import NewsAPI


class MockNewsAPI(NewsAPI):

    def __init__(self, license_keys):
        self.license_keys = license_keys
        self.fail_get_headlines = False
        self.fail_to_program_y_text = False

    def get_headlines(self, source, max_articles=0, sort=False, reverse=False):
        if self.fail_get_headlines is True:
            return None
        else:
            article =  unittest.mock.Mock()
            article.title = "Headline"
            article.description = source
            return [article]

    def to_program_y_text(self, headlines):
        if self.fail_to_program_y_text is True:
            return None
        else:
            return super(MockNewsAPI, self).to_program_y_text(headlines)

class MockNewsAPIExtension(NewsAPIExtension):

    def __init__(self):
        self.fail_get_headlines = False
        self.fail_to_program_y_text = False

    def get_news_api_api(self, bot, clientid):
        self.news_api = MockNewsAPI(bot.license_keys)
        self.news_api.fail_get_headlines = self.fail_get_headlines
        self.news_api.fail_to_program_y_text = self.fail_to_program_y_text
        return self.news_api

class NewsAPIExtensionTests(unittest.TestCase):

    def test_get_news(self):

        extension = MockNewsAPIExtension()
        self.assertIsNotNone(extension)

        bot = unittest.mock.Mock()
        bot.license_keys = "license.keys"

        extension.fail_get_headlines = False
        extension.fail_to_program_y_text = False
        results = extension.get_news(bot, "testid", "BBC", 10, True, False)
        self.assertIsNotNone(results)

        extension.fail_get_headlines = True
        extension.fail_to_program_y_text = False
        results = extension.get_news(bot, "testid", "BBC", 10, True, False)
        self.assertIsNotNone(results)

        extension.fail_get_headlines = False
        extension.fail_to_program_y_text = True
        results = extension.get_news(bot, "testid", "BBC", 10, True, False)
        self.assertIsNotNone(results)

    def test_parse_data(self):

        extension = NewsAPIExtension()
        self.assertIsNotNone(extension)

        source, max, sort, reverse = extension.parse_data("")
        self.assertIsNone(source)
        self.assertEqual(10, max)
        self.assertEqual(False, sort)
        self.assertEqual(False, reverse)

        source, max, sort, reverse = extension.parse_data("SOURCE BBC")
        self.assertEqual("BBC", source)
        self.assertEqual(10, max)
        self.assertEqual(False, sort)
        self.assertEqual(False, reverse)

        source, max, sort, reverse = extension.parse_data("SOURCE BBC MAX 20")
        self.assertEqual("BBC", source)
        self.assertEqual(20, max)
        self.assertEqual(False, sort)
        self.assertEqual(False, reverse)

        source, max, sort, reverse = extension.parse_data("SOURCE BBC MAX 20 SORT TRUE")
        self.assertEqual("BBC", source)
        self.assertEqual(20, max)
        self.assertEqual(True, sort)
        self.assertEqual(False, reverse)

        source, max, sort, reverse = extension.parse_data("SOURCE BBC MAX 20 SORT FALSE")
        self.assertEqual("BBC", source)
        self.assertEqual(20, max)
        self.assertEqual(False, sort)
        self.assertEqual(False, reverse)

        source, max, sort, reverse = extension.parse_data("SOURCE BBC MAX 20 SORT ERROR")
        self.assertEqual("BBC", source)
        self.assertEqual(20, max)
        self.assertEqual(False, sort)
        self.assertEqual(False, reverse)

        source, max, sort, reverse = extension.parse_data("SOURCE BBC MAX 20 SORT TRUE REVERSE TRUE")
        self.assertEqual("BBC", source)
        self.assertEqual(20, max)
        self.assertEqual(True, sort)
        self.assertEqual(True, reverse)

        source, max, sort, reverse = extension.parse_data("SOURCE BBC MAX 20 SORT TRUE REVERSE FALSE")
        self.assertEqual("BBC", source)
        self.assertEqual(20, max)
        self.assertEqual(True, sort)
        self.assertEqual(False, reverse)

        source, max, sort, reverse = extension.parse_data("SOURCE BBC MAX 20 SORT TRUE REVERSE ERROR")
        self.assertEqual("BBC", source)
        self.assertEqual(20, max)
        self.assertEqual(True, sort)
        self.assertEqual(False, reverse)

    def test_execute(self):

        extension = MockNewsAPIExtension()
        self.assertIsNotNone(extension)

        bot = unittest.mock.Mock()
        bot.license_keys = "license.keys"

        result = extension.execute(bot, "testid", "SOURCE BBC")
        self.assertIsNotNone(result)
        self.assertEquals("Headline - BBC", result)

        result = extension.execute(bot, "testid", "SOURCE BBC MAX 20")
        self.assertIsNotNone(result)
        self.assertEquals("Headline - BBC", result)

        result = extension.execute(bot, "testid", "SOURCE BBC MAX 20 SORT TRUE")
        self.assertIsNotNone(result)
        self.assertEquals("Headline - BBC", result)

        result = extension.execute(bot, "testid", "SOURCE BBC MAX 20 SORT FALSE")
        self.assertIsNotNone(result)
        self.assertEquals("Headline - BBC", result)

        result = extension.execute(bot, "testid", "SOURCE BBC MAX 20 SORT ERROR")
        self.assertIsNotNone(result)
        self.assertEquals("Headline - BBC", result)

        result = extension.execute(bot, "testid", "SOURCE BBC MAX 20 SORT TRUE REVERSE TRUE")
        self.assertIsNotNone(result)
        self.assertEquals("Headline - BBC", result)

        result = extension.execute(bot, "testid", "SOURCE BBC MAX 20 SORT TRUE REVERSE FALSE")
        self.assertIsNotNone(result)
        self.assertEquals("Headline - BBC", result)

        result = extension.execute(bot, "testid", "SOURCE BBC MAX 20 SORT TRUE REVERSE ERROR")
        self.assertIsNotNone(result)
        self.assertEquals("Headline - BBC", result)

        result = extension.execute(bot, "testid", "OTHER MAX 20 SORT TRUE REVERSE ERROR")
        self.assertIsNotNone(result)
        self.assertEquals("", result)

        result = extension.execute(bot, "testid", "SOURCE BBC MAX 20 SORT TRUE OTHER ERROR")
        self.assertIsNotNone(result)
        self.assertEquals("Headline - BBC", result)
