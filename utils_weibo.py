'''
author: 段炼
time: 2021-01-16 10:32:29

provide functions for back end
'''

import re
import time
import random
# from flask import Flask, jsonify
from utils_gstore import * # query(), insert(), delete()
from processdata import removelr, restorelr
from gStore.api.http.python.src.GstoreConnector import *

# for requirement 1

def _login(gc, email, pwd):
    '''
    input: 
        gc: GstoreConnector
        email: e.g. 'asd@123.com'
        pwd: password, e.g. 'asd123'
    output:
        log in status
    '''
    r = query(gc, [email, "pwd", ''])
    if r[0] == pwd:
        uid = query(gc, ['', "email", email])[0][4:]
        return 'log in successed', uid
    else:
        return 'wrong password', ''

def _register(gc, email, username, pwd):
    '''
    input: 
        gc: GstoreConnector
        email: e.g. 'asd@123.com'
        username: e.g. 'asdasdasd'
        pwd: password, e.g. 'asd123'
    output:
        1 if succeed, 0 if failed
    '''
    judge_success = 0
    uid = random.randint(4000000000, 9000000000)
    judge_success += insert(gc, ['uid/%d' % uid, 'name', username])
    judge_success += insert(gc, ['uid/%d' % uid, 'email', email])
    judge_success += insert(gc, ['uid/%d' % uid, 'pwd', pwd])
    judge_success += insert(gc, ['uid/%d' % uid, 'loc', '北京大学王选计算机研究所'])
    judge_success += insert(gc, ['uid/%d' % uid, 'followersnum', 0])
    judge_success += insert(gc, ['uid/%d' % uid, 'friendsnum', 0])
    judge_success += insert(gc, [email, 'pwd', pwd])
    if judge_success == 7:
        return 1
    else:
        return 0

def _userinfo(gc, uid):
    '''
    input:
        gc: GstoreConnector
        uid, e.g. '1637970500'
    output:
        4 dict, e.g. {0: '荒野大飙客---jeep'}, {0: '2390'}, {0: '436'}, {0: '辽宁-沈阳'}
    '''
    name = dict()
    followersnum = dict()
    friendsnum = dict()
    loc = dict()
    name[0] = query(gc, ["uid/%s" % uid, "name", ''])[0]
    followersnum[0] = query(gc, ["uid/%s" % uid, "followersnum", ''])[0]
    friendsnum[0] = query(gc, ["uid/%s" % uid, "friendsnum", ''])[0]
    try:
        loc[0] = query(gc, ["uid/%s" % uid, "loc", ''])[0]
    except:
        loc[0] = ' ' # in case a new registered user don't have a location
    return name, followersnum, friendsnum, loc

def _changeinfo(gc, uid, newloc):
    '''
    if delete, newloc = ' '
    if change, newloc = new loc
    if add, newloc = new loc
    input:
        gc: GstoreConnector
        uid, e.g. '1637970500'
    output:
        1 = succeed, 0 = failed
    '''
    judge_success = 0
    oldloc = query(gc, ['uid/%s' % uid, 'loc', ''])
    judge_success += delete(gc, ['uid/%s' % uid, 'loc', oldloc[0]])
    judge_success += insert(gc, ['uid/%s' % uid, 'loc', re.sub(" ", "-", newloc)])
    if judge_success == 2:
        return 1
    else:
        return 0
    return 

# for requirement 2

def _userfollowing(gc, uid):
    '''
    input:
        gc: GstoreConnector
        uid, e.g. '2494667455'
    output:
        a following uid list of uid, e.g. ['1182391231', '2803301701', '2656274875', '3034112034', '3141880141', '1937187173', '2853316154']
    '''
    return [i[4:] for i in query(gc, ["uid/%s" % uid, "userrelation", ''])]

def myfollowings(gc, uid):
    '''
    input:
        gc: GstoreConnector
        uid, e.g. '2494667455'
    output:
        detailed dictionaries of a uid's friends, e.g. {0: '1182391231', 1: '2803301701', 2: '2656274875', 3: '3034112034', 4: '3141880141', 5: '1937187173', 6: '2853316154'}, {0: '潘石屹', 1: '人民日报', 2: '央视新闻', 3: '我们都是甘肃人', 4: '食品界姜昆', 5: '甘肃发布', 6: '王旭江营养师'}, {0: '16856984', 1: '19977043', 2: '18249317', 3: '85475', 4: '14957', 5: '2700471', 6: '1623'}, {0: '90', 1: '272', 2: '172', 3: '529', 4: '2234', 5: '302', 6: '1255'}
        and location informations
    '''
    flist = _userfollowing(gc, uid)
    uiddict = dict()
    name = dict()
    followersnum = dict()
    friendsnum = dict()
    loc = dict()
    for i in range(len(flist)):
        fid = flist[i]
        finfo = _userinfo(gc, fid)
        uiddict[i] = fid
        name[i] = finfo[0][0]
        followersnum[i] = finfo[1][0]
        friendsnum[i] = finfo[2][0]
        loc[i] = finfo[3][0]
    return uiddict, name, followersnum, friendsnum, loc

