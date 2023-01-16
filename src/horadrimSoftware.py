# B+ tee in python
import json
import math
import itertools
import os
import sys
import io
import time
from numpy.distutils.system_info import p
from os.path import exists


def sortfunc(lst, typeline, mode):
        isint = []

        for templine in typeline:
            cracked = templine.split()

            isint.append([cracked[0], '*0' in cracked])
        if mode == 0:
            lst.sort(key=lambda x: x[4] if [x[0], False] in isint else int(x[4]))
            lst.sort(key=lambda x: x[0])
            return lst
        if mode == 1:
            return isint


def jayson(typonamo, mode):
    if exists("nodes_" + typonamo + ".json"):
        filejay = open("nodes_" + typonamo + ".json", 'r')
        jaylines = filejay.readlines()
        hunt = 0
        tobereturned = set()
        for jayline in jaylines:
            if hunt > 0:
                hunt -= 1
                if (hunt == 3) or (hunt == 0 and '\"' in jayline):
                    if ":" in jayline:
                        hunt = 0
                        continue
                    jayline.strip('\"')
                    tobereturned.add(tuple(jayline.split()))
            if "    \"keys\": [\n" in jayline:
                hunt = 5
        if mode == 0:
            lsti = list(tobereturned)
            lsti.sort(key=lambda x: 10000 * x[3] + 100 * x[2] + x[1])
            return lsti


# print(jayson("angel", 0))
allTrees = []

counter = 0
if exists('id_txt'):
    id_file = open('id.txt', 'r')

    for line in id_file:
        counter = int(line.split()[-1])
    id_file.close()


# Node creation
class Node:
    id_iter = itertools.count(counter)

    def __init__(self, order=3, values=[], keys=[], nextKey=None, check_leaf=False):
        self.id = next(Node.id_iter)
        self.order = order
        self.values = values
        self.keys = keys
        self.nextKey = nextKey
        self.check_leaf = check_leaf
        id_f = open('id.txt', 'a')
        id_f.write(str(self.id) + ' ')
        id_f.close()
        # Node.class_counter += 1
        # parentDict[self] = parentDictValue
        # nodes.append(self)

    # Insert at the leaf
    def insert_at_leaf(self, leaf, value, key):

        if self.values:
            temp1 = self.values
            for i in range(len(temp1)):
                if value == temp1[i]:
                    self.keys[i].append(key)
                    break
                elif value < temp1[i]:
                    self.values = self.values[:i] + [value] + self.values[i:]
                    self.keys = self.keys[:i] + [[key]] + self.keys[i:]
                    break
                elif i + 1 == len(temp1):
                    self.values.append(value)
                    self.keys.append([key])
                    break
        else:
            self.values = [value]
            self.keys = [[key]]


