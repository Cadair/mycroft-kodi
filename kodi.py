"""
A helper library of functions for interacting with the Kodi JSON-RPC API.
"""
from __future__ import absolute_import, print_function, division


def find_films_matching(kodi, search):
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
    movies = kodi.VideoLibrary.GetMovies()['result']['movies']
    results = []
    for m in movies:
        if search in m['label'].lower():
            results.append(m)
    return results


def play_film(kodi, movieid):
    """
    Play a movie by id.
    """
    kodi.Playlist.Clear(playlistid=1)
    kodi.Playlist.Add(playlistid=1, item={'movieid': movieid})
    kodi.Player.Open(item={'playlistid': 1})


def stop_playback(kodi):
    players = kodi.Player.GetActivePlayers()['result']
    for player in players:
        kodi.Player.Stop(playerid=player['playerid'])


def playpause_playback(kodi):
    players = kodi.Player.GetActivePlayers()['result']
    for player in players:
        kodi.Player.PlayPause(playerid=player['playerid'])
