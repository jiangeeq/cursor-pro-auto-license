# Cursor Pro Automation Tool User Guide

README also available in: [中文](./README.md)

## Online Documentation
[cursor-auto-free-doc.vercel.app](https://cursor-auto-free-doc.vercel.app)

## Note
Recently, some users have sold this software on platforms like Xianyu. Please avoid such practices—there's no need to earn money this way.

## GUI Interface Guide
This project now provides a graphical user interface for easier use.

### Installation Steps
1. Make sure you have Python 3.6 or higher installed
2. Run the installation script: `python install_gui.py`
3. Follow the prompts to complete the installation
4. After installation, you can launch the GUI through the desktop shortcut or by running `python gui_launcher.py`

### Interface Features
- **Home**: Displays system status and quick action buttons
- **Account Registration**: Configure email, domain, and database information to automatically register Cursor Pro accounts
- **Authentication**: Update Cursor authentication information
- **Settings**: Configure browser and advanced settings
- **Logs**: Display operation logs
- **Account Management**: Manage registered accounts
- **Auto Update Check**: Automatically checks for new versions at startup and prompts users to update

## Sponsor for More Updates
![image](./screen/afdian-[未认证]阿臻.jpg)

## License
This project is licensed under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/).  
This means you may:  
- **Share** — Copy and redistribute the material in any medium or format.  
But you must comply with the following conditions:
- **Non-commercial** — You may not use the material for commercial purposes.

## Features
Automated account registration and token refreshing to free your hands.

## New Features
- **Graphical User Interface**: Now provides a PySide6-based GUI for easier use.
- **Web API Support**: Now you can configure a Web API service to automatically save registered account information for easy querying and management.
- **Version Update Detection**: Automatically checks for the latest version at startup, displays update notifications, and supports forced updates.

## Configuration
Please refer to the `env.example` file for configuration. To enable API functionality, set the following environment variables:
```
API_ENABLED=true
API_BASE_URL=http://localhost:8000
```

When API is enabled, the program will fetch the latest version information from the API and prompt for updates at startup.

## Important Notes
1. **Ensure you have Chrome installed. If not, [download here](https://www.google.com/intl/en_pk/chrome/).**  
2. **You must log into your account, regardless of its validity. Logged-in is mandatory.**  
3. **A stable internet connection is required, preferably via an overseas node. Do not enable global proxy.**

## Configuration Instructions
Please refer to our [online documentation](https://cursor-auto-free-doc.vercel.app) for detailed configuration instructions.

## Download
[https://github.com/chengazhen/cursor-auto-free/releases](https://github.com/chengazhen/cursor-auto-free/releases)

## Update Log
- **2025-01-09**: Added logs and auto-build feature.  
- **2025-01-10**: Switched to Cloudflare domain email.  
- **2025-01-11**: Added headless mode and proxy configuration through .env file.
- **2025-01-20**: Added IMAP to replace tempmail.plus.
- **2025-01-25**: Added MySQL database support for storing account information.
- **2025-01-30**: Added graphical user interface based on PySide6.

## Special Thanks
This project has received support and help from many open source projects and community members. We would like to express our special gratitude to:

### Open Source Projects
- [go-cursor-help](https://github.com/yuaotian/go-cursor-help) - An excellent Cursor machine code reset tool with 9.1k Stars. Our machine code reset functionality is implemented using this project, which is one of the most popular Cursor auxiliary tools.

Inspired by [gpt-cursor-auto](https://github.com/hmhm2022/gpt-cursor-auto); optimized verification and email auto-registration logic; solved the issue of not being able to receive email verification codes.
