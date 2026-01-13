from setuptools import setup, find_packages

# 读取 requirements.txt 文件中的依赖
with open('requirements.txt', 'r') as f:
    install_requires = [line.strip() for line in f.readlines() if line.strip()]

setup(
    name='fastfeishu',
    version='1.0.0',
    author='yuzhuoyang',
    author_email='this.jibuzixin@gmail.com',
    description='飞书文档快速操作API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',  # 指定描述内容类型为 Markdown
    packages=find_packages(),  # 自动查找项目中的包
    install_requires=install_requires,
    python_requires='>=3.11,<3.12',  # 版本太高会有依赖冲突
)