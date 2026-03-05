import os
import requests
import time

# ========== 配置（从GitHub密钥自动读取，你不用改）==========
APPID = os.getenv("APPID")
APPSECRET = os.getenv("APPSECRET")
TEMPLATE_ID = os.getenv("TEMPLATE_ID")
OPENID = os.getenv("OPENID")

# ========== 终极出题提示词（不变，贴合山东事业编统考）==========
def generate_questions():
    prompt = """
你是一位山东公务员，也是一位山东公考出题人，并且还是一位资深的公考指导员，
你对公务员和事业单位的考试了如指掌。请记住你的身份。
你做事说话完全符合该身份，对考生知无不言、言无不尽。

我要参加2026年山东省事业单位统考，
你必须从出题人角度指导，严格基于山东近3年真题规律与山东省情，
禁止幻觉、禁止超纲、禁止外省题目。

出题规则（必须严格执行）：
1. 职业能力倾向测验（职测）
   每个模块出 5 道题，共 25 题：
   - 常识判断（山东时政、省情、法律、经济、科技）
   - 言语理解与表达（逻辑填空、片段阅读、语句排序）
   - 数量关系（数学运算，山东高频题型）
   - 判断推理（图形、定义、类比、逻辑）
   - 资料分析（山东最爱考的统计类型）

2. 综合应用能力（综应）
   每个模块出 1 道题，共 5 题：
   - 归纳概括题
   - 提出对策题
   - 综合分析题
   - 公文写作题（通知/请示/报告/倡议书）
   - 文章写作题（山东事业编作文主题）

出题要求：
1. 考点来源：山东近3年高频考点 + 结合山东省情预测的2026必考考点
2. 难度：基础、中等、偏难 随机分布
3. 样式：最新山东事业单位统考真题样式
4. 每道题必须包含：题目、选项（客观题）、答案、【出题人思路】（考点、命题意图、山东考情、陷阱提示）
5. 输出必须有内容，禁止空内容，即使出题异常，也需明确提示文字（不少于10字）

输出格式清晰、可直接刷题，不要多余开场白和结尾。
"""

    # 稳定免费的联网AI接口（无需API KEY，直接调用）
    try:
        resp = requests.get(
            "https://api.lolimi.cn/API/ai/wx.php",
            params={"msg": prompt},
            timeout=180
        )
        data = resp.json()
        content = data.get("content", "")
        # 新增：避免空内容，空内容时直接判定失败并提示
        if not content or len(content.strip()) < 10:
            return "出题服务暂时不可用，将在5分钟后重新尝试出题。", False
        # 判断是否出题成功（排除空内容、失败提示）
        if "出题服务暂时不可用" not in content and "出题接口异常" not in content:
            return content, True
        else:
            return "出题服务暂时不可用，将在5分钟后重新尝试出题。", False
    except Exception as e:
        print(f"出题接口异常：{str(e)}")
        return "出题接口异常，将在5分钟后重新尝试出题。", False

# ========== 微信测试号推送（替换PushPlus，完全免费）==========
def get_access_token():
    # 获取微信推送授权token（免费，有效期2小时，自动刷新）
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        # 新增：判断token获取是否成功
        if "errcode" in data and data["errcode"] != 0:
            print(f"获取token失败：{data.get('errmsg', '未知错误')}")
            return ""
        return data.get("access_token", "")
    except Exception as e:
        print(f"获取token异常：{str(e)}")
        return ""

def send_to_wechat(content):
    access_token = get_access_token()
    if not access_token:
        print("推送失败：未获取到微信授权token")
        return False  # 推送失败返回False
    # 推送接口地址
    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
    # 推送内容（适配模板格式，确保content不为空）
    content = content.strip() if content.strip() else "当前出题暂未获取到内容，将在5分钟后重试"
    data = {
        "touser": OPENID,
        "template_id": TEMPLATE_ID,
        "data": {
            "content": {
                "value": content,
                "color": "#000000"
            }
        }
    }
    try:
        resp = requests.post(url, json=data, timeout=30)
        resp_data = resp.json()
        # 判断推送是否成功（微信返回errcode为0则成功）
        if resp_data.get("errcode", 1) != 0:
            print(f"推送失败：{resp_data.get('errmsg', '未知错误')}")
            return False
        return True
    except Exception as e:
        print(f"推送异常：{str(e)}")
        return False

# ========== 重试逻辑（5次重试，每次间隔5分钟）==========
def run_with_retry():
    max_retries = 5  # 最大重试次数
    retry_interval = 300  # 重试间隔（5分钟=300秒）
    for retry in range(max_retries):
        # 生成题目
        content, success = generate_questions()
        if success:
            # 出题成功，推送题目
            send_success = send_to_wechat(content)
            if send_success:
                print("出题及推送成功")
                return
            else:
                # 推送失败，也算重试一次
                error_msg = f"出题成功，但推送失败，{max_retries - retry - 1}次重试机会，5分钟后重试。"
                send_to_wechat(error_msg)
                print(error_msg)
        else:
            # 出题失败，推送失败提示
            send_to_wechat(content)
            print(f"第{retry + 1}次出题失败，{max_retries - retry - 1}次重试机会，5分钟后重试。")
        
        # 不是最后一次重试，等待5分钟
        if retry < max_retries - 1:
            time.sleep(retry_interval)
    
    # 5次重试均失败，推送最终提示，次日自动重试
    final_msg = "今日出题已尝试5次，均未成功，将在次日自动重试，请留意明日推送。"
    send_to_wechat(final_msg)
    print(final_msg)

if __name__ == "__main__":
    run_with_retry()
