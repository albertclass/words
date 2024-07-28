'''
程序思想：
有两个本地语音库，美音库Speech_US，英音库Speech_US
调用有道api，获取语音MP3，存入对应的语音库中
'''

import os
import sqlite3
import urllib.request
import time
class youdao():
    def __init__(self, type: int = 1, rootpath: str = './'):
        '''
        调用youdao API
        type = 0：美音
        type = 1：英音

        判断当前目录下是否存在两个语音库的目录
        如果不存在，创建
        '''
        self._type = type  # 发音方式

        # 文件根目录
        self._dirRoot = os.path.abspath(rootpath)
        if 0 == self._type:
            self._dirSpeech = os.path.join(self._dirRoot, "phonetic", 'us')  # 美音库
        else:
            self._dirSpeech = os.path.join(self._dirRoot, "phonetic", 'en')  # 英音库

        # 判断是否存在美音库
        if not os.path.exists(self._dirSpeech):
            # 不存在，就创建
            os.makedirs(self._dirSpeech)

    def down(self, word) -> str | None:
        '''
        下载单词的MP3
        判断语音库中是否有对应的MP3
        如果没有就下载
        '''
        word = word.lower()  # 小写
        if not word.isprintable():
            return None
        
        word = word.replace(' ', '+')
        word = word.replace('.', '')
       # split word to list, each two letters a group
        subdirs = []
        if len(word) > 0:
            subdirs.append(word[0])
            
        if len(word) > 1:
            subdirs.append(word[1:3])
            
        if len(word) > 3:
            subdirs.append(word[3:7])
            
        if len(word) > 7:
            subdirs.append(word[7:12])
        
        filepath_old = os.path.join(self._dirSpeech, *subdirs[:2], word[7:], f"{word}.mp3")
        filepath = os.path.join(self._dirSpeech, *subdirs, f"{word}.mp3")
        
        if os.path.exists(filepath_old):
            # 如果存在旧文件，就移动到新文件夹
            os.rename(filepath_old, filepath)
            # 删除空文件夹
            if os.path.exists(os.path.dirname(filepath_old)) and len(os.listdir(os.path.dirname(filepath_old))) == 0:
                os.rmdir(os.path.dirname(filepath_old))
                
        if not os.path.exists(filepath):
            # 如果不存在，就下载
            if os.path.exists(os.path.dirname(filepath)) == False:
                # 如果目录不存在，就创建
                os.makedirs(os.path.dirname(filepath))
                
            urlpath = 'http://dict.youdao.com/dictvoice?type=' + str(self._type) + '&audio=' + word.replace('+', '%20')
            # 调用下载程序，下载到目标文件夹
            # print('不存在 %s.mp3 文件\n将URL:\n' % word, self._url, '\n下载到:\n', self._filePath)
            # 下载到目标地址
            urllib.request.urlretrieve(urlpath, filename=filepath)
            print(f"下载完成 {word}.mp3, 保存位置：{filepath}")
        else:
            print(f'已经存在 {word}.mp3, 保存位置：{filepath}')

        if os.path.getsize(filepath) == 13:
            delete = False
            with open(filepath, 'rb') as f:
                if f.read() == b'{\"code\": 403}':
                    delete = True
            
            if delete:
                print(f'删除无效文件 {filepath}\n下载地址：{urlpath}')
                os.remove(filepath)
                
                time.sleep(5)

        # 返回声音文件路径
        return os.path.relpath(filepath, self._dirRoot)

if __name__ == "__main__":
    sp = youdao()
    connection = sqlite3.connect('dict.db')
    cursor = connection.cursor()
    
    dict_select_audio = """
        SELECT word, audio FROM stardict
    """
    
    dict_update_audio = """
        UPDATE stardict SET audio = ? WHERE word = ?
    """
    
    cursor.execute(dict_select_audio)
    old = time.time()
    word_count = 0
    save_count = 0
    rows = cursor.fetchall()
    for row in rows:
        word = row[0]
        if word.isalpha() == False:
            word_count += 1
            print(f"跳过 {word}, 不是单词")
            continue
        
        audio = sp.down(word)
        if audio is not None and audio != row[1]:
            cursor.execute(dict_update_audio, (audio, word))
            
        word_count += 1
        if time.time() - old > 60:
            connection.commit()
            print(f"等待 5 秒 ..., 已经下载 {word_count}/{len(rows)} 个单词")
            time.sleep(10)
            old = time.time()
        
    connection.commit()
    connection.close()
    

    
