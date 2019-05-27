#!/usr/bin/python
# -*- coding: UTF-8 -*-
import tkinter as tk
from tkinter import scrolledtext
import configparser
import time
import requests
import threading
import json

# 账户配置文件
account_file_name = 'account.conf'
# 接口配置文件
api_file_name = 'api.conf'


# tk操作
class Tk(object):

    def __init__(self):
        self.tk = tk.Tk()
        self.tk.title('自动学习 V1.0')
        self.tk.geometry('750x500')
        self.tk.resizable(width=False, height=False)
        self.time = tk.StringVar()
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.remember = tk.StringVar()
        self.auto = tk.StringVar()
        self.log = scrolledtext.ScrolledText(width=93, height=29)
        self.log.grid(row=3, column=1, columnspan=3, sticky='W')
        self.button = ''

    # 单例
    @classmethod
    def instance(cls):
        key = '__instance'
        if hasattr(cls, key):
            return getattr(cls, key)
        else:
            instance = Tk()
            setattr(cls, key, instance)
            return instance

    # 界面绘制
    def layout(self, username, password, remember, auto, click):
        self.username.set(username)
        self.password.set(password)
        self.remember.set(remember)
        self.auto.set(auto)
        tk.Label(text='账号').grid(row=0, padx=10, pady=10)
        tk.Label(text='密码').grid(row=1)
        tk.Entry(textvariable=self.username, width=30).grid(row=0, column=1)
        tk.Entry(textvariable=self.password, width=30).grid(row=1, column=1)
        tk.Checkbutton(text='记住密码', variable=self.remember).grid(row=2, column=1, sticky='W', pady=10)
        tk.Checkbutton(text='自动学习', variable=self.auto).grid(row=2, column=1, sticky='E')
        self.button = tk.Button(text='开始学习', command=click, padx=10, pady=5)
        self.button.grid(row=0, rowspan=2, column=2, padx=20)
        tk.Label(textvariable=self.time, font='Arial 18', fg='red').grid(row=2, column=2)
        tk.Label(text='记住密码：点击开始学习按钮后，自动保存本次输入的账号密码').grid(row=0, column=3, sticky='W')
        tk.Label(text='自动学习：下次打开study.exe，10秒后自动开始学习', ).grid(row=1, column=3, sticky='W')
        tk.Label(text='日志输出：').grid(row=3, column=0, sticky='en')

    # 自动学习倒计时
    def count_down(self, count_down):
        self.button['state'] = 'disabled'
        if count_down > 0:
            self.time.set(count_down)
            log('%s 秒后开始学习' % count_down)
            count_down -= 1
            self.tk.after(1000, self.count_down, count_down)
        else:
            self.button['state'] = 'normal'
            study.study_btn_click()

    # 输出日志
    def logging(self, value, warn=False):
        time.sleep(1)
        self.log.insert('end', '%s ------- %s -------%s\n' %
                        (time.strftime('%Y-%m-%d %H:%M:%S'), value, '（异常）' if warn else ''))

    # tk主界面启动
    def mainloop(self):
        self.tk.mainloop()

    # 退出程序
    def quit(self):
        self.tk.quit()

    # 测试用
    def test(self, value=None):
        if isinstance(value, dict):
            for k, v in value.items():
                self.log.insert('end', '%s ： %s \n ' % (k, v))
        elif isinstance(value, list):
            for v in value:
                self.log.insert('end', '%s , ' % (v,))
        else:
            self.log.insert('end', '%s , ' % (value,))


# 多线程
def t(func, args):
    tt = threading.Thread(target=func, args=args)
    tt.setDaemon(True)
    tt.start()


# 全局函数-输出日志
def logging():
    instance = Tk.instance()
    return instance


# 输出日志
def log(value, warn=False):
    t(logging().logging, (value, warn))


# 显示测试数据
def test(value):
    t(logging().test, (value,))


