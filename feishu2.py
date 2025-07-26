from SDKFeishu import get_access_token, Bitable
import json
app_id = "cli_a80ba38980f9100e"
app_secret = "FO2EhOTnXF8V2nCpC67Vffs5XqOUqWXN"
access_token = get_access_token(app_id, app_secret)


bitable = Bitable(access_token, "YArHb3TzlaLGDtsh9ZAc7lV8nde")
table_id = "tbl66TuSMne9yEjZ"

def create_link_record_and_fetch_content(text, line_id):
    if ',' in text and ',' in line_id:
        text_list = [t.strip() for t in text.split(',')]
        line_id_list = [l.strip() for l in line_id.split(',')]
        
        if len(text_list) != len(line_id_list):
            return None
        
        fields = {}
        for single_text, single_line_id in zip(text_list, line_id_list):
            fields[f"{single_line_id}"] = f"{single_text}"
        
        create_result = bitable.create_table_record(table_id, fields)
        
        return process_create_result(create_result)
    
    else:
        fields = {
            f"{line_id}": f"{text}"
        }
        
        create_result = bitable.create_table_record(table_id, fields)
        
        return process_create_result(create_result)

def process_create_result(create_result, record_index=None):
    if isinstance(create_result, dict):
        if create_result.get('code') == 0 and 'data' in create_result:
            record_id = create_result['data']['record']['record_id']
            return record_id
        else:
            return None
    elif isinstance(create_result, str):
        try:
            result_data = json.loads(create_result)
            if result_data.get('code') == 0 and 'data' in result_data:
                record_id = result_data['data']['record']['record_id']
                return record_id
            else:
                return None
        except json.JSONDecodeError:
            return None
    else:
        return None
        

