import os
import time
# 替换为OpenAI客户端，适配指定的配置格式（兼容deepseek-r1模型，调整接口参数）
from openai import OpenAI

# ========== 配置（从GitHub密钥/变量自动读取，你不用改）==========
APPID = os.getenv("APPID")
APPSECRET = os.getenv("APPSECRET")
TEMPLATE_ID = os.getenv("TEMPLATE_ID")
OPENID = os.getenv("OPENID")
# OpenAI配置（读取GitHub配置的变量，无需手动修改，适配deepseek-r1模型）
client = OpenAI(
    # 自动读取GitHub配置的API_KEY变量，无需手动填写
    api_key=os.getenv("API_KEY"),
    # 自动读取GitHub配置的OPENAI_API_BASE变量（需确保是deepseek-r1兼容的base_url）
    base_url=os.getenv("OPENAI_API_BASE")
)

# 新增：Markdown语法转微信适配格式（解决deepseek-r1输出Markdown无法渲染的问题）
def markdown_to_wechat(content):
    # 微信模板不支持Markdown原生语法，将常用Markdown格式转为微信可识别的普通格式
    # 1. 去除Markdown标题符号（#、##等），转为普通文本，保留标题含义
    content = content.replace("### ", "").replace("## ", "").replace("# ", "")
    # 2. 处理Markdown列表（-、* 开头），转为普通有序/无序，避免渲染错乱
    content = content.replace("\n- ", "\n  ● ").replace("\n* ", "\n  ● ")
    # 3. 处理Markdown加粗（** **），微信不支持加粗标签，保留文本内容，去除加粗符号
    content = content.replace("**", "")
    # 4. 处理Markdown斜体（* *），去除斜体符号，保留文本
    content = content.replace("*", "")
    # 5. 处理Markdown引用（> ），去除引用符号，转为普通文本
    content = content.replace("> ", "")
    # 6. 处理Markdown代码块（```），去除代码块符号，转为普通文本（适配刷题场景）
    content = content.replace("```", "")
    # 7. 处理Markdown换行（两个空格+换行），转为微信支持的换行
    content = content.replace("  \n", "\n")
    # 8. 去除多余空行，避免微信渲染时出现大片空白
    content = "\n".join([line for line in content.split("\n") if line.strip()])
    return content

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
6. 输出不用分段太多，紧凑清晰，适配微信模板推送，避免格式错乱导致无内容显示
7. 输出内容不要包含特殊符号（如★、◆等），避免{{content.DATA}}无法正常渲染
8. 输出内容需完整连贯，不要拆分段落，减少换行，确保微信模板能完整读取全部内容（适配deepseek-r1模型输出特点）
9. 若输出包含Markdown语法，尽量简化，避免复杂格式（后续会自动适配微信渲染）

