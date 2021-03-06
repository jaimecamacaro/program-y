"""
Copyright (c) 2016-17 Keith Sterling http://www.keithsterling.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import logging
import time
import os
import tweepy
from tweepy.error import RateLimitError

from programy.clients.client import BotClient
from programy.config.sections.client.twitter import TwitterConfiguration

class TwitterBotClient(BotClient):

    def __init__(self, argument_parser=None):
        self.clientid = "Twitter"
        BotClient.__init__(self, argument_parser)

    def set_environment(self):
        self.bot.brain.properties.add_property("env", "Twitter")

    def get_client_configuration(self):
        return TwitterConfiguration()

    def get_username(self, bot):
        self._username = bot.license_keys.get_key("TWITTER_USERNAME")
        self._username_len = len(self._username) # Going to get used quite a lot

    def get_consumer_secrets(self, bot):
        consumer_key = bot.license_keys.get_key("TWITTER_CONSUMER_KEY")
        consumer_secret = bot.license_keys.get_key("TWITTER_CONSUMER_SECRET")
        return consumer_key, consumer_secret

    def get_access_secrets(self, bot):
        access_token = bot.license_keys.get_key("TWITTER_ACCESS_TOKEN")
        access_token_secret = bot.license_keys.get_key("TWITTER_ACCESS_TOKEN_SECRET")
        return access_token, access_token_secret

    def create_api(self, consumer_key, consumer_secret, access_token, access_token_secret):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        return tweepy.API(auth)

    def initialise(self):
        self._welcome_message = self.configuration.client_configuration.welcome_message
        self.get_username(self.bot)
        consumer_key, consumer_secret = self.get_consumer_secrets(self.bot)
        access_token, access_token_secret = self.get_access_secrets(self.bot)
        self._api = self.create_api(consumer_key, consumer_secret,  access_token, access_token_secret)

    #############################################################################################
    # Direct Messages

    def get_direct_messages(self, last_message_id):
        if last_message_id == -1:
            if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug("Getting latest direct messages")
            messages = self._api.direct_messages()
        else:
            if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug("Getting latest direct messages since : %s" % last_message_id)
            messages = self._api.direct_messages(since_id=last_message_id)
        messages.sort(key=lambda msg: msg.id)
        return messages

    def process_direct_message_question(self, userid, text):
        if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug("Direct Messages: %s -> %s"%(userid, text))
        response = self.bot.ask_question(userid, text)
        self._api.send_direct_message(userid, text=response)

    def process_direct_messages(self, last_message_id):
        if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug ("Processing direct messages since [%s]"%last_message_id)

        messages = self.get_direct_messages(last_message_id)

        for message in messages:
            if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug("message: %s"% message.text)
            try:
                self.process_direct_message_question(message.sender_id, message.text)
            except Exception as err:
                if logging.getLogger().isEnabledFor(logging.ERROR): logging.error(err)

        if len(messages) > 0:
            last_message_id = messages[-1].id

        return last_message_id

    #############################################################################################
    # Followers

    def unfollow_non_followers(self, friends, followers_ids):
        for friend_id in friends:
            if friend_id not in followers_ids:
                if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug ("Removing previous friendship with [%d]"%(friend_id))
                self._api.destroy_friendship(friend_id)

    def follow_new_followers(self, followers, friends):
        for follower in followers:
            if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug ("Checking follower [%s]"%follower.screen_name)
            if follower.id not in friends:
                if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug("Following %s"%follower.screen_name)
                follower.follow()
                self._api.send_direct_message(follower.id, text=self._welcome_message)

    def process_followers(self):
        if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug("Processing followers")
        followers = self._api.followers()
        followers_ids = [x.id for x in followers]
        friends = self._api.friends_ids()

        # Unfollow anyone I follow that does not follow me
        self.unfollow_non_followers(friends, followers_ids)

        # Next follow those new fellows following me
        self.follow_new_followers(followers, friends)

    #############################################################################################
    # Status (Tweets)

    def get_statuses(self, last_status_id):
        if last_status_id == -1:
            if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug("Getting latest statuses")
            statuses = self._api.home_timeline()
        else:
            if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug("Getting latest statuses since : %s" % last_status_id)
            statuses = self._api.home_timeline(since_id=last_status_id)
        statuses.sort(key=lambda msg: msg.id)
        return statuses

    def get_question_from_text(self, text):
        if '@' not in text:
            return None

        text = text.strip()
        pos = text.find(self._username)
        if pos == -1:
            return None

        pos = pos - 1   # Take into account @ sign
        question = text[(pos+self._username_len)+1:]
        return question.strip()

    def process_status_question(self, userid, text):
        if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug("Status Update: %s -> %s"%(userid, text))

        question = self.get_question_from_text(text)
        if question is not None:
            if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug("%s -> %s"%(userid, question))

            response = self.bot.ask_question(userid, question)

            user = self._api.get_user(userid)
            status = "@%s %s"%(user.screen_name, response)

            if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug(status)
            self._api.update_status(status)

    def process_statuses(self, last_status_id):
        if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug ("Processing status updates since [%s]"%last_status_id)

        statuses = self.get_statuses(last_status_id)

        for status in statuses:
            print ("[%s] - [%s]"%(status.author.screen_name, self._username))
            if status.author.screen_name != self._username:
                if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug("status: %s" % status.text)
                try:
                    self.process_status_question(status.user.id, status.text)
                except Exception as err:
                    if logging.getLogger().isEnabledFor(logging.ERROR): logging.error(err)

        if len(statuses) > 0:
            last_status_id = statuses[-1].id

        return last_status_id

    #############################################################################################
    # Message ID Storage

    def get_last_message_ids(self):
        last_direct_message_id = -1
        last_status_id = -1

        if self.configuration.client_configuration.storage == 'file':
            if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug("Reads messages ids from [%s]" % self.configuration.client_configuration.storage_location)
            if os.path.exists(self.configuration.client_configuration.storage_location):
                try:
                    with open(self.configuration.client_configuration.storage_location, "r+") as idfile:
                        last_direct_message_id = int(idfile.readline().strip())
                        last_status_id = int(idfile.readline().strip())
                except Exception as e:
                    logging.exception(e)

        return (last_direct_message_id, last_status_id)

    def store_last_message_ids(self, last_direct_message_id, last_status_id):
        if self.configuration.client_configuration.storage == 'file':
            if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug("Writing messages ids to [%s]" % self.configuration.client_configuration.storage_location)
            try:
                with open(self.configuration.client_configuration.storage_location, "w+") as idfile:
                    idfile.write("%d\n"%last_direct_message_id)
                    idfile.write("%d\n"%last_status_id)
            except Exception as e:
                logging.exception(e)

    #############################################################################################
    # Execution

    def poll(self, last_direct_message_id, last_status_id):
        if self.configuration.client_configuration.use_direct_message is True:
            if self.configuration.client_configuration.auto_follow is True:
                self.process_followers()

            last_direct_message_id = self.process_direct_messages(last_direct_message_id)
            if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug(
                "Last message id = %d" % last_direct_message_id)

        if self.configuration.client_configuration.use_status is True:
            last_status_id = self.process_statuses(last_status_id)
            if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug("Last status id = %d" % last_status_id)

        self.store_last_message_ids(last_direct_message_id, last_status_id)

        time.sleep(self.configuration.client_configuration.polling_interval)

    def use_polling(self):

        print("Twitter client running as [%s]..."%self._username)

        (last_direct_message_id, last_status_id) = self.get_last_message_ids()

        running = True
        while running is True:
            try:
                self.poll(last_direct_message_id, last_status_id)

            except KeyboardInterrupt:
                running = False

            except RateLimitError as re:
                if logging.getLogger().isEnabledFor(logging.ERROR): logging.error("Rate limit exceeded, sleeping for 15 minutes")
                if self.configuration.client_configuration.poll_sleep != -1:
                    time.sleep(self.configuration.client_configuration.rate_limit_sleep)
                else:
                    time.sleep(15*60)

            except Exception as e:
                logging.exception(e)

        if logging.getLogger().isEnabledFor(logging.DEBUG): logging.debug("Exiting gracefully...")

    def use_streaming(self):
        raise NotImplemented("Streaming currently not supported in this release")

    def run(self):

        self.initialise()

        if self.configuration.client_configuration.polling is True:
            self.use_polling()
        elif self.configuration.client_configuration.streaming is True:
            self.use_streaming()
        else:
            if logging.getLogger().isEnabledFor(logging.ERROR): logging.error("No Twitter interactiong model specified in config ( polling or streaming )")

if __name__ == '__main__':

    def run():
        print("Loading Twitter client, please wait. See log output for progres...")
        twitter_app = TwitterBotClient()
        twitter_app.run()

    run()