def _userweiboid(gc, uid):
    '''
    input:
        gc: GstoreConnector
        uid, e.g. '2494667455'
    output:
        all weibo mids of a uid, a list, e.g. ['3706605815083743', '3706579930616591', '3708732549328579', '3709040477431142']
    '''
    return sorted([i[4:] for i in query(gc, ["uid/%s" % uid, "mid", ''])], reverse=True)

def _getaweibo(gc, mid):
    '''
    input:
        gc: GstoreConnector
        uid, e.g. '3708732549328579'
    output:
        a dict of details of a weibo, e.g. {0: '2014-05-10 17:30:05'}, {0: '【兰州治理雾霾水炮霸气亮相[吃惊]】兰州东方红广场，两台军绿色炮筒式的机器引得民众围观。据记者了解，这种治理雾霾的高射远程风送式喷雾机，可将自来水雾化并喷出600米远的水雾，对雾霾、粉尘比较大的施工场地都有除尘及降温的作用。PS：省城的世界咱不懂，感觉高端、大气、上档次的样子！[奥特曼]'}, {0: '微博 weibo.com'}, {0: '2494667455'}
    '''
    date = dict()
    text = dict()
    source = dict()
    uid = dict()
    date[0] = query(gc, ["mid/%s" % mid, "date", ''])[0]
    text[0] = restorelr(query(gc, ["mid/%s" % mid, "text", ''])[0])
    source[0] = query(gc, ["mid/%s" % mid, "source", ''])[0]
    uid[0] = query(gc, ["mid/%s" % mid, "uid", ''])[0][4:]
    return date, text, source, uid

def userweibo(gc, uid):
    '''
    input:
        gc: GstoreConnector
        uid, e.g. '2494667455'
    output:
        all weibo details of a uid, a json, e.g. {0: '2014-05-04 20:39:13', 1: '2014-05-04 18:56:23', 2: '2014-05-10 17:30:05', 3: '2014-05-11 13:53:43'}, {0: '兰州的房价也不便宜啊！[崩溃][可怜]//@喵小姐的玻璃心: 去兰州买房子吧！', 1: '【4月兰州主城区房屋均价为7479元/㎡ 今年以来第三次下跌】中国指数研究院5月1日发布的数据显示，4月份，中国100个城市(新建)住宅平均价格为每平方米11013元人民币，环比上涨0.10%。兰州方面，4月份，兰州主城区房屋均价为7479元/㎡，环比下跌1.29%。http://t.cn/8sBwadt PS：天水房价会降吗？[思考]', 2: '【兰州治理雾霾水炮霸气亮相[吃惊]】兰州东方红广场，两台军绿色炮筒式的机器引得民众围观。据记者了解，这种治理雾霾的高射远程风送式喷雾机，可将自来水雾化并喷出600米远的水雾，对雾霾、粉尘比较大的施工场地都有除尘及降温的作用。PS：省城的世界咱不懂，感觉高端、大气、上档次的样子！[奥特曼]', 3: '【西安雾炮车、兰州水炮 霸气亮相[吃惊]】近日，一台多功能抑尘车在西安新城区投入使用。而在兰州东方红广场，两台军绿色炮筒式的机器引得民众围观。据悉，此款“神器”在雾霾天可以进行液雾降尘、分解淡化空气中的颗粒浓度、以及降低PM2.5浓度，达到清洁净化空气的效果。PS：高大上的感觉！[奥特曼]'}, {0: '微博 weibo.com', 1: '微博 weibo.com', 2: '微博 weibo.com', 3: '微博 weibo.com'}, {0: '2494667455', 1: '2494667455', 2: '2494667455', 3: '2494667455'}
    '''
    mids = _userweiboid(gc, uid)
    print(mids)
    date = dict()
    text = dict()
    source = dict()
    uid = dict()
    fail_id = 0
    for i in range(len(mids)):
        mid = mids[i]
        try:
            w = _getaweibo(gc, mid)
            date[i - fail_id] = w[0][0]
            text[i - fail_id] = w[1][0]
            source[i - fail_id] = w[2][0]
            uid[i - fail_id] = w[3][0]
        except:
            fail_id += 1
    return date, text, source, uid

