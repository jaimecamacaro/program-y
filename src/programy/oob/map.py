import logging
import xml.etree.ElementTree as ET

from programy.oob.oob import OutOfBandProcessor

"""
<oob>
    <map>Kinghorn</map>
</oob>
"""
class MapOutOfBandProcessor(OutOfBandProcessor):

    def __init__(self):
        OutOfBandProcessor.__init__(self)
        self._location = None

    def parse_oob_xml(self, oob: ET.Element):
        if oob is not None and oob.text is not None:
            self._location = oob.text
            return True
        else:
            if logging.getLogger().isEnabledFor(logging.ERROR): logging.error("Unvalid map oob command - missing location text!")
            return False

    def execute_oob_command(self, bot, clientid):
        if logging.getLogger().isEnabledFor(logging.INFO): logging.info("MapOutOfBandProcessor: Showing a map for location=%s", self._location)
        return "MAP"