# 账户操作
class Account(object):
    def __init__(self):
        self.count_down = 10
        self.tk = Tk.instance()
        log('获取账户信息')
        self.account = configparser.ConfigParser()
        self.account.read(account_file_name)
        self.remember = self.account['main']['remember']
        self.auto = self.account['main']['auto']
        if self.remember == '1':
            self.username = self.account['main']['username']
            self.password = self.account['main']['password']
        self.api = self.get_api()
        log('获取账户信息（成功）')

    def save_account(self):
        log('保存登录状态')
        self.username = self.tk.username.get()
        self.password = self.tk.password.get()
        self.account['main'] = {
            'username': '' if self.tk.remember.get() == '0' else self.username,
            'password': '' if self.tk.remember == '0' else self.password,
            'remember': self.tk.remember.get(),
            'auto': self.tk.auto.get(),
        }
        log('保存登录状态（成功）')
        self.account.write(open('account.conf', 'w'))

    # 获取api
    @staticmethod
    def get_api():
        api_config = configparser.RawConfigParser()
        api_config.read(api_file_name, encoding='utf-8')
        api = {}
        host = ''
        api['corpcode'] = api_config['code']['corpcode']
        for v in api_config.items('api'):
            if v[0] == 'host':
                host = v[1]
            else:
                api[v[0]] = '%s%s' % (host, v[1])
        return api


# http操作
class Http(object):
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }

    @classmethod
    def instance(cls):
        key = '__instance__'
        if hasattr(cls, key):
            return getattr(cls, key)
        else:
            instance = Http()
            setattr(cls, key, instance)
            return instance

    def get_session_id(self):
        return self.session.cookies.get('eln_session_id')

    def post(self, url, params=None, json_ret=True):
        if not params:
            params = {'elsSign': self.get_session_id()}
        else:
            params.update({'elsSign': self.get_session_id()})
        r = self.session.post(url, params, headers=self.headers)
        if json_ret:
            return r.json()
        return r.text

    def get(self, url, params={}, json_ret=True):
        params.update({'elsSign': self.get_session_id()})
        r = self.session.get(url, params=params, headers=self.headers)
        if json_ret:
            return r.json()
        return r.text


