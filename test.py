#!/usr/bin/env python3
# debug_api.py
import json

from openai import OpenAI, OpenAIError

# ---------- 1. 填写你自己的配置 ----------
CFG = {
    "api_key": "sk-swuyugqxspwgdmkunxwijtftwuldciegnhpgoyuwvaajwwvm",  # 你的 SiliconFlow API key
    "ai_model": "deepseek-ai/DeepSeek-V3",              # 要测试的模型
}

# ---------- 2. 调试函数 ----------
def debug_siliconflow() -> None:
    client = OpenAI(
        base_url="https://api.siliconflow.cn/v1",
        api_key=CFG["api_key"],
    )

    prompt = """
当前阶段：联调
剩余工作日：7 天
已加班(9点后)小时：{"张三": 12.3, "李四": 8.7}

【要求】
1. 无每日上限，按剩余工作日均摊
2. 每人给一句健康建议
3. 仅返回一段合法 JSON，不要添加 Markdown 或多余文字：
{
  "张三": {"再分配": 2.5, "建议": "多喝水"},
  "李四": {"再分配": 3.0, "建议": "早点睡"}
}
"""
    try:
        resp = client.chat.completions.create(
            model=CFG["ai_model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.3,
        )
        raw = resp.choices[0].message.content or ""
        print("原始返回 >>>")
        print(raw)
        print("-" * 40)

        # 去掉可能的 ```json 包裹
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("\n", 1)[0]

        parsed = json.loads(raw)
        print("解析成功 >>>")
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
    except OpenAIError as e:
        print("❌ 网络或 API 错误：", e)
    except json.JSONDecodeError as e:
        print("❌ JSON 解析错误：", e)
        print("原始返回：", raw)
    except Exception as e:
        print("❌ 其他异常：", e)

if __name__ == "__main__":
    debug_siliconflow()