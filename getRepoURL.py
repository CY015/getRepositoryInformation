#!/usr/bin/python
#-*-coding:utf-8-*-
import csv
import sys
import os
import pandas as pd
import gzip
import requests
import json
import jsonlines
# import urllib3

# 获得所有仓库数据
def getRepoURL():
    failed_url = []

    # 获取原始数据
    for f_idx, gz in enumerate(gz_files):

        # 获取原始数据的文件名作为保存文件的名字
        gz_name = gz.split('.')[0]
        print(gz_name)

        # 读取每个gz压缩文件
        with gzip.GzipFile(gz_dir + gz, 'r') as f:
            # 初始化仓库信息
            rawInfo = []
            f_read = jsonlines.Reader(f)

            # 读取每一行json
            for u_idx, jsonFile in enumerate(f_read):
                                
                # 测试
                if u_idx == 10000:
                    break

                URL = jsonFile["repo"]["url"]
                # requests.exceptions.ConnectionError: HTTPSConnectionPool(host='api.github.com', port=443)
                # 由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败
                try:
                    response = requests.get(URL,headers=header).content.decode('utf-8')
                except:
                    # 记录一下连接失败的仓库url
                    failed_url.append([URL])
                    continue
                Info = json.loads(response)

                # 返回有'message'字段，里面包含'block'或者'Not Found'
                # 暂时只注意到这两个类型是无法进入或者访问仓库
                try:
                    # print('message' in Info)
                    if 'message' in Info:
                        continue
                except:
                    # print(URL)
                    # print(Info)
                    break

                # 获取项目相关信息
                # 仓库地址 / 程序主要使用语言 / forks 数量 / star 数量
                repoURL = Info['html_url']
                language = Info['language']
                forks = Info['forks_count']
                star = Info['stargazers_count']

                rawInfo.append([repoURL, language, forks, star])

            # 去重并存下所有项目的信息
            csv_files = gz_name + '.csv'
            saveToCSV(removeDuplication(rawInfo), csv_files)

            # 没能成功访问api.github.com的仓库api地址(第一个try模块处)
            print("failed to Connect 'api.github.com', Repositories urls:", failed_url, "\n\n")


# 去重
# 只保证单个json.gz文件生成的仓库信息数据内信息不重复，如果要对多个去重则需要加载全部的数据 在main调用loadCSV()
def removeDuplication(rawData):
    print('rawData:'+str(rawData)+'\n\n')
    repoInfo = []
    for r in rawData:
        if r not in repoInfo:
            repoInfo.append(r)
    # test
    print(str(repoInfo)+'\n\n')
    rInfo = pd.DataFrame(repoInfo,columns=['repoURL','Language','forks_count','stars_count'])

    return rInfo


# 筛选项目信息
def filtration(csvFile, rFilter):
    fRepoInfo = []
    csvRead = csv.reader(open(csvFile, encoding='utf-8'))
    for i, row in enumerate(csvRead):
        # 去掉csv第一行
        # 忽略第一列自动添加的序号
        if i == 0:
            continue
        else:
            # 先判断第三列fork数是否符合
            # 再判断语言是否符合
            # 如果需要增加star数量作为判断指标，那么在判断加在fork之后(因为一般情况下star数量会多于fork数量，可以先通过fork数量筛选掉大部分项目)
            if int(row[3]) >= rFilter['forks_count']:
                if row[2] in rFilter['language']:
                    fRepoInfo.append(row[1:])
    

    finalRepoInfo = pd.DataFrame(fRepoInfo,columns=['repoURL','Language','forks_count','stars_count'])
    finalRepoFile = '_'.join(rFilter['language']) + '_minforks=' + str(rFilter['forks_count']) + '.csv'
    saveToCSV(finalRepoInfo, finalRepoFile)
            

# 存储至CSV
def saveToCSV(data, fname):
    fPath = csv_dir + fname
    data.to_csv(path_or_buf=fPath,header=True)


# 加载CSV中的内容
# 存成无重复项目仓库信息的csv文件
def loadCSV(csvPath):
    csv_files = os.listdir(csvPath)
    csv_files = [i for i in csv_files if i.endswith('.csv')]
    allRepo = []

    # 遍历csv文件
    for c_idx, csvF in enumerate(csv_files):
        f = csvPath + csvF
        csvRead = csv.reader(open(f, encoding='utf-8'))
        for i, row in enumerate(csvRead):
            # 去掉csv第一行
            # 忽略第一列自动添加的序号
            if i == 0:
                continue
            else:
                allRepo.append(row[1:])

    # 存成无重复项目仓库信息的csv文件
    saved_Filename = 'withoutRepeat.csv'
    saveToCSV(removeDuplication(allRepo), saved_Filename)


if __name__ == '__main__':
    gz_dir = 'F:/3_DataCollect/data/raw/'
    gz_files = os.listdir(gz_dir)
    gz_files = [i for i in gz_files if i.endswith('.json.gz')]

    csv_dir = 'F:/3_DataCollect/data/done/'

    filterFile = csv_dir + 'withoutRepeat.csv'

    # 加入token可以有更多的访问次数(最多每小时5000次对github的api请求)
    # token 在Github上个人设置里申请 Settings -> Develop Settings -> Personal access tokens
    # token申请完后需要记住，以后登录时不会显示token，除非重新申请
    # 头部授权格式：token (token内容)
    # 参考：https://www.jianshu.com/p/628a0747c492
    header = {
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
        'Authorization': 'token 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'
    }

    # 过滤条件
    # 使用语言 / fork数量 / star数量
    repoFilter = {
        'language': ['Java','Python','C'], 
        'forks_count': 1, 
        'star_count': 1
    }

    getRepoURL()
    # loadCSV(csv_dir)
    filtration(filterFile, repoFilter)