from flask import Flask, request, jsonify
from pyquery import PyQuery as pq
import os

app = Flask(__name__)

def parse_openscap_report(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        document = pq(content)

    # Extracting the title of the report
    title = document('title').text() if document('title') else 'Title not found'

    # Extracting Evaluation Characteristics
    eval_characteristics = {}
    eval_section = document('#characteristics')
    if eval_section:
        eval_section('table.table-bordered tr').each(lambda i, el: eval_characteristics.update(
            {pq(el).find('th').text().strip(): pq(el).find('td').text().strip()}
        ))

    # Extracting compliance status
    compliance_status_text = document('#compliance-and-scoring .alert-danger').text().strip() if document('#compliance-and-scoring .alert-danger') else 'Not found'

    # Extracting Rule Details
    rule_details = []
    document('.panel.panel-default.rule-detail').each(lambda i, el: rule_details.append({
        'title': pq(el).find('.panel-title').text().strip(),
        'id': pq(el).find('.rule-id').text().strip() if pq(el).find('.rule-id') else 'N/A',
        'result': pq(el).find('.rule-result').text().strip() or pq(el).find('.rule-result abbr').attr('title').strip() if pq(el).find('.rule-result abbr') else 'Unknown',
        'severity': pq(el).find('td:contains("Severity") + td').text().strip() if pq(el).find('td:contains("Severity") + td') else 'No severity',
        'description': pq(el).find('.description').text().strip() if pq(el).find('.description') else 'No description',
        'rationale': pq(el).find('.rationale').text().strip() if pq(el).find('.rationale') else 'No rationale'
    }))

    # Extracting Rule Details from the new table format
    rule_details_table = document('table.table-striped.table-bordered')
    if rule_details_table:
        rows = list(rule_details_table('tr'))[1:]  # Skip the header row
        for row in rows:
            columns = pq(row).find('td')
            if len(columns) == 3:
                rule_details.append({
                    'title': columns.eq(0).text().strip(),
                    'severity': columns.eq(1).text().strip(),
                    'result': columns.eq(2).text().strip(),
                    'description': 'N/A',
                    'rationale': 'N/A',
                    'id': 'N/A'  # Adding default value for 'id'
                })

    return {
        'title': title,
        'eval_characteristics': eval_characteristics,
        'compliance_status': compliance_status_text,
        'rule_details': rule_details
    }

def generate_html_report(report_data):
    html_content = f"""
    <html>
    <head>
        <title>Cyberjeet Compliance Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            h1, h2, h3 {{ color: #2E4053; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .severity-low {{ color: green; }}
            .severity-medium {{ color: orange; }}
            .severity-high {{ color: red; }}
            .result-pass {{ color: green; }}
            .result-fail {{ color: red; }}
        </style>
    </head>
    <body>
        <h1>Cyberjeet Compliance Report</h1>
        <h2>Report Title: {report_data['title']}</h2>
        
        <h3>Evaluation Characteristics</h3>
        <table>
            <tr><th>Characteristic</th><th>Value</th></tr>
    """
    for key, value in report_data['eval_characteristics'].items():
        html_content += f"<tr><td>{key}</td><td>{value}</td></tr>"

    html_content += f"""
        </table>

        <h3>Compliance Status</h3>
        <p>{report_data['compliance_status']}</p>

        <h3>Rule Details</h3>
        <table>
            <tr><th>Title</th><th>ID</th><th>Result</th><th>Severity</th><th>Description</th><th>Rationale</th></tr>
    """
    for detail in report_data['rule_details']:
        result_class = 'result-pass' if detail['result'].lower() == 'pass' else 'result-fail'
        severity_class = 'severity-low' if detail['severity'].lower() == 'low' else ('severity-medium' if detail['severity'].lower() == 'medium' else 'severity-high')
        html_content += f"""
            <tr>
                <td>{detail['title']}</td>
                <td>{detail['id']}</td>
                <td class="{result_class}">{detail['result']}</td>
                <td class="{severity_class}">{detail['severity']}</td>
                <td>{detail['description']}</td>
                <td>{detail['rationale']}</td>
            </tr>
        """
    
    html_content += """
        </table>
    </body>
    </html>
    """
    
    with open('compliance_report_grcofcyberjeet.html', 'w', encoding='utf-8') as file:
        file.write(html_content)
    print("Report generated: compliance_report_grcofcyberjeet.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        file_path = os.path.join('.', file.filename)
        file.save(file_path)
        report_data = parse_openscap_report(file_path)
        generate_html_report(report_data)
        return jsonify({"message": "File received and report generated"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=65432)
