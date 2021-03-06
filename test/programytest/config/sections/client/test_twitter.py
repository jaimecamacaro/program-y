import unittest

from programy.config.file.yaml_file import YamlConfigurationFile
from programy.config.sections.client.twitter import TwitterConfiguration
from programy.config.sections.client.console import ConsoleConfiguration


class TwitterConfigurationTests(unittest.TestCase):

    def test_init(self):
        yaml = YamlConfigurationFile()
        self.assertIsNotNone(yaml)
        yaml.load_from_text("""
            twitter:
              polling: true
              polling_interval: 59
              rate_limit_sleep: 900
              streaming: true
              use_status: true
              use_direct_message: true
              auto_follow: true
              storage: file
              storage_location: ./storage/twitter.data
              welcome_message: Thanks for following me
        """, ConsoleConfiguration(), ".")

        twitter_config = TwitterConfiguration()
        twitter_config.load_config_section(yaml, ".")

        self.assertTrue(twitter_config.polling)
        self.assertEqual(59, twitter_config.polling_interval)
        self.assertEqual(900, twitter_config.rate_limit_sleep)
        self.assertTrue(twitter_config.streaming)
        self.assertTrue(twitter_config.use_status)
        self.assertTrue(twitter_config.use_direct_message)
        self.assertTrue(twitter_config.auto_follow)
        self.assertEquals("file", twitter_config.storage)
        self.assertEquals("./storage/twitter.data", twitter_config.storage_location)
        self.assertEquals("Thanks for following me", twitter_config.welcome_message)