def _allweiboid(gc, uid):
    '''
    input:
        gc: GstoreConnector
        uid, e.g. '2494667455'
    output:
        all weibo mids of a uid's following friends in decending order(which is, from new to old), a list, e.g. ['3709310032673383', '3709300209751270', '3709298662375147', '3709124640197897',...
    '''
    fids = _userfollowing(gc, uid)
    res = []
    for f in fids:
        res += _userweiboid(gc, f)
    return sorted(res, reverse=True)

def allweibo(gc, uid, page = 0, num = 10):
    '''
    input:
        gc: GstoreConnector
        uid: e.g. '2494667455'
        page: the xth page
        num: weibo num per page
    output: 
        {0: '2014-05-12 07:44:51', 1: '2014-05-12 07:05:48', 2: '2014-05-12 06:59:39', 3: '2014-05-11 19:28:07', 4: '2014-05-11 19:20:27', 5: '2014-05-11 17:18:02', 6: '2014-05-11 16:04:12', 7: '2014-05-11 15:30:40', 8: '2014-05-11 13:33:23', 9: '2014-05-11 09:40:28'}, {0: '【[话筒]救命贴！】今天是国家防灾减灾日，地震、火灾、暴雨、雷电、雾霾、高温、沙尘暴、暴雪……遇到“要命”的自然灾害该怎么办？戳图↓↓↓9张图教你救命技能！扩散周知！', 1: '【汶川，雄起！】2008年5月12日14时28分04秒，四川汶川发生里氏8.0级地震。地震共造成69227人遇难，17923人失踪，37万多人受伤。“只有经历地狱般的磨难，才能炼出创造天堂的力量；只有流过血的手指，才能弹奏出世间的绝唱”。今天，#汶川地震6周年#，时光穿越灾难，也见证重生。祝福汶川，中国加油！', 2: '【写给成长的九封信】世界上唯一可以不劳而获的是贫穷，唯一可以无中生有的是梦想。九封信，写给迷茫、焦虑、不想碌碌无为的你，愿每一封都能对你有所启发。新的一周，早安。', 3: '【西安：“治霾神器”来啦[围观]】近日，西安新城区引进一台大型雾炮车。它负载的大型雾炮喷射水雾可达120米远、70米高，且颗粒极为细小。在雾霾天可进行液雾降尘、分解淡化空气中的颗粒浓度，将漂浮在空气中的污染颗粒物迅速逼降地面，达到清洁净化空气的效果。http://t.cn/8skwd7Z', 4: '【[话筒]警惕！手机病毒"窃听大盗"偷窃你的隐私！】"窃听大盗"手机病毒近日被截获，它通过论坛链接、扫描二维码等方式，骗取用户安装，无法正常卸载。感染后会偷录用户通话，窃取短信文本，调用摄像头偷拍，定位用户地理位置，窃取QQ、微信的语音、照片等，并直接发到木马作者的邮箱。提醒注意查杀！', 5: '【上海警方安检时查获两枚舰炮炮弹】5月11日下午，上海市青浦区西岑镇公安道口检查站民警在对过往车辆进行安检时，在一辆汽车后备箱发现两个包裹，用X光机检查发现包裹里装有两枚管状物品，经开箱检查，发现是2枚100毫米舰炮炮弹。目前车主已被警方控制，情况正在进一步调查中。(央视记者陆学贤 俞翔)', 6: '【母亲节，教妈妈用微博吧[心]】母亲节来临，@上海市公安局松江分局门卫 发表一组手绘画，教妈妈用微博：“妈妈，您说了好几次想玩微博，我知道这不是赶时髦，您就是想知道我过得怎么样[泪]。让儿子教您学会用微博，就像当初您手把手教我用计算器一样。”转给自己的妈妈，祝她一切安好，母亲节快乐！', 7: '【深圳狂风暴雨，大范围积涝，市民最好别出门！】今天上午6时30分至14时，深圳全市普遍记录到大暴雨，局部特大暴雨，最大降雨量达276.5毫米。深圳市气象局表示，这是当地自2008年以来最大的一场暴雨！目前暴雨红色预警正在生效，深圳大范围严重积涝，大家最好不要出门，请在室内躲避！！(央视记者陈喆)', 8: '【“治霾神器”亮相西安 】近日，西安新城区引进一台大型雾炮车。它负载的大型雾炮可喷射120米远、70米高的水雾，水雾颗粒极为细小，在雾霾天可以进行液雾降尘、分解淡化空气中的颗粒浓度、将漂浮在空气中的污染颗粒物迅速逼降地面，达到清洁净化空气的效果。你期待神器么？http://t.cn/8skwd7Z', 9: '【救救它们 刻不容缓！[泪]】母亲节，可能正有大象妈妈惨遭屠杀。肯尼亚表示，今年平均每2天就有一只大象被残杀。被砍断象牙惨死的母象，眼睛还死死盯着被盗猎者脱出母体暴晒的小象…李克强总理在内罗毕焚烧象牙纪念地强调，中国正严厉打击象牙非法贸易。没有买卖，就没有杀害。拒绝买卖！支持的转！'}, {0: '微博 weibo.com', 1: '人民日报微博', 2: '人民日报微博', 3: '人民日报微博', 4: '微博 weibo.com', 5: '微博 weibo.com', 6: '人民日报微博', 7: '微博 weibo.com', 8: '微博 weibo.com', 9: '微博 weibo.com'}, {0: '2656274875', 1: '2803301701', 2: '2803301701', 3: '2803301701', 4: '2656274875', 5: '2656274875', 6: '2803301701', 7: '2656274875', 8: '2656274875', 9: '2656274875'}
    '''
    mids = _allweiboid(gc, uid)
    date = dict()
    text = dict()
    source = dict()
    uid = dict()
    if num * page + num <= len(mids) - 1:
        r = range(num * page, num * page + num)
    elif num * page <= len(mids) - 1 and num * page + num > len(mids) - 1:
        r = range(num * page, len(mids))
    else:
        print('page num exceeds!')
    for i in r:
        mid = mids[i]
        w = _getaweibo(gc, mid)
        date[i] = w[0][0]
        text[i] = w[1][0]
        source[i] = w[2][0]
        uid[i] = w[3][0]
    return date, text, source, uid

