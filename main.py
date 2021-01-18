'''
author: 王晨朔
time: 2021-01-16 10:32:29

back end functions
'''

import time
import random
# from flask import Flask, jsonify
from utils_gstore import * # query(), insert(), delete()
from utils_weibo import * 
from processdata import removelr, restorelr
from gStore.api.http.python.src.GstoreConnector import *

def login(email, pwd):
    '''
    input: 
        email: e.g. 'asd@123.com'
        pwd: password, e.g. 'asd123'
    output:
        log in status, 'log in successed' or 'wrong password'
    '''
    time_start = time.time()
    gc = GstoreConnector("127.0.0.1", 12355, "root", "123456")

    judge_success = _login(gc, email, pwd)

    time_end = time.time()
    print('time cost', time_end-time_start, 's')

    return judge_success

def register(email, username, pwd):
    '''
    input: 
        email: e.g. 'asd@123.com'
        username: e.g. 'asdasdasd'
        pwd: password, e.g. 'asd123'
    output:
        1 if succeed, 0 if failed
    '''
    time_start = time.time()
    gc = GstoreConnector("127.0.0.1", 12355, "root", "123456")

    judge_success = _register(gc, email, username, pwd)

    time_end = time.time()
    print('time cost', time_end-time_start, 's')

    return judge_success

def userhomepage(visiter, host, pagenum=0):
    '''
    show a user's homepage
    input:
        visiter: uid of 'me', string, e.g. '2494667455'
        host: uid of 'you', string, e.g. '1637970500'
        pagenum: the xth page of weibo(10 weibo per page), int, e.g. 5
    output:
        hostinfo
            name: name of 'you'('1637970500')
            followersnum: num in the dataset, INSTEAD OF THE REAL NUMBER!!
            friendsnum: num in the dataset, INSTEAD OF THE REAL NUMBER!!
            loc: location
        hostweibo: 4 dict, each formatted as {id: value}, 
            date: e.g. {0: '2014-05-04 20:39:13', 1: '2014-05-04 18:56:23', 2: '2014-05-10 17:30:05', 3: '2014-05-11 13:53:43'}
            text
            source
            uid
        fo: 0=myself(visiter and host are same), 1=friend(<->), 2=following(->), 3=followed(<-)
    '''
    time_start = time.time()
    gc = GstoreConnector("127.0.0.1", 12355, "root", "123456")

    name, followersnum, friendsnum, loc = _userinfo(gc, host)
    jsonify(name)
    jsonify(followersnum)
    jsonify(friendsnum)
    jsonify(loc)

    date, text, source, uid = userweibo(gc, host)
    jsonify(date)
    jsonify(text)
    jsonify(source)
    jsonify(uid)

    followed = 0 # host -> visiter
    following = 0 # visiter -> host
    if host != visiter:
        if host in _userfollowing(gc, visiter):
            following = 1
        if visiter in _userfollowing(gc, host):
            followed = 1
    if following and followed:
        fo = 1
    elif following and not followed:
        fo = 2
    elif not following and followed:
        fo = 3
    else:
        fo = 0

    time_end = time.time()
    print('time cost', time_end-time_start, 's')

    return render_template()

def changeinfo(uid, newloc):
    '''
    change info(loc for now)
    '''
    time_start = time.time()
    gc = GstoreConnector("127.0.0.1", 12355, "root", "123456")

    judge_success = _changeinfo(gc, uid, newloc)

    time_end = time.time()
    print('time cost', time_end-time_start, 's')

    return judge_success

def weibopage(uid, page=0):
    '''
    show weibo from uid followed peoples
    input:
        uid: e.g. '2494667455'
        page: the xth page
    output: 4 dict
        date
        text
        source
        uid
    '''
    time_start = time.time()
    gc = GstoreConnector("127.0.0.1", 12355, "root", "123456")

    date, text, source, uid = allweibo(gc, uid, page = 0, num = 10)
    jsonify(date)
    jsonify(text)
    jsonify(source)
    jsonify(uid)

    time_end = time.time()
    print('time cost', time_end-time_start, 's')

    return render_template()

def sendweibo(uid, text):
    '''
    input: 
        uid: e.g. '2494667455'
        text: e.g. '123'
    output:
        1 if succeed, 0 if failed
    '''
    time_start = time.time()
    gc = GstoreConnector("127.0.0.1", 12355, "root", "123456")

    judge_success = sendweibo(gc, uid, text)

    time_end = time.time()
    print('time cost', time_end-time_start, 's')

    return judge_success

def userfollowing(uid):
    '''
    input:
        uid, e.g. '2494667455'
    output:
        uiddict
        name
    '''
    time_start = time.time()
    gc = GstoreConnector("127.0.0.1", 12355, "root", "123456")

    uiddict, name, _, _ = myfollowings(gc, uid)
    jsonify(uiddict)
    jsonify(name)

    # uiddict, name, followersnum, friendsnum = myfollowings(gc, uid)
    # jsonify(uiddict)
    # jsonify(name)
    # jsonify(followersnum)
    # jsonify(friendsnum)

    time_end = time.time()
    print('time cost', time_end-time_start, 's')

    return render_template()


def userfollower(uid):
    '''
    input:
        uid, e.g. '2494667455'
    output:
        uiddict
        name
    '''
    time_start = time.time()
    gc = GstoreConnector("127.0.0.1", 12355, "root", "123456")

    uiddict, name, _, _ = myfollower(gc, uid)
    jsonify(uiddict)
    jsonify(name)

    # uiddict, name, followersnum, friendsnum = myfollower(gc, uid)
    # jsonify(uiddict)
    # jsonify(name)
    # jsonify(followersnum)
    # jsonify(friendsnum)

    time_end = time.time()
    print('time cost', time_end-time_start, 's')

    return render_template()

def follow(uid1, uid2):
    '''
    MUST make sure that 1 dose not follow 2 before!
    output:
        1 if succeed, 0 if failed
    '''
    time_start = time.time()
    gc = GstoreConnector("127.0.0.1", 12355, "root", "123456")

    judge_success = _follow(gc, uid1, uid2)

    time_end = time.time()
    print('time cost', time_end-time_start, 's')

    return judge_success

def unfollow(uid1, uid2):
    '''
    MUST make sure that 1 followed 2 before!
    output:
        1 if succeed, 0 if failed
    '''
    time_start = time.time()
    gc = GstoreConnector("127.0.0.1", 12355, "root", "123456")

    judge_success = _unfollow(gc, uid1, uid2)

    time_end = time.time()
    print('time cost', time_end-time_start, 's')

    return judge_success

def multihop(uid1, uid2):
    '''
    find multihop graph uid1 -> uid2
    output:
        nodedict
        startdict
        enddict
    '''
    time_start = time.time()
    gc = GstoreConnector("127.0.0.1", 12355, "root", "123456")

    nodedict, startdict, enddict = findrelation(gc, uid, page = 0, num = 10)
    jsonify(nodedict)
    jsonify(startdict)
    jsonify(enddict)

    time_end = time.time()
    print('time cost', time_end-time_start, 's')

    return render_template()


if __name__ == "__main__":
    app.run(debug=True)