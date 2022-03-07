from typing import Optional
from ctypes import wintypes, windll, create_unicode_buffer
import win32api
import time

def getForegroundWindowTitle() -> Optional[str]:
    hWnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(hWnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hWnd, buf, length + 1)
    
    if buf.value:
        return buf.value
    else:
        return None
    
prev_pos = curr_pos = [0, 0]
curr_window_title = ''
while True:
    prev_pos = win32api.GetCursorPos()
    window_title = getForegroundWindowTitle()
    now = int( time.time() )
    pos_str = ','.join(str(j) for j in prev_pos)
    
    if prev_pos[0] != curr_pos[0] or prev_pos[1] != curr_pos[1] or curr_window_title != window_title:
        print(str(prev_pos[0]) + ' ' + str(curr_pos[0]))
        print(str(prev_pos[1]) + ' ' + str(curr_pos[1]))
        out = '1\t' + str(pos_str) + '\t' + str(now) + '\t' + str(window_title) + '\n'
        
        f = open("POC.txt", "a")
        f.write(out)
        f.close()
    curr_pos = prev_pos
    curr_window_title = window_title
    time.sleep(2)
