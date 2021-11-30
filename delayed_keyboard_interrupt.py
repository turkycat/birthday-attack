import signal
import logging

# this class will serve as a critical section guard to prevent keyboard interrupt
# SIGINT is sent with CTRL + C which normally evaluates to KeyboardException
# if this signal is unhandled (normal case) it crashes the app
class DelayedKeyboardInterrupt:

    def __enter__(self):
        self.signal_received = False
        # signal.signal sets self.handler as a new handler, returns the old handler
        self.old_handler = signal.signal(signal.SIGINT, self.handler)
                
    def handler(self, sig, frame):
        self.signal_received = (sig, frame)
        print("KeyboardInterrupt received. Program will exit when the current operation is complete.")
        logging.debug('SIGINT received. Delaying KeyboardInterrupt.')
    
    def __exit__(self, type, value, traceback):
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            self.old_handler(*self.signal_received)