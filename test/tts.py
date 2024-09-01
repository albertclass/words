import pyttsx3

engine = pyttsx3.init()

word = "congratulation"  # 这里设置你要朗读的英语单词

engine.setProperty('volume', 1.2)  # 设置音量
engine.say(word)
engine.runAndWait()

engine.say("Congratulations! You have finished the exercise!")
engine.runAndWait()