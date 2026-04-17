import os
from dotenv import load_dotenv 
from langchain_openai import ChatOpenAI
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch
# from langchain_core.tools import tool
from pydantic import BaseModel, Field
import requests,json

from langchain.agents import create_agent
from langchain.tools import tool
import matplotlib
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import pymysql

# 加载环境变量
load_dotenv(override=True)

# 内置搜索工具
search_tool = TavilySearch(max_results=5, topic="general")

class WeatherQuery(BaseModel):
    city: str = Field(description="The city name in Chinese (e.g., '北京', '上海')")

@tool(args_schema = WeatherQuery)
def get_weather(city):
    """
    查询即时天气函数
    :param city: 必要参数，字符串类型，用于表示查询天气的具体城市中文名称，\
    注意，中国的城市需要使用中文名称，例如如果需要查询北京市天气，则city参数需要输入'北京'；
    :return：易客天气API查询即时天气的结果，具体URL请求地址为：http://v1.yiketianqi.com/free/day\
    返回结果对象类型为解析之后的JSON格式对象，并用字符串形式进行表示，其中包含了全部重要的天气信息
    """
    # Step 1.构建请求
    url = "http://v1.yiketianqi.com/free/day"

    # Step 2.设置查询参数
    params = {
        "appid": "78831521",               # 用户appid
        "appsecret": "4m3jWLhn",          # 用户appsecret
        "city": city,                      # 城市名称（中文）
        "unescape": "1"                    # 直接输出中文
    }

    # Step 3.发送GET请求
    response = requests.get(url, params=params)
    
    # Step 4.解析响应
    data = response.json()
    return json.dumps(data, ensure_ascii=False)


tools = [search_tool,get_weather]

# 创建模型
model = ChatOpenAI(
    model="qwen-plus-latest",  # 或您指定的模型名称
    openai_api_key=os.getenv("DASHSCOPE_API_KEY"),  # 替换为您的实际 API Key
    openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 替换为您的 base URL
    temperature=0.7,
    max_tokens=1000
)

prompt = """
你是一名乐于助人的智能助手，擅长根据用户的问题选择合适的工具来查询信息并回答。

当用户的问题涉及**天气信息**时，你应优先调用`get_weather`工具，查询用户指定城市的实时天气，并在回答中总结查询结果。

当用户的问题涉及**新闻、事件、实时动态**时，你应优先调用`search_tool`工具，检索相关的最新信息，并在回答中简要概述。

如果问题既包含天气又包含新闻，请先使用`get_weather`查询天气，再使用`search_tool`查询新闻，最后将结果合并后回复用户。

所有回答应使用**简体中文**，条理清晰、简洁友好。
"""

# 创建图
graph = create_react_agent(model=model, tools=tools, prompt=prompt)