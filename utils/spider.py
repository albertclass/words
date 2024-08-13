'''
程序思想：
有两个本地语音库，美音库Speech_US，英音库Speech_US
调用有道api，获取语音MP3，存入对应的语音库中
'''

import os
import sqlite3
import urllib.request
import time
import hashlib

class youdao():
    def __init__(self, type: int = 1):
        '''
        调用youdao API
        type = 0：美音
        type = 1：英音

        判断当前目录下是否存在两个语音库的目录
        如果不存在，创建
        '''
        self._type = type  # 发音方式

        # 文件根目录
        # self._dirRoot = os.path.abspath(rootpath)
        # if 0 == self._type:
        #     self._dirSpeech = os.path.join(self._dirRoot, "phonetic", 'us')  # 美音库
        # else:
        #     self._dirSpeech = os.path.join(self._dirRoot, "phonetic", 'en')  # 英音库

        # 判断目录是否存在
        # if not os.path.exists(self._dirRoot):
        #     # 不存在，就创建
        #     os.makedirs(self._dirRoot)

    def path(self, word) -> str:
        '''
        返回单词的MP3路径
        '''
        word = word.lower()
        # split word to list, each two letters a group

        md5 = hashlib.md5()
        md5.update(word.encode('utf-8'))
        hex = md5.hexdigest()

        # new save path
        return os.path.join(hex[:2], f"{word}.mp3")
        
    def down(self, word, saveto) -> str:
        '''
        下载单词的MP3
        判断语音库中是否有对应的MP3
        如果没有就下载
        '''
        word = word.lower()  # 小写
        if not word.isprintable():
            return "单词中包含不可打印字符"
        
        messageTips:list[str] = []
        
        if not os.path.exists(saveto):
            # 如果不存在，就下载
            if os.path.exists(os.path.dirname(saveto)) == False:
                # 如果目录不存在，就创建
                os.makedirs(os.path.dirname(saveto))
                
            urlpath = 'http://dict.youdao.com/dictvoice?type=' + str(self._type) + '&audio=' + word.replace(' ', '%20').replace('.', '')
            # 调用下载程序，下载到目标文件夹
            # print('不存在 %s.mp3 文件\n将URL:\n' % word, self._url, '\n下载到:\n', self._filePath)
            # 下载到目标地址
            try:
                urllib.request.urlretrieve(urlpath, filename=saveto)
                messageTips.append(f"下载完成 {word}.mp3, 保存位置：{saveto}")
            except Exception as e:
                messageTips.append(f"下载失败 {word}.mp3, 保存位置：{saveto}\n下载地址：{urlpath}\n错误信息：{type(e)}-{e}")
                return '\n'.join(messageTips)
        # else:
        #     messageTips.append(f'已经存在 {word}.mp3, 保存位置：{saveto}')

        if os.path.getsize(saveto) == 13:
            delete = False
            with open(saveto, 'rb') as f:
                if f.read() == b'{\"code\": 403}':
                    delete = True
            
            if delete:
                messageTips.append(f'删除无效文件 {saveto}\n下载地址：{urlpath}')
                os.remove(saveto)
                
                time.sleep(5)

        # 返回声音文件路径
        return '\n'.join(messageTips)

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
    skip_count = 0
    
    rows = cursor.fetchall()
    total = len(rows)
    for row in rows:
        word = row[0]
        word_count += 1
        if word.isalpha() == False:
            skip_count += 1
            print(f"{word_count}/{len(rows)} 跳过 {word}, 不是单词, 已跳过 {skip_count}")
            continue
        
        # if os.path.exists(path_old) and path_old != path_new:
        #     if os.path.exists(os.path.dirname(path_new)) == False:
        #         os.makedirs(os.path.dirname(path_new))
            
        #     # 如果存在旧文件，就移动到新文件夹
        #     os.rename(path_old, path_new)
        #     # 删除空文件夹
        #     dir_old = os.path.dirname(path_old)
        #     while os.path.exists(dir_old) and len(os.listdir(dir_old)) == 0:
        #         os.rmdir(dir_old)
        #         dir_old = os.path.dirname(dir_old)
                
        #     cursor.execute(dict_update_audio, (os.path.join(hex[:2], f"{word}.mp3"), word))
        #     print(f"{word_count:6d}/{total:6d} 移动文件 {path_old} ==> {path_new}")
        
        
        path_rel = sp.path(word)
        path_new = os.path.join(os.path.abspath('.'), 'phonetic', 'en', path_rel)
        
        if row[1] is None or not os.path.exists(os.path.join(os.path.abspath('.'), 'phonetic', 'en', row[1])):
            tips = sp.down(word, path_new)
            cursor.execute(dict_update_audio, (path_rel, word))
            save_count += 1
        
            print(f"{word_count:6d}/{total:6d} {tips}")

        if time.time() - old > 60 and save_count > 0:
            connection.commit()
            save_count = 0
            print(f"等待 5 秒 ..., 已经下载 {word_count}/{len(rows)} 个单词")
            time.sleep(10)
            old = time.time()
        
    connection.commit()
    connection.close()
    

    
