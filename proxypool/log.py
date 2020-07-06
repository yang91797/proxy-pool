import datetime
import os

file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'log')


def msg(message):
    time = datetime.datetime.now()
    date = str(time).split(maxsplit=1)[0]
    path = os.path.join(file_path, '%smsg.text' % date)
    message = '%s : %s' % (message, time)
    with open(path, mode='a+', encoding='utf-8') as f:
        f.write(message + '\n')



