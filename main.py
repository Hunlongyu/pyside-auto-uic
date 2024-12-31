import os
import sys
import time
import pystray
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from subprocess import Popen, CREATE_NO_WINDOW, PIPE
from PIL import Image

# 全局变量，记录暂停状态
paused = False

class UICCompilerHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        global paused
        # 只处理文件修改事件，避免重复触发
        if not paused and not event.is_directory and event.src_path.endswith('.ui') and event.event_type == 'modified':
            time.sleep(1)  # 等待文件写入完成
            file_path = event.src_path
            file_name = os.path.basename(file_path)
            file_dir = os.path.dirname(file_path)
            output_file = os.path.join(file_dir, f"ui_{os.path.splitext(file_name)[0]}.py")
            try:
                Popen(["pyside6-uic", file_path, "-o", output_file], stdout=PIPE, stderr=PIPE, creationflags=CREATE_NO_WINDOW)
                icon.notify(
                    message=f"{output_file} was compiled successfully.",
                    title="Compiled Successfully"
                )
            except Exception as e:
                icon.notify(
                    message=f"Failed to compile {file_name}: {e}",
                    title="Compilation Failed"
                )

def quit_window(icon, item):
    icon.stop()
    observer.stop()
    sys.exit()

def toggle_pause(icon, item):
    global paused
    paused = not paused
    icon.update_menu()  # 更新菜单状态

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else r'.'

    event_handler = UICCompilerHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    # 创建菜单项
    menu = pystray.Menu(
        pystray.MenuItem(
            '暂停',
            toggle_pause,
            checked=lambda item: paused  # 动态检查 paused 状态
        ),
        pystray.MenuItem('退出', quit_window)
    )
    image = Image.open(resource_path("logo.ico"))
    icon = pystray.Icon("UIC Compiler", image, "UIC Compiler", menu)
    try:
        icon.run()
    except Exception:
        icon.stop()
        observer.stop()
    finally:
        observer.join()