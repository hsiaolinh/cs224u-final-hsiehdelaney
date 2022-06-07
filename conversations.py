#!/usr/bin/env python3

#!/usr/bin/env python3

"""Conversation class to present conversations from the LogoSearch corpus in a format
   convenient for pairwise interrogation."""

from pathlib import Path
from lxml import etree


class Conversation:
    def __init__(
        self, uuid, conversation_root=Path(__file__).parent / "logosearch-conversations"
    ):
        self.uuid = uuid
        self.conversation_root = Path(conversation_root)
        xml_path = self.conversation_root / f"{uuid}.xml"

        if not xml_path.exists():
            raise ValueError(f"Conversation {uuid} cannot be found!")

        with xml_path.open(encoding="utf8") as _fh:
            self.tree = etree.parse(_fh)

    @staticmethod
    def get_turn_text(turn):
        etree.strip_elements(turn, "note", with_tail=False)
        return etree.tostring(turn, encoding="unicode", method="text").strip()

    def get_speakers(self):
        """Return a dictionary of speakers in the conversation by UUID."""
        return {
            speaker.attrib["id"]: speaker.text for speaker in self.tree.find("speakers")
        }

    def get_turns(self):
        """Return a list of tuples (speaker, turn) for turns in the conversation."""
        speakers = self.get_speakers()
        discourse = self.tree.find("discourse")
        return [(speakers[turn.attrib["spkr"]], self.get_turn_text(turn)) for turn in discourse]

    def get_pairwise_turns(self):
        """Yield tuples (this_turn, next_turn) for pairs of turns in the conversation."""
        discourse = self.tree.find("discourse")

        # In Python >= 3.10 this could be done more efficiently and readably with
        #   from itertools import pairwise
        #   for this_turn, next_turn in pairwise(discourse):
        #       ...

        for this_turn, next_turn in zip(discourse, discourse[1:]):
            this_turn_text = self.get_turn_text(this_turn)
            next_turn_text = self.get_turn_text(next_turn)
            if this_turn_text and next_turn_text:
                yield (this_turn_text, next_turn_text)
