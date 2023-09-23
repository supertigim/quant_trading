#import win32ui
from pywinauto.application import Application
from pywinauto import timings
from pywinauto import findwindows
import time
import os

def update_kiwoom_sw():

    app = Application(backend="win32").start("C:/KiwoomFlash3/bin/nkministarter.exe")

    title = "번개3 Login"
    timings.wait_until_passes(20, 0.5, lambda: findwindows.find_windows(title=title)[0])
    #dig = app[title]  #위의 dlg값과 동일

    pw = os.getenv('kiwoom_p')
    pw2 = os.getenv('kiwoom_p2')

    app.Dialog.Edit2.type_keys(pw)
    app.Dialog.Edit3.type_keys(pw2)
    app.Dialog.Button0.click()

    main_title = "번개3"
    timings.wait_until_passes(100, 0.5, lambda: findwindows.find_windows(title=main_title)[0])

    print("번개3(키움 OCX) 시작")

    time.sleep(3) 
    
    os.system("taskkill /im nkmini.exe")   

    #app = Application().connect(title=main_title)
    #app.kill(soft=False)
    
    print("번개3 종료")

def test():
    os.system("taskkill /im nkmini.exe")
    
def main():
    #test()
    update_kiwoom_sw()

if __name__ == "__main__":
    main()