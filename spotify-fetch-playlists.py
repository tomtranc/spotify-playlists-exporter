# Spotify Fetch all playlist
import sys
import json
import requests
from requests.exceptions import HTTPError
from datetime import date
 
# global vars
spotifyHost = "https://api.spotify.com"
userId = sys.argv[1]
token = sys.argv[2]
file = f"spotify-playlists-{date.today()}.txt"

# functions
def sendRequest(url) :
    try:
        response = requests.get(url, headers = {"Authorization": "Bearer " + token});
        response.raise_for_status()
        return response.json() # convert to JSON

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err} {response.text}')
    except Exception as err:
        print(f'Other error occurred: {err} {response.text}')
    return requests.get(url, headers = {"Authorization": "Bearer " + token});

def getPlaylists(limit, offset) :
    return sendRequest(f"{spotifyHost}/v1/users/{userId}/playlists?limit={limit}&offset={offset}");

def getSongs(playlistId, limit, offset) :
    return sendRequest(f'{spotifyHost}/v1/playlists/{playlistId}/tracks?limit={limit}&offset={offset}');

def getArtist(song) :
    artists = [];
    for artist in song['track']['artists'] :
        artists.append(artist['name'])
    return ';'.join(artists)

def writeCsvFile(song) :
    artist = str(getArtist(song))
    print("Writing: " + song['track']['name'] + "\tartists: " + artist)
    f = open(file, "a", encoding = "utf-8")
    f.write(f"{playlistName} | {playlistId} | {artist} | {song['track']['name']} | {song['track']['album']['name']}\n")
    f.close()

def fetchSongsFromPlaylistId(tracks) :
    totalSongsWritten = 0
    # print(f'Playlist Name: {jsonResponse["name"]}\t Id: {jsonResponse["id"]}')
    for song in tracks['items'] :
        # print(f"{getArtist(song)}, {song['track']['name']}, Album: {song['track']['album']['name']}")
        writeCsvFile(song)
        totalSongsWritten += 1

    if tracks['next'] != None :
        nextTracks = sendRequest(tracks['next'])
        totalSongsWritten += fetchSongsFromPlaylistId(nextTracks)

    return totalSongsWritten

print('userId:\t' + userId)
print('token:\t' + token)

# Main
if __name__ == "__main__" :
    # fetch playlists
    # TODO handles more than 50 playlists
    jsonResponse = getPlaylists(50, 0)

    # init file with headers
    f = open(file, "w", encoding = "utf-8")
    f.write(f"Playlist | PlaylistId | Artists | Song Title | Album\n")
    f.close()

    # traverse and get all playlist and tracks
    totalSongsAll = 0
    totalSongsByOwner = 0
    totalSongsExported = 0
    for playlist in jsonResponse['items']:
        totalSongsAll += playlist['tracks']['total']
        if playlist['owner']['id'] == userId:
            tracks = getSongs(playlist["id"], 100, 0)
            playlistName = playlist['name']
            playlistId = playlist['id']
            totalSongsByOwner += playlist['tracks']['total']
            totalSongsExported += fetchSongsFromPlaylistId(tracks)

    print(f"Total Songs By all: " + str(totalSongsAll))
    print(f"Total Songs Saved By Onwer: " + str(totalSongsByOwner))
    print(f"Total Songs Exported: " + str(totalSongsExported))
    if totalSongsByOwner != totalSongsExported :
        print(f"Number of songs exported {totalSongsExported} did not match with number of songs in Spotify {totalSongsByOwner}!! Verify again")
