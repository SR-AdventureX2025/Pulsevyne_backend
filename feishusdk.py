from SDKFeishu import get_access_token, Bitable
import time
import json


app_id = ""
app_secret = ""
access_token = get_access_token(app_id, app_secret)


bitable = Bitable(access_token, "")
table_id = ""

def get_table_record_content(table_id):
    try:
        records = bitable.find_table_record(table_id)
        if isinstance(records, str):
            try:
                records_data = json.loads(records)
            except json.JSONDecodeError:
                return "暂无内容"
        elif isinstance(records, dict):
            records_data = records
        elif isinstance(records, list):

            if records:

                for record in reversed(records):
                    if isinstance(record, dict):
                        fields = record.get('fields', {})
                        if '网页内容' in fields:
                            web_content = fields['网页内容']

                            if isinstance(web_content, list) and web_content:

                                content_text = ""
                                for content_item in web_content:
                                    if isinstance(content_item, dict) and 'text' in content_item:
                                        content_text += content_item['text']
                                if content_text and content_text != "正在获取中...":
                                    return content_text
                            elif isinstance(web_content, str):
                                if web_content and web_content != "正在获取中...":
                                    return web_content
                            elif isinstance(web_content, dict):
                                return web_content
            return "暂无内容"
        else:
            return "暂无内容"

        if records_data.get('code') == 0 and 'data' in records_data:
            items = records_data['data'].get('items', [])
            

            for item in reversed(items):  
                fields = item.get('fields', {})
                if '网页内容' in fields:
                    web_content = fields['网页内容']

                    if isinstance(web_content, list) and web_content:

                        content_text = ""
                        for content_item in web_content:
                            if isinstance(content_item, dict) and 'text' in content_item:
                                content_text += content_item['text']
                        if content_text and content_text != "正在获取中...":
                            return content_text
                    elif isinstance(web_content, str):

                        if web_content and web_content != "正在获取中...":
                            return web_content
                    elif isinstance(web_content, dict):
                        return web_content
            
            return "暂无内容"
        else:
            return "暂无内容"
            
    except Exception as e:
        error_msg = f"获取表格记录内容时发生错误: {str(e)}"
        return error_msg
        
    

def create_link_record_and_fetch_content(url):
    try:
        fields = {
            "链接": {
            "link": f"{url}",
            "text": f"{url}"
            }
        }
        create_result = bitable.create_table_record(table_id, fields)

        if isinstance(create_result, dict):
            if create_result.get('code') == 0 and 'data' in create_result:
                record_id = create_result['data']['record']['record_id']
            else:
                return None
        elif isinstance(create_result, str):
            try:
                result_data = json.loads(create_result)
                if result_data.get('code') == 0 and 'data' in result_data:
                    record_id = result_data['data']['record']['record_id']
                else:
                    return None
            except json.JSONDecodeError:
                return None
        else:
            return None
        

        max_wait_time = 60 
        interval = 5 
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            web_content = get_table_record_content(table_id)
            
            if web_content and web_content not in ["暂无内容", "正在获取中..."]:
                return web_content
            
            time.sleep(interval)

        return "获取网页内容超时。"
        
    except Exception as e:
        error_msg = f"处理过程中发生错误: {str(e)}"
        return error_msg

def add_link_and_get_content(url):
    return create_link_record_and_fetch_content(url)


