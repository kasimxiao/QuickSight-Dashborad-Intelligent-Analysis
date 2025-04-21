# QuickSight Insight

这是一个用于自动化截取 Amazon QuickSight 仪表板并使用 Claude 进行分析的工具。

## 环境要求

- Python 3.7+
- Chrome 浏览器 (用于Selenium截图)
- AWS账号配置 (用于访问AWS服务)

## 安装步骤

1. 安装依赖包：
```bash
pip install -r requirements.txt
```

2. 安装Chrome WebDriver：
   - 确保已安装Chrome浏览器
   - 下载对应版本的ChromeDriver并添加到系统PATH中

3. 配置AWS凭证：
   - 确保已配置AWS凭证（~/.aws/credentials）
   - 或设置环境变量：
     ```
     export AWS_ACCESS_KEY_ID=your_access_key
     export AWS_SECRET_ACCESS_KEY=your_secret_key
     export AWS_DEFAULT_REGION=your_region
     ```

4. 配置config.ini：
   - 复制config.ini.example为config.ini
   - 填写必要的配置信息：
     - AWS服务配置（S3、SES、Bedrock等）
     - QuickSight仪表板URL
     - 任务配置

## 目录结构

```
.
├── README.md
├── requirements.txt
├── config.ini
├── main.py                 # 主程序入口
├── img_handler.py          # 图片处理模块
├── claude_handler.py       # Claude API处理模块
├── s3_handler.py          # S3操作模块
├── ses_handler.py         # SES邮件发送模块
├── sts.py                 # AWS STS处理模块
└── output/                # 输出目录
    └── {task_name}/      # 任务输出目录
```

## 配置文件说明

config.ini需要配置以下内容：

```ini
[task]
task = task1,task2  # 要执行的任务列表，用逗号分隔

[task1]
url = https://quicksight.aws.amazon.com/...  # QuickSight仪表板URL
window_size = 1920,1080  # 截图窗口大小
frequency = 24  # 执行频率（小时）
descriptions = 任务1描述  # 任务描述
prompt = 分析该图表并...  # Claude分析提示词

[s3]
bucket = your-bucket  # S3存储桶名称
region = ap-northeast-1  # S3区域

[ses]
region = ap-northeast-1  # SES区域

[bedrock]
region = us-west-2  # Bedrock区域
model_id = anthropic.claude-3-5-sonnet-20241022-v2:0  # Claude模型ID

[iam]
role_arn = arn:aws:iam::...  # IAM角色ARN
```

## 使用方法

1. 配置完成后，直接运行main.py：
```bash
python main.py
```

2. 程序会：
   - 根据配置的任务列表执行截图
   - 使用Claude分析图表内容
   - 通过邮件发送分析结果

## 注意事项

1. 确保AWS账号有足够的权限访问相关服务
2. 建议使用IAM角色或用户进行权限管理
3. 注意配置
