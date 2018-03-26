# -*- coding: utf-8 -*-

"""
Module implementing RecognizeWindow.
"""
import time
import http.client as httplib
from hashlib import md5
import urllib
import random
import json
import sys
import cv2
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Ui_RecognizeWindow import Ui_Dialog
from common import config
from common.baiduocr import get_text_from_image

global file_name, app_id, app_key, app_secret, text
app_id = '10689406'
app_key = 'BAubMHA9tfxbMQxuGoOwpwgg'
app_secret = '1Ke1XWpQdKCitRfbVAORf8S92eAGBXvX'
text = '我是赵义柔'

class MyThread(QThread):
    def __init__(self, parent = None):
        super(MyThread, self).__init__(parent)
    def run(self):
        pass
        #global file_name
        

class RecognizeWindow(QDialog, Ui_Dialog):
    
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(RecognizeWindow, self).__init__(parent)
        
        self.setupUi(self)
        self.setWindowTitle("图片文字识别软件-赵明2018.3.25（待完善）")
        self.setWindowIcon(QIcon('H:\\study\\pyqt5\\recognize\\zm.jpg'))   #图标的位置
        self.initBaiDu()
    
    def initBaiDu(self):
        self.appKey = '20180326000140245'# 就是自己注册应用ID
        self.secretKey = 'R8skVX9_Q0pIZntJzBrs'# 就是应用密钥
        self.httpClient = None
        self.myurl = '/api/trans/vip/translate'
        self.salt = random.randint(1, 65536) # 随机数

    def lang_transform(self, lang):
        '''
        tranform the language into correct format that ai.youdao.com accepted
        中文  zh-CHS
        日文  ja
        英文  EN
        韩文  ko
        法文  fr
        俄文  ru
        葡萄牙文    pt
        西班牙文    es
        '''
        if lang == "Chinese":
            return "zh"
        if lang == "Japanease":
            return "ja"
        if lang == "English":
            return "en"
        if lang == "Korea":
            return "kor"
        if lang == "Russia":
            return "ru"
        if lang == "French":
            return "fra"
        if lang == "Auto":
            return "auto"
        
    @pyqtSlot()
    def on_Button_bro_clicked(self):
        global file_name
        file_name, file_type = QFileDialog.getOpenFileName(self,"选择一张图片",".","*.jpg")
        self.label_picAdr.setText(file_name)
        img = cv2.imread(file_name)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        height, width, bytesPerComponent = img.shape
        qimg = QImage(img_rgb.data, width, height,3*width, QImage.Format_RGB888)#原始图
        qpiximg = QPixmap.fromImage(qimg)
        self.label_img.setPixmap(qpiximg.scaled(self.label_img.width(), self.label_img.height()))
    @pyqtSlot()
    def on_pushButton_recognize_clicked(self):
        #thread.start()
        img = cv2.imread(file_name)
        f = open(file_name, 'rb')
        im = f.read()
        #img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        height, width, bytesPerComponent = img.shape
        text = get_text_from_image(im, app_id, app_key, app_secret, 0, 3)
        self.textEdit_text.setMaximumWidth(400)
        self.textEdit_text.setText(text)
        
    @pyqtSlot()
    def on_pushButton_translate_clicked(self):
        start = time.time()
        end = time.time()
        trans = self.get_translation( self.textEdit_text.toPlainText())
        self.textEdit_translateLanguage.setPlainText(trans)
        self.textEdit_translateLanguage.setStatusTip("翻译时间：%.2fs"%(end-start))
    
    def get_translation(self, query):
        self.toLang = self.lang_transform(self.comboBox_chooseLanguage.currentText() )  # 目标语言
        self.fromLang =  self.lang_transform(self.comboBox_fromLang.currentText() )  # 源语言
        sign = self.appKey + query + str(self.salt) + self.secretKey     # 签名
        m1 = md5()
        m1.update( sign.encode() )
        sign = m1.hexdigest()       # 计算签名的哈希值
        self.myurl = self.myurl+'?appid='+self.appKey+'&q='+urllib.parse.quote(query)+'&from='+self.fromLang+'&to='+self.toLang+'&salt='+str(self.salt)+'&sign='+sign
        try:
            httpClient = httplib.HTTPConnection('api.fanyi.baidu.com')
            httpClient.request('GET', self.myurl)

            #response是HTTPResponse对象
            response = httpClient.getresponse()
            res = response.read().decode('unicode-escape') # unicode解码

            hjson = json.loads(res)
#
            exp = str(hjson['trans_result'][0]["dst"])
#            exp = exp[0]
#            exp = exp.replace(',','\r\n')
#            exp = exp.replace('[',' ')
#            exp = exp.replace(']',' ')
#            exp = exp.replace('\'',' ')

            return exp

        except Exception as e:
            print (e)
        finally:
            if httpClient:
                httpClient.close()
        
        
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlg = RecognizeWindow()
    dlg.show()
    thread = MyThread()
    sys.exit(app.exec_())