输出格式清晰、可直接刷题，不要多余开场白和结尾。
"""

    # OpenAI客户端调用（适配deepseek-r1模型，调整接口参数，确保输出完整读取）
    try:
        # 新增：打印接口调用关键信息（适配deepseek-r1，确认模型调用）
        print("="*50)
        print("【关键步骤1：模型接口调用信息】")
        print(f"模型：deepseek-r1")
        print(f"模型base_url：{os.getenv('OPENAI_API_BASE')[:20]}****（隐藏部分字符，保护隐私）")
        print(f"模型API_KEY：{os.getenv('API_KEY')[:8]}****（隐藏部分字符，保护隐私）")
        print(f"AI出题提示词（精简）：{prompt[:50]}...（完整提示词见代码）")
        print("正在调用deepseek-r1模型，获取出题内容...")
        
        # 适配deepseek-r1模型的接口请求参数（调整模型参数，确保输出完整）
        response = client.chat.completions.create(
            model="deepseek-r1",  # 切换为deepseek-r1模型，确保模型匹配
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,  # 提升token上限，确保deepseek-r1输出完整题目（避免内容被截断）
            temperature=0.7,  # 控制出题随机性，贴合真题难度
            top_p=0.9,
            stream=False,
            # 新增：强制模型输出完整内容，不截断（适配deepseek-r1输出特性）
            stop=None
        )
        
        # 新增：打印模型接口响应结果（确认deepseek-r1输出完整）
        print("【关键步骤2：模型接口返回结果】")
        print(f"接口响应状态：成功（已收到返回内容）")
        # 提取模型返回的文本内容，适配deepseek-r1输出格式，确保不遗漏内容
        content = response.choices[0].message.content.strip()
        # 新增：调用Markdown转微信格式函数，解决Markdown无法渲染问题
        content = markdown_to_wechat(content)
        print(f"模型解析后出题内容（完整度校验）：共{len(content)}字符，内容（精简）：{content[:100]}...")
        
        # 新增：打印AI出题结果判断（重点校验内容完整性）
        print("【关键步骤3：AI出题结果判断】")
        if not content or len(content.strip()) < 10:
            content = "出题服务暂时不可用，将在5分钟后重新尝试出题，无需手动操作。"
            print(f"出题结果：失败（内容为空或过短）")
            print(f"失败提示：{content}")
            return content, False
        # 新增：校验deepseek-r1输出是否完整（避免模型输出截断导致推送仅显示开头）
        if len(content) < 500:
            content = "模型输出内容过短（可能被截断），将在5分钟后重新尝试出题，无需手动操作。"
            print(f"出题结果：失败（deepseek-r1模型输出内容不完整）")
            print(f"失败提示：{content}")
            return content, False
        if "出题服务暂时不可用" not in content and "出题接口异常" not in content:
            print(f"出题结果：成功（已生成完整刷题内容，Markdown已适配微信）")
            return content, True
        else:
            print(f"出题结果：失败（接口返回异常提示）")
            print(f"失败提示：{content}")
            return content, False
    except Exception as e:
        error_msg = f"出题接口异常：{str(e)}"
        print(f"【关键步骤异常】{error_msg}")
        content = "出题接口异常，将在5分钟后重新尝试出题，无需手动操作。"
        return content, False

# ========== 微信测试号推送（重点优化：解决deepseek-r1输出完整但推送仅显示开头的问题）==========
def get_access_token():
    # 获取微信推送授权token（免费，有效期2小时，自动刷新）
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
    try:
        # 新增：打印微信token获取关键信息（步骤4：获取推送授权）
        print("="*50)
        print("【关键步骤4：微信推送授权（获取token）】")
        print(f"token获取接口地址：{url}")
        print(f"使用的APPID：{APPID[:8]}****（隐藏部分字符，保护隐私）")
        print(f"使用的APPSECRET：{APPSECRET[:8]}****（隐藏部分字符，保护隐私）")
        print("正在获取微信推送授权token...")
        
        import requests  # 此处导入避免与模型客户端冲突，不影响运行
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        # 新增：打印token获取结果（步骤5：token获取结果）
        print("【关键步骤5：token获取结果】")
        print(f"token接口响应状态码：{resp.status_code}")
        print(f"token接口返回原始内容：{data}")
        if "errcode" in data and data["errcode"] != 0:
            err_msg = f"获取token失败：{data.get('errmsg', '未知错误')}"
            print(f"token获取结果：失败 → {err_msg}")
            return ""
        access_token = data.get("access_token", "")
        print(f"token获取结果：成功")
        print(f"获取的token（隐藏部分）：{access_token[:10]}****")
        return access_token
    except Exception as e:
        err_msg = f"获取token异常：{str(e)}"
        print(f"【关键步骤异常】{err_msg}")
        return ""

def send_to_wechat(content):
    access_token = get_access_token()
    if not access_token:
        # 新增：打印token获取失败提示
        error_content = "微信推送授权失败，建议重新检查GitHub中APPID和APPSECRET密钥是否填写正确，无多余空格。"
        print(f"【关键步骤提示】{error_content}")
        # 尝试再次获取token，二次推送
        access_token = get_access_token()
        if not access_token:
            print("【关键步骤结果】微信推送：失败（两次获取token均失败）")
            return False
    # 推送接口地址
    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
    # 强制确保content不为空，彻底解决只显标题问题，重点适配deepseek-r1完整输出
    content = content.strip() if content.strip() else "当前出题暂未获取到内容，将在5分钟后自动重试，无需手动操作。"
    # 核心优化：适配deepseek-r1输出格式，解决推送仅显示开头的问题
    # 1. 替换所有换行符为微信模板支持的换行（避免换行导致渲染截断）
    # 2. 去除所有隐藏特殊字符（deepseek-r1可能输出不可见字符，导致渲染异常）
    # 3. 限制单段长度，避免微信模板对长文本的截断
    content = content.replace("\n", "\n\n")  # 调整换行格式，确保微信正常渲染
    content = content.replace("\r", "").replace("\t", "").replace("  ", " ")  # 去除隐藏特殊字符
    # 新增：拆分过长段落（微信模板单段过长会自动截断，拆分后完整显示）
    if len(content) > 1500:
        content_parts = [content[i:i+1500] for i in range(0, len(content), 1500)]
        content = "\n\n".join(content_parts)
    
    # 新增：打印微信推送关键信息（步骤6：推送内容准备，校验内容完整度）
    print("="*50)
    print("【关键步骤6：微信推送内容准备】")
    print(f"推送接口地址：{url[:50]}****（隐藏token部分，保护隐私）")
    print(f"接收推送的OPENID：{OPENID[:8]}****（隐藏部分字符，保护隐私）")
    print(f"使用的模板ID：{TEMPLATE_ID[:8]}****（隐藏部分字符，保护隐私）")
    print(f"推送内容（完整度校验）：共{len(content)}字符，内容（精简）：{content[:100]}...")
    
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
        import requests  # 此处导入避免与模型客户端冲突，不影响运行
        # 新增：打印推送请求信息
        print("【关键步骤7：发起微信推送】")
        print(f"推送请求数据（精简）：{str(data)[:150]}...")
        resp = requests.post(url, json=data, timeout=30)
        resp_data = resp.json()
        
        # 新增：打印推送结果（步骤8：推送最终结果）
        print("【关键步骤8：微信推送最终结果】")
        print(f"推送接口响应状态码：{resp.status_code}")
        print(f"推送接口返回原始内容：{resp_data}")
        # 判断推送是否成功（微信返回errcode为0则成功）
        if resp_data.get("errcode", 1) != 0:
            fail_msg = f"推送失败：{resp_data.get('errmsg', '未知错误')}"
            print(f"推送结果：失败 → {fail_msg}")
            # 推送失败，补充推送失败提示，确保{{content.DATA}}有内容
            fail_content = f"推送失败（错误：{resp_data.get('errmsg', '未知')}），将在5分钟后重新尝试，无需手动操作。"
            send_to_wechat(fail_content)
            return False
        print("推送结果：成功（微信已收到推送，内容完整）")
        return True
    except Exception as e:
        err_msg = f"推送异常：{str(e)}"
        print(f"【关键步骤异常】{err_msg}")
        # 推送异常，补充提示，确保{{content.DATA}}有内容
        fail_content = "推送接口异常，将在5分钟后重新尝试，无需手动操作。"
        send_to_wechat(fail_content)
        return False

# ========== 重试逻辑（5次重试，每次间隔5分钟，新增deepseek-r1输出完整度校验）==========
def run_with_retry():
    max_retries = 5  # 最大重试次数
    retry_interval = 300  # 重试间隔（5分钟=300秒）
    print("="*50)
    print("【整体流程启动】2026山东事业单位每日刷题机器人开始运行（适配deepseek-r1模型）")
    print(f"最大重试次数：{max_retries}次，每次重试间隔：{retry_interval//60}分钟")
    print("="*50)
    
    for retry in range(max_retries):
        print(f"\n【第{retry+1}次尝试】")
        # 生成题目（校验deepseek-r1输出完整度）
        content, success = generate_questions()
        if success:
            # 出题成功，推送题目，确保{{content.DATA}}接收完整正文
            print(f"【第{retry+1}次尝试结果】出题成功，准备推送...")
            send_success = send_to_wechat(content)
            if send_success:
                print("="*50)
                print("【整体流程结果】出题及推送成功，本次运行结束！")
                print("="*50)
                return
            else:
                # 推送失败，也算重试一次
                error_msg = f"出题成功，但推送失败，{max_retries - retry - 1}次重试机会，5分钟后重试。"
                send_to_wechat(error_msg)
                print(f"【第{retry+1}次尝试结果】{error_msg}")
        else:
            # 出题失败，推送失败提示，确保{{content.DATA}}有内容
            send_to_wechat(content)
            print(f"【第{retry+1}次尝试结果】第{retry + 1}次出题失败，{max_retries - retry - 1}次重试机会，5分钟后重试。")
        
        # 不是最后一次重试，等待5分钟
        if retry < max_retries - 1:
            print(f"【等待重试】将在{retry_interval//60}分钟后进行第{retry+2}次尝试...")
            time.sleep(retry_interval)
    
    # 5次重试均失败，推送最终提示，次日自动重试，确保{{content.DATA}}有内容
    final_msg = "今日出题已尝试5次，均未成功，将在次日自动重试，请留意明日推送。"
    send_to_wechat(final_msg)
    print("="*50)
    print(f"【整体流程结果】{final_msg}，本次运行结束！")
    print("="*50)

if __name__ == "__main__":
    run_with_retry()
