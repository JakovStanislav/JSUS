import sys
import threading
from queue import Queue

import backend
import frontend
__version__ = '0.1.0'

def main():
    back_to_front_queue = Queue()
    front_to_back_queue = Queue()

    pnet_pc_read_thread = threading.Thread(
        target=backend.start_pnet_pc_read_thread,
        args=(back_to_front_queue, front_to_back_queue))
    gui_thread = threading.Thread(target=frontend.start_gui_thread,
                                  args=(
                                  back_to_front_queue, front_to_back_queue))

    pnet_pc_read_thread.start()
    gui_thread.start()


if __name__ == '__main__':
    sys.exit(main())
