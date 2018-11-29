import os
import csv
import time
import shutil
from lyric import Lyric
from pypinyin import pinyin, Style
from pydub import AudioSegment
from collections import defaultdict

global zhuyin_dict

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

    print("folder Done.")
    return


def word_to_csv(fold, full_seq):
    # 把每個字的資訊記錄成.csv
    with open(fold + "/" + fold.split('/')[-1] + ".csv", 'w', newline='') as csvfile:

        # writer = csv.writer(csvfile)
        # writer.writerow(['# of words', 'duration', 'word', 'pinyin'])
        timing = word_segment(full_seq)

        pinyins = []
        for i in full_seq:
            if i[2][0] == "":
                pinyins.append(" ")
            else:
                pinyins.append(i[2][0])
        pinyins = "".join(pinyins)
        temp = []
        for each in pinyins:
            if len(each) == 1:
                temp.append(each)
            else:
                for _ in each:
                    temp.append(_)
        pinyins = temp
        pinyins = pinyin(pinyins, style=Style.BOPOMOFO)

        # 不考慮音調start
        # for count, i in enumerate(pinyins):
        #     pinyins[count][0] = pinyins[count][0].replace('ˊ', '')
        #     pinyins[count][0] = pinyins[count][0].replace('ˇ', '')
        #     pinyins[count][0] = pinyins[count][0].replace('ˋ', '')
        #     pinyins[count][0] = pinyins[count][0].replace('˙', '')
        # 不考慮音調end

        for count, i in enumerate(full_seq):
            num_of_word = str(count+1).zfill(3)
            duration = timing[count][1] - timing[count][0]
            word = i[2].replace(' ', '')
            # print(word + str(count))
            # print(pinyins[count][0])
            if Lyric.is_chinese(word):
                zhuyin = pinyins[count][0]
            else:
                zhuyin = ""

            zhuyin_dict[zhuyin] = [zhuyin_dict[zhuyin][0], zhuyin_dict[zhuyin][1] + 1]

            # try:
            #     writer.writerow([num_of_word, duration, word, zhuyin])
            # except UnicodeEncodeError:
            #     print("★★★★★★★★★")

        print(".csv Done.")
        return


def song_split(fold, full_seq):
    file_name = fold + "/" + fold.split('/')[-1] + ".mp3"
    sound = AudioSegment.from_mp3(file_name)
    timing = word_segment(full_seq)

    for count, i in enumerate(full_seq):
        save_name = str(count).zfill(3) + "." + i[2][0] + ".mp3"
        save_path = fold
        if os.path.isfile(save_path + "/" + save_name):
            print("【Note: 應該轉過檔囉！】")
            return
        segment = sound[timing[count-1][0]:timing[count-1][1]]
        segment.export(save_path + "/" + save_name)

        p = float("{0:.2f}".format(count / len(full_seq)*100))
        print('\r' + "單首切割進度" + str(p) + "%", end='')

    print("\nSplit Done.")
    return


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
        return False
    names = [os.listdir(lyc_fold)[int(index)] for index in indexes]
    chosen_name = max(names, key=lambda _: len(_))
    # print("From %d files chose \"%s.\"" % (len(names), chosen_name))

    return chosen_name


start_time = time.time()

zhuyin_dict = defaultdict(lambda: ["", 0])
lyric_dir = "SongSegment/lyric"
process = 1
for count, file_name in enumerate(os.listdir("SongSegment/未整理")):
    process += 1
    if file_name == "desktop.ini":
        continue
    song_dir = "SongSegment/未整理/" + file_name
    print(song_dir)
    if choose_lyric(song_dir, lyric_dir):
        lyric_name = lyric_dir + "/" + choose_lyric(song_dir, lyric_dir)
    l = Lyric(lyric_name)
    # song_split(song_dir, l.seq)
    word_to_csv(song_dir, l.seq)
    length = len(os.listdir("SongSegment/未整理"))


    print("總共%d首歌，已處理%d首歌" % (length, process))
print(sorted(zhuyin_dict.items(), key=lambda d: d[1], reverse=True))
print(len(zhuyin_dict))
end_time = time.time()
print("運行時間：%d 秒" % (end_time-start_time))

# zhuyin_dict = {}
# for file_name in os.listdir("SongSegment/未整理"):
#     if file_name == "desktop.ini":
#         continue
#     sid = file_name.split('_')[1]
#     zhuyin_dict[sid] = zhuyin_dict.get(sid, 0) + 1
# print(sorted(zhuyin_dict.items(), key=lambda d: d[1], reverse=True))
# print(len(zhuyin_dict))