def sendweibo(gc, uid, text):
    '''
    input: 
        gc: GstoreConnector
        uid: e.g. '2494667455'
        text: e.g. '123'
    output:
        1 if succeed, 0 if failed
    '''
    judge_success = 0
    mid = 4000000000000000 + int(time.time() * 10000)
    judge_success += insert(gc, ['mid/%d' % mid, 'date', str(time.strftime("%Y-%m-%d,%H:%M:%S", time.localtime()))]) # TODO 
    judge_success += insert(gc, ['mid/%d' % mid, 'text', removelr(text)]) # remove <>, which conflicts with triplet languages
    judge_success += insert(gc, ['mid/%d' % mid, 'source', 'Gstore客户端'])
    judge_success += insert(gc, ['mid/%d' % mid, 'uid', 'uid/%s' % uid])
    judge_success += insert(gc, ['uid/%s' % uid, 'mid', 'mid/%d' % mid])
    if judge_success == 5:
        return 1
    else:
        return 0

# for requirement 3

def myfollower(gc, uid):
    '''
    input:
        gc: GstoreConnector
        uid, e.g. '2494667455'
    output:
        {0: '3034112034', 1: '1937187173', 2: '3502379363', 3: '1991134077', 4: '2675741931', 5: '1636231703', 6: '2551449930', 7: '1708282850', 8: '3237311842', 9: '3732170811', 10: '1761616465', 11: '1181610342', 12: '2796751050', 13: '2687674807', 14: '1473275170', 15: '2379548461', 16: '1839854235', 17: '2425207004', 18: '1958203793', 19: '1789537050'}, {0: '我们都是甘肃人', 1: '甘肃发布', 2: '刘璟燕lily', 3: '居者不易', 4: 'yiyi太感性', 5: '刘小玉认真每一天', 6: '崛清', 7: '煜子儿', 8: 'XYB快乐成长', 9: '吉他弹给牛听', 10: '月中天', 11: '风向自由', 12: '郭露-_-', 13: '清汤挂面-yy', 14: '三金毛', 15: '苏武魁', 16: '木头鱼冬瓜', 17: '萍客', 18: '长驱直入你的心', 19: '尕荷'}, {0: '85475', 1: '2700471', 2: '84', 3: '474', 4: '522', 5: '510', 6: '473', 7: '3424', 8: '41', 9: '22', 10: '1392', 11: '2386', 12: '411', 13: '117', 14: '608', 15: '20', 16: '489', 17: '538', 18: '970', 19: '667'}, {0: '529', 1: '302', 2: '43', 3: '96', 4: '183', 5: '304', 6: '632', 7: '325', 8: '272', 9: '75', 10: '531', 11: '312', 12: '154', 13: '120', 14: '858', 15: '163', 16: '312', 17: '337', 18: '144', 19: '540'}
        and location informations
    '''
    flist = query(gc, ['', "userrelation", 'uid/%s' % uid])
    uiddict = dict()
    name = dict()
    followersnum = dict()
    friendsnum = dict()
    loc = dict()
    for i in range(len(flist)):
        fid = flist[i][4:]
        finfo = _userinfo(gc, fid)
        uiddict[i] = fid
        name[i] = finfo[0][0]
        followersnum[i] = finfo[1][0]
        friendsnum[i] = finfo[2][0]
        loc[i] = finfo[3][0]
    return uiddict, name, followersnum, friendsnum, loc

