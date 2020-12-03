from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.event import EventDispatcher
from kivy.properties import ListProperty, ObjectProperty, StringProperty, \
                            BoundedNumericProperty, NumericProperty, BooleanProperty
import threading, queue

# # Abstract the interface that we use to interact with the hardware
# # this includes multiple state machines for things like opening and closing
# # doors, reading of button presses, and recording their values constantly.
# class ArenaEventProcessor(EventDispatcher):
#     stopEv = threading.Event()
#     def __init__(self, hw_interface):
#         self.arena = hw_interface
#         self.eventQueue = queue.Queue()
#         self.lights_thread = threading.Thread(target=self.lights_processor).start()
#         self.hw_thread = threading.Thread(target=self.buttons_and_switches)
        
#     def stop(self):
#         self.stopEv.set()
#         self.lights_thread.join()
#         self.hw_thread.join()
#     def buttons_and_switches(self):

#         pass

#     def lights_processor(self):
#         while True:
#             # Stop running this thread so the main Python process can exit.
#             if self.stop.is_set():
#                 return
#             try:
#                 self.get_nowait()
#             except queue.Empty:
#                 pass
#             time.sleep(0.01)
#         self.thread.join()



#from Queue import Queue

#class KivyQueue(queue.Queue):
#    '''
#    A Multithread safe class that calls a callback whenever an item is added
#    to the queue. Instead of having to poll or wait, you could wait to get
#    notified of additions.

#    >>> def callabck():
#    ...     print('Added')
#    >>> q = KivyQueue(notify_func=callabck)
#    >>> q.put('test', 55)
#    Added
#    >>> q.get()
#    ('test', 55)

#    :param notify_func: The function to call when adding to the queue
#    '''

#    notify_func = None

#    def __init__(self, notify_func, **kwargs):
#        Queue.__init__(self, **kwargs)
#        self.notify_func = notify_func

#    def put(self, key, val):
#        '''
#        Adds a (key, value) tuple to the queue and calls the callback function.
#        '''
#        Queue.put(self, (key, val), False)
#        self.notify_func()

#    def get(self):
#        '''
#        Returns the next items in the queue, if non-empty, otherwise a
#        :py:attr:`Queue.Empty` exception is raised.
#        '''
#        return Queue.get(self, False)