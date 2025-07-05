from DrissionPage import ChromiumOptions, Chromium
import sys
import os
import logging
from dotenv import load_dotenv

# 尝试使用UTF-8编码加载.env文件
try:
    load_dotenv(encoding="utf-8")
except UnicodeDecodeError:
    # 如果UTF-8失败，尝试使用latin1编码
    load_dotenv(encoding="latin1")


class BrowserManager:
    def __init__(self):
        self.browser = None

    def init_browser(self, user_agent=None):
        """初始化浏览器"""
        co = self._get_browser_options(user_agent)
        self.browser = Chromium(co)
        return self.browser

    def close_browser(self, browser_instance=None):
        """关闭指定的浏览器实例或默认浏览器"""
        try:
            # 确定要关闭的浏览器实例
            browser_to_close = browser_instance if browser_instance else self.browser
            
            if browser_to_close:
                try:
                    # 尝试关闭所有标签页 - 安全地访问tabs属性
                    if hasattr(browser_to_close, 'tabs'):
                        tabs = getattr(browser_to_close, 'tabs', None)
                        if tabs:
                            for tab in list(tabs):
                                try:
                                    tab.quit()
                                except Exception as tab_e:
                                    logging.debug(f"关闭标签页时出现非致命错误: {str(tab_e)}")
                except Exception as tab_close_e:
                    logging.debug(f"关闭所有标签页时出现非致命错误: {str(tab_close_e)}")
                
                # 尝试正常关闭浏览器
                try:
                    browser_to_close.quit()
                except Exception as e:
                    logging.error(f"关闭浏览器失败: {str(e)}")
                    
                    # 尝试强制关闭浏览器进程
                    try:
                        # 安全地访问driver属性
                        if hasattr(browser_to_close, 'driver'):
                            driver = getattr(browser_to_close, 'driver', None)
                            if driver:
                                driver.quit()
                    except Exception as driver_e:
                        logging.debug(f"关闭浏览器驱动时出现错误: {str(driver_e)}")
        except Exception as e:
            logging.error(f"关闭浏览器过程中出错: {str(e)}")
        finally:
            # 如果关闭的是内部浏览器，重置引用
            if not browser_instance and self.browser:
                self.browser = None

    def _get_browser_options(self, user_agent=None):
        """获取浏览器配置"""
        co = ChromiumOptions()
        try:
            extension_path = self._get_extension_path("turnstilePatch")
            co.add_extension(extension_path)
        except FileNotFoundError as e:
            logging.warning(f"警告: {e}")

        browser_path = os.getenv("BROWSER_PATH")
        if browser_path:
            co.set_paths(browser_path=browser_path)

        co.set_pref("credentials_enable_service", False)
        co.set_argument("--hide-crash-restore-bubble")
        proxy = os.getenv("BROWSER_PROXY")
        if proxy:
            co.set_proxy(proxy)

        co.auto_port()
        if user_agent:
            co.set_user_agent(user_agent)

        # 从.env文件获取BROWSER_HEADLESS设置
        # 确保布尔值判断正确，只有明确设置为"true"才是True，其他任何值都是False
        browser_headless = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
        logging.debug(f"浏览器无头模式设置: {browser_headless}")
        co.headless(browser_headless)  # 根据配置决定是否使用无头模式

        # Mac 系统特殊处理
        if sys.platform == "darwin":
            co.set_argument("--no-sandbox")
            co.set_argument("--disable-gpu")

        return co

    def _get_extension_path(self,exname='turnstilePatch'):
        """获取插件路径"""
        root_dir = os.getcwd()
        extension_path = os.path.join(root_dir, exname)

        # PyInstaller创建的临时文件夹中查找资源
        # sys._MEIPASS是PyInstaller打包时的一个特殊属性
        try:
            if getattr(sys, "_MEIPASS", None):
                extension_path = os.path.join(sys._MEIPASS, exname)
        except AttributeError:
            # 如果_MEIPASS不存在，继续使用之前的路径
            pass

        if not os.path.exists(extension_path):
            raise FileNotFoundError(f"插件不存在: {extension_path}")

        return extension_path

    def quit(self):
        """关闭浏览器"""
        if self.browser:
            try:
                self.browser.quit()
            except:
                pass
            finally:
                self.browser = None
