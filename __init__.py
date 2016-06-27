from __future__ import absolute_import, print_function

from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from kodipydent import Kodi
import kodi

_author__ = 'Stuart Mumford'

LOGGER = getLogger(__name__)


class KodiSkill(MycroftSkill):
    """
    A Skill to control playback on a Kodi instance via the json-rpc interface.
    """

    def __init__(self):
        super(KodiSkill, self).__init__(name="KodiSkill")

        self.kodi = Kodi('10.21.5.180')

    def initialize(self):
        self.load_data_files(dirname(__file__))

        self.register_regex("film (?P<Film>.*)")
        self.register_regex("movie (?P<Film>.*)")
        self.register_regex("with (?P<Film>.*)")
        self.register_regex("containing (?P<Film>.*)")
        self.register_regex("matching (?P<Film>.*)")
        self.register_regex("including (?P<Film>.*)")

        self.build_play_film_intent()
        self.build_film_search_intent()

    def build_play_film_intent(self):
        play_films_intent = IntentBuilder("PlayFilmsIntent").require("PlayFilmKeywords").require("Film").build()

        self.register_intent(play_films_intent,
                             self.handle_play_film_intent)

    def handle_play_film_intent(self, message):
        kodi.play_film_by_search(self.kodi, message.metadata['Film'])

    def build_film_search_intent(self):
        find_films_intent = IntentBuilder("SearchFilmsIntent").require("SearchFilmKeywords").require("Film").build()

        self.register_intent(find_films_intent, self.handle_film_search_intent)

    def handle_film_search_intent(self, message):
        results = kodi.find_films_matching(self.kodi, message.metadata['Film'])
        self.speak_multi_film_match(message.metadata['Film'], results)

    def build_stop_intent(self):
        stop_intent = IntentBuilder("StopIntent").require("StopKeywords").build()
        self.register_intent(stop_intent, self.handle_stop_intent)

    def handle_stop_intent(self, message):
        kodi.stop_playback()

    def build_playpause_intent(self):
        playpause_intent = IntentBuilder("PlayPauseIntent").require("PlayPauseKeywords").build()
        self.register_intent(playpause_intent, self.handle_playpause_intent)

    def handle_playpause_intent(self, message):
        kodi.playpause_playback()

    # Mycroft Actions, speaking etc. #
    def speak_multi_film_match(self, search, results):
        """
        Tell the user about a list of results.
        """
        output = "I found the following movies matching {}: ".format(search)
        for film in results:
            output += "{}, ".format(film['label'])

        self.speak(output)

    def play_film_by_search(self, film_search):
        """
        Search for films using the query, then play if only one result,
        otherwise tell the user about the results.

        Parameters
        ----------

        mycroft : `MycroftSkill` instance
            The current Mycroft instance.

        film_search : `string` A string to search the library for.
        """
        results = kodi.find_films_matching(film_search)
        if len(results) == 1:
            kodi.play_film(results[0]['movieid'])
        elif len(results):
            self.speak_multi_film_match(film_search, results)
        else:
            self.speak("I found no results for the search: {}.".format(film_search))

    def stop():
        pass


def create_skill():
    return KodiSkill()
