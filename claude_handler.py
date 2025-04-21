import boto3
import base64
import json
import configparser
import os

def read_config():
    """读取配置文件"""
    cf = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
    cf.read(config_path, encoding="utf-8")
    return cf

def encode_image(image_path):
    """将图片文件转换为base64编码"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        raise Exception(f"读取图片文件失败: {str(e)}")

def analyze_image_with_claude(image_path, task_name=None):
    """使用Claude分析单张图片内容"""
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
    
    # 确保图片路径是绝对路径
    if not os.path.isabs(image_path):
        image_path = os.path.abspath(image_path)

        
    # 检查文件是否存在
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"找不到图片文件: {image_path}")
    
    # 准备图片数据
    base64_image = encode_image(image_path)
    
    # 获取prompt
    if task_name and cf.has_option(task_name, 'prompt'):
        prompt = cf.get(task_name, 'prompt')
    else:
        prompt = """分析图片中的内容,提供详细描述。"""

    # 构建请求体
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_image
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
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

