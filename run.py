from proxypool.api import app
from proxypool.schedule import Schedule
from proxypool.log import msg


def main():
    try:
        s = Schedule()
        s.run()
        app.run()
    except Exception as e:
        info = '出错啦：%s' % e
        print(info)
        msg(info)


if __name__ == '__main__':
    main()

