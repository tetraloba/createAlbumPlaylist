import glob
from os import path

from mutagen.flac import FLAC
from mutagen.mp3 import MP3

# root_dir_path = "../musicServer/src/music"
# playlist_dir_path = "../musicServer/src/playlists"
playlist_dir_path = "../playlists2"

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
    with open(path.join(playlist_dir_path, album + '.m3u'), "w") as f:
        for number, audio in sorted(tracks.items()):
            f.write(audio + '\n')

