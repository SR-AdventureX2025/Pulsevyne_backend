from SDKFeishu import get_access_token, Bitable
import json

app_id = ""
app_secret = ""
access_token = get_access_token(app_id, app_secret)

bitable = Bitable(access_token, "")
table_id = ""

def get_table_data_and_count_column(column_id):
    try:
        records = bitable.find_table_record(table_id)
        
        if isinstance(records, str):
            try:
                records_data = json.loads(records)
            except json.JSONDecodeError:
                return {
                    'success': False,
                    'error': '解析表格数据失败',
                    'column_id': column_id,
                    'count': 0,
                    'data': []
                }
        elif isinstance(records, dict):
            records_data = records
        elif isinstance(records, list):
            column_data = []
            non_empty_count = 0
            
            for record in records:
                if isinstance(record, dict):
                    fields = record.get('fields', {})
                    if column_id in fields:
                        field_value = fields[column_id]
                        if field_value is not None and str(field_value).strip():
                            column_data.append({
                                'record_id': record.get('record_id', ''),
                                'value': field_value
                            })
                            non_empty_count += 1
            
            return {
                'success': True,
                'message': f'成功获取列 {column_id} 的数据',
                'column_id': column_id,
                'count': non_empty_count,
                'data': column_data,
                'total_records': len(records)
            }
        else:
            return {
                'success': False,
                'error': '表格数据格式异常',
                'column_id': column_id,
                'count': 0,
                'data': []
            }
        
        if records_data.get('code') == 0 and 'data' in records_data:
            items = records_data['data'].get('items', [])
            
            column_data = []
            non_empty_count = 0
            
            for item in items:
                fields = item.get('fields', {})
                if column_id in fields:
                    field_value = fields[column_id]
                    if field_value is not None and str(field_value).strip():
                        column_data.append({
                            'record_id': item.get('record_id', ''),
                            'value': field_value
                        })
                        non_empty_count += 1
            
            return {
                'success': True,
                'message': f'成功获取列 {column_id} 的数据',
                'column_id': column_id,
                'count': non_empty_count,
                'data': column_data,
                'total_records': len(items)
            }
        else:
            return {
                'success': False,
                'error': f'获取表格数据失败: {records_data.get("msg", "未知错误")}',
                'column_id': column_id,
                'count': 0,
                'data': []
            }
            
    except Exception as e:
        error_msg = f"获取表格数据时发生错误: {str(e)}"
        return {
            'success': False,
            'error': error_msg,
            'column_id': column_id,
            'count': 0,
            'data': []
        }

def get_all_table_data():
    try:
        records = bitable.find_table_record(table_id)
        
        if isinstance(records, str):
            try:
                records_data = json.loads(records)
            except json.JSONDecodeError:
                return {'success': False, 'error': '解析表格数据失败'}
        elif isinstance(records, dict):
            records_data = records
        elif isinstance(records, list):
            return {
                'success': True,
                'message': '成功获取表格数据',
                'data': records,
                'total_records': len(records)
            }
        else:
            return {'success': False, 'error': '表格数据格式异常'}
        
        if records_data.get('code') == 0 and 'data' in records_data:
            items = records_data['data'].get('items', [])
            return {
                'success': True,
                'message': '成功获取表格数据',
                'data': items,
                'total_records': len(items)
            }
        else:
            return {
                'success': False,
                'error': f'获取表格数据失败: {records_data.get("msg", "未知错误")}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'获取表格数据时发生错误: {str(e)}'
        }

if __name__ == "__main__":
    test_column_id = "test_column"
    result = get_table_data_and_count_column(test_column_id)
    
    all_data = get_all_table_data()


        

