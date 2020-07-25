# -*- coding: utf-8 -*- 
from pykiwoom.kiwoom import Kiwoom

def main():
    kiwoom = Kiwoom()
    kiwoom.CommConnect(block=True) # 컴포트 연결 
    
    print("It's been a while to write a program") 

if __name__ == '__main__':
    main()

# end of file