from selenium import webdriver
import time
import configparser
import os
from datetime import datetime
from sts import get_sts_url
from s3_handler import upload_to_s3

def read_config():
    """读取配置文件"""
    cf = configparser.ConfigParser()
    cf.read(os.path.join(os.path.dirname(__file__), 'config.ini'), encoding="utf-8")
    return cf


def capture_quicksight_screenshot(task_name):
    """根据任务名称捕获QuickSight仪表板截图"""
    try:
        # 读取配置
        cf = read_config()
            
        # 获取任务配置
        url = cf.get(task_name, 'url')
        window_size = cf.get(task_name, 'window_size').split(',')
        #sts授权
        access_url = get_sts_url(cf.get('iam', 'role_arn'))
        
        # 配置Chrome并获取截图
        option = webdriver.ChromeOptions()
        option.add_argument('--no-sandbox')
        option.add_argument('--headless')  # 无界面模式
        option.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=option)
        
        try:
            driver.get(access_url)
            driver.get(url)
            driver.set_window_size(int(window_size[0]), int(window_size[1]))
            time.sleep(10)
            
            # 保存截图
            timestamp = datetime.now().strftime("%Y%m%d%H%M")
            screenshot_name = f'{task_name}_{timestamp}.png'
            task_dir = os.path.join(os.path.dirname(__file__), 'output', task_name)
            os.makedirs(task_dir, exist_ok=True)
            screenshot_path = os.path.join(task_dir, screenshot_name)
            driver.get_screenshot_as_file(screenshot_path)
            
            # 上传到S3
            s3_url = upload_to_s3(screenshot_path, f"{task_name}/{screenshot_name}")
            return screenshot_path
            
        finally:
            driver.quit()
            
    except Exception as e:
        raise
