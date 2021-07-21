from setuptools import setup, find_packages

setup(
    name="aliyun-scripts",
    version="1.0.0",
    description="Automate aliyun ECS and EIP management",
    author="PIG208",
    author_email="p359101898@gmail.com",
    install_requires=[
        "aliyun-python-sdk-core==2.13.35",
        "aliyun-python-sdk-ecs==4.24.3",
        "aliyun-python-sdk-vpc==3.0.14",
    ],
    packages=find_packages(),
    project_urls={
        "Source": "https://github.com/PIG208/aliyun-script",
    },
    entry_points={
        "console_scripts": [
            "aliyun-ecs=aliyun_scripts.tools.ecs_tool:main",
            "aliyun-eip=aliyun_scripts.tools.eip_tool:main",
            "aliyun-ui=aliyun_scripts.gui.app:main",
        ],
    },
)
