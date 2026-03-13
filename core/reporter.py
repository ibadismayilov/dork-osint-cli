import os
import json
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

def generate_html_report(results, target_name, output_path=None):
    template_dir = os.path.join(os.path.dirname(__file__), '../templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('report_template.html')

    processed_results = []
    domain_counts = {}

    for item in results:
        title = item.get('title', 'No Title')
        link = item.get('link', '#')
        domain = item.get('domain') or item.get('displayLink', 'Unknown')
        ip = item.get('ip') or 'Scanning...'

        processed_results.append({
            'title': title,
            'link': link,
            'domain': domain,
            'ip': ip
        })

        domain_counts[domain] = domain_counts.get(domain, 0) + 1

    chart_labels = list(domain_counts.keys())
    chart_data = list(domain_counts.values())

    report_content = template.render(
        target=target_name,
        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
        total_results=len(processed_results),
        results=processed_results,

        chart_labels=json.dumps(chart_labels),
        chart_data=json.dumps(chart_data)
    )

    if output_path is None:
        output_path = "."
    os.makedirs(output_path, exist_ok=True)
    report_filename = f"report_{target_name.replace('.', '_')}.html"
    full_path = os.path.join(output_path, report_filename)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    return full_path
