from __future__ import absolute_import

from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from kodipydent import Kodi

_author__ = 'Stuart Mumford'

LOGGER = getLogger(__name__)


class KodiSkill(MycroftSkill):
    """
    A Skill to control playback on a Kodi instance via the json-rpc interface.
    """

    def __init__(self):
        super(KodiSkill, self).__init__(name="KodiSkill")

        self.kodi = Kodi('10.21.5.254')

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
        self.play_film_by_search(message.metadata['Film'])

    def build_film_search_intent(self):
        find_films_intent = IntentBuilder("SearchFilmsIntent").require("SearchFilmKeywords").require("Film").build()

        self.register_intent(find_films_intent, self.handle_film_search_intent)

    def handle_film_search_intent(self, message):
        results = self.find_films_matching(message.metadata['Film'])
        self.speak_multi_film_match(message.metadata['Film'], results)

    def find_films_matching(self, search):
        """
        Search the movie database for all the films matching a string.

        Parameters
        ----------

        Kodi : `beekeeper.api.API`
            The current Kodi connection.

        search : `search`
            The search string

        Returns
        -------

        results: `list`
            All the results matching the search.
            (list of 'label', 'movieid' dicts.)
        """
        movies = self.kodi.VideoLibrary.GetMovies()['result']['movies']
        results = []
        for m in movies:
            if search in m['label'].lower():
                results.append(m)
        return results

    def speak_multi_film_match(self, search, results):
        """
        Tell the user about a list of results.
        """
        output = "I found the following movies matching {}: ".format(search)
        for film in results:
            output += "{}, ".format(film['label'])

        self.speak(output)

    def play_film(self, movieid):
        """
        Play a movie by id.
        """
        self.kodi.Playlist.Clear(playlistid=1)
        self.kodi.Playlist.Add(playlistid=1, item={'movieid': movieid})
        self.kodi.Player.Open(item={'playlistid': 1})

    def play_film_by_search(self, film_search):
        """
        Search for films using the query, then play if only one result,
        otherwise tell the user about the results.
        """
        results = self.find_films_matching(film_search)
        if len(results) == 1:
            self.play_film(results[0]['movieid'])
        elif len(results):
            self.speak_multi_film_match(film_search, results)
        else:
            self.speak("I found no results for the search: {}.".format(film_search))

    def stop():
        pass


def create_skill():
    return KodiSkill()
