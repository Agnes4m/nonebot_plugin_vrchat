<!-- markdownlint-disable MD026 MD031 MD033 MD036 MD041 MD046 MD051 -->
<div align="center">
  <img src="https://raw.githubusercontent.com/Agnes4m/nonebot_plugin_l4d2_server/main/image/logo.png" width="180" height="180"  alt="AgnesDigitalLogo">
  <br>
  <p><img src="https://s2.loli.net/2022/06/16/xsVUGRrkbn1ljTD.png" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot_plugin_vrchat

_✨使用第三方api实现vrchat相关操作✨_

<a href="https://github.com/Agnes4m/nonebot_plugin_vrchat/stargazers">
        <img alt="GitHub stars" src="https://img.shields.io/github/stars/Agnes4m/nonebot_plugin_vrchat" alt="stars">
</a>
<a href="https://github.com/Agnes4m/nonebot_plugin_vrchat/issues">
        <img alt="GitHub issues" src="https://img.shields.io/github/issues/Agnes4m/nonebot_plugin_vrchat" alt="issues">
</a>
<a href="https://jq.qq.com/?_wv=1027&k=HdjoCcAe">
        <img src="https://img.shields.io/badge/QQ%E7%BE%A4-399365126-orange?style=flat-square" alt="QQ Chat Group">
</a>
<a href="https://pypi.python.org/pypi/nonebot_plugin_vrchat">
        <img src="https://img.shields.io/pypi/v/nonebot_plugin_vrchat.svg" alt="pypi">
</a>
    <img src="https://img.shields.io/badge/python-3.8 | 3.9 | 3.10 | 3.11-blue.svg" alt="python">
    <img src="https://img.shields.io/badge/nonebot-2.0.* | 2.1.*-red.svg" alt="NoneBot">
</div>

## 说明

![logo](/nonebot_plugin_vrchat/img/theme.jpg)

本插件适配nonebot2框架，目的是在qq群中获取好友和地图的信息

使用到了saa插件，这代表这个这个插件支持v11,v12,kook,tg适配器

~~元宇宙大失败~~

## 安装


## 💿 安装

以下提到的方法 任选**其一** 即可

<details open>
<summary>[推荐] 使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

```bash
nb plugin install nonebot-plugin-vrchat
```

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

```bash
pip install nonebot-plugin-vrchat
```

</details>
<details>
<summary>pdm</summary>

```bash
pdm add nonebot-plugin-vrchat
```

</details>
<details>
<summary>poetry</summary>

```bash
poetry add nonebot-plugin-vrchat
```

</details>
<details>
<summary>conda</summary>

```bash
conda install nonebot-plugin-vrchat
```

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分的 `plugins` 项里追加写入

```toml
[tool.nonebot]
plugins = [
    # ...
    "nonebot_plugin_pjsk"
]
```

</details>

## 指令

- vrc帮助： 获取指令帮助
- vrc登录： 登录（需要输入账号密码，建议私聊）
- vrc在线好友： 查询当前在线好友
- vrc全部好友： 查询当前全部好友状态

## 感谢

- [vrchat第三方api](https://github.com/vrchatapi/vrchatapi-python)

## 其他

- 插件报错或建议q群：[q群: VR CHAT交流群](http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=SgA58TsEk1S4axSecQaPObNiwiOrlVwH&authKey=6Ob3NjrYayRDY029j6bPDH40oLQeZYYJQ7zlT4Pju0Iqb2uN3b4FBSBZV7d%2BrruK&noverify=0&group_code=579924932)
- [爱发电](https://afdian.net/a/agnes_digital) 感谢大家的赞助！你们的赞助将是我继续创作的动力！


## 📝 更新日志

<details>
<summary>点击展开</summary>

### 0.0.3

- 通过nonebot2商店检查，删除qqguild

### 0.0.2

- 使用pre-commit格式化项目

### 0.0.1

- 新建项目
- 增加“查询全部好友”功能
- 增加“查询在线好友功能”功能

</details>