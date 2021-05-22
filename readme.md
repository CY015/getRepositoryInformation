# 获取GitHub仓库信息脚本

## 信息聚合 GH Archive
* [Github Archive](https://www.gharchive.org/)
* Linux / Mac OS下使用命令来获得对应时间内所有使用者的各种event
```shell
wget https://data.gharchive.org/YYYY-MM-DD-HH.json.gz
```

## 脚本内各函数解析
### getRepoURL()
* 获取仓库api并进行解析

1. 仓库api地址: json文件里键`"repo"`下的`"url"`键值  
   <details>
   <summary>单条json示例</summary>  
   
    ```json
    {
      "id": "15847076753",
      "type": "CreateEvent",
      "actor": {
          "id": 483114,
          ...
      },
      "repo": {
          "id": 95529911,
          "name": "ow2-proactive/proactive-examples",
          "url": "https://api.github.com/repos/ow2-proactive/proactive-examples"
      },
      "payload": {
          ...
      },
      "public": true,
      "created_at": "2021-04-07T13:00:00Z",
      "org": {    
          ...
      }
    }
    ```
   
    </details>

2. 用`requests`模块模拟访问仓库api地址  
   <details>
   <summary>响应信息示例</summary>  
   
    ```json
    {
      "id": 95529911,
      "node_id": "MDEwOlJlcG9zaXRvcnk5NTUyOTkxMQ==",
      "name": "proactive-examples",
      "full_name": "ow2-proactive/proactive-examples",
      "private": false,
      "owner": {
        "login": "ow2-proactive",
        ...
      },
      "html_url": "https://github.com/ow2-proactive/proactive-examples",
      "description": "This repository centralizes all the proactive objects (workflows, rules,..)",
      "fork": false,
        ...
      "stargazers_count": 6,
      "watchers_count": 6,
      "language": "Python",
        ...
      "forks_count": 29,
        ...
      "organization": {
        ...
      },
      "network_count": 29,
      "subscribers_count": 16
    }
    ```
   
  </details>

3. 获取仓库相关信息  
   1. 目前只提取了：  
   `"html_url"` 仓库地址  
   `"language"` 主要使用语言(如果有多种语言的情况下，这里只显示使用占比最大的一种语言)  
   `"stargazers_count"` stars数量  
   `"watchers_count"` watch数量  
   `"forks_count"` forks数量  

   *按需索取，获取对应的键值即可*


#### 此函数中有可能出现的Exception
1. requests会报错`requests.exceptions.ConnectionError: HTTPSConnectionPool(host='api.github.com', port=443)`，原因是由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败
2. requests访问后返回的信息含有`'message'`字段，键值为`'block'`或者`'Not Found'`，是无法进入或者访问仓库，暂时只注意到这两个类型。一般是仓库删掉了或者是private(猜测)



### removeDuplication(rawData)
* 删除一个文件内的重复仓库信息
* 输入：`rawData`: `getRepoURL`中存储仓库信息的List
* 输出：不含重复仓库信息的List  
**只保证单个json.gz文件生成的仓库信息数据内信息不重复**

### filtration(csvFile, rFilter)
* 根据条件进行筛选(如forks数量，程序语言等)
* 输入：`csvFile`: 需要进行筛选的csv文件  `fFilter`: 筛选条件(在main函数里定义)
* 输出：存储名为`language_minforks=x.csv`的文件

### saveToCSV(data, fname)
* 将数据存储成csv文件
* 输入：`data`: dataframe数据  `fname`: 文件名
* 输出：`fname.csv`

### loadCSV(csvPath)
* 加载该路径下所有csv中的内容，存成无重复项目仓库信息的csv文件
* 输入：`csvPath`：存储着所有仓库信息的csv文件路径

## Python环境配置
Python3  
pandas  
requests  
json  
jsonlines

## json.gz文件
### 下载
Linux  
Mac OS  
Windows的`wget`命令暂时没用过
### 处理
* 在Python环境下无需解压gz文件，Python自带的`gzip`包可完成对gz文件的读取

## TODO
* 可以考虑多线程(使用多个token验证?)
* 但Github API在每个小时内有访问次数[限制](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)(会限制每个IP访问次数上限是5000次/h)，可以考虑多个IP地址进行API的访问
```json
{
  "message":"API rate limit exceeded for 116.22.142.244. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)",  
  "documentation_url":"https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting"
}
```
