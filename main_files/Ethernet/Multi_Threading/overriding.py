import threading

class MyThread(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        print("Thread has began")

def main():
    t = MyThread()
    t.start()
    print(t.is_alive())
    t.join()
    print(t.is_alive())

if __name__ == "__main__":
    main()
