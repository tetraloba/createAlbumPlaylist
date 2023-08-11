from os import listdir, path

from mutagen.flac import FLAC
from mutagen.mp3 import MP3

# ./Artist/Album/Audio.flac と仮定する。
audio_exts = ['mp3', 'flac']

def create_playlist(album_path):
    playlist = ""
    audio_files = [path.join(album_path, audio_file) for audio_file in listdir(album_path) if path.splitext(audio_file)[1][1:] in audio_exts]
    audio_files_dict = dict()
    for audio_file in audio_files:
        if path.splitext(audio_file)[1][1:] == 'mp3':
            audio_files_dict[int(str(MP3(audio_file).tags['TRCK']).split('/')[0])] = audio_file
        else:
            audio_files_dict[int(FLAC(audio_file).tags['tracknumber'][0])] = audio_file
    audio_files_sorted = sorted(audio_files_dict.items())
    for audio_file in audio_files_sorted:
        playlist += audio_file[1].replace(root_dir_path + '/', '') + "\n"
            # replace, 100%上手く行く保証は有るか？ パス中に../なんて出てこないか。
            # こういう文字列操作って効率悪かった気もする。
    return playlist

root_dir_path = "../musicServer/src/music"
playlist_dir_path = "../musicServer/src/playlists"

artists = [i for i in listdir(root_dir_path) if '.' not in i]
for artist in artists:
    artist_path = path.join(root_dir_path, artist)
    albums = listdir(artist_path)
    for album in albums:
        with open(path.join(playlist_dir_path, album + '.m3u'), "w") as f:
            print(album)
            f.write(create_playlist(path.join(artist_path, album)))
