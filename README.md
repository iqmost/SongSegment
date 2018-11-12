SongSegment
=============================
把整首歌根據歌詞檔切成逐字音檔。
* 執行前建議先確定一下output的directory跟name是否正確。

    ``fold + "/" + fold.split('/')[-1] + ".csv"``

    ``segment.export(save_path + "/" + save_name)``


Note
----
    l = Lyric(lyric_name)
``lyric_name``傳入參照的歌詞檔位置

    song_split(song_dir, l.seq)
    
``song_split()``實作切割

``song_dir``傳入放歌曲的目錄位置，切割出來的音檔、CSV檔，都會放置於此


    word_to_csv(song_dir, l.seq)
    
``word_to_csv()``產出CSV檔
