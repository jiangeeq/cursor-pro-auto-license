# Cursor Pro 自动化工具使用说明


[English doc](./README.EN.md)


## 在线文档
[cursor-auto-free-doc.vercel.app](https://cursor-auto-free-doc.vercel.app)


## 公众号

![公众号](./screen/qrcode_for_gh_c985615b5f2b_258.jpg)

## 图形界面使用说明
本项目现已提供图形界面，方便小白用户使用。

### 安装步骤
1. 确保已安装Python 3.6或更高版本
2. 运行安装脚本：`python install_gui.py`
3. 按照提示完成安装
4. 安装完成后，可以通过桌面快捷方式或运行`python gui_launcher.py`启动图形界面

### 界面功能
- **主页**：显示系统状态和快速操作按钮
- **账号注册**：配置邮箱、域名和数据库信息，自动注册Cursor Pro账号
- **认证信息**：更新Cursor的认证信息
- **设置**：配置浏览器和高级设置
- **日志**：显示操作日志
- **账号管理**：管理已注册的账号
- **自动更新检测**：启动时自动检查新版本，提示用户更新

## 英文名字集
https://github.com/toniprada/usa-names-dataset

## 新增功能
- **图形用户界面**：现在提供了基于PySide6的图形界面，方便小白用户使用。
- **Web API支持**: 现在可以配置Web API服务，注册成功的账号信息将自动保存到远程服务，方便后续查询和管理。
- **版本更新检测**: 启动时自动检查最新版本，有新版本时弹出更新提示，支持强制更新。

## 配置说明
请参考 `env.example` 文件进行配置。如需启用API功能，请设置以下环境变量：
```
API_ENABLED=true
API_BASE_URL=http://localhost:8000
```

启用API后，程序将从API获取最新版本信息并在启动时提示更新。

## 许可证声明
本项目采用 [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/) 许可证。
这意味着您可以：
- 分享 — 在任何媒介以任何形式复制、发行本作品
但必须遵守以下条件：
- 非商业性使用 — 您不得将本作品用于商业目的

## 声明
- 本项目仅供学习交流使用，请勿用于商业用途。
- 本项目不承担任何法律责任，使用本项目造成的任何后果，由使用者自行承担。


## 感谢 linuxDo 这个开源社区(一个真正的技术社区)
https://linux.do/

## 特别鸣谢
本项目的开发过程中得到了众多开源项目和社区成员的支持与帮助，在此特别感谢：

## 请我喝杯茶 | buy me a cup of tea
<img src="./screen/image.png" width="300"/>
<img src="./screen/28613e3f3f23a935b66a7ba31ff4e3f.jpg" width="300"/>
<img src="./screen/mm_facetoface_collect_qrcode_1738583247120.png" width="300"/>


