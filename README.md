# Aliyun ECS Scripts 阿里云 ECS 脚本

由于经常需要启动关闭 ECS，或者更换弹性公网 IP，又不想每次都登录控制台，就写了一个简单的脚本来简化操作。

使用官方提供的 Python SDK 进行开发。

## 开始

### 环境准备

```
git clone https://github.com/PIG208/aliyun-script.git
cd aliyun-script
pip install .
```

只需要使用脚本的话可以直接通过 git 安装:

```
pip install -e git+https://github.com/PIG208/aliyun-script.git#egg=aliyun-scripts
```

### 使用方法

程序会默认读取用户目录下的配置文件 (即`~/config.json`和`~/secrets.json`)

你也可以通过 `--config` 来指定 `config.json`, `--secrets` 来指定 `secrets.json`

```
pig208@PIG:$ aliyun-ecs -s [指令|command]
```

目前支持的指令如下:

- stop: 停止 ECS
- start: 开始 ECS
- rebind: 解绑 ECS 的弹性公网 IP，分配一个新的并且绑定
- ip: ECS 目前的公网 IP
- status: ECS 目前的状态

效果:

```
pig208@PIG:$ aliyun-ecs -s status
The status of i-asdasdasdasdasdasd (pig208-server) is:
Running
pig208@PIG:$ aliyun-ecs -s ip
The ip of i-asdasdasdasdasdasd (pig208-server) is:
47.123.123.123
```

你也可以使用图形界面:

```
pig208@PIG:$ aliyun-ui
```

## 配置

配置通过两个.json 文件管理:

- config.json

  "Target" 为需要进行操作的 ECS 的 InstanceId;

  相关: [弹性公网 IP](https://help.aliyun.com/document_detail/36016.htm?spm=a2c4g.11186623.2.2.27b829c6x47dDY#doc-api-Vpc-AllocateEipAddress)

```
{
  "Target": "i-1ijonfi1n3f1i3example",
  "InstanceChargeType": "PostPaid",
  "InternetChargeType": "PayByTraffic",
  "BandWidth": 5,
  "ISP": "BGP_PRO"
}

```

- secrets.json

  在这里配置你的 API [Access Key](https://help.aliyun.com/document_detail/113593.html)

```
{
  "user_name": "TestUser@asdasdasd.onaliyun.com",
  "accessKey_id": "eXAMPLEDaccessKeyas123",
  "accessKey_secret": "eXAMPLEDaccessKeyas123Secretasd123",
  "region_id": "cn-hongkong"
}
```
