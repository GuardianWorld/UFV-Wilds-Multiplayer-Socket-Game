import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class HotReloader:
    def __init__(self, script):
        self.script = script
        self.process = self.start_process()
        self.observer = Observer()
        self.event_handler = self.ReloadHandler(self)

    class ReloadHandler(FileSystemEventHandler):
        def __init__(self, reloader):
            self.reloader = reloader

        def on_modified(self, event):
            if event.src_path.endswith('.py'):
                print(f"[HotReloader] Detected change in {event.src_path}")
                self.reloader.restart_process()

    def start_process(self):
        print(f"[HotReloader] Starting {self.script}")
        return subprocess.Popen([sys.executable, self.script])

    def restart_process(self):
        print(f"[HotReloader] Restarting {self.script}")
        self.process.terminate()
        self.process.wait()
        self.process = self.start_process()

    def start(self):
        self.observer.schedule(self.event_handler, path='.', recursive=True)
        self.observer.start()
        print(f"[HotReloader] Watching for changes in {self.script}...")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

def hot_reload(script):
    reloader = HotReloader(script)
    reloader.start()

if __name__ == "__main__":
    script = ""
    if len(sys.argv) < 2:
        quit()
    
    script = sys.argv[1]
    hot_reload(script)
