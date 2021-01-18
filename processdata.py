'''
author: 王晨朔
time: 2021-01-11 12:13:51

preprocess data, convert weibodatabase.sql into data.nt

for nodes, we name it direcly with its information, except for uid and mid, wiich we name it as '<uid/xxxx>' and '<mid/xxxx>'

for edges, if from uid/mid to information, the edge type woule be tihe type of information related, for which is convience for match; if the edge is between uid/mids, edge type would be "userrelation", "uid", or "mid" (please refer to func processSqlInserts for details)
'''

import re
import time
from tqdm import tqdm

def mergeandmove(lst):
    '''
    input: a list [1,2,3,4...]
    output: a list [12, ,3,4...]
    '''
    res = [lst[0] + ", " + lst[1]]
    for i in lst[2:]:
        res.append(i)
    return res

def removelr(text):
    '''
    remove <> in text
    '''
    text = re.sub(">", "》》", text)
    text = re.sub("<", "《《", text)
    text = re.sub(' ', 'kgkgkgkgkgkgkgkg', text)
    return text

def restorelr(text):
    '''
    restore <>  from 《《 or 》》in text
    '''
    text = re.sub("》》", ">", text)
    text = re.sub("《《", "<", text)
    text = re.sub('kgkgkgkgkgkgkgkg', ' ', text)
    return text

def processSqlInserts(tf, text, logger):
    '''
    input: 
        tf: write target_file
        text: string formatted as lines of 'INSERT INTO `table` VALUES ();'
        logger: write logs
    output: write <><><> triplets directly
    NOTE: 
        1. part of user and weibo informations are omitted, #TODO
        2. 
    '''
    sql_lst = text.split("\n")
    for i in tqdm(range(len(sql_lst))):
        sql_query = sql_lst[i]
        info = re.findall("VALUES (\(.*?\));$", sql_query)
        relation_type = re.findall("INSERT INTO `(.*?)` VALUES", sql_query) # tabel name in mySQL, 'user', 'userrelation', 'weibo', 'weiborelation'
        if info == [] or relation_type == []:
            logger.write(sql_query) # record the failed sentences, and add it to .nt file by hand
            logger.write("\n")
        else:
            info = [i[1:-1] if i[0]=='\'' else i for i in info[0][1:-1].split(", ")] # remove ' there may exist , in weibo tex, so naive split would fail!! merged after.
            relation_type = relation_type[0]
            if relation_type == 'user':
                tf.write("<uid/%s>\t<name>\t<%s>.\n" % (info[0], removelr(info[2])))
                # tf.write("<uid/%s>\t<pwd>\t<%s>.\n" % (info[0], ''))
                # tf.write("<uid/%s>\t<email>\t<%s>.\n" % (info[0], ''))
                tf.write("<uid/%s>\t<loc>\t<%s>.\n" % (info[0], re.sub(' ', '-', info[5])))
                tf.write("<uid/%s>\t<followersnum>\t<%s>.\n" % (info[0], info[8]))
                tf.write("<uid/%s>\t<friendsnum>\t<%s>.\n" % (info[0], info[9]))
            elif relation_type == 'userrelation':
                tf.write("<uid/%s>\t<userrelation>\t<uid/%s>.\n" % (info[0], info[1])) # treat as directed, from source to target
            elif relation_type == 'weibo':
                while len(info[3]) == 0 or info[3][0] != '<': # if the text of weibo were cutted by ', ', then merge that
                    info = info[:2] + mergeandmove(info[2:])
                tf.write("<mid/%s>\t<date>\t<%s>.\n" % (info[0], info[1]))
                tf.write("<mid/%s>\t<text>\t<%s>.\n" % (info[0], removelr(info[2])))
                tf.write("<mid/%s>\t<source>\t<%s>.\n" % (info[0], re.sub("<.*?>", "", info[3]))) # remove <a href='balabala'>
                tf.write("<mid/%s>\t<uid>\t<uid/%s>.\n" % (info[0], info[7]))
                tf.write("<uid/%s>\t<mid>\t<mid/%s>.\n" % (info[7], info[0]))
            elif relation_type == 'weiborelation':
                pass

if __name__ == "__main__":

    logger = open("processdata.log", "w") # logfile records the failed lines during converting
    target_file = open("data.nt", "w")
    f = open("weibodatabase.sql")
    text = f.read()
    f.close()
    processSqlInserts(target_file, text, logger)
    target_file.close()
    logger.close()