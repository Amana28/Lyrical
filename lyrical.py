import os
import pprint
import requests
import lyricsgenius
import pandas as pd
import sqlalchemy as db
from pandas import option_context


# LYRICAL.OVH API
def get_lyrics():
    """This function prints lyrics of a song given the artist name and
    song title """
    artist = input("Enter artist name: ").capitalize()
    title = input("Enter song title: ").capitalize()

    base_url = 'https://api.lyrics.ovh/v1/'
    url = base_url + artist + "/" + title

    response = requests.get(url)
    print(response)

    lyrics = response.json()
    l_values = lyrics.values()

    for line in l_values:
        print(line)


# GENIUS API
token = "pN39MdQbjguuvRXwSxcZ9FuPYb5zh-DzG_QT5qTME7NWwhZHRiLzeHDUUP8dK1_7"
genius = lyricsgenius.Genius(token)


def get_artist_data(artist_name, max_songs):
    """This function returns a dictionary containing data for multiple
     songs given artist name and maximum number of songs"""
    artist = genius.search_artist(artist_name, max_songs, sort="popularity")
    artist_dict = artist.to_dict()
    return artist_dict


def dict_to_df_to_db(artist_dictionary):
    """Creates a database from a dictionary containing artist info"""
    songs_list = artist_dictionary['songs']
    data = {}
    for songs_dict in songs_list:
        for element in songs_dict:
            print(element)
        data[songs_dict['title']] = [songs_dict["id"], songs_dict["title"],
                                     songs_dict["artist_names"],
                                     songs_dict["album"]["name"],
                                     songs_dict["song_art_image_url"],
                                     songs_dict["release_date"]]
    df = pd.DataFrame.from_dict(data, orient='index')
    engine = db.create_engine('sqlite:///artist_info.db')
    df.to_sql("Artist_Information", con=engine, if_exists='replace',
              index=False)
    query_result = engine.execute("SELECT * \
    FROM Artist_Information;").fetchall()
    data_frame = pd.DataFrame(query_result)
    data_frame.columns = ["SONG_ID", "TITLE", "ARTISTS", "ALBUM", "ALBUM_ART",
                          "RELEASED"]
    return data_frame


def multiply(num1, num2):
    return num1 * num2


def get_frequency(given_word, artist_data):
    total_lyrics = ""
    for songs_dict in artist_data['songs']:
        total_lyrics += songs_dict["lyrics"]
    counter = 0
    for word in total_lyrics.split():
        if word.lower() == given_word:
            counter += 1
    return counter


def main():
    print("\n")
    print("Would you rather get lyrics for a specific song or get information \
about multiple songs")
    print("Enter 1 for a specific song")
    print("Enter 2 to get information about multiple songs by an artist")
    user_input = input("Input: ")
    if user_input == "1":
        get_lyrics()
    elif user_input == "2":
        artist_name = input("Enter artist name: ").capitalize()
        max_songs = int(input(f"How many songs of {artist_name} do \
you want?: "))
        artist_data = get_artist_data(artist_name, max_songs)
        df = dict_to_df_to_db(artist_data)
        with option_context('display.max_colwidth', 100):
            print(df)
        print("\n")
        answer = input("Would you like the lyrics to any of these songs \
(type y/n): ").lower()
        if answer == 'y':
            song_name = input(f"Which of {artist_name}'s songs do you want \
the lyrics to? ").lower()
            print("\n")
            for song in artist_data['songs']:
                if song["title"].lower() == song_name:
                    pprint.pprint(song['lyrics'])
                    print()
                    print("Thank you, Bye!!")
                else:
                    print("Song Not Found!")
        ans = input("Would you like to get the frequency of a specific word \
in the above songs? (Enter y/n): ").lower()
        if ans == 'y':
            word = input("Enter the word: ")
            frequency = get_frequency(word, artist_data)
            print(f"\nThe word {word} appears {frequency} times in the \
above {max_songs} songs.")
            print("\nThanks for using our Program!")
        else:
            print("Thank You, Good Bye!")


if __name__ == "__main__":
    main()
