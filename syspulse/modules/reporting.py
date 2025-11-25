"""
Report Generation Module

Generates JSON and HTML reports from scan results.
Supports before/after comparisons and scan history.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class ReportGenerator:
    """Generate reports from scan results"""

    def __init__(self):
        self.reports_dir = Path.home() / '.syspulse' / 'reports'
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_json_report(
        self,
        browser_data: Optional[Dict] = None,
        startup_data: Optional[Dict] = None,
        storage_data: Optional[Dict] = None,
        process_data: Optional[Dict] = None,
        output_file: Optional[Path] = None
    ) -> Path:
        """
        Generate JSON report from scan results

        Args:
            browser_data: Browser scan results
            startup_data: Startup scan results
            storage_data: Storage scan results
            process_data: Process scan results
            output_file: Custom output file path

        Returns:
            Path to generated report
        """
        timestamp = datetime.now()

        report = {
            'metadata': {
                'timestamp': timestamp.isoformat(),
                'version': '2.0.0-alpha.4',
                'report_type': 'system_scan'
            },
            'scans': {}
        }

        if browser_data:
            report['scans']['browser'] = browser_data

        if startup_data:
            report['scans']['startup'] = startup_data

        if storage_data:
            report['scans']['storage'] = storage_data

        if process_data:
            report['scans']['process'] = process_data

        # Determine output file
        if not output_file:
            filename = f"syspulse_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            output_file = self.reports_dir / filename

        # Write report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        return output_file

    def generate_html_report(
        self,
        browser_data: Optional[Dict] = None,
        startup_data: Optional[Dict] = None,
        storage_data: Optional[Dict] = None,
        process_data: Optional[Dict] = None,
        output_file: Optional[Path] = None
    ) -> Path:
        """
        Generate HTML report from scan results

        Args:
            browser_data: Browser scan results
            startup_data: Startup scan results
            storage_data: Storage scan results
            process_data: Process scan results
            output_file: Custom output file path

        Returns:
            Path to generated report
        """
        timestamp = datetime.now()

        # Generate HTML content
        html = self._generate_html_content(
            timestamp,
            browser_data,
            startup_data,
            storage_data,
            process_data
        )

        # Determine output file
        if not output_file:
            filename = f"syspulse_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.html"
            output_file = self.reports_dir / filename

        # Write report
        with open(output_file, 'w') as f:
            f.write(html)

        return output_file

    def _generate_html_content(
        self,
        timestamp: datetime,
        browser_data: Optional[Dict],
        startup_data: Optional[Dict],
        storage_data: Optional[Dict],
        process_data: Optional[Dict]
    ) -> str:
        """Generate HTML content for report"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SysPulse Report - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .header .tagline {{
            font-size: 1.2em;
            opacity: 0.9;
            margin-bottom: 20px;
        }}

        .header .timestamp {{
            font-size: 0.9em;
            opacity: 0.8;
        }}

        .content {{
            padding: 40px;
        }}

        .section {{
            margin-bottom: 40px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}

        .section h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8em;
            display: flex;
            align-items: center;
        }}

        .section h2::before {{
            content: '';
            width: 8px;
            height: 8px;
            background: #667eea;
            border-radius: 50%;
            margin-right: 12px;
        }}

        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .stat-card .label {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 8px;
        }}

        .stat-card .value {{
            color: #333;
            font-size: 1.8em;
            font-weight: 700;
        }}

        .item-list {{
            list-style: none;
        }}

        .item {{
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 6px;
            border-left: 3px solid #ddd;
        }}

        .item.high {{
            border-left-color: #e74c3c;
        }}

        .item.medium {{
            border-left-color: #f39c12;
        }}

        .item.low {{
            border-left-color: #27ae60;
        }}

        .item-header {{
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }}

        .item-detail {{
            color: #666;
            font-size: 0.9em;
        }}

        .recommendation {{
            color: #667eea;
            font-style: italic;
            margin-top: 5px;
            font-size: 0.9em;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}

        .no-data {{
            color: #999;
            font-style: italic;
            padding: 20px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 SysPulse</h1>
            <div class="tagline">Control the bullshit. Make your computer run better.</div>
            <div class="timestamp">Generated: {timestamp.strftime('%B %d, %Y at %I:%M %p')}</div>
        </div>

        <div class="content">
"""

        # Browser section
        if browser_data:
            html += self._generate_browser_section(browser_data)

        # Startup section
        if startup_data:
            html += self._generate_startup_section(startup_data)

        # Storage section
        if storage_data:
            html += self._generate_storage_section(storage_data)

        # Process section
        if process_data:
            html += self._generate_process_section(process_data)

        html += """
        </div>

        <div class="footer">
            <p>Generated by SysPulse v2.0.0-alpha.4</p>
            <p>Made with 🔧 and frustration at bloated utility software.</p>
        </div>
    </div>
</body>
</html>
"""

        return html

    def _generate_browser_section(self, data: Dict) -> str:
        """Generate browser section HTML"""
        summary = data.get('summary', {})

        html = f"""
            <div class="section">
                <h2>🌐 Browser Profiles</h2>

                <div class="stat-grid">
                    <div class="stat-card">
                        <div class="label">Total Profiles</div>
                        <div class="value">{summary.get('total_profiles', 0)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Total Cache</div>
                        <div class="value">{summary.get('total_cache_size', 'N/A')}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Total Extensions</div>
                        <div class="value">{summary.get('total_extensions', 0)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Unused Profiles</div>
                        <div class="value">{summary.get('unused_profiles_count', 0)}</div>
                    </div>
                </div>

                <ul class="item-list">
"""

        for profile in data.get('profiles', []):
            recommendation_class = 'high' if 'safe to delete' in profile.get('recommendation', '').lower() else 'medium' if 'consider cleaning' in profile.get('recommendation', '').lower() else 'low'

            html += f"""
                    <li class="item {recommendation_class}">
                        <div class="item-header">[{profile.get('browser', 'Unknown')}] {profile.get('name', 'Unknown')}</div>
                        <div class="item-detail">Cache: {profile.get('cache_size_human', 'N/A')} | Extensions: {profile.get('extensions_count', 0)} | Last used: {profile.get('days_since_used', 'Never')} days ago</div>
                        <div class="recommendation">→ {profile.get('recommendation', 'No recommendation')}</div>
                    </li>
"""

        html += """
                </ul>
            </div>
"""

        return html

    def _generate_startup_section(self, data: Dict) -> str:
        """Generate startup section HTML"""
        summary = data.get('summary', {})

        html = f"""
            <div class="section">
                <h2>🚀 Startup Programs</h2>

                <div class="stat-grid">
                    <div class="stat-card">
                        <div class="label">Total Items</div>
                        <div class="value">{summary.get('total_items', 0)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">High Impact</div>
                        <div class="value">{summary.get('high_impact_count', 0)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Safe to Disable</div>
                        <div class="value">{summary.get('safe_to_disable_count', 0)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Est. Boot Delay</div>
                        <div class="value">{summary.get('estimated_boot_delay_seconds', 0)}s</div>
                    </div>
                </div>

                <ul class="item-list">
"""

        for item in data.get('top_recommendations', []):
            impact_class = 'high' if item.get('impact') == 'HIGH' else 'medium' if item.get('impact') == 'MEDIUM' else 'low'

            html += f"""
                    <li class="item {impact_class}">
                        <div class="item-header">[{item.get('impact', 'UNKNOWN')}] {item.get('name', 'Unknown')}</div>
                        <div class="item-detail">{item.get('description', 'No description')}</div>
                        <div class="recommendation">→ {item.get('recommendation', 'No recommendation')}</div>
                    </li>
"""

        html += """
                </ul>
            </div>
"""

        return html

    def _generate_storage_section(self, data: Dict) -> str:
        """Generate storage section HTML"""
        summary = data.get('summary', {})

        html = f"""
            <div class="section">
                <h2>💾 Storage</h2>

                <div class="stat-grid">
                    <div class="stat-card">
                        <div class="label">Total Analyzed</div>
                        <div class="value">{summary.get('total_size', 'N/A')}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Safe to Clean</div>
                        <div class="value">{summary.get('safe_to_clean_size', 'N/A')}</div>
                    </div>
                </div>

                <ul class="item-list">
"""

        for cleanup in summary.get('high_priority_cleanups', []):
            html += f"""
                    <li class="item medium">
                        <div class="item-header">{cleanup.get('name', 'Unknown')}: {cleanup.get('size', 'N/A')}</div>
                        <div class="recommendation">→ {cleanup.get('recommendation', 'No recommendation')}</div>
                    </li>
"""

        html += """
                </ul>
            </div>
"""

        return html

    def _generate_process_section(self, data: Dict) -> str:
        """Generate process section HTML"""
        summary = data.get('summary', {})

        html = f"""
            <div class="section">
                <h2>⚙️ Background Processes</h2>

                <div class="stat-grid">
                    <div class="stat-card">
                        <div class="label">Total Processes</div>
                        <div class="value">{summary.get('total_processes', 0)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Total CPU</div>
                        <div class="value">{summary.get('total_cpu_percent', 0)}%</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Total Memory</div>
                        <div class="value">{summary.get('total_memory_gb', 0)} GB</div>
                    </div>
                </div>

                <h3 style="margin: 20px 0 10px 0; color: #333;">Top CPU Consumers</h3>
                <ul class="item-list">
"""

        for proc in summary.get('top_cpu', [])[:5]:
            html += f"""
                    <li class="item high">
                        <div class="item-header">[{proc.get('cpu_percent', 0)}%] {proc.get('name', 'Unknown')}</div>
                        <div class="item-detail">{proc.get('description', 'No description')} | Memory: {proc.get('memory_mb', 0):.1f} MB</div>
                        <div class="recommendation">→ {proc.get('recommendation', 'No recommendation')}</div>
                    </li>
"""

        html += """
                </ul>
            </div>
"""

        return html

    def list_reports(self) -> List[Dict]:
        """List all saved reports"""
        reports = []

        for report_file in sorted(self.reports_dir.glob('syspulse_report_*.json'), reverse=True):
            try:
                with open(report_file, 'r') as f:
                    data = json.load(f)

                reports.append({
                    'file': str(report_file),
                    'timestamp': data.get('metadata', {}).get('timestamp', 'Unknown'),
                    'version': data.get('metadata', {}).get('version', 'Unknown'),
                    'size': report_file.stat().st_size,
                    'scans': list(data.get('scans', {}).keys())
                })
            except:
                pass

        return reports


if __name__ == "__main__":
    # Quick test
    generator = ReportGenerator()

    # Test data
    test_browser_data = {
        'summary': {
            'total_profiles': 3,
            'total_cache_size': '8.4 GB',
            'total_extensions': 47,
            'unused_profiles_count': 1
        },
        'profiles': [
            {
                'browser': 'Chrome',
                'name': 'Personal',
                'cache_size_human': '1.2 GB',
                'extensions_count': 15,
                'days_since_used': 2,
                'recommendation': 'Actively used - no action needed'
            }
        ]
    }

    # Generate test report
    json_file = generator.generate_json_report(browser_data=test_browser_data)
    print(f"JSON report generated: {json_file}")

    html_file = generator.generate_html_report(browser_data=test_browser_data)
    print(f"HTML report generated: {html_file}")
