import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from mainwindow import Ui_MainWindow
import time
import json
import platform
from utils.baidu import getBaiduVideoName
from utils.baidu import Baidu

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.mp4List = None
        self.setupUi(self)

        self.tableWidget.setColumnWidth(0, 200)
        self.tableWidget.setColumnWidth(1, 200)
        self.tableWidget.setColumnWidth(2, 100)
        self.tableWidget.setColumnWidth(3, 300)

        #浏览
        self.pushButton_6.clicked.connect(self.select_filePath)

        #确定
        self.getTitle_t = GetTitleThread()
        self.pushButton_4.clicked.connect(self.getTitle)
        self.getTitle_t.signal_getTitle.connect(self.button_getTitle_callback)

        #生成
        self.makeVideo_t = MakeVideoThread()
        self.pushButton_3.clicked.connect(self.makeVideo)
        self.makeVideo_t.signal_makeVideo.connect(self.button_makeVideo_callback)

        with open('./config.ini', 'r', encoding='utf8') as file:
            jsonData = json.load(file)
            baiduCookie = jsonData['baiduCookie']
            filePath = jsonData['filePath']

            if baiduCookie is not None and baiduCookie != '':
                self.lineEdit.setText(baiduCookie)

            if filePath is not None and filePath != '':
                self.lineEdit_5.setText(filePath)


    def select_filePath(self):
        filePath = QtWidgets.QFileDialog.getExistingDirectory(self, "选择视频存储路径")
        if platform.system() == 'Windows':
            filePath = filePath.replace("/","\\")
        self.lineEdit_5.setText(filePath)


    def getTitle(self):

        baiduUrls = self.lineEdit_2.text()
        if baiduUrls is None or baiduUrls == '':
            self.statusBar().showMessage("请输入百度图文地址")
            return
        self.getTitle_t.getTitle(baiduUrls)


    def button_getTitle_callback(self, baiduVideoList):

        if baiduVideoList is not None:
            # 填充table
            for index, baiduVideo in enumerate(baiduVideoList):
                self.tableWidget.setRowCount(index)
                self.tableWidget.insertRow(index)

                url_item = QtWidgets.QTableWidgetItem()
                url_item.setText(baiduVideo['url'])
                self.tableWidget.setItem(index, 0, url_item)

                title_item = QtWidgets.QTableWidgetItem()
                title_item.setText(baiduVideo['title'])
                self.tableWidget.setItem(index, 1, title_item)

                status_item = QtWidgets.QTableWidgetItem()
                status_item.setText('')
                self.tableWidget.setItem(index, 2, status_item)

                filePath_item = QtWidgets.QTableWidgetItem()
                filePath_item.setText('')
                self.tableWidget.setItem(index, 3, filePath_item)

        self.baiduVideoList = baiduVideoList
        self.statusBar().showMessage("共有{}条视频".format(len(baiduVideoList)))


    def makeVideo(self):

        baiduCookie = self.lineEdit.text()
        filePath = self.lineEdit_5.text()
        baiduVideoList = self.baiduVideoList

        if baiduCookie is None or baiduCookie == '':
            self.statusBar().showMessage("请输入百度的cookie")
            return

        if filePath is None or filePath == '':
            self.statusBar().showMessage("请视频生成的路径")
            return

        if baiduVideoList is None:
            self.statusBar().showMessage("请先确定视频")
            return

        #修改config.ini文件
        config = {}
        config['baiduCookie'] = baiduCookie
        config['filePath'] = filePath
        configData = json.dumps(config)
        with open('./config.ini', 'w', encoding='utf8') as file:
            file.write(configData)

        self.makeVideo_t.makeVideo(baiduVideoList, filePath, baiduCookie)


    def button_makeVideo_callback(self, baiduVideo):

        index = baiduVideo['index']

        status_item = QtWidgets.QTableWidgetItem()
        status_item.setText(baiduVideo['status'])
        self.tableWidget.setItem(index, 2, status_item)

        filePath_item = QtWidgets.QTableWidgetItem()
        filePath_item.setText(baiduVideo['filePath'])
        self.tableWidget.setItem(index, 3, filePath_item)



class GetTitleThread(QtCore.QThread):
    signal_getTitle = QtCore.pyqtSignal(list)  # 信号

    def __init__(self, parent=None):
        super(GetTitleThread, self).__init__(parent)
        self.filePath = None

    def getTitle(self, baiduUrls):
        self.baiduUrls = baiduUrls
        self.start()

    def run(self):

        baiduVideoList = []
        for index, baiduUrl in enumerate(self.baiduUrls.split(",")):
            baiduVideo = {}
            title = getBaiduVideoName(baiduUrl)
            baiduVideo['index'] = index
            baiduVideo['url'] = str(baiduUrl)
            baiduVideo['title'] = str(title)
            baiduVideoList.append(baiduVideo)

        self.signal_getTitle.emit(baiduVideoList)  # 发送信号


class MakeVideoThread(QtCore.QThread):
    signal_makeVideo = QtCore.pyqtSignal(dict)  # 信号

    def __init__(self, parent=None):
        super(MakeVideoThread, self).__init__(parent)
        self.filePath = None

    def makeVideo(self, baiduVideoList, filePath, baiduCookie):
        self.baiduVideoList = baiduVideoList
        self.filePath = filePath
        self.baiduCookie = baiduCookie
        self.start()

    def run(self):

        for baiduVideo in self.baiduVideoList:
            url = baiduVideo['url']

            baiduVideo['status'] = '生成中'
            baiduVideo['filePath'] = ''
            self.signal_makeVideo.emit(baiduVideo)  # 发送信号

            baidu = Baidu(url, self.baiduCookie, self.filePath)
            baidu.getVideoName()
            if (baidu.create_vidpress()):
                count = 0
                while count < 40:
                    print("生成中")
                    count = count + 1
                    if baidu.checkArticleVideoIsSuccess():
                        print("生成完成")
                        break
                    time.sleep(60)

                if baidu.mp4Url is not None:
                    baidu.download()
                    baiduVideo['status'] = '成功'
                    baiduVideo['filePath'] = str(baidu.filePath)

                else:
                    baiduVideo['status'] = '失败'

                baidu.delete_vidpress()

            self.signal_makeVideo.emit(baiduVideo)  # 发送信号


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())