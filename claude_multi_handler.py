import boto3
import base64
import json
import configparser
import os
from claude_handler import read_config, encode_image

def analyze_images_with_claude(image_paths, task_name=None):
    """使用Claude同时分析多张图片内容"""
    try:
        # 读取配置
        cf = read_config()
        
        # 获取Bedrock配置
        region = cf.get('bedrock', 'region', fallback='us-west-2')
        model_id = cf.get('bedrock', 'model_id', fallback='anthropic.claude-3-5-sonnet-20241022-v2:0')
        
        # 创建Bedrock Runtime客户端
        bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=region
        )
        
        # 处理图片路径列表
        if isinstance(image_paths, str):
            image_paths = [image_paths]
            
        # 构建消息内容
        content = []
        for image_path in image_paths:
            # 确保图片路径是绝对路径
            if not os.path.isabs(image_path):
                image_path = os.path.abspath(image_path)
                
            # 检查文件是否存在
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"找不到图片文件: {image_path}")
            
            # 添加图片内容
            base64_image = encode_image(image_path)
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": base64_image
                }
            })
        
        # 获取prompt
        if task_name and cf.has_option(task_name, 'prompt'):
            prompt = cf.get(task_name, 'prompt')
        else:
            prompt = """分析图片中的内容,提供详细描述。如果有多张图片，请分别描述每张图片的内容，并说明它们之间的关系（如果有的话）。"""
        
        # 添加文本prompt
        content.append({
            "type": "text",
            "text": prompt
        })

        # 构建请求体
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ]
        }

        # 调用Bedrock的Claude模型
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(body)
        )
        
        # 解析响应
        response_body = json.loads(response.get('body').read())
        return response_body['content'][0]['text']
    
    except Exception as e:
        error_msg = f"分析图片时发生错误: {str(e)}"
        print(error_msg)  # 打印错误信息以便调试
        raise Exception(error_msg)
