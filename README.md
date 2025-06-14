<!-- markdownlint-disable MD026 MD031 MD033 MD036 MD041 MD046 MD051 -->
<div align="center">
  <img src="https://raw.githubusercontent.com/Agnes4m/nonebot_plugin_l4d2_server/main/image/logo.png" width="180" height="180"  alt="AgnesDigitalLogo">
  <br>
  <p><img src="https://s2.loli.net/2022/06/16/xsVUGRrkbn1ljTD.png" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot_plugin_vrchat

_✨ 使用第三方 api 实现 vrchat 相关操作 ✨_

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
    <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">
    <img src="https://img.shields.io/badge/nonebot-2.1.0+-red.svg" alt="NoneBot">
</a>
</a>
    <img src="https://img.shields.io/badge/pydantic-v2.11+-blue.svg" alt="python">
    <img src="https://img.shields.io/badge/pydantic-v2.11+-red.svg" alt="NoneBot">
</a>
<a href="https://github.com/nonebot/plugin-alconna">
        <img src="https://img.shields.io/badge/%E9%80%82%E9%85%8D%E5%99%A8-nonebot_plugin_alconna-greg" alt="adpters">
</a>
</div>

## 说明(国内服务器可使用)

![logo](./img/theme.jpg)

本插件适配 nonebot2 框架，目的是在 qq 群中获取好友和地图的信息

首先你应该私聊机器人发送`vrc登录`，按提示输入账号密码和验证码，才能正常使用功能

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

- `vrc帮助`： 获取指令帮助
- `vrc登录`： 登录（需要输入账号密码，建议私聊）
- `vrc全部好友`： 查询当前全部好友状态
- `vrc查询好友【text】`：查询用户名称
- `vrc查询世界【text】`： 查询世界名称

## 感谢

- [vrchat 第三方 api](https://github.com/vrchatapi/vrchatapi-python)

## 其他

- 插件报错或建议：发iss或者 [q 群](https://qm.qq.com/q/qK3156ysN2) 或者邮箱
- [爱发电](https://afdian.tv/a/agnes_digital) 感谢大家的赞助！你们的赞助将是我继续创作的动力！

## 📝 更新日志

<details>
<summary>点击展开</summary>

### 0.1.2

- 修复了无法加载cookie的bug
- 新增i18n

### 0.1.1

- 新增了无法加载cookie的bug
- 修改了部分注释

### 0.1.0

- 修复人物图片错误
- 新增好友参数显示
- 新增查询好友图片

### 0.0.6

- 修复了图片错误
- 添加公共ck以供查询 by 饼干
- 修复查询用户因为部分参数为空导致被跳过的问题
- 重构了项目
- 新增查询好友用户距离上次时间

### 0.0.5

- 新增查询世界功能
- 新增人物图片 by 饼干佬
- 合并后不知道哪里出问题了）
- 暂时将适配器改成v11通过检查

### 0.0.4

- 新增查询用户功能
- 适配 nonebot2.1.\*
- 部分逻辑改进

### 0.0.3

- 通过 nonebot2 商店检查，删除 qqguild

### 0.0.2

- 使用 pre-commit 格式化项目

### 0.0.1

- 新建项目
- 增加“查询全部好友”功能
- 增加“查询在线好友功能”功能

</details>
