import logging
import xml.etree.ElementTree as ET

from programy.oob.oob import OutOfBandProcessor

"""
<oob>
    <url>http://<star/>.com</url>
</oob>
"""

class URLOutOfBandProcessor(OutOfBandProcessor):

    def __init__(self):
        OutOfBandProcessor.__init__(self)
        self._url = None

    def parse_oob_xml(self, oob: ET.Element):
        if oob is not None and oob.text is not None:
            self._url = oob.text
            return True
        else:
            if logging.getLogger().isEnabledFor(logging.ERROR): logging.error("Unvalid url oob command - missing url!")
            return False

    def execute_oob_command(self, bot, clientid):
        if logging.getLogger().isEnabledFor(logging.INFO): logging.info("URLOutOfBandProcessor: Loading=%s", self._url)
        return "URL"
