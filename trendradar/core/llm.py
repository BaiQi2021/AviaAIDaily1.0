# coding=utf-8
"""
LLM 客户端模块

提供与 LLM API 交互的功能，用于生成新闻总结
"""

import requests
import json
from typing import List, Dict, Optional

class DeepSeekClient:
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com", model: str = "deepseek-chat"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model

    def summarize(self, stats: List[Dict]) -> str:
        """
        对新闻统计结果进行总结
        
        Args:
            stats: 统计结果列表，包含每个词组的新闻列表
            
        Returns:
            str: 总结文本
        """
        if not stats:
            return ""
        
        # 收集所有新闻标题
        news_items = []
        for group in stats:
            group_name = group.get('word', '未分类')
            for title_data in group.get('titles', []):
                news_items.append({
                    'group': group_name,
                    'title': title_data.get('title', ''),
                    'source': title_data.get('source_name', '')
                })
        
        if not news_items:
            return ""
            
        # 构建提示词
        prompt = "请对以下新闻进行简练而充实的总结，按话题分类概括主要内容：\n\n"
        
        # 为了避免上下文过长，限制新闻数量，每个分组最多取前5条
        processed_groups = {}
        for item in news_items:
            group = item['group']
            if group not in processed_groups:
                processed_groups[group] = []
            if len(processed_groups[group]) < 5:
                processed_groups[group].append(item)
                
        for group, items in processed_groups.items():
            prompt += f"【{group}】\n"
            for item in items:
                prompt += f"- {item['title']}\n"
            prompt += "\n"
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个专业的新闻分析助手。请对提供的新闻标题进行分析总结，要求语言精练，但内容充实。请使用Markdown格式输出。"},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        
        try:
            print("正在调用 DeepSeek API 生成总结...")
            response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content']
            print("总结生成成功")
            return content
        except Exception as e:
            print(f"DeepSeek API调用失败: {e}")
            return ""
