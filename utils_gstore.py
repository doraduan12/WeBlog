'''
author: 王晨朔
time: 2021-01-14 18:48:34

provide 3 basic func to query / insert / delete triplet

'''

import json
from gStore.api.http.python.src.GstoreConnector import *

def query(gc, triplet, return_type = 'node'):
    '''
    give 2 of 3, return the left one
    input: 
        gc: GstoreConnector
        triplet: a triplet list, 3 position in which is 'head entity, relation, tail entity', there must contains 2 items(any 2 is valid), othervise invalid
        return_type: 
            node: return matched modes
            triplet: return matched triplets
    output: result a list of lists, which are triplets queried from graph
    '''
    sql = 'SELECT *\nWHERE {\n'
    total_provided = 0
    is_empty = -1
    for i in range(3):
        if triplet[i] != '':
            sql += ('<%s>' % triplet[i])
            total_provided += 1
        else:
            sql += '?s'
            is_empty = i
    if total_provided < 2:
        return 'invalid'
    else:
        sql += '.\n}'
        res = gc.query("weibo", "json", sql)
        res = json.loads(res)
        bindings = res['results']['bindings']
        node_res = [bindings[i]['s']['value'] for i in range(len(bindings))]
        if return_type == 'node':
            return node_res
        else:
            triplet_res = [['','',''] for i in range(len(node_res))]
            for i in range(len(triplet_res)):
                triplet_res[i][0] = triplet[0]
                triplet_res[i][1] = triplet[1]
                triplet_res[i][2] = triplet[2]
                triplet_res[i][is_empty] = node_res[i]
            return triplet_res

def insert(gc, triplet):
    '''
    insert a triplet into db
    '''
    #TODO: judge valid
    #TODO: judge if is exist
    sql = '''
    INSERT DATA
        { 
        <%s> <%s> <%s> . 
        }
    ''' % (triplet[0], triplet[1], triplet[2])
    res = gc.query("weibo", "json", sql)
    # print(triplet, res)
    res = json.loads(res)
    return int(res["StatusMsg"] == 'update query returns true.') # return 1 if succeed

def delete(gc, triplet):
    '''
    find and delete a triplet from db
    '''
    #TODO: judge valid
    sql = '''
    DELETE DATA
        { 
        <%s> <%s> <%s> . s
        }
    ''' % (triplet[0], triplet[1], triplet[2])
    res = gc.query("weibo", "json", sql)
    res = json.loads(res)
    return int(res["StatusMsg"] == 'update query returns true.') # return 1 if succeed

def multihopquery(gc, s, e, num):
    '''
    find num-hop edges between start and end
    '''
    if num==1:
        sql = '''
        SELECT *
        WHERE {
            <uid/%s> <userrelation> <uid/%s> . 
            }
        ''' % (s, e)
    elif num==2:
        sql = '''
        SELECT *
        WHERE {
            <uid/%s> <userrelation> ?e1 . 
            ?e1 <userrelation> <uid/%s> . 
            }
        ''' % (s, e)
    elif num==3:
        sql = '''
        SELECT *
        WHERE {
            <uid/%s> <userrelation> ?e1. 
            ?e1 <userrelation> ?e2 . 
            ?e2 <userrelation> <uid/%s> . 
            }
        ''' % (s, e)
    elif num==4:
        sql = '''
        SELECT *
        WHERE {
            <uid/%s> <userrelation> ?e1 . 
            ?e1 <userrelation> ?e2 . 
            ?e2 <userrelation> ?e3 . 
            ?e3 <userrelation> <uid/%s> . 
            }
        ''' % (s, e)
    else:
        print('invalid hop num')
    res = gc.query("weibo", "json", sql)
    res = json.loads(res)
    res = res["results"]["bindings"]

    start = list()
    end = list()

    if num==1:
        if len(res) == 1:
            start.append(s)
            end.append(e)
    elif num==2:
        for i in range(len(res)):
            start.append(s)
            end.append(res[i]['e1']['value'][4:])
            start.append(res[i]['e1']['value'][4:])
            end.append(e)
    elif num==3:
        for i in range(len(res)):
            start.append(s)
            end.append(res[i]['e1']['value'][4:])
            start.append(res[i]['e1']['value'][4:])
            end.append(res[i]['e2']['value'][4:])
            start.append(res[i]['e2']['value'][4:])
            end.append(e)
    elif num==4:
        for i in range(len(res)):
            start.append(s)
            end.append(res[i]['e1']['value'][4:])
            start.append(res[i]['e1']['value'][4:])
            end.append(res[i]['e2']['value'][4:])
            start.append(res[i]['e2']['value'][4:])
            end.append(res[i]['e3']['value'][4:])
            start.append(res[i]['e3']['value'][4:])
            end.append(e)
    return start, end

if __name__ == "__main__":

    gc = GstoreConnector("127.0.0.1", 12355, "root", "123456")
    # res = query(gc, ['uid/1836546175', 'userrelation', ''])
    # res = insert(gc, ['a', 'b', 'd'])

    res = query(gc, ['uid/1860096194', 'email', ''])
    # res = query(gc, ['uid/1860096194', 'loc', ''])
    # res = query(gc, ['uid/1860096194', 'pwd', ''])
    res = query(gc, ['1860096194@gstore.com', 'pwd', ''])
    # res = query(gc, ['uid/1860096194', 'name', ''])

    # res = multihopquery(gc, '1994559105', '5014897108', 1)
    # res = multihopquery(gc, '1994559105', '1692055890', 1)
    # res = multihopquery(gc, '1994559105', '1692055890', 2)
    # res = multihopquery(gc, '1994559105', '1692055890', 3)
    # res = multihopquery(gc, '1994559105', '1692055890', 4)
    