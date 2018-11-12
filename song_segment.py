import os
import csv
import time
import shutil
from lyric import Lyric
from pypinyin import pinyin, Style
from pydub import AudioSegment
from collections import defaultdict


def word_segment(full_seq):
    # 回傳每個字的開始時間、結束時間
    # lst = [[0 for _ in range(2)] for _ in range(len(seq))]
    lst = []
    for s in full_seq:
        lst.append([s[0], s[0] + s[1]])
    return lst
    # lst [ #of word ] [ 0 for start, 1 for end ]


def mp3_folder():
    # 把mp3檔，用新的資料夾裝起來，檔名相同。
    target_dir = "SongSegment/未整理"
    all_name = os.listdir(target_dir)
    print(all_name)
    for i in range(len(all_name)):
        ndir_name = target_dir + all_name[i].replace(".mp3", "")
        if not os.path.exists(ndir_name):
            os.makedirs(ndir_name)
        shutil.move(target_dir + all_name[i], ndir_name)
        print(all_name[i])

    return print("folder Done.")


def word_to_csv(fold, full_seq):
    # 把每個字的資訊記錄成.csv
    with open(fold + "/" + fold.split('/')[-1] + ".csv", 'w', newline='') as csvfile:

        writer = csv.writer(csvfile)
        writer.writerow(['# of words', 'duration', 'word', 'pinyin'])
        timing = word_segment(full_seq)

        pinyins = []
        for i in full_seq:
            pinyins.append(i[2][0])
        pinyins = "".join(pinyins)
        pinyins = pinyin(pinyins, style=Style.BOPOMOFO)

        a = 0
        for i in full_seq:
            a = a + 1
            num_of_word = str(a).zfill(3)
            duration = timing[a-1][1] - timing[a-1][0]
            word = i[2][0]
            zhuyin = ""
            try:
                if Lyric.is_chinese(pinyins[a-1][0]):
                    zhuyin = pinyins[a-1][0]
            except IndexError:
                zhuyin = ""
                print("\r★★★ValueError，歌詞出現非中文字符")
            try:
                writer.writerow([num_of_word, duration, word, zhuyin])
            except UnicodeEncodeError:
                print("★★★'cp950' codec can't encode character 'u5227' in position 8: illegal multibyte sequence")

        return print(".csv Done.")


def song_split(fold, full_seq):
    file_name = fold + "/" + fold.split('/')[-1] + ".mp3"
    sound = AudioSegment.from_mp3(file_name)
    timing = word_segment(full_seq)

    a = 0
    for i in full_seq:
        save_name = str(a+1).zfill(3) + "." + i[2][0] + ".mp3"
        save_path = fold
        segment = sound[timing[a][0]:timing[a][1]]
        a = a+1
        segment.export(save_path + "/" + save_name)
        # print(save_path + "/" + save_name)

        p = float("{0:.2f}".format(a / len(full_seq)*100))
        print('\r' + "單首切割進度" + str(p) + "%", end='')

    return print("\nSplit Done.")


def choose_lyric(song_fold, lyc_fold):
    lyric_dict = defaultdict(lambda: ["", 0])
    song_id = song_fold.split('_')[-3]
    for index, name in enumerate(os.listdir(lyc_fold)):
        if name.split('_')[0] == song_id:
            filename = lyc_fold + "/" + str(name)
            content = "".join(str(s) for T in Lyric(filename).seq for s in T)
            lyric_dict[content] = [lyric_dict[content][0] + "," + str(index), lyric_dict[content][1] + 1]
    try:
        indexes = max(lyric_dict.values(), key=lambda v: v[1])[0].split(',')[1:]
    except ValueError:
        print("★★★Value Error，研判是因為沒有歌詞檔")
    names = [os.listdir(lyc_fold)[int(index)] for index in indexes]
    chosen_name = max(names, key=lambda _: len(_))
    print("From %d files chose \"%s.\"" % (len(names), chosen_name))

    return chosen_name


start_time = time.time()

lyric_dir = "SongSegment/lyric"
for i in os.listdir("SongSegment/未整理"):
    song_dir = "SongSegment/未整理/" + i
    print(song_dir)
    lyric_name = lyric_dir + "/" + choose_lyric(song_dir, lyric_dir)
    l = Lyric(lyric_name)
    song_split(song_dir, l.seq)
    word_to_csv(song_dir, l.seq)

end_time = time.time()
print("運行時間：%d 秒" % (end_time-start_time))
