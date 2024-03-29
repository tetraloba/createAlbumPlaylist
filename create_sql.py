import glob
from os import path
import datetime

from mutagen.flac import FLAC
from mutagen.mp3 import MP3

# root_dir_path = "../musicServer/src/music"
playlist_dir_path = "../musicServer/src/playlists"
# playlist_dir_path = "../playlists2"

# コマンドライン引数が有ればコマンドライン引数のパス、なければカレントディレクトリから。 #todo
root_dir_path = "./"
# デバッグ用
root_dir_path = "../musicServer/src/music"

# SQL用にシングルクォートをエスケープ処理する
def escape_sq(s:str):
    return s.replace("'", "''")

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
with open(path.join(playlist_dir_path, 'insert_albums' + '.sql'), "w") as f:
    f.write("INSERT INTO albums VALUES \n")
    first = True
    for album, tracks in albums.items():
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
        album = escape_sq(album)
        album_artist = escape_sq(album_artist)
        if album_year != '':
            album_year = "'" + str(datetime.date(int(album_year), 1, 1)) + "'"
        else:
            album_year = 'NULL'
        album_length = str(datetime.timedelta(seconds=int(album_length)))
        if not first:
            f.write(',\n')
        first = False
        f.write("("
                f"'{album}',"
                f"'{album_artist}',"
                f"{album_track_total},"
                f"{album_year},"
                f"'{album_length}',"
                "DEFAULT"
                ")")
            # f.write(audio + '\n')
    f.write(";\n")


with open(path.join(playlist_dir_path, 'insert_audios' + '.sql'), 'w') as f:
    f.write("INSERT INTO audio_meta VALUES \n")
    first = True
    for flac_file in flac_file_list:
        tags = FLAC(flac_file).tags
        if not first:
            f.write(',\n')
        first = False
        # メタデータに含まれるアポストロフィをエスケープ処理
        title = escape_sq(str(tags['title'][0]))
        artist = escape_sq(str(tags['artist'][0]))
        album = escape_sq(str(tags['album'][0]))
        file_path = escape_sq(flac_file)
        length = str(datetime.timedelta(seconds=int(FLAC(flac_file).info.length)))
        # SQL文を書き込み
        f.write("("
                f"'{title}',"
                f"'{artist}',"
                f"{tags['tracknumber'][0]},"
                f"'{album}',"
                f"'{length}',"
                "'flac',"
                f"'{file_path}'"
                ")")
    for mp3_file in mp3_file_list:
        tags = MP3(mp3_file).tags
        if not first:
            f.write(',\n')
        first = False
        # メタデータに含まれるアポストロフィをエスケープ処理
        title = escape_sq(str(tags['TIT2'][0]))
        artist = escape_sq(str(tags['TPE1'][0]))
        album = escape_sq(str(tags['TALB'][0]))
        file_path = escape_sq(mp3_file)
        length = str(datetime.timedelta(seconds=int(MP3(mp3_file).info.length)))
        # SQL文を書き込み
        f.write("("
                f"'{title}',"
                f"'{artist}',"
                f"{str(tags['TRCK'][0]).split('/')[0]},"
                f"'{album}',"
                f"'{length}',"
                "'mp3',"
                f"'{file_path}'"
                ")")
    f.write(';\n')