# 学习程序主体
class Study(object):
    def __init__(self):
        self.tk = Tk.instance()
        self.account = Account()
        self.http = Http.instance()
        # 课程评估判断,每次运行只运行一次，防止评估失败导致死循环
        self.assess = True

    # 学习程序启动
    def start(self):

        # tk界面布局
        self.tk.layout(self.account.username, self.account.password, self.account.remember, self.account.auto,
                       self.study_btn_click)
        # 自动学习勾选状态
        if self.account.auto == '1':
            self.tk.count_down(self.account.count_down)

        # tk界面启动
        self.tk.mainloop()

    # 开始学习按钮
    def study_btn_click(self):
        if self.tk.button['text'] == '停止学习':
            self.tk.quit()
        else:
            self.tk.button['text'] = '停止学习'
            self.log_in()

    # 登陆
    def log_in(self):
        log('正在登陆')
        username = self.tk.username.get()
        password = self.tk.password.get()
        api = self.account.api
        params = {
            'corpCode': api['corpcode'],
            'loginName': username,
            'password': password,
            'returnUrl': 'http://tianan-cyber.21tb.com/os/html/index.init.do',
            'courseId': '',
            'securityCode': '',
            'continueLogin': 'true',
            'hyperEspCode': ''
        }
        r = self.http.post(api['login'], params=params)
        if self.http.get_session_id():
            log('%s 登录成功' % username)
            self.tk.time.set('学习中')
            self.account.save_account()
            self.get_my_course()
        else:
            # 密码正确，时间受限，也保存账户状态
            log(r.get('message'), True)
            if r.get('message') == '您受到登录时间段的限制!':
                self.account.save_account()
            self.tk.button['text'] = '开始学习'
            self.tk.time.set('')

    # 获取我的选课
    def get_my_course(self):
        log('进入我的课程')
        params = {
            'courseType': 'NEW_COURSE_CENTER',
            'page.pageSize': '100',
            'page.sortName': 'STUDYTIME',
            'page.pageNo': '1',
            'courseStudyRecord.courseStatus': 'STUDY',
            '_': int(time.time())
        }
        log('获取我的课程')
        r = self.http.get(self.account.api['my_course'], params)
        rows = r.get('rows')
        course_list = []
        course_need_assess = []
        # 获取课程列表
        # 有学分的课程，即学完的课程，不管
        # 没有学分的课程，看完视频的，需要评估获取学分
        # 没看完视频的，继续看视频
        # 看完视频，重新获取课程列表，重新执行此循环
        for i in rows:
            # 有分数的课程
            if i.get('getScoreTime') is not None:
                continue
            # 未学完的课程加入到列表
            # 只获取可评估的课程
            if i.get('stepToGetScore') == 'COURSE_EVALUATE':
                try:
                    f = float(i.get('currentStepRate'))
                    if f == 100.0:
                        # 视频看完需要评估
                        log('有看完的课程，需要评估以获取学分')
                        obj = {
                            'id': i.get('courseId'),
                            'name': i.get('courseName')
                        }
                        course_need_assess.append(obj)
                    else:
                        # 需要看视频的课程
                        log('有未看完的课程:%s' % i.get('courseName'))
                        obj = {
                            'id': i.get('courseId'),
                            'name': i.get('courseName')
                        }
                        course_list.append(obj)
                except Exception as e:
                    log('currentStepRate异常：%s-%s' % (i.get('currentStepRate'), type(i.get('currentStepRate'))))

        # 有评估先评估
        if len(course_need_assess):
            if self.assess:
                log('优先评估获取学分')
                t(self.get_score, (course_need_assess,))
                return
            else:
                log('尝试评估失败，跳过评估，继续学习')
        #  无课就选，有课可看就看
        if not len(course_list):
            log('无已选课程，选择新课程')
            self.select_course()
        else:
            log('获取课程（%s门）' % (len(course_list)))
            t(self.study, (course_list[0],))

    # 评估以获取学分
    def get_score(self, course_list):
        for course in course_list:
            course_id = course['id']
            course_name = course['name']
            log('开始评估：%s' % course_name)
            # self.http.post('http://tianan-cyber.21tb.com/els/html/course/course.checkUserCanStudyCourse.do',{'courseId':{})
            # self.http.post('http://tianan-cyber.21tb.com/els/html/studyCourse/studyCourse.checkUserScoInitComplete.do',course_id)
            # self.http.post('http://tianan-cyber.21tb.com/els/html/courseInfo/courseinfo.checkOlineUrlHttp.do',course_id)
            # self.http.post('http://tianan-cyber.21tb.com/els/html/courseInfo/courseinfo.checkMsUrl.do',course_id)

            time.sleep(3)
            param_star = {
                'star': '5',
                'courseId': course_id
            }
            r_star = self.http.post(self.account.api['save_star'], param_star)
            if r_star.get('success'):
                param_selection = {
                    'willGoStep': 'COURSE_EVALUATE',
                    'answers': json.dumps([
                        {'name': 'f766d1ca2a2847e897bee3df17e2cec5', 'value': '447a40ed37cf41faa48e9d31960edf2e'},
                        {'name': '9b62c4ea9e304256bc6bb8fab0dab0f1', 'value': 'b70124d460e34d2da4fdfff684b3add1'},
                        {'name': '8f6de1d1f49b4f1483a8a5fceac6894b', 'value': '913239e0041a434aa350de208106d229'},
                        {'name': '3ba4bdce9d4b48a6be84b1c62edd6a76', 'value': '808261399ffb4e0fa3a2e65e533170ac'},
                        {'name': '703b4ee66a5c49729221f0395066c9df', 'value': ''}
                    ]),
                    'courseId': course_id,
                    'courseType': 'NEW_COURSE_CENTER',
                }
                r_selection_choice = self.http.post(self.account.api['selection_choice'], param_selection)
                log('评估成功！获得学分 %s' % r_selection_choice.get('courseScore'))
        log('全部课程评估完毕，选择新课继续学习')
        self.assess = False
        self.get_my_course()

    # 选择新课程
    def select_course(self):
        # 全部选课——课程评估——未选
        log('获取课程中心')
        get_course = {
            'courseType': 'NEW_COURSE_CENTER',
            'courseInfo.courseStatus': 'UNCHECKED',
            'courseInfo.stepToGetScore': 'COURSE_EVALUATE',
            'page.pageSize': '12',
            'page.pageNo': '1',
            'page.sortName': 'publishDate',
            'courseStudyRecord.courseStatus': 'STUDY',
            '_': int(time.time())
        }
        # 获取课程
        r = self.http.get(self.account.api['course_center'], get_course)
        # 课程列表
        rows = r.get('rows')
        # 选择一个课程
        course_id = rows[0]['courseId']
        course_name = rows[0]['courseTitle']
        # 确认选课
        confirm = {
            '_': int(time.time())
        }
        r_confirm = self.http.get(self.account.api['select_confirm'], confirm)
        if r_confirm.get('success'):
            select_course = {
                'courseId': course_id,
                'timeLimit': 'noLimit',
                '_': int(time.time())
            }
            r_select = self.http.post(self.account.api['select_course'], select_course)
            if r_select.get('status') == '200':
                # 选课成功，重新获取课程列表，开始学习
                if r_select.get('message') == '操作成功！！':
                    log('选课成功： %s' % course_name)
                    log('返回课程中心继续学习')
                    self.get_my_course()

    # 开始学习
    def study(self, course):
        time_step = 180
        log('学习课程：%s' % (course['name']))
        self.http.post(self.account.api['enter_course'] % course['id'], json_ret=False)
        course_api = self.account.api['course_show'] % course['id']
        log('获取课程地址： %s' % course_api)
        self.http.post(course_api, json_ret=False)
        item_list = self.get_course_item(course['id'])
        log('获取课程列表')
        # 展示课程
        log('有子课 %s 门' % len(item_list))
        log('开始学习')
        for index, v in enumerate(item_list):
            sco_id = v['id']
            log('开始学习：%s-%s' % (index + 1, v['name']))
            location = self.select_item(course['id'], sco_id)
            cnt = 0
            while True:
                location += time_step * cnt
                cnt += 1
                log('课程进度： %s' % location)
                self.do_heartbeat()
                self.update_time_step()
                ret = self.do_save(course['id'], sco_id, location)
                if ret:
                    log('子课程已完成： %s' % v['name'])
                    break
                log('学习%s秒后继续' % time_step)
                time.sleep(time_step)
        #   子课全部学完，重新获取课程列表
        log('子课全部学完：%s' % course['name'])
        self.get_my_course()

    # 获取课程下的子课
    def get_course_item(self, course_id):
        url = self.account.api['course_item'] % course_id
        r = self.http.get(url)
        children = r['children']
        item_list = []
        for item in children:
            if len(item['children']) == 0:
                obj = {
                    'name': item['text'],
                    'id': item['id']
                }
                item_list.append(obj)
            else:
                for i in item['children']:
                    obj = {
                        'name': i['text'],
                        'id': i['id']
                    }
                    item_list.append(obj)
        return item_list

    # 获取课程进度
    def select_item(self, course_id, sco_id):
        params = {
            'courseId': course_id,
            'scoId': sco_id,
            'firstLoad': 'true'
        }
        r = self.http.post(self.account.api['select_resource'], params)
        try:
            location = float(r['location'])
        except Exception as e:
            location = 0.1

        select_check_api = self.account.api['select_check']
        api = select_check_api % (course_id, sco_id)
        re = self.http.post(api, json_ret=False)
        return location

    # 防挂机心跳
    def do_heartbeat(self):
        r = ''
        log('防挂机心跳发送')
        try:
            r = self.http.post(self.account.api['heartbeat'], {'_ajax_toKen': 'os'})
            log('心跳发送成功，%s' % r.get('success'))
        except Exception as e:
            log('失败：%s' % r.get('failure'))
            log('失败日志：%s' % str(r))

    # 与服务器同步刷新学习记录
    def update_time_step(self):
        r = self.http.post(self.account.api['update_time_step'])
        log('同步学习记录：%s' % r.strip('"').capitalize())

    # 保存进度条
    def do_save(self, course_id, sco_id, location):
        log('保存进度条')
        params = {
            'courseId': course_id,
            'scoId': sco_id,
            'location': location,
            'logId': '',
            'current_app_id': ''
        }
        r = self.http.post(self.account.api['save_progress'], params)
        try:
            if not r:
                params_res = {'courseId': course_id, 'scoId': sco_id}
                r2 = self.http.post(self.account.api['select_resource'], params_res)
                if r2.get('isComplete') == 'true':
                    return True
            # log('courseProgress:%s' % r.get('courseProgress', '-'))
            # log('completeRate:%s' % r.get('completeRate'))
            # log('completed:%s' % r.get('completed', '-'))
            if r.get('completed', '-') == 'true':
                log('保存进度条（成功）')
                return True
        except Exception as e:
            log(e)
        return False


if __name__ == '__main__':
    study = Study()
    study.start()
