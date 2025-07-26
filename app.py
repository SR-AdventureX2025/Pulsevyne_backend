from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from test import ai, key, base_url
from feishusdk import add_link_and_get_content
from feishu2 import create_link_record_and_fetch_content
from feishu3 import get_table_data_and_count_column, get_all_table_data

app = Flask("脉藤PulseVyne")
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate-suggestions', methods=['POST'])
def generate_suggestions():
    try:
        data = request.get_json()
        user_input = data.get('input', '')
        
        if not user_input.strip():
            return jsonify({'success': False, 'error': '输入内容不能为空'})
        
        prompt = """你是一个专业的行动建议助手，根据用户的需求生成3-5个具体可行的行动建议。
        
        请严格按照以下格式输出：
        1. 每个建议前面加一个相关的emoji表情
        2. 每个建议的格式为：{标题}\n{内容}
        3. 建议之间用空行分隔
        4. 标题要简洁有力，内容要具体可操作
        5. 建议要切实可行，符合实际情况
        6. 不要添加序号或其他格式标记
        
        示例格式：
        🎯 制定明确目标
        设定具体、可衡量的目标，并制定详细的时间计划。
        
        📝 记录进展情况
        每天记录执行情况和遇到的问题，便于及时调整策略。"""
        
        ai_instance = ai(
            api_key=key,
            base_url=base_url,
            user_input=user_input,
            prompt=prompt
        )
        
        ai_response = ai_instance.run()
        
        suggestions = parse_suggestions(ai_response)
        
        return jsonify({
            'success': True,
            'message': '行动建议生成成功',
            'data': {
                'suggestions': suggestions,
                'raw_response': ai_response
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get-link-content', methods=['POST'])
def get_link_content():
    try:
        data = request.get_json()
        url = data.get('url', '')
        
        if not url.strip():
            return jsonify({'success': False, 'error': '链接不能为空'})
        
        if not (url.startswith('http://') or url.startswith('https://')):
            return jsonify({'success': False, 'error': '请输入有效的链接格式（以http://或https://开头）'})
        
        content = add_link_and_get_content(url)
        
        if content and content != '暂无内容':
            return jsonify({
                'success': True,
                'message': '网页内容获取成功',
                'data': {
                    'url': url,
                    'content': content
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '无法获取网页内容，请检查链接是否有效或稍后重试'
            })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'处理失败: {str(e)}'})

@app.route('/api/create-feishu-record', methods=['POST'])
def create_feishu_record():
    try:
        data = request.get_json()
        text = data.get('text', '')
        line_id = data.get('line_id', '')
        
        if not text.strip():
            return jsonify({'success': False, 'error': '文本内容不能为空'})
        
        if not line_id.strip():
            return jsonify({'success': False, 'error': '行ID不能为空'})
        
        result = create_link_record_and_fetch_content(text, line_id)
        
        if result is not None:
            # 检查是否为批量创建（返回列表）还是单条创建（返回字符串）
            if isinstance(result, list):
                return jsonify({
                    'success': True,
                    'message': f'飞书记录批量创建成功，共创建{len(result)}条记录',
                    'data': {
                        'text': text,
                        'line_id': line_id,
                        'record_ids': result,
                        'count': len(result)
                    }
                })
            else:
                return jsonify({
                    'success': True,
                    'message': '飞书记录创建成功',
                    'data': {
                        'text': text,
                        'line_id': line_id,
                        'record_id': result
                    }
                })
        else:
            return jsonify({
                'success': False,
                'error': '创建飞书记录失败，请检查参数或稍后重试'
            })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'处理失败: {str(e)}'})

@app.route('/api/get-table-column-stats', methods=['POST'])
def get_table_column_stats():
    try:
        data = request.get_json()
        column_id = data.get('column_id', '')
        
        if not column_id.strip():
            return jsonify({'success': False, 'error': '列ID不能为空'})
        
        result = get_table_data_and_count_column(column_id)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result.get('message', '统计完成'),
                'data': {
                    'column_id': result.get('column_id'),
                    'count': result.get('count'),
                    'data': result.get('data', []),
                    'total_records': result.get('total_records', 0)
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', '统计失败')
            })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'处理失败: {str(e)}'})

@app.route('/api/get-all-table-data', methods=['GET'])
def get_all_table_data_api():
    try:
        result = get_all_table_data()
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result.get('message', '获取成功'),
                'data': {
                    'records': result.get('data', []),
                    'total_records': result.get('total_records', 0)
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', '获取失败')
            })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'处理失败: {str(e)}'})

