#!/usr/bin/env python
# coding:utf-8
"""
作者:sleshep
邮箱:x@icexz.com
日期:16-9-19
时间:上午 11:50
"""
import struct
import time
from ctypes import *
from logging import basicConfig, getLogger, DEBUG

basicConfig()
log = getLogger(__name__)
log.setLevel(DEBUG)
user32 = WinDLL('user32.dll')
kernel32 = WinDLL('kernel32.dll')

WM_LBUTTONDOWN = 0x201
WM_LBUTTONUP = 0x202


def read_chess_memory():
    hwnd = get_llk_hwnd()
    chess = create_string_buffer(11 * 19)

    if hwnd:
        pid = c_int()
        user32.GetWindowThreadProcessId(hwnd, byref(pid))
        h_process = kernel32.OpenProcess(0xf0000 | 0x100000 | 0xfff, 0, pid)
        kernel32.ReadProcessMemory(h_process, 0x129fb4, byref(chess), 11 * 19, byref(pid))
        kernel32.CloseHandle(h_process)
    return chess


def get_llk_hwnd():
    hwnd = user32.FindWindowA('#32770'.encode('ascii'), 'QQ 游戏 - 连连看角色版'.encode('gb2312'))
    if not hwnd:
        log.info('找不到游戏了.')
    return hwnd


def make_long(x, y):
    return c_long((x << 16) + y)


def click_both(x, y, xx, yy):
    # print('a({},{}) b({},{})'.format(x, y, xx, yy))
    hwnd = get_llk_hwnd()
    if hwnd:
        first_x = 28
        first_y = 199
        user32.SendMessageA(hwnd, WM_LBUTTONDOWN, 0, make_long(first_y + y * 35, first_x + x * 31))
        user32.SendMessageA(hwnd, WM_LBUTTONUP, 0, make_long(first_y + y * 35, first_x + x * 31))
        user32.SendMessageA(hwnd, WM_LBUTTONDOWN, 0, make_long(first_y + yy * 35, first_x + xx * 31))
        user32.SendMessageA(hwnd, WM_LBUTTONUP, 0, make_long(first_y + yy * 35, first_x + xx * 31))


def clear_all():
    chess = read_chess_memory()
    for x in range(19):
        for y in range(11):
            for xx in range(19):
                for yy in range(11):
                    if chess.raw[19 * y + x] != 0 and chess.raw[19 * yy + xx] != 0 and (xx != x or yy != y) and \
                                    chess.raw[19 * y + x] == chess.raw[19 * yy + xx]:
                        click_both(x, y, xx, yy)


def get_chess_count():
    return len(list(filter(int, read_chess_memory().raw)))


def send_redeploy():
    hwnd = get_llk_hwnd()
    if hwnd:
        log.info('检测到无解,重列！')
        y = 197
        x = 652
        user32.SendMessageA(hwnd, WM_LBUTTONDOWN, 0, make_long(y, x))
        user32.SendMessageA(hwnd, WM_LBUTTONUP, 0, make_long(y, x))
        time.sleep(2)


def fully_clear():
    while get_chess_count():
        last_count = get_chess_count()
        clear_all()
        if last_count == get_chess_count() and last_count != 0:
            send_redeploy()


def start_game():
    hwnd = get_llk_hwnd()
    if hwnd:
        y = 570
        x = 668
        user32.SendMessageA(hwnd, WM_LBUTTONDOWN, 0, make_long(y, x))
        user32.SendMessageA(hwnd, WM_LBUTTONUP, 0, make_long(y, x))


def quick_start():
    """
    大厅快速开始没法 SendMessage ，所以只能移动鼠标然后再点
    """
    hwnd = user32.FindWindowA(0, '连连看'.encode('gb2312'))
    if hwnd:
        rect = create_string_buffer(16)
        user32.GetWindowRect(hwnd, byref(rect))
        left_x, left_y, *_ = struct.unpack('<IIII', rect.raw)
        x = 275 + left_x
        y = 150 + left_y
        user32.SetCursorPos(x, y)
        time.sleep(.5)
        user32.mouse_event(0x0002, x, y, 0, 0)
        time.sleep(.5)
        user32.mouse_event(0x0004, x, y, 0, 0)
        time.sleep(3)


def main():
    while 1:
        if not get_llk_hwnd():
            log.info('没找到游戏，估计被踢出来了，现在重新进..')
            quick_start()
        start_game()
        time.sleep(1)
        fully_clear()


if __name__ == '__main__':
    main()
