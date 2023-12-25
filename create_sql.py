import glob
from os import path
import datetime

from mutagen.flac import FLAC
from mutagen.mp3 import MP3

# root_dir_path = "../musicServer/src/music"
playlist_dir_path = "../musicServer/src/playlists"
# playlist_dir_path = "../playlists2"

# コマンドライン引数が有ればコマンドライン引数のパス、なければカレントディレクトリから。
root_dir_path = "./"
# デバッグ用
root_dir_path = "../musicServer/src/music"

# {album:{track_num:auido}}
albums = dict()

# FLACファイルを取得・解析してalbumsに登録
flac_file_list = glob.glob('**/*.flac', recursive=True)
for flac_file in flac_file_list:
    albums[str(FLAC(flac_file).tags['album'][0])] = {**albums.get(str(FLAC(flac_file).tags['album'][0]), dict()) , **{int(FLAC(flac_file).tags['tracknumber'][0]):flac_file}}
# mp3ファイルを取得・解析してalbumsに登録
mp3_file_list = glob.glob('**/*.mp3', recursive=True)
for mp3_file in mp3_file_list:
    albums[str(MP3(mp3_file).tags['TALB'][0])] = {**albums.get(str(MP3(mp3_file).tags['TALB'][0]), dict()), **{int(str(MP3(mp3_file).tags['TRCK'][0]).split('/')[0]):mp3_file}}

# albumsに基づいてプレイリストを書き出し
for album, tracks in albums.items():
    with open(path.join(playlist_dir_path, album.replace('/', '_') + '.sql'), "w") as f:
        album_artist = ''
        album_track_total = 0
        album_year = 0
        album_length = 0
        for number, audio in sorted(tracks.items()):
            if audio[-1] == 'c': # FLAC
                tags = FLAC(audio).tags
                if tags.get('albumartist', None):
                    album_artist = str(tags['albumartist'][0])
                else:
                    album_artist = str(tags['artist'][0])
                if tags.get('tracktotal', None):
                    album_track_total = int(tags['tracktotal'][0])
                else:
                    album_track_total = max(int(tags['tracknumber'][0]), len(tracks), album_track_total)
                album_year = str(tags['date'][0])
                album_length += float(str(FLAC(audio).info.length))
            elif audio[-1] == '3': #MP3
                tags = MP3(audio).tags
                if tags.get('TPE2', None):
                    album_artist = str(tags['TPE2'][0])
                else:
                    album_artist = str(tags['TPE1'][0])
                if 2 <= len(str(tags['TRCK'][0]).split('/')):
                    album_track_total = int(str(tags['TRCK'][0]).split('/')[1])
                else:
                    album_track_total = max(int(str(tags['TRCK'][0]).split('/')[0]), len(tracks), album_track_total)
                album_year = str(tags['TDRC'][0])
                album_length += float(str(MP3(audio).info.length))
        if len(tracks) < album_track_total:
            print(f"トラック数が不足。 {album}: {len(tracks)}/{album_track_total}")
        album = album.replace("'", "\\'")
        album_artist = album_artist.replace("'", "\\'")
        if album_year != '':
            album_year = "'" + str(datetime.date(int(album_year), 1, 1)) + "'"
        else:
            album_year = 'NULL'
        album_length = str(datetime.timedelta(seconds=int(album_length)))
        f.write("INSERT INTO albums VALUES (\n"
                f"\t'{album}',\n"
                f"\t'{album_artist}',\n"
                f"\t{album_track_total},\n"
                f"\t{album_year},\n"
                f"\t'{album_length}',\n"
                "\tDEFAULT\n"
                ");\n")
            # f.write(audio + '\n')

