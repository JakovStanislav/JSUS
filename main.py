import sys
import threading
from queue import Queue

import backend
import frontend
__version__ = '0.1.0'

def main():
    back_to_front_queue = Queue()
    front_to_back_queue = Queue()

    read_thread = threading.Thread(
        target=backend.start_read_thread,
        args=(back_to_front_queue, front_to_back_queue))
    gui_thread = threading.Thread(target=frontend.start_gui_thread,
                                  args=(
                                  back_to_front_queue, front_to_back_queue))

    read_thread.start()
    gui_thread.start()


if __name__ == '__main__':
    sys.exit(main())
