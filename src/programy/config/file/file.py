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

from abc import ABCMeta, abstractmethod


class BaseConfigurationFile(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def load_from_text(self, text, bot_root):
        """
        Never Implemented
        """
        raise NotImplemented()

    @abstractmethod
    def load_from_file(self, filename, bot_root):
        """
        Never Implemented
        """
        raise NotImplemented()

    @abstractmethod
    def get_section(self, section_name, parent_section=None):
        """
        Never Implemented
        """
        raise NotImplemented()

    @abstractmethod
    def get_keys(self, child_section):
        """
        Never Implemented
        """
        raise NotImplemented()

    @abstractmethod
    def get_child_section_keys(self, section_name, parent_section):
        """
        Never Implemented
        """
        raise NotImplemented()

    @abstractmethod
    def get_option(self, section, option_name, missing_value=None):
        """
        Never Implemented
        """
        raise NotImplemented()

    @abstractmethod
    def get_multi_line_option(self, section, option_name, missing_value=[]):
        """
        Never Implemented
        """
        raise NotImplemented()

    @abstractmethod
    def get_multi_file_option(self, section, option_name, missing_value=[]):
        """
        Never Implemented
        """
        raise NotImplemented()

    def convert_to_bool(self, value):
        if value.upper() == 'TRUE':
            return True
        elif value.upper() == 'FALSE':
            return False
        else:
            raise Exception("Invalid boolean config value [%s]"%value)

    def convert_to_int(self, value):
        if value.isdigit():
            return int(value)
        else:
            raise Exception("Invalid integer config value [%s]"%value)

