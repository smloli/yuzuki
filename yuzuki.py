import requests
import json
import random
import time
import threading
import re


class Yuzuki:
    ua = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'

    def __init__(self, **kwargs):
        self.username = kwargs['username']
        self.password = kwargs['password']
        self.root = kwargs['root']
        self.comment_count = kwargs['comment_count']
        self.follow_count = kwargs['follow_count']
        self.index = kwargs['index']
        try:
            self.token = self.login()
        except Exception:
            return
        else:
            self.headers = {
                'authorization': self.token,
                'user-agent': self.ua
            }

    # 登录
    def login(self):
        url = self.root + '/wp-json/jwt-auth/v1/token'
        headers = {
            'referer': self.root + '/',
            'user-agent': self.ua
        }
        data = {
            'username': self.username,
            'password': self.password
        }
        result = session.post(url, headers=headers, data=data)
        result = json.loads(result.text)
        token = f"Bearer {result['token']}"
        return token

    # 签到
    def sign(self):
        url = self.root + '/wp-json/b2/v1/userMission'
        headers = self.headers
        headers['referer'] = self.root + '/task'
        session.post(url, headers=headers)
        print('签到成功！')

    # 获取随机的帖子ID
    def get_task_data(self):
        url = self.root + '/wp-json/b2/v1/getTaskData'
        result = session.post(url, headers=self.headers)
        result = json.loads(result.text)
        return result

    # 自动回复comment_count个帖子
    def comment(self):
        url = self.root + '/wp-json/b2/v1/commentSubmit'
        comment_list = ['感谢楼主分享', '卷纸', '路过', '积分', '感谢大佬分享']
        for i in range(self.comment_count):
            post_result = self.get_task_data()
            post_id = post_result['task']['task_comment']['url'][self.index:-5]
            data = {
                'comment_post_ID': post_id,
                'author': '小萝莉',
                'comment': comment_list[random.randint(0, 4)],
                'comment_parent': '0'
            }
            result = session.post(url, headers=self.headers, data=data)
            comment_id = re.findall(r'comment-(\d+)', result.text)[0]
            print(f'评论 {i + 1}/{self.comment_count}')
            self.like(comment_id, i)
            if i == self.comment_count - 1:
                return
            time.sleep(45)

    # 点赞自己的评论
    def like(self, comment_id, count):
        url = self.root + '/wp-json/b2/v1/commentVote'
        data = {
            'type': 'comment_up',
            'comment_id': comment_id
        }
        session.post(url, headers=self.headers, data=data)
        print(f'点赞 {count + 1}/{self.comment_count}')

    # 关注
    def follow(self):
        id_list = []
        ids_dict = {}
        c = 0
        reg = r'v-if="follow\[(\d+)\]'
        page_max_reg = r'/(\d+) 页'
        page_url = self.root + '/?s=&type=user'
        result = session.get(page_url, headers=self.headers)
        result = re.findall(page_max_reg, result.text)
        page_max = int(result[0])
        follow_url = self.root + '/wp-json/b2/v1/AuthorFollow'
        check_url = self.root + '/wp-json/b2/v1/checkFollowByids'
        for page in range(page_max):
            page += 1
            user_info_url = self.root + '/page/' + str(page) + '?s&type=user'
            r = session.get(user_info_url, headers=self.headers)
            r = re.findall(reg, r.text)
            # 将用户id添加到字典
            for j in r:
                ids_dict[f'ids[{c}]'] = j
                c += 1
            c = 0
            # 检测字典里的用户是否已关注
            check_list = session.post(check_url, headers=self.headers, data=ids_dict)
            check_list = json.loads(check_list.text)
            for tmp in check_list:
                if not check_list[tmp]:
                    # 当列表里有follow_count个用户ID就退出这一层循环
                    if len(id_list) == self.follow_count:
                        break
                    id_list.append(tmp)
            # 同上
            if len(id_list) == self.follow_count:
                break
        # 关注用户
        for k in id_list:
            count = 1
            data = {
                'user_id': k
            }
            session.post(follow_url, headers=self.headers, data=data)
            print(f'关注 {count}/{self.follow_count}')
            count += 1
            time.sleep(1)

    def run(self):
        self.sign()
        self.comment()
        self.follow()


if __name__ == '__main__':
    session = requests.session()
    MeiMeng = Yuzuki(username='', password='', root='https://www.clubmeitu.com', index=26, comment_count=1, follow_count=0)
    Yuzhaizu = Yuzuki(username='', password='', root='https://www.otakv.co', index=17, comment_count=6, follow_count=2)
    Sizhaiwang = Yuzuki(username='', password='', root='https://www.szhai.me', index=21, comment_count=6, follow_count=2)
    meimeng = threading.Thread(target=MeiMeng.run)
    yuzhaizu = threading.Thread(target=Yuzhaizu.run)
    sizhaiwang = threading.Thread(target=Sizhaiwang.run)
    meimeng.start()
    yuzhaizu.start()
    sizhaiwang.start()