@app.route('/api/generate-feedback', methods=['POST'])
def generate_feedback():
    try:
        data = request.get_json()
        execution_summary = data.get('execution_summary', {})
        
        required_fields = ['weekly_executions', 'average_rating', 'completion_rate', 'execution_frequency', 'action_plan', 'reason']
        for field in required_fields:
            if field not in execution_summary:
                return jsonify({'success': False, 'error': f'缺少必需字段: {field}'})
        

        weekly_executions = execution_summary.get('weekly_executions', 0)
        average_rating = execution_summary.get('average_rating', 0)
        completion_rate = execution_summary.get('completion_rate', 0)
        execution_frequency = execution_summary.get('execution_frequency', '')
        action_plan = execution_summary.get('action_plan', '')
        reason = execution_summary.get('reason', '')
        

        status_feedback = generate_status_feedback(
            weekly_executions, average_rating, completion_rate, execution_frequency, action_plan, reason
        )
        
        improvement_suggestions = generate_improvement_suggestions(
            weekly_executions, average_rating, completion_rate, execution_frequency, action_plan, reason
        )
        
        return jsonify({
            'success': True,
            'message': '进展反馈生成成功',
            'data': {
                'status_feedback': status_feedback,
                'improvement_suggestions': improvement_suggestions,
                'execution_summary': {
                    'weekly_executions': weekly_executions,
                    'average_rating': average_rating,
                    'completion_rate': completion_rate,
                    'execution_frequency': execution_frequency,
                    'action_plan': action_plan,
                    'reason': reason
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def generate_status_feedback(weekly_executions, average_rating, completion_rate, execution_frequency, action_plan, reason):
    try:
        status_description = f"""执行总结数据分析：
        本周执行次数：{weekly_executions}次
        平均评分：{average_rating}分
        完成率：{completion_rate}%
        执行频率：{execution_frequency}
        行动计划：{action_plan}
        理论：{reason}
        
        请基于以上数据提供具体的总结数据分析"""
        
        
        prompt = """你是一个专业的执行状态分析师，根据用户的执行数据提供正向的，夸赞用户的状态反馈。但是在夸赞的过程要包含详细的总结与解决方案
        
        请严格按照以下格式输出2-3个执行状态反馈：
        1. 每个反馈的格式为：{标题}\n{内容}
        2. 反馈之间用空行分隔
        3. 标题要简洁明确，内容要客观分析当前状态
        4. 重点分析执行表现和趋势
        5. 不要添加序号或其他格式标记
        6. 不要使用过于客观的语言,要夸赞用户
        7. 要在内容里包含对于用户所干的事情的直接描述和评价，比如执行的任务、完成的工作、遇到的问题等。


        
        示例格式：
        执行频率表现
        窝去！！！！你太棒了！！！你太厉害了！！！（内容）
        
        质量评分分析
        哇！！你居然…………（内容）"""
        
        ai_instance = ai(
            api_key=key,
            base_url=base_url,
            user_input=status_description,
            prompt=prompt
        )
        
        ai_response = ai_instance.run()
        
        feedback_list = parse_suggestions(ai_response)
        
        return feedback_list
        
    except Exception as e:
        return [{
            'emoji': '',
            'title': '状态反馈生成失败',
            'content': '无法生成执行状态反馈，请稍后重试。'
        }]

def generate_improvement_suggestions(weekly_executions, average_rating, completion_rate, execution_frequency, action_plan, reason):
    try:
        improvement_description = f"""执行改进分析：
        本周执行次数：{weekly_executions}次
        平均评分：{average_rating}分
        完成率：{completion_rate}%
        执行频率：{execution_frequency}
        行动计划：{action_plan}
        理论：{reason}
        
        请基于以上数据提供具体的改进建议和优化方案。"""
        
        prompt = """你是一个专业的执行改进顾问，根据用户的执行数据提供具体的改进建议。
        
        请严格按照以下格式输出3-4个改进建议：
        1. 每个建议的格式为：{标题}\n{内容}
        2. 建议之间用空行分隔
        3. 标题要明确指向改进方向，内容要提供具体可行的改进措施
        4. 重点关注如何提升执行效果和质量
        5. 不要添加序号或其他格式标记
        6. 不要使用过于客观的语言,要夸赞用户
        7. 要在内容里包含对于用户所干的事情的直接描述和评价，比如执行的任务、完成的工作、遇到的问题等。
        """
        
        ai_instance = ai(
            api_key=key,
            base_url=base_url,
            user_input=improvement_description,
            prompt=prompt
        )
        
        ai_response = ai_instance.run()
        
        suggestions_list = parse_suggestions(ai_response)
        
        return suggestions_list
        
    except Exception as e:
        return [{
            'emoji': '⚠️',
            'title': '改进建议生成失败',
            'content': '无法生成执行改进建议，请稍后重试。'
        }]

def parse_suggestions(response):
    suggestions = []
    
    parts = response.strip().split('\n\n')
    
    for part in parts:
        if part.strip():
            lines = part.strip().split('\n')
            if len(lines) >= 2:
                title_line = lines[0].strip()
                if len(title_line) > 0:
                    title_start = 0
                    for i, char in enumerate(title_line):
                        if not is_emoji(char) and char != ' ':
                            title_start = i
                            break
                    
                    emoji = title_line[:title_start].strip()
                    title = title_line[title_start:].strip()
                    
                    content = '\n'.join(lines[1:]).strip()
                    
                    suggestions.append({
                        'emoji': emoji,
                        'title': title,
                        'content': content
                    })
    
    return suggestions

def is_emoji(char):
    return ord(char) > 127

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=14514)