# B plus tree
class BplusTree:
    def __init__(self, root, type, check_leaf=True, order=3):
        self.root = root
        self.root.check_leaf = check_leaf
        self.type = type
        self.treeNodes = []
        self.parentDict = {}
        allTrees.append(self)

    # Insert operation
    def insert(self, value, key):

        value = str(value)

        old_node = self.search(value)

        old_node.insert_at_leaf(old_node, value, key)

        if len(old_node.values) == old_node.order:
            node1 = Node(old_node.order)
            self.treeNodes.append(node1)
            node1.check_leaf = True
            self.parentDict[node1] = self.parentDict[old_node]
            # node1.parent = old_node.parent
            mid = int(math.ceil(old_node.order / 2)) - 1
            node1.values = old_node.values[mid + 1:]
            node1.keys = old_node.keys[mid + 1:]
            node1.nextKey = old_node.nextKey
            old_node.values = old_node.values[:mid + 1]
            old_node.keys = old_node.keys[:mid + 1]
            old_node.nextKey = node1
            self.insert_in_parent(old_node, node1.values[0], node1)

    # Search operation for different operations
    def search(self, value):
        current_node = self.root
        for key in current_node.keys:
            if type(key) is not Node:
                return current_node
        if len(current_node.keys) == 0:
            return current_node

        while not current_node.check_leaf:

            temp2 = current_node.values

            for idx in range(len(temp2)):

                if value == temp2[idx]:
                    if len(current_node.keys) > idx + 1:
                        if type(current_node.keys[idx + 1]) is list:
                            return current_node
                        current_node = current_node.keys[idx + 1]
                        break
                    else:
                        return current_node

                elif value < temp2[idx]:
                    if type(current_node.keys[idx]) is list:
                        return current_node
                    current_node = current_node.keys[idx]
                    break

                elif idx + 1 == len(current_node.values):
                    current_node = current_node.keys[idx + 1]
                    break

        return current_node

    def filter(self, value, operator):

        current_node = self.root

        if operator == '=':
            for key in current_node.keys:
                if type(key) is not Node:
                    return current_node
            if len(current_node.keys) == 0:
                return current_node

            while not current_node.check_leaf:
                temp2 = current_node.values
                for i in range(len(temp2)):
                    if value == temp2[i]:
                        if len(current_node.keys) > i + 1:
                            if type(current_node.keys[i + 1]) is list:
                                return current_node
                            current_node = current_node.keys[i + 1]
                            break
                        else:
                            return current_node

                    elif value < temp2[i]:
                        if type(current_node.keys[i]) is list:
                            return current_node
                        current_node = current_node.keys[i]
                        break

                    elif i + 1 == len(current_node.values):
                        current_node = current_node.keys[i + 1]
                        break
            return current_node

    # Find the node
    def find(self, value, key):
        l = self.search(value)
        for i, item in enumerate(l.values):
            if item == value:
                if key in l.keys[i]:
                    return True
                else:
                    return False
        return False

    # Inserting at the parent
    def insert_in_parent(self, n, value, ndash):
        if self.root == n:
            rootNode = Node(n.order)
            self.treeNodes.append(rootNode)
            rootNode.values = [value]
            rootNode.keys = [n, ndash]
            self.root = rootNode
            self.parentDict[n] = rootNode
            # n.parent = rootNode
            self.parentDict[ndash] = rootNode
            # ndash.parent = rootNode
            return

        parentNode = self.parentDict[n]
        temp3 = parentNode.keys
        for i in range(len(temp3)):
            if temp3[i] == n:
                parentNode.values = parentNode.values[:i] + \
                                    [value] + parentNode.values[i:]
                parentNode.keys = parentNode.keys[:i + 1] + [ndash] + parentNode.keys[i + 1:]
                if len(parentNode.keys) > parentNode.order:
                    parentdash = Node(parentNode.order)
                    self.treeNodes.append(parentdash)
                    self.parentDict[parentdash] = self.parentDict[parentNode]
                    # parentdash.parent = parentNode.parent
                    mid = int(math.ceil(parentNode.order / 2)) - 1
                    parentdash.values = parentNode.values[mid + 1:]
                    parentdash.keys = parentNode.keys[mid + 1:]
                    value_ = parentNode.values[mid]
                    if mid == 0:
                        parentNode.values = parentNode.values[:mid + 1]
                    else:
                        parentNode.values = parentNode.values[:mid]
                    parentNode.keys = parentNode.keys[:mid + 1]
                    for j in parentNode.keys:
                        # j.parent = parentNode
                        self.parentDict[j] = parentNode
                    for j in parentdash.keys:
                        # j.parent = parentdash
                        self.parentDict[j] = parentdash
                    self.insert_in_parent(parentNode, value_, parentdash)

    # Delete a node
    def delete(self, value, key):
        node_ = self.search(value)

        temp = 0
        for i, item in enumerate(node_.values):
            if item == value:
                temp = 1

                if key in node_.keys[i]:
                    if len(node_.keys[i]) > 1:
                        node_.keys[i].pop(node_.keys[i].index(key))
                    elif node_ == self.root:
                        node_.values.pop(i)
                        node_.keys.pop(i)
                    else:
                        node_.keys[i].pop(node_.keys[i].index(key))
                        del node_.keys[i]
                        node_.values.pop(node_.values.index(value))
                        self.deleteEntry(node_, value, key)
                else:
                    # print("Value not in Key")
                    return
        if temp == 0:
            # print("Value not in Tree")
            return

    # Delete an entry
    def deleteEntry(self, node_, value, key):

        if not node_.check_leaf:
            for i, item in enumerate(node_.keys):
                if item == key:
                    node_.keys.pop(i)
                    break
            for i, item in enumerate(node_.values):
                if item == value:
                    node_.values.pop(i)
                    break

        if self.root == node_ and len(node_.keys) == 1:
            self.root = node_.keys[0]
            self.parentDict[node_.keys[0]] = None
            # node_.keys[0].parent = None
            del node_
            return
        elif (len(node_.keys) < int(math.ceil(node_.order / 2)) and node_.check_leaf == False) or (
                len(node_.values) < int(math.ceil((node_.order - 1) / 2)) and node_.check_leaf == True):

            is_predecessor = 0
            # parentNode = node_.parent
            parentNode = self.parentDict[node_]
            PrevNode = -1
            NextNode = -1
            PrevK = -1
            PostK = -1
            for i, item in enumerate(parentNode.keys):

                if item == node_:
                    if i > 0:
                        PrevNode = parentNode.keys[i - 1]
                        PrevK = parentNode.values[i - 1]

                    if i < len(parentNode.keys) - 1:
                        NextNode = parentNode.keys[i + 1]
                        PostK = parentNode.values[i]

            if PrevNode == -1:
                ndash = NextNode
                value_ = PostK
            elif NextNode == -1:
                is_predecessor = 1
                ndash = PrevNode
                value_ = PrevK
            else:
                if len(node_.values) + len(NextNode.values) < node_.order:
                    ndash = NextNode
                    value_ = PostK
                else:
                    is_predecessor = 1
                    ndash = PrevNode
                    value_ = PrevK

            if len(node_.values) + len(ndash.values) < node_.order:
                if is_predecessor == 0:
                    node_, ndash = ndash, node_
                ndash.keys += node_.keys
                if not node_.check_leaf:
                    ndash.values.append(value_)
                else:
                    ndash.nextKey = node_.nextKey
                ndash.values += node_.values

                if not ndash.check_leaf:
                    for j in ndash.keys:
                        self.parentDict[j] = ndash
                        # j.parent = ndash

                self.deleteEntry(self.parentDict[node_], value_, node_)
                del node_
            else:
                if is_predecessor == 1:
                    if not node_.check_leaf:
                        ndashpm = ndash.keys.pop(-1)
                        ndashkm_1 = ndash.values.pop(-1)
                        node_.keys = [ndashpm] + node_.keys
                        node_.values = [value_] + node_.values
                        parentNode = self.parentDict[node_]
                        for i, item in enumerate(parentNode.values):
                            if item == value_:
                                p.values[i] = ndashkm_1
                                break
                    else:
                        ndashpm = ndash.keys.pop(-1)
                        ndashkm = ndash.values.pop(-1)
                        node_.keys = [ndashpm] + node_.keys
                        node_.values = [ndashkm] + node_.values
                        parentNode = self.parentDict[node_]
                        for i, item in enumerate(p.values):
                            if item == value_:
                                parentNode.values[i] = ndashkm
                                break
                else:
                    if not node_.check_leaf:
                        ndashp0 = ndash.keys.pop(0)
                        ndashk0 = ndash.values.pop(0)
                        node_.keys = node_.keys + [ndashp0]
                        node_.values = node_.values + [value_]
                        parentNode = self.parentDict[node_]
                        for i, item in enumerate(parentNode.values):
                            if item == value_:
                                parentNode.values[i] = ndashk0
                                break
                    else:
                        ndashp0 = ndash.keys.pop(0)
                        ndashk0 = ndash.values.pop(0)
                        node_.keys = node_.keys + [ndashp0]
                        node_.values = node_.values + [ndashk0]
                        parentNode = self.parentDict[node_]
                        for i, item in enumerate(parentNode.values):
                            if item == value_:
                                parentNode.values[i] = ndash.values[0]
                                break

                if not ndash.check_leaf:
                    for j in ndash.keys:
                        self.parentDict[j] = ndash
                if not node_.check_leaf:
                    for j in node_.keys:
                        self.parentDict[j] = node_
                if not parentNode.check_leaf:
                    for j in parentNode.keys:
                        self.parentDict[j] = parentNode


