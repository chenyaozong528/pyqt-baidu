import time
import os
import requests
import datetime
import json
from selenium import webdriver
from bs4 import BeautifulSoup


class Baidu():

    def __init__(self, url, cookie, localFileDir):
        self.url = url
        self.localFileDir = localFileDir
        self.filePath = None
        self.fileName = None
        self.job_id = None
        self.status = None
        self.mp4Url = None
        self.des = None
        self.header = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "origin": "https://ai.baidu.com",
            "referer": "https://ai.baidu.com/creation/external/labprojectlist",
            "Cookie": cookie
        }


    def checkArticleVideoIsSuccess(self):

        self.query_vidpress()
        if self.status == "4":
            return True
        return False


    def download(self):
        fileName = self.fileName
        filePath = self.localFileDir

        # 增加日期文件夹
        os.chdir(filePath)
        date = datetime.datetime.now().strftime('%Y%m%d')
        if not os.path.exists(date):
            os.makedirs(date)

        filePath = filePath + os.sep + date
        self.filePath = filePath + os.sep + fileName + ".mp4"

        down_res = requests.get(self.mp4Url, verify=False, headers=self.header)
        with open(self.filePath, "wb") as code:
            code.write(down_res.content)


    def getVideoName(self):
        # chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--start-maximized')
        # chrome_options.add_argument('disable-infobars')
        # chrome_options.add_argument('headless')
        # driver = webdriver.Chrome(chrome_options=chrome_options)
        # driver.get(self.url)
        # self.fileName = driver.find_element_by_xpath('//*[@id="detail-page"]/div[3]/div/div[1]/h2').text
        # driver.close()

        header = {
            "Host": "baijiahao.baidu.com",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
        }

        response = requests.get(self.url, verify=False, headers=header)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "lxml")
        self.fileName = soup.findAll("title")[0].text

    def create_vidpress(self):
        url = "https://ai.baidu.com/article/external/create_vidpress"

        params = {
            "news_url": self.url,
            "tts_per": 4100,
            "duration": 120
        }

        response = requests.post(url, verify=False, headers=self.header, data=params)
        response.encoding = 'utf-8'
        html = response.text
        result = json.loads(html)
        if result['ret'] == 0 :
            self.job_id = result['content']['job_id']
            print("生成视频任务id:{}".format(self.job_id))
            return True
        else:
            self.des = result['msg']
            return False


    def query_vidpress(self):

        url = "https://ai.baidu.com/article/external/query_vidpress"

        response = requests.post(url, verify=False, headers=self.header)
        response.encoding = 'utf-8'
        html = response.text
        result = json.loads(html)
        if result['ret'] == 0 :
            jobId = str(self.job_id)
            status = result['content'][jobId]['status']
            self.status = status
            print("视频任务id:{}  状态:{}".format(self.job_id, status))
            if status == "4":
                mp4Url = result['content'][jobId]['video_addr']
                self.mp4Url = mp4Url
                print("视频任务id:{}  mp4地址:{}".format(self.job_id, mp4Url))


    def delete_vidpress(self):
        url = "https://ai.baidu.com/article/external/delete_vidpress"
        params = {
            "job_id": self.job_id
        }

        response = requests.post(url, verify=False, headers=self.header, data=params)
        response.encoding = 'utf-8'
        html = response.text
        result = json.loads(html)
        if result['ret'] == 0 :
            print("删除生成的视频成功")



def getVideoAndDownload(url):

    local_file_dir = "/Users/chenyaozong/xigua"
    baidu = Baidu(url, local_file_dir)
    baidu.getVideoName()
    baidu.create_vidpress()
    count = 0
    while count < 40:
        print("生成中")
        count = count + 1
        if baidu.checkArticleVideoIsSuccess():
            print("生成完成")
            break
        time.sleep(60)

    baidu.download()
    baidu.delete_vidpress()


def getBaiduVideoName(url):
    header = {
        "Host": "baijiahao.baidu.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
    }

    response = requests.get(url, verify=False, headers=header)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "lxml")
    return soup.findAll("title")[0].text


if __name__ == "__main__":

    url = "https://baijiahao.baidu.com/s?id=1673356699222239058"
    header = {
        "Host":"baijiahao.baidu.com",
        "Accept-Encoding":"gzip, deflate, br",
        "Accept-Language":"zh-CN,zh;q=0.9,en;q=0.8",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
    }

    response = requests.get(url, verify=False, headers = header)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "lxml")
    trs = soup.findAll("title")
    print(trs[0].text)
