
# JOI AI

JOI AI 是一个开源智能语音机器人项目，借助大语言模型与众多云厂商的服务，致力于打造更好的全息 AI 语音助手。
JOI AI 具有高定制化功能，可以设定你想要的任意角色作为你的语伴，同时具有良好的设备兼容性。

## 特性

- 模块化。功能插件、语音识别、语音合成、对话机器人都做到了高度模块化，丰富的插件系统。
- 中文支持。集成百度、科大讯飞、阿里、腾讯、Apple、微软Edge、VITS声音克隆TTS 等多家中文语音识别和语音合成技术。
- 对话机器人支持。支持 OpenAI ChatGPT ，图灵机器人等在线对话机器人。
- 全局监听，离线唤醒。支持 [Porcupine](https://github.com/Picovoice/porcupine) 和 [snowboy](https://github.com/Kitt-AI/snowboy) 两套离线语音指令唤醒引擎。
- 灵活可配置。支持定制机器人名字，定制对话机器人角色形象，定制对话机器人语音。
- 智能家居。
- 后台配套支持。提供配套后台，可实现远程操控、修改配置和日志查看等功能。
- 开放API。可利用后端开放的API，实现更丰富的功能。
- 安装简单，支持更多平台。能在 Mac 以及更多 Linux 系统中运行。

## 环境要求

### Python 版本

joi-ai 只支持 Python 3.7+，不支持 Python 2.x 。

### 设备要求

joi-ai 支持运行在以下的设备和系统中：

- Intel Chip Mac (不支持 M1 芯片)
- 64bit Ubuntu（12.04 and 14.04）
- 全系列的树莓派（Raspbian 系统）
- Pine 64 with Debian Jessie 8.5（3.10.102）
- Intel Edison with Ubilinux （Debian Wheezy 7.8）
- 装有 WSL（Windows Subsystem for Linux） 的 Windows



## 安装

### 克隆仓库

```bash
git clone https://github.com/zexiplus/joi-ai
```

### 2. 安装 sox, ffmpeg 和 PyAudio

#### Linux 系统

```bash
sudo apt-get update -y
sudo apt-get install portaudio19-dev python-pyaudio python3-pyaudio sox pulseaudio libsox-fmt-all ffmpeg
pip3 install pyaudio
```

如果遇到 pip3 安装慢的问题，可以考虑使用 Pypi 镜像。例如 [清华大学 Pypi 镜像](https://mirror.tuna.tsinghua.edu.cn/help/pypi/) 。

#### Mac 系统

```bash
brew install portaudio --HEAD  # 安装 Git 最新版本，确保 Big Sur 系统可用
brew install sox ffmpeg
pip3 install pyaudio
```

如果你没有 Homebrew ，参考[本文](http://brew.sh/)安装

### 3. 安装依赖的库

```bash
cd joi-ai
pip3 install -r requirements.txt
```

### 4. 编译 _snowboydetect.so

不管你打算使用 snowboy 还是 Porcupine 作为离线唤醒引擎，**编译 `_snowboydetect.so` 依然是必要的**，因为当离线唤醒后，joi-ai 会使用 snowboy 的 VAD 能力来在主动聆听时候判断是否应该结束聆听。

#### 安装 swig

首先确保你的系统已经装有 swig 。

对于 Linux 系统：

```bash
cd $HOME
wget https://wzpan-1253537070.cos.ap-guangzhou.myqcloud.com/misc/swig-3.0.10.tar.gz
tar xvf swig-3.0.10.tar.gz
cd swig-3.0.10
sudo apt-get -y update
sudo apt-get install -y libpcre3 libpcre3-dev
./configure --prefix=/usr --without-clisp --without-maximum-compile-warnings
make
sudo make install
sudo install -v -m755 -d /usr/share/doc/swig-3.0.10
sudo cp -v -R Doc/* /usr/share/doc/swig-3.0.10
sudo apt-get install -y libatlas-base-dev
```

如果提示找不到 `python3-config` 命令，你还需要安装 `python3-dev`：

```bash
sudo apt-get install python3-dev  # 注意 Ubuntu 18.04 可能叫 python3-all-dev
```

对于 Mac 系统：

```bash
brew install swig wget
```

#### 构建 snowboy

```bash
cd $HOME
wget https://wzpan-1253537070.cos.ap-guangzhou.myqcloud.com/wukong/snowboy.tar.bz2 # 使用我fork出来的版本以确保接口及Ubuntu 22兼容
tar -xvjf snowboy.tar.bz2
cd snowboy/swig/Python3
make
cp _snowboydetect.so wukon-robot的根目录/snowboy/
```

如果 make 阶段遇到问题，尝试在 [snowboy 项目 issue 中找到解决方案](https://github.com/Kitt-AI/snowboy/issues) 。

#### CentOS 没声音问题解决

有用户在 CentOS 系统中遇到播放没声音的问题。解决方法是：

```sh
mknod /dev/dsp c 14 3
chmod 666 /dev/dsp
```

## 配置

首次执行 joi 后，系统就会帮你在 `~/.joi` 目录下生成 config.yml 配置文件。

```bash
python3 joi.py
```

这个配置文件有不少项目都是必配的项目，只有配置正确， joi-ai 才可以正常使用。

几个 tips：

1. 不建议直接修改 default.yml 里的内容，否则会给后续通过 `git pull` 更新带来麻烦。你应该拷贝一份放到 `$HOME/.joi/config.yml` 中。

配置文件的读取优先级：`$HOME/.joi/config.yml` > `static/default.yml` 。如果存在 `$HOME/.joi/config.yml` 文件，则只读取该文件的配置，而不读取 default.yml ；如果不存在，则读取 default.yml 作为兜底配置。

1. 不论使用哪个厂商的API，都建议注册并填上自己注册的应用信息，而不要用默认的配置。这是因为这些API都有使用频率和并发数限制，过多人同时使用会影响服务质量。

2. 任一技能插件都允许关闭，方法是在配置文件中为该插件添加一个 `enable: false` 的设置。例如，如果你想关闭新闻头条插件，而该插件的 `SLUG` 是 `headline_news` ，那么可以如下设置：

   ```yaml
   # 新闻头条
   # 聚合数据新闻头条API
   # https://www.juhe.cn/docs/api/id/235
   headline_news:
       enable: false
       key: 'AppKey'  # 其他配置Copy to clipboardErrorCopied
   ```

3. 出于安全考虑，后端管理端的 `validate` 和 `cookie_secret` 都 **应该** 修改！

其中 `cookie_secret` 可以使用本地生成的一串字符串。你可以使用如下方式生成：

```bash
>>> import os
>>> os.urandom(24)
```

将这个结果直接复制到 `cookie_secret` 配置中即可。例如：

```yaml
server:
    enable: true
    host: '0.0.0.0'  # ip 地址
    port: '5001'     # 端口号
    username: 'joi'  # 用户名
    # cookie 的 secret ，用于对 cookie 的内容进行加密及防止篡改
    # 建议使用 os.urandom(24) 生成一串随机字符串
    cookie_secret: '__GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__'
    # 密码的 md5，可以用 python3 joi.py md5 "密码" 获得
    # 初始密码为 joi@2049
    # 建议修改
    validate: '41724998a398a3f11ac18a1b7e2537e0'
```

## 运行

### 运行前声卡检查和设置

请确保麦克风和音响配置正确再启动 joi-ai

### 运行 joi-ai

``` bash
cd joi-ai 所在的目录
python3 joi.py
```

第一次启动时将提示你是否要到用户目录下创建一个配置文件，输入 `y` 即可。

然后通过唤醒词 “snowboy” 唤醒 joi 进行交互（该唤醒词可自定义, 以提升唤醒成功率和准确率）。

### 管理端

joi-ai 默认在运行期间还会启动一个后台管理端，提供了远程对话、查看修改配置、查看 log 等能力。

- 默认地址：<http://localhost:5001>
- 默认账户名：joi
- 默认密码：joi@2049

建议正式使用时修改用户名和密码，以免泄漏隐私。

### 后台运行

直接在终端中启动 joi-ai ，等关掉终端后 joi-ai 的进程可能就没了。

要想在后台保持运行 joi-ai ，可以在 [tmux](http://blog.jobbole.com/87278/) 或 supervisor 中运行。

## 退出

要退出 joi-ai ，根据当前情况的不同有不同的方式：

### 如果 joi-ai 正在前台工作

可以直接按组合键 `Ctrl+4` 或 `Ctrl+\` 即可。

### 如果 joi-ai 正在后台工作

可以执行如下命令：

``` bash
ps auwx | grep joi  # 查看joi的PID号
kill -9 PID号
```

---

sidebar_position: 5
---

## 后台 API

### 鉴权

所有接口都需要带上 `validate` 参数，该参数值和配置文件中的 `server/validate` 参数值相同。示例：

``` bash
curl localhost:5001/history?validate=f4bde2a342c7c75aa276f78b26cfbd8a
```

接口返回：

```
{"code": 0, "message": "ok", "history": "[{\"type\": 1, \"text\": \"\\u4f1f\\u6d32 \\u4f60\\u597d\\uff01\\u8bd5\\u8bd5\\u5bf9\\u6211\\u558a\\u5524\\u9192\\u8bcd\\u53eb\\u9192\\u6211\\u5427\", \"time\": \"2019-02-07 19:10:19\", \"uuid\": \"f464d430-2ac8-11e9-bd1e-8c8590caf9a5\"}, {\"type\": 0, \"text\": \"\\u4eca\\u5929\\u5929\\u6c14\\u600e\\u4e48\\u6837\", \"time\": \"2019-02-07 19:10:33\", \"uuid\": \"fca4c218-2ac8-11e9-bd1e-8c8590caf9a5\"}, {\"type\": 1, \"text\": \"[Weather] \\u6df1\\u5733\\u5929\\u6c14\\uff1a\\u4eca\\u5929\\uff1a\\u591a\\u4e91\\uff0c20\\u523028\\u6444\\u6c0f\\u5ea6\\u3002\\u4eca\\u5929\\u5929\\u6c14\\u4e0d\\u9519\\uff0c\\u7a7a\\u6c14\\u6e05\\u65b0\\uff0c\\u9002\\u5408\\u51fa\\u95e8\\u8fd0\\u52a8\\u54e6\", \"time\": \"2019-02-07 19:10:33\", \"uuid\": \"fceec836-2ac8-11e9-bd1e-8c8590caf9a5\"}, {\"type\": 0, \"text\": \"\\u73b0\\u5728\\u51e0\\u70b9\", \"time\": \"2019-02-07 19:33:34\", \"uuid\": \"chat58b0d6a2-8395-1453-6383-4e27c421ea89\"}, {\"type\": 1, \"text\": \"2019\\u5e7402\\u670807\\u65e5 \\u661f\\u671f\\u56db \\u4e0b\\u5348 7:33\", \"time\": \"2019-02-07 19:33:35\", \"uuid\": \"3445dcd6-2acc-11e9-bd1e-8c8590caf9a5\"}]"}
```

### 管理

用于管理 joi-ai ，包括重启/打开勿扰模式/关闭勿扰模式。

- url：/operate
- method: POST
- 参数：

| 参数名 |  是否必须 | 说明  |
| ---   | ------- | ----- |
| validate | 是 | 参见 [鉴权](#鉴权) |
| type  | 是 |  管理类型类型。详见 [管理类型取值](#管理类型取值) |

### 管理类型取值

| 取值 | 说明 |
| ---- |  ---- |
| 0    | 重启 joi-ai |
| 1    | 打开勿扰模式 |
| 2    | 关闭勿扰模式 |

- 示例：

``` bash
curl -X POST localhost:5001/operate -d "type=restart&validate=f4bde2a342c7c75aa276f78b26cfbd8a"
```

- 返回：

| 字段名 |  说明  |
| ---   | ----- |
| code  | 返回码。0：成功；1：失败 |
| message | 结果说明 |

### 日志

用于查看 joi-ai 保存的日志。出于性能上的考虑，默认只返回最后 200 行的内容，相当于做了一次 `tail -n 200` 。

- url：/log
- method: GET
- 参数：

| 参数名 |  是否必须 | 说明  |
| ---   | ------- | ----- |
| validate | 是 | 参见 [鉴权](#_1) |
| lines | 可选 | 最大读取的日志行数。默认值为 200  |

- 示例：

``` bash
curl localhost:5001/log?validate=f4bde2a342c7c75aa276f78b26cfbd8a&lines=10
```

- 返回：

| 字段名 |  说明  |
| ---   | ----- |
| code  | 返回码。0：成功；1：失败 |
| message | 结果说明 |
| log | 日志内容 |

## 对话

### 发起对话

用于发起一次对话。

- url：/chat
- method: POST
- 参数：

| 参数名 |  是否必须 | 说明  |
| ---   | ------- | ----- |
| validate | 是 | 参见 [鉴权](#_1) |
| type  | 是 |  query 类型。 "text": 文本型 query ； "voice"：语音型 query |
| query | 仅当 type 为 "text" 时需要 |  发起对话的内容的 urlencode 后的值。例如 ”现在几点？“ 的 urlencode 结果 |
| uuid  | 仅当 type 为 "text" 时需要 |  为这个文本 query 赋予的一个 uuid。例如可以使用随机字符+时间戳。|
| voice | 仅当 type 为 "voice" 时需要  | 语音。需为 单通道，采样率为 16k 的 wav 格式语音的 base64 编码。 |

- 示例：

``` bash
curl -X POST localhost:5001/chat -d "type=text&query=%E7%8E%B0%E5%9C%A8%E5%87%A0%E7%82%B9&validate=f4bde2a342c7c75aa276f78b26cfbd8a&uuid=chated17be5d-0240-c9ba-2b2e-7eb98588cf34"
```

- 返回：

| 参数名 |  说明  |
| ---   | ----- |
| code  | 返回码。0：成功；1：失败 |
| message | 结果说明 |
| resp | 返回对话文本 |
| audio | TTS 音频的 url 地址（注意：不缓存的音频将在一分钟后被自动清理）    |

### 对话历史

用于查看 joi-ai 启动到现在的所有会话记录。

- url：/history
- method: GET
- 参数：

| 参数名 |  是否必须 | 说明  |
| ---   | ------- | ----- |
| validate | 是 | 参见 [鉴权](#_1) |

- 示例：

``` bash
curl localhost:5001/history?validate=f4bde2a342c7c75aa276f78b26cfbd8a
```

- 返回：

| 字段名 |  说明  |
| ---   | ----- |
| code  | 返回码。0：成功；1：失败 |
| message | 结果说明 |
| history | 会话历史 |

### 查看配置

用于查看 joi-ai 现有的配置。

- url：/config
- method: GET
- 参数：

| 参数名 |  是否必须 | 说明  |
| ---   | ------- | ----- |
| validate | 是 | 参见 [鉴权](#_1) |
| key | 可选 | 某个配置的键值。例如：`robot_name_cn` 。如果要多级key的对应value，则使用 `/一级key/二级key/...` 的形式，例如 `/server/host` 可以取 `server` 的 `host` 配置。 |

- 示例：

``` bash
curl localhost:5001/config?validate=f4bde2a342c7c75aa276f78b26cfbd8a\&key=server
```

- 返回：

| 字段名 |  说明  |
| ---   | ----- |
| code  | 返回码。0：成功；1：失败 |
| message | 结果说明 |
| config | 全部的配置，仅当不传 `key` 参数时提供 |
| value | `key` 提供的配置，仅当传 `key` 参数时提供；如果找不到这个 `key`，则返回 `null` |

### 修改配置

用于配置 joi-ai 。

- url：/config
- method: POST
- 参数：

| 参数名 |  是否必须 | 说明  |
| ---   | ------- | ----- |
| validate | 是 | 参见 [鉴权](#鉴权) |
| config | 是 | 配置内容，必须为 yaml 可解析的文本经过 urlencode 后的值 |

- 示例：

``` bash
curl -X localhost:5001/config -d "config=robot_name_cn%3A+'%E5%AD%99%E6%82%9F%E7%A9%BA'%0Afirst_name%3A+'%E4%BC%9F%E6%B4%B2'%0Alast_name%3A+'%E6%BD%98'%0Atimezone%3A+HKT%0Alocation%3A+'%E6%B7%B1%E5%9C%B3'%0A%0A%23+%E5%90%8E%E5%8F%B0%E7%AE%A1%E7%90%86%E7%AB%AF%0Aserver%3A%0A++++enable%3A+true%0A++++host%3A+'0.0.0.0'++%23+ip+%E5%9C%B0%E5%9D%80%0A++++port%3A+'5001'+++++%23+%E7%AB%AF%E5%8F%A3%E5%8F%B7++++%0A++++username%3A+'joi'..."
```

- 返回：

| 字段名 |  说明  |
| ---   | ----- |
| code  | 返回码。0：成功；1：失败 |
| message | 结果说明 |
