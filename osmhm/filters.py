import connect
from sendNotification import sendNotification
from queries import *


def suspiciousFilter(changesets):
    """Set of rudimentary filters towards detecting possibly bad changesets.    

    1: Large amount of additions
    2: Large amount of modifications
    3: Large amount of deletions
    4: Large amount of combined actions
    5: High proportion of deletions
    6: High proportion of modifications
    """
    whitelist = query_white_list()

    conn = connect.connect()
    cur = conn.cursor()

    for changesetid, changeset in changesets.iteritems():
        if changeset['username'] in whitelist:
            continue
        if changeset['create'] > 1500:
            info = (changeset['timestamp'], changesetid,
                    changeset['username'].encode('utf8'),
                    1, changeset['create'])
            cur.execute("""INSERT INTO history_filters
                            (timestamp,changeset,username,flag,quantity)
                            VALUES (%s, %s, %s, %s, %s);""", info)
        if changeset['modify'] > 1500:
            info = (changeset['timestamp'], changesetid,
                    changeset['username'].encode('utf8'),
                    2, changeset['modify'])
            cur.execute("""INSERT INTO history_filters
                            (timestamp,changeset,username,flag,quantity)
                            VALUES (%s, %s, %s, %s, %s);""", info)
        if changeset['delete'] > 1500:
            info = (changeset['timestamp'], changesetid,
                    changeset['username'].encode('utf8'),
                    3, changeset['delete'])
            cur.execute("""INSERT INTO history_filters
                            (timestamp,changeset,username,flag,quantity)
                            VALUES (%s, %s, %s, %s, %s);""", info)
        if changeset['create'] + changeset['modify'] + changeset['delete'] > 1500:
            info = (changeset['timestamp'], changesetid,
                    changeset['username'].encode('utf8'),
                    4, changeset['create'] + changeset['modify'] + changeset['delete'])
            cur.execute("""INSERT INTO history_filters
                            (timestamp,changeset,username,flag,quantity)
                            VALUES (%s, %s, %s, %s, %s);""", info)
        if changeset['delete'] > 0 and float(changeset['create']+changeset['modify'])/float(changeset['delete']) < 0.001:
            info = (changeset['timestamp'], changesetid,
                    changeset['username'].encode('utf8'),
                    5, float(changeset['create']+changeset['modify'])/float(changeset['delete']))
            cur.execute("""INSERT INTO history_filters
                            (timestamp,changeset,username,flag,quantity)
                            VALUES (%s, %s, %s, %s, %s);""", info)
        if changeset['modify'] > 0 and float(changeset['create']+changeset['delete'])/float(changeset['modify']) < 0.001:
            info = (changeset['timestamp'], changesetid,
                    changeset['username'].encode('utf8'),
                    6, float(changeset['create']+changeset['delete'])/float(changeset['modify']))
            cur.execute("""INSERT INTO history_filters
                            (timestamp,changeset,username,flag,quantity)
                            VALUES (%s, %s, %s, %s, %s);""", info)

    cur.execute("UPDATE file_list SET read_flag = '%s';" % (True))
    conn.commit()


def userFilter(changesets):
    notifyList = []

    watchedUsers = query_user_list()

    conn = connect.connect()
    cur = conn.cursor()

    if watchedUsers:
        for changesetid, changeset in changesets.iteritems():
            for user in watchedUsers:
                if changeset['username'] == user:
                    info = (changeset['timestamp'], changesetid,
                            changeset['username'].encode('utf8'),
                            changeset['create'], changeset['modify'],
                            changeset['delete'])
                    cur.execute("""INSERT INTO history_users
                                (timestamp,changeset,username,create,modify,delete)
                                VALUES (%s, %s, %s, %s, %s, %s);""", info)
                    notifyList.append([info].append(user))

        conn.commit()
    if notifyList:
        sendNotification(notifyList, 'user')    


def objectFilter(objects):
    notifyList = []

    watchedObjects = query_object_list()

    conn = connect.connect()
    cur = conn.cursor()

    if watchedObjects:
        for obj in watchedObjects:
            for node in objects.nodes.values():
                if 'n'+str(node['id']) == obj:
                    info = (node['timestamp'], node['changeset'],
                            node['username'].encode('utf8'),
                            node['action'], 'n'+str(node['id']))
                    cur.execute("""INSERT INTO history_objects
                                    (timestamp,changeset,username,action,element)
                                    VALUES (%s, %s, %s, %s, %s);""", info)
                    notifyList.append(obj + [info])

            for way in objects.ways.values():
                if 'w'+str(way['id']) == obj:
                    info = (way['timestamp'], way['changeset'],
                            way['username'].encode('utf8'),
                            way['action'], 'w'+str(way['id']))
                    cur.execute("""INSERT INTO history_objects
                                    (timestamp,changeset,username,action,element)
                                    VALUES (%s, %s, %s, %s, %s);""", info)
                    notifyList.append(obj + [info])

            for relation in objects.relations.values():
                if 'r'+str(relation['id']) == obj:
                    info = (relation['timestamp'], relation['changeset'],
                            relation['username'].encode('utf8'),
                            relation['action'], 'r'+str(relation['id']))
                    cur.execute("""INSERT INTO history_objects
                                    (timestamp,changeset,username,action,element)
                                    VALUES (%s, %s, %s, %s, %s);""", info)
                    notifyList.append(obj + [info])

        conn.commit()
    if notifyList:
        sendNotification(notifyList, 'object')
