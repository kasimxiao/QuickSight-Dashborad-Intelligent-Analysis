from img_handler import capture_quicksight_screenshot, read_config
from claude_handler import analyze_image_with_claude
from email_sender import send_analysis_email
import json
import os
from datetime import datetime


def get_last_file_time_diff(task_dir):
    try:
        # 获取最后修改的文件
        last_file = max([os.path.join(task_dir, f) for f in os.listdir(task_dir)], 
                       key=os.path.getmtime)
        
        # 计算时间差（小时）
        hours_diff = (datetime.now() - 
                     datetime.fromtimestamp(os.path.getmtime(last_file))).total_seconds() / 3600
        return hours_diff
    
    except Exception as e:
        return 0

def process_task(task_name):
    """处理单个任务"""
    # 获取上一轮执行时间与当前时间的时间差（小时）
    task_dir = os.path.join(os.path.dirname(__file__), 'output', task_name)
    hours_diff = get_last_file_time_diff(task_dir)

    cf = read_config()
    frequency = cf.get(task_name, 'frequency')

    if round(float(frequency), 2) <= hours_diff :
        #小于设置执行频次，不执行
        return True

    # 获取截图
    screenshot_path = capture_quicksight_screenshot(task_name)
    
    # 使用Claude分析图片
    analysis_result = analyze_image_with_claude(screenshot_path, task_name)

    # 发送分析结果邮件
    send_analysis_email(task_name, analysis_result, screenshot_path)

    return True
        
def process_all_tasks():
    """处理所有配置的任务"""

    # 读取配置
    cf = read_config()
    task_list = cf.get('task', 'task').split(',')
    
    results = []
    for task_name in task_list:
        task_name = task_name.strip()
        process_task(task_name)
        
    return results
        

if __name__ == "__main__":
    results = process_all_tasks()
    print(results)