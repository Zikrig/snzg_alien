
import config
import threading

def f1():
    import vk
def f2():
    import tg

t1 = threading.Thread(target=f1)
t2 = threading.Thread(target=f2)

t1.start()
t2.start()





