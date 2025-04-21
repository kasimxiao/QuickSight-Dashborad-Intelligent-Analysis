import os
import boto3
import configparser

def read_config():
    """读取配置文件"""
    cf = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
    cf.read(config_path, encoding="utf-8")
    return cf

def upload_to_s3(file_path, s3_key):
    """上传文件到S3存储桶"""
    try:
        cf = read_config()
        bucket = cf.get('s3', 'bucket')
        region = cf.get('s3', 'region')
        
        s3_client = boto3.client('s3', region_name=region)
        s3_client.upload_file(file_path, bucket, s3_key)
        
    except Exception as e:
        error_msg = f"上传到S3时发生错误: {str(e)}"
        raise Exception(error_msg)
