import os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from img_handler import read_config
from ses_handler import create_ses_client, create_html_content

def send_analysis_email(task_name, analysis_result, image_path):
    """发送分析结果邮件"""

    # 读取配置
    cf = read_config()
    sender = cf.get('ses', 'sender')
    recipient = cf.get(task_name, 'email')
    subject = f"{cf.get(task_name, 'descriptions', fallback=task_name)} - QuickSight分析报告"
    
    # 创建邮件消息
    msg = MIMEMultipart('related')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    
    # 创建HTML内容
    html_content = create_html_content(analysis_result, image_path, task_name)
    html_part = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(html_part)
    
    # 验证图片文件
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"找不到图片文件: {image_path}")
    
    # 添加图片
    with open(image_path, 'rb') as f:
        img = MIMEImage(f.read())
        img.add_header('Content-ID', '<dashboard_image>')
        img.add_header('Content-Disposition', 'inline')
        msg.attach(img)
    
    # 发送邮件
    ses_client = create_ses_client()
    response = ses_client.send_raw_email(
        Source=sender,
        Destinations=[recipient],
        RawMessage={'Data': msg.as_string()}
    )
    
    print(f"邮件发送成功: {response['MessageId']}")
    return response