# allNodes = []
# parentDict = {}
bplustree = ''


def nodeCreator(node_list):
    # global allNodes
    for idx in range(len(node_list)):
        if node_list[idx].nextKey is None:
            pass
        else:
            for _node in node_list:
                if type(node_list[idx].nextKey) is dict and _node.id == node_list[idx].nextKey['id']:
                    # print(_node, 'node')
                    node_list[idx].nextKey = _node
        for key_idx in range(len(node_list[idx].keys)):
            if type(node_list[idx].keys[key_idx]) is not dict:
                pass
            else:
                for _node in node_list:
                    if type(node_list[idx].keys[key_idx]) is dict and _node.id == \
                            node_list[idx].keys[key_idx]['id']:
                        # print(_node, 'node')
                        node_list[idx].keys[key_idx] = _node


if exists('types.txt'):
    type_file = open('types.txt', 'r')
    for line in type_file:
        type_name = line.split()[0]
        type_file_name = 'bplus_' + type_name + '.json'
        if exists(type_file_name):
            parent_key_file_name = 'parent_keys_' + type_name + '.json'
            parent_value_file_name = 'parent_values_' + type_name + '.json'
            node_file_name = 'nodes_' + type_name + '.json'
            bplus_file_name = type_file_name
            bplus_json = open(bplus_file_name)
            bplus1 = json.load(bplus_json)
            allNodes = []

            if not exists(parent_key_file_name):
                b_root = Node(bplus1['root']['order'], bplus1['root']['values'], bplus1['root']['keys'],
                              bplus1['root']['nextKey'], bplus1['root']['check_leaf'])
                allNodes.append(b_root)
                for node in allNodes:
                    if node.id == bplus1['root']['id']:
                        bpluss = BplusTree(node, type_name, check_leaf=False)
                        bpluss.parentDict[node] = None
                        bpluss.treeNodes.append(node)
            if exists(parent_key_file_name):
                parent_keys_json = open(parent_key_file_name)
                parent_values_json = open(parent_value_file_name)
                nodes_json = open(node_file_name)

                parent_keys = json.load(parent_keys_json)
                parent_values = json.load(parent_values_json)
                nodes = json.load(nodes_json)

                parent_keys_json.close()
                parent_values_json.close()

                bpluss = ''
                for node in nodes:
                    n = Node(node['order'], node['values'], node['keys'], node['nextKey'], node['check_leaf'])
                    n.id = node['id']
                    allNodes.append(n)

                nodeCreator(allNodes)
                for node in allNodes:
                    if node.id == bplus1['root']['id']:
                        bpluss = BplusTree(node, type_name, check_leaf=False)

                for index in range(len(parent_values)):
                    for node in allNodes:
                        if parent_values[index] is None:
                            bpluss.parentDict[allNodes[index]] = None
                        elif parent_values[index]['id'] == node.id:
                            bpluss.parentDict[allNodes[index]] = node
                for node in allNodes:
                    bpluss.treeNodes.append(node)

