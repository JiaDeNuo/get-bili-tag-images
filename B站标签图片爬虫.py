# -*- coding = utf-8 -*-


import requests
import os
import re

head = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/87.0.4280.88 Safari/537.36"
}


def main():
    base_url = 'https://api.bilibili.com/x/tag/info?tag_name='
    tage_id, tage_name = get_tag_id(base_url)  # 得到tag的id和名字
    filename = make_file(tage_name)  # 在当前脚本目录下生成并打开存放图片的文件夹
    url = 'https://api.vc.bilibili.com/topic_svr/v1/topic_svr/topic_new?topic_id=' + str(tage_id)  # 生成tag的url
    get_img(url, tage_name, filename)  # 爬取图片保存到文件夹


def get_tag_id(base_url):
    """得到tag的id"""
    tage_name = input('输入标签名：')
    base_url += tage_name
    response = requests.get(url=base_url, headers=head).json()
    if response["code"] == 16001:
        print("该频道尚不存在")
        get_tag_id(base_url)
    else:
        tage_id = response['data']["tag_id"]
        return tage_id, tage_name


def make_file(tage_name):
    """生成文件夹"""
    filename = f'./{tage_name}的图片'
    if not os.path.exists(filename):
        os.mkdir(filename)  # 创建文件夹
    os.system(f'start explorer {tage_name}的图片')  # 打开文件夹
    return filename


def get_img(url, tage_name, filename):
    """爬取图片"""
    find_img = re.compile(r'"img_src":"(.*?)","img_width"', re.S)  # 正则规则抓取图片url
    flag = ''
    while flag != 'Q' and flag != 'q':
        r = requests.get(url=url, headers=head).json()
        try:
            for i in r['data']['cards']:  # 遍历当前页面的帖子
                a = i['card']  # 帖子里的内容
                images = re.findall(find_img, a)  # 帖子里的所有图片的url
                for img in images:  # 爬取每个图片
                    img_name = img.split('/')[-1]  # 生成图片名
                    img_path = filename + '/' + img_name  # 加载图片路径
                    if os.path.isfile(img_path):  # 有之前爬过的图片不再爬取
                        print('图片' + img_name + '已存在')
                    else:
                        img_data = requests.get(url=img, headers=head).content  # 得到图片二进制数据
                        with open(img_path, 'wb') as fp:  # 写入图片
                            fp.write(img_data)
                            print('下载完成：' + img_name)
            offset_id = r['data']['offset']  # 当前的页面留给后面待加载内容的id
            url = 'https://api.vc.bilibili.com/topic_svr/v1/topic_svr/topic_history?topic_name=' + tage_name + \
                  '&offset_dynamic_id=' + offset_id  # 当前页面显示完后动态加载的页面url
            flag = input('按任意键继续(按 q 退出): ')  # 模拟翻到网页最下面后继续加载更多内容，注释掉这行将不停爬取直至没有更多内容
        except KeyError:  # tag最后无新帖子：最后一次加载的页面 r['data']里没有['cards']，发生KeyError
            print('已无更多内容')
            break
    print('程序停止')


if __name__ == '__main__':
    main()
