from datetime import datetime
import boto3
import os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from botocore.exceptions import ClientError, BotoCoreError
from img_handler import read_config

def create_ses_client():
    """创建SES客户端"""
    try:
        cf = read_config()
        region = cf.get('ses', 'region', fallback='ap-northeast-1')
        return boto3.client(service_name='ses', region_name=region)
    except Exception as e:
        raise Exception(f"创建SES客户端失败: {str(e)}")

def read_email_template():
    """读取邮件HTML模板"""
    try:
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'email_template.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            # 将模板内容中的花括号转义，只保留需要替换的变量占位符
            template = f.read()
            # 将CSS中的花括号转义
            template = template.replace('{', '{{').replace('}', '}}')
            # 恢复需要替换的变量占位符
            template = template.replace('{{description}}', '{description}')
            template = template.replace('{{datetime}}', '{datetime}')
            template = template.replace('{{analysis_text}}', '{analysis_text}')
            return template
    except Exception as e:
        raise Exception(f"读取邮件模板失败: {str(e)}")

def create_html_content(analysis_result, image_path, task_name):
    """创建HTML格式的邮件内容"""
    # 获取任务描述
    cf = read_config()
    description = cf.get(task_name, 'descriptions', fallback=task_name)
    
    # 格式化分析结果
    if isinstance(analysis_result, dict) and 'content' in analysis_result:
        analysis_text = analysis_result['content']
    else:
        analysis_text = str(analysis_result)
    
    # 将分析结果中的换行转换为HTML换行
    analysis_text = analysis_text.replace('\n', '<br>')
    
    # 读取HTML模板并填充内容
    template = read_email_template()
    html_content = template.format(
        description=description,
        datetime=datetime.now().strftime("%Y-%m-%d %H:%M"),
        analysis_text=analysis_text
    )
    
    return html_content