inputFile = sys.argv[1]
outputFile = sys.argv[2]
file1 = open(inputFile)
Lines = file1.readlines()
TypeLines = []
if exists('types.txt'):
    typefile = open("types.txt", 'r')
    TypeLines = typefile.readlines()

logfile = open("horadrimLog.csv", 'a+')
outFile = open(outputFile, 'w')
for line in Lines:
    line = line.strip('\n')
    words = line.split()
    logfile.write(str(time.time()) + "," + line + ",")

    if words[0] == "create":
        if words[1] == "type":
            type_name_file = words[2]
            typename = words[2]
            mightabort = 0
            for tyline in TypeLines:
                tywords = tyline.split()
                if len(tywords) <= 0:
                    continue
                if tywords[0] == typename:
                    logfile.write("failure\n")
                    mightabort = 1
            if mightabort:
                continue
            fieldnum = int(words[3])
            if fieldnum > 12:
                logfile.write("failure\n")
                continue
            primnum = int(words[4])
            if primnum > fieldnum:
                logfile.write("failure\n")
                continue
            newtype = [""]
            for i in range(1, fieldnum + 1):
                isprim = ""
                if i == primnum:
                    newtype[0] = words[4 + 2 * i - 1]
                    isprim = "*"
                else:
                    isprim = "+"
                isint = ""
                if words[4 + 2 * i] == "str":
                    isint = "1"
                elif words[4 + 2 * i] == "int":
                    isint = "0"
                newtype.append(isprim + isint)

            for nw in newtype:
                typename += (" " + nw)
            typename += "\n"
            TypeLines.append(typename)
            tries = 0
            while (True):
                tries += 1
                with open(str(tries) + ".txt", "a+") as writer:
                    notimportant = 44
                datafile = open(str(tries) + ".txt", "r")
                datalines = datafile.readlines()
                if len(datalines) == 0:
                    with open(str(tries) + ".txt", "a+") as writer:
                        writer.write("Header " + words[2] + " 1 " + str(tries) + "\n")
                    break
                page_id = 0
                for data in datalines:
                    datawords = data.split()
                    if datawords[0] == "Header":
                        page_id += 1
                if page_id == 20:
                    continue
                with open(str(tries) + ".txt", "a+") as writer:
                    writer.write("Header " + words[2] + " " + str(page_id + 1) + " " + str(tries) + "\n")
                break
            logfile.write("success\n")
            n = Node(3)
            bplustree = BplusTree(n, type_name_file)
            bplustree.parentDict[n] = None
            bplustree.treeNodes.append(n)
            continue

        elif words[1] == "record":
            type_name = words[2]
            primaryname = ""
            dat = ""
            if len(TypeLines) == 0:
                logfile.write("failure\n")

            for tyline in TypeLines:
                tywords = tyline.split()
                if len(tywords) <= 0:
                    logfile.write("failure\n")
                    continue

                if tywords[0] == type_name:

                    if len(tywords) == (len(words) - 1):

                        mightabort = 0
                        for k in range(2, len(tywords)):
                            if tywords[k][0] == '*':
                                primaryname = words[k + 1]
                            dat = dat + " " + words[k + 1]
                            if (tywords[k][1] == "0") and (not words[k + 1].isnumeric()):
                                logfile.write("failure\n")
                                mightabort = 1
                                break
                        if mightabort:
                            break
                        for tree in allTrees:
                            if tree.type == type_name:
                                for key in tree.search(words[3]).keys:
                                    for header in key:
                                        if header.split(' ')[4] == words[3]:
                                            logfile.write("failure\n")
                                            mightabort = 1
                                            break
                        if mightabort:
                            break
                        logfile.write("success\n")

                        correct = 0
                        page_id = 0
                        endgame = 0
                        position = 0
                        maybe = 0
                        tries = 0
                        otherpageid = 0

                        for kl in range(2):
                            cantfind = 1
                            while (1):
                                tries += 1
                                if not (os.path.exists(str(tries) + ".txt")):
                                    break
                                datafile = open(str(tries) + ".txt", "r")
                                datalines = datafile.readlines()
                                datafile.close()

                                for data in datalines:
                                    position += 1
                                    datawords = data.split()
                                    if correct:
                                        if datawords[0] == "Header":
                                            position -= 1
                                            cantfind = 0
                                            break
                                        page_id += 1
                                        if page_id == 10:
                                            correct = 0
                                            page_id = 0
                                    if datawords[0] == "Header" and datawords[1] == type_name:
                                        otherpageid = datawords[2]
                                        correct = 1
                                if correct:
                                    datalines.insert(position,
                                                     type_name + " " + str(page_id + 1) + " " + otherpageid + " " + str(
                                                         tries) + " " + primaryname + dat + "\n")

                                    for tree in allTrees:
                                        if tree.type == type_name:
                                            for key in tree.search(words[3]).keys:
                                                for header in key:
                                                    if header.split(' ')[4] == words[3]:
                                                        print('duplicate')
                                            for index in range(len(tywords)):
                                                if tywords[index][0] == '*':
                                                    tree.insert(words[index + 1], type_name + " " + str(
                                                        page_id + 1) + " " + otherpageid + " " + str(
                                                        tries) + " " + words[index + 1])

                                            node_file_name = 'nodes_' + tree.type + '.json'

                                            jsonNodeValues = json.dumps(tree.treeNodes, default=lambda o: o.__dict__,
                                                                        indent=2)  # convert nodes to json format

                                            parentKeys = list(tree.parentDict.keys())
                                            parentValues = list(tree.parentDict.values())
                                            jsonParentKeys = json.dumps(parentKeys, default=lambda o: o.__dict__,
                                                                        indent=2)  # convert all parent keys to json format
                                            jsonParentValues = json.dumps(parentValues, default=lambda o: o.__dict__,
                                                                          indent=2)  # convert all parent values to json format

                                            # write all the bplustree parent dictionary keys in the file
                                            parent_key_file_name = 'parent_keys_' + tree.type + '.json'
                                            parent_value_file_name = 'parent_values_' + tree.type + '.json'

                                            bplus_file_parent_keys = open(parent_key_file_name, 'w')
                                            bplus_file_parent_keys.write(jsonParentKeys)
                                            bplus_file_parent_keys.close()
                                            bplus_file_parent_values = open(parent_value_file_name, 'w')
                                            bplus_file_parent_values.write(jsonParentValues)
                                            bplus_file_parent_values.close()
                                            node_file = open(node_file_name, 'w')
                                            node_file.write(jsonNodeValues)
                                            node_file.close()
                                    with open(str(tries) + ".txt", "w") as op:
                                        datalines = "".join(datalines)
                                        op.write(datalines)
                                    cantfind = 0
                                    break
                            tries = 0
                            if (cantfind == False):
                                break
                            while (cantfind):
                                tries += 1
                                with open(str(tries) + ".txt", "a+") as writer:
                                    notimportant = 44
                                datafile = open(str(tries) + ".txt", "r")
                                datalines = datafile.readlines()
                                if len(datalines) == 0:
                                    with open(str(tries) + ".txt", "a+") as writer:
                                        writer.write("Header " + words[2] + " 1 " + str(tries) + "\n")
                                    break
                                page_id = 0
                                for data in datalines:
                                    datawords = data.split()
                                    if datawords[0] == "Header":
                                        page_id += 1
                                if page_id == 20:
                                    continue
                                with open(str(tries) + ".txt", "a+") as writer:
                                    writer.write(
                                        "Header " + words[2] + " " + str(page_id + 1) + " " + str(tries) + "\n")
                                break
                        break
                    logfile.write("failure\n")
                    break
        else:
            logfile.write("failure\n")
    elif words[0] == "update":
        if words[1] != "record":
            logfile.write("failure\n")
            continue
        type_name = words[2]
        isExists = False
        for tyline in TypeLines:
            tywords = tyline.split()
            if len(tywords) <= 0:
                continue
            if tywords[0] == type_name:
                if len(tywords) == (len(words) - 2):
                    mightabort = 0
                    for k in range(2, len(tywords)):
                        if (tywords[k][1] == "0") and (not words[k + 2].isnumeric()):
                            logfile.write("failure\n")
                            mightabort = 1
                            break
                    if mightabort:
                        break
                    primname = words[3]
                    # search primname in database and change values if found **************
                    for tree in allTrees:
                        if tree.type == type_name:
                            for key in tree.search(words[3]).keys:
                                for header in key:
                                    header_split = header.split()
                                    if header_split[4] == words[3]:
                                        isExists = True
                                        file_for_update = open(header_split[3] + '.txt', 'r')
                                        lines_update = (file_for_update.readlines())
                                        file_for_update.close()
                                        for line_ in lines_update:
                                            split = line_.split()
                                            if split[0] == header_split[0] and header_split[1] == split[1] and \
                                                    header_split[
                                                        2] == split[2] and header_split[3] == split[3] and header_split[
                                                4] == split[
                                                4]:
                                                update_line = line_[0:-2]
                                                updated_version = []
                                                for element in lines_update:
                                                    if element[0:-2] == update_line:
                                                        updated_version = element.split()
                                                        updated_version[4:] = (words[3:])
                                                        str_line = ''
                                                        for item in updated_version:
                                                            if item != updated_version[-1]:
                                                                str_line += (item + ' ')
                                                            else:
                                                                str_line += item + '\n'
                                                        lines_update[lines_update.index(element)] = str_line

                                        file_for_write = open(header_split[3] + '.txt', 'w')
                                        for item in lines_update:
                                            file_for_write.write(item)
                                        file_for_write.close()

                    if not isExists:
                        logfile.write("failure\n")
                        break

                    logfile.write("success\n")
                    break
                logfile.write("failure\n")
                break
    elif words[0] == "delete":
        if words[1] == "type":
            type_name = words[2]
            for tyline in TypeLines:
                tywords = tyline.split()
                if tywords[0] == type_name:
                    TypeLines.remove(tyline)
                    # delete all values from this type in the database
                    rip = jayson(type_name, 0)
                    if rip == None:
                        break

                    tries = rip[0][3]
                    guysdone = 0
                    while guysdone < len(rip):
                        # print(guysdone)
                        listfile = open(str(tries) + ".txt", 'r')
                        listlines = listfile.readlines()
                        temp_list_lines = listlines.copy()
                        listingtime = 0
                        for listline in listlines:
                            if guysdone >= len(rip): continue
                            if not rip[guysdone][3] == tries:
                                continue
                            listwords = listline.split()
                            if listingtime:
                                if listwords[0] == "Header":
                                    listingtime = 0
                                else:
                                    mayprim = listwords[4]
                                    guysdone += 1
                                    temp_list_lines.remove(listline)
                            if listwords[0] == "Header" and listwords[1] == type_name:
                                listingtime = 1
                                temp_list_lines.remove(listline)
                        rewrite = open(str(tries) + ".txt", 'w')
                        for line_ in temp_list_lines:
                            rewrite.write(line_)
                        if guysdone == len(rip):
                            break
                        tries = rip[guysdone][3]

                    # upto here young man
                    parent_key_file_name = 'parent_keys_' + type_name + '.json'
                    parent_value_file_name = 'parent_values_' + type_name + '.json'
                    node_file_name = 'nodes_' + type_name + '.json'
                    bplus_file_name = 'bplus_' + type_name + '.json'
                    # delete all values from this type in the database
                    os.remove(parent_key_file_name)
                    os.remove(parent_value_file_name)
                    os.remove(node_file_name)
                    os.remove(bplus_file_name)
                    for tree in allTrees:
                        if tree.type == type_name:
                            allTrees.remove(tree)
                    logfile.write("success\n")
                    break
            logfile.write("failure\n")
            continue
        elif words[1] == "record":
            type_name = words[2]
            isExists = False
            deleted_key = []
        for tyline in TypeLines:
            tywords = tyline.split()
            if tywords[0] == type_name:
                primname = words[3]

                for tree in allTrees:
                    if tree.type == type_name:
                        for key in tree.search(words[3]).keys:
                            for header in key:
                                header_split = header.split()
                                if header_split[4] == words[3]:
                                    deleted_key = header_split
                                    isExists = True
                                    file_for_delete = open(header_split[3] + '.txt', 'r')
                                    lines_delete = (file_for_delete.readlines())
                                    file_for_delete.close()
                                    for line_ in lines_delete:
                                        split = line_.split()
                                        if split[0] == header_split[0] and header_split[1] == split[1] and header_split[
                                            2] == split[2] and header_split[3] == split[3] and header_split[4] == split[
                                            4]:
                                            removed_line = line_[0:-2]
                                            for element in lines_delete:
                                                if element[0:-2] == removed_line:
                                                    lines_delete.remove(element)
                                    file_for_write = open(header_split[3] + '.txt', 'w')
                                    for item in lines_delete:
                                        file_for_write.write(item)
                                    file_for_write.close()

                if not isExists:
                    logfile.write("failure\n")
                    break
                for tree in allTrees:
                    if tree.type == type_name:
                        deleted_str = ''
                        for key in deleted_key:
                            if key != deleted_key[-1]:
                                deleted_str += (key + ' ')
                            else:
                                deleted_str += key
                        tree.delete(words[3], deleted_str)

                        node_file_name = 'nodes_' + tree.type + '.json'

                        jsonNodeValues = json.dumps(tree.treeNodes, default=lambda o: o.__dict__,
                                                    indent=2)  # convert nodes to json format

                        parentKeys = list(tree.parentDict.keys())
                        parentValues = list(tree.parentDict.values())
                        jsonParentKeys = json.dumps(parentKeys, default=lambda o: o.__dict__,
                                                    indent=2)  # convert all parent keys to json format
                        jsonParentValues = json.dumps(parentValues, default=lambda o: o.__dict__,
                                                      indent=2)  # convert all parent values to json format

                        # write all the bplustree parent dictionary keys in the file
                        parent_key_file_name = 'parent_keys_' + tree.type + '.json'
                        parent_value_file_name = 'parent_values_' + tree.type + '.json'

                        bplus_file_parent_keys = open(parent_key_file_name, 'w')
                        bplus_file_parent_keys.write(jsonParentKeys)
                        bplus_file_parent_keys.close()
                        bplus_file_parent_values = open(parent_value_file_name, 'w')
                        bplus_file_parent_values.write(jsonParentValues)
                        bplus_file_parent_values.close()
                        node_file = open(node_file_name, 'w')
                        node_file.write(jsonNodeValues)
                        node_file.close()
                # search if in database,delete if it exists, give error if it doesn't
                logfile.write("success\n")
                break
        else:
            logfile.write("failure\n")
            continue
    elif words[0] == "filter":
        if not (words[1] == "record"):
            logfile.write("failure\n")
            continue
        filtr = words[3]
        comparernum = max(filtr.find('<'), filtr.find('>'),
                          filtr.find('='))  # assumption: primary name will come before comparer
        if comparernum < 0:
            logfile.write("failure\n")
            continue
        primname = filtr[0:comparernum]
        comparedelement = filtr[comparernum + 1:]
        comparerstring = filtr[comparernum]
        type_name = words[2]
        for tyline in TypeLines:
            tywords = tyline.split()
            if tywords[0] == type_name:
                if tywords[1] != primname:
                    logfile.write("failure\n")
                    break
                # added random letters here
                ste = jayson(type_name, 0)
                tries = ste[0][3]
                guysdone = 0
                write_list = []
                while guysdone < len(ste):
                    filterfile = open(str(tries) + ".txt", 'r')
                    filterlines = filterfile.readlines()
                    filteringtime = 0
                    for filterline in filterlines:
                        if guysdone >= len(ste): break
                        if not ste[guysdone][3] == tries:
                            tries = ste[guysdone][3]
                            break
                        filterwords = filterline.split()
                        if filteringtime:
                            if filterwords[0] == "Header":
                                filteringtime = 0
                            else:
                                mayprim = filterwords[4]
                                guysdone += 1

                                if [type_name, True] in sortfunc([],TypeLines, 1):
                                    if (comparerstring == '>' and int(mayprim) > int(comparedelement)) or (
                                            comparerstring == '<' and int(mayprim) < int(comparedelement)) or (
                                            comparerstring == '=' and int(mayprim) == int(comparedelement)):
                                        write_list.append(filterwords)
                                else:
                                    if (comparerstring == '>' and (mayprim) > (comparedelement)) or (
                                            comparerstring == '<' and (mayprim) < (comparedelement)) or (
                                            comparerstring == '=' and (mayprim) == (comparedelement)):
                                        write_list.append(filterwords)

                        if filterwords[0] == "Header" and filterwords[1] == type_name:
                            filteringtime = 1
                lst = sortfunc(write_list,TypeLines, 0)
                for write_line in lst:
                    for klct in range(len(write_line) - 5):
                        outFile.write(write_line[5 + klct] + " ")
                    outFile.write("\n")

                # search type pages in database, get elements that fit the description
                logfile.write("success\n")
                break
        continue
    elif words[0] == "search":
        if not (words[1] == "record"):
            logfile.write("failure\n")
            continue
        isExists = False
        type_name = words[2]
        for tyline in TypeLines:
            tywords = tyline.split()
            if tywords[0] == type_name:
                for tree in allTrees:
                    if tree.type == type_name:
                        for key in tree.search(words[3]).keys:
                            for header in key:
                                header_split = header.split(' ')
                                if header_split[4] == words[3]:
                                    isExists = True
                                    file_for_search = open(header_split[3] + '.txt', 'r')
                                    lines_searched = (file_for_search.readlines())
                                    file_for_search.close()
                                    for line_ in lines_searched:
                                        split = line_.split()
                                        if split[0] == header_split[0] and header_split[1] == split[1] and header_split[
                                            2] == split[2] and header_split[3] == split[3] and header_split[4] == split[
                                            4]:
                                            for item in split[5:]:
                                                if item != split[len(split) - 1]:
                                                    outFile.write(item + ' ')
                                                else:
                                                    outFile.write(item + '\n')
                if not isExists:
                    logfile.write("failure\n")
                # search type pages in database, get elements that fit the description
                logfile.write("success\n")
                break
        continue
    elif words[0] == "list":
        if words[1] == "type":
            mightabort = 1
            for tyline in TypeLines:
                mightabort = 0
            if mightabort:
                logfile.write("failure\n")
                continue
            typeSet = set()
            for element in TypeLines:
                typeSet.add(element.split()[0])
            if exists('types.txt'):
                type_file = open('types.txt', 'r')
                type_array = type_file.readlines()
                for item in type_array:
                    typeSet.add(item.split()[0])
            for item in sorted(typeSet):
                outFile.write(item + '\n')
            logfile.write("success\n")
        elif words[1] == "record":
            mightabort = 1
            type_name = words[2]
            for tyline in TypeLines:
                tywords = tyline.split()
                if len(tywords) <= 0: continue
                if tywords[0] == type_name:

                    mightabort = 0
                    # search all values and print their values
                    if not exists("nodes_" + type_name + ".json"):
                        mightabort = 1
                        break
                    ste = jayson(type_name, 0)
                    tries = ste[0][3]
                    guysdone = 0
                    write_list = []
                    while (guysdone < len(ste)):
                        listfile = open(str(tries) + ".txt", 'r')
                        listlines = listfile.readlines()
                        listingtime = 0
                        for listline in listlines:
                            if guysdone >= len(ste): break
                            if not ste[guysdone][3] == tries:
                                tries = ste[guysdone][3]
                                break
                            listwords = listline.split()
                            if listingtime:
                                if listwords[0] == "Header":
                                    listingtime = 0
                                else:
                                    mayprim = listwords[4]
                                    guysdone += 1
                                    write_list.append(listwords)

                            if (listwords[0] == "Header" and listwords[1] == type_name):
                                listingtime = 1

                    lst = sortfunc(write_list,TypeLines, 0)
                    for write_line in lst:
                        for klct in range(len(write_line) - 5):
                            outFile.write(write_line[5 + klct] + " ")
                        outFile.write("\n")

                    logfile.write("success\n")
                    break
            if mightabort:
                logfile.write("failure\n")
                continue
    else:
        logfile.write("failure\n")
# logfile.write("\n")
typefile2 = open("types.txt", 'w')
for tyline2 in TypeLines:
    if tyline2 != "\n":
        typefile2.write(tyline2)

###assumption: inputs will be legit


# write bplustree root in the file
for tree in allTrees:
    tree.parentDict = None
    bplus_file_name = 'bplus_' + tree.type + '.json'
    jsonBPlusValues = json.dumps(tree, default=lambda o: o.__dict__,
                                 indent=2)  # convert bpluss tree root to json format
    bplus_file = open(bplus_file_name, 'w')
    bplus_file.write(jsonBPlusValues)
    bplus_file.close()