def _follow(gc, uid1, uid2):
    '''
    MUST make sure that 1 dose not follow 2 before!
    '''
    judge_success = 0
    judge_success += insert(gc, ['uid/%s' % uid1, 'userrelation', 'uid/%s' % uid2])
    followernum = int(query(gc, ['uid/%s' % uid2, 'followersnum', ''])[0])
    judge_success += delete(gc, ['uid/%s' % uid2, 'followersnum', followernum]) # change uid2's follower num
    judge_success += insert(gc, ['uid/%s' % uid2, 'followersnum', followernum + 1])
    if judge_success == 3:
        return 1
    else:
        return 0

def _unfollow(gc, uid1, uid2):
    '''
    MUST make sure that 1 followed 2 before!
    '''
    judge_success = 0
    judge_success += delete(gc, ['uid/%s' % uid1, 'userrelation', 'uid/%s' % uid2])
    followernum = int(query(gc, ['uid/%s' % uid2, 'followersnum', ''])[0])
    judge_success += delete(gc, ['uid/%s' % uid2, 'followersnum', followernum]) # change uid2's follower num
    judge_success += insert(gc, ['uid/%s' % uid2, 'followersnum', followernum - 1])
    if judge_success == 3:
        return 1
    else:
        return 0

# for requirement 4

def findrelation(gc, uid1, uid2):
    s = list()
    e = list()
    for i in [1,2,3,4]:
        start, end = multihopquery(gc, uid1, uid2, i)
        s += start
        e += end
    nodes = list(set(start + end))
    startdict = dict()
    enddict = dict()
    nodedict = dict()
    reversenodedict = dict()
    for i in range(len(nodes)):
        nodedict[i] = nodes[i]
        reversenodedict[nodes[i]] = i
    for i in range(len(s)):
        startdict[i] = reversenodedict[s[i]]
        enddict[i] = reversenodedict[e[i]]
    return nodedict, startdict, enddict

if __name__ == "__main__":

    gc = GstoreConnector("127.0.0.1", 12355, "root", "123456")

    time_start = time.time()

    # print(_register(gc, 'asd@123.com', 'asdasdasd', 'asd123'))
    # print(_login(gc, 'asd@123.com', 'asd123'))
    # print(_login(gc, 'asd@123.com', 'ass123'))
    # print(_login(gc, '1860096194@gstore.com', 'gstore'))
    # print(_userinfo(gc, '1637970500'))

    # print(_userfollowing(gc, '2494667455'))
    # print(myfollowings(gc, '2494667455'))
    # print(_userweiboid(gc, '2494667455'))
    # print(_getaweibo(gc, '3708732549328579'))
    print(userweibo(gc, '2494667455'))
    # print(_allweiboid(gc, '2494667455'))
    # print(allweibo(gc, '2494667455', page = 0))
    # print(allweibo(gc, '2494667455', page = 10))
    print(sendweibo(gc, '2494667455', '<><123>是事实和还得靠拉杀手锏撒客户端凯撒将回答是建行卡'))
    print(userweibo(gc, '2494667455'))

    # print(myfollowings(gc, '2494667455'))
    # print(myfollower(gc, '2494667455'))
    # print(_follow(gc, '2494667455', '1638781994'))
    # print(_unfollow(gc, '2494667455', '1638781994'))

    # print(findrelation(gc, '1994559105', '1692055890'))
    # print(_changeinfo(gc, '2167418067', 'gst'))

    time_end = time.time()
    print('time cost', time_end-time_start, 's')