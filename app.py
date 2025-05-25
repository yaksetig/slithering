from flask import Flask, request, render_template_string, jsonify
import subprocess
import tempfile
import os
import json
import shutil

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🛡️ Slither Smart Contract Analyzer</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container { 
            max-width: 1200px;
            margin: 0 auto;
            background: white; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 { 
            font-size: 2.5rem; 
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p { 
            opacity: 0.9; 
            font-size: 1.1rem;
        }
        
        .content { padding: 40px; }
        
        .upload-area { 
            border: 3px dashed #3498db; 
            padding: 50px; 
            text-align: center; 
            margin: 30px 0; 
            border-radius: 15px;
            transition: all 0.3s ease;
            cursor: pointer;
            background: #f8f9fa;
        }
        
        .upload-area:hover { 
            border-color: #2980b9; 
            background: #e3f2fd;
            transform: translateY(-2px);
        }
        
        .upload-area.dragover { 
            border-color: #27ae60; 
            background: #e8f5e8;
            transform: scale(1.02);
        }
        
        .upload-icon {
            font-size: 3rem;
            margin-bottom: 15px;
            color: #3498db;
        }
        
        textarea { 
            width: 100%; 
            height: 400px; 
            margin: 20px 0; 
            padding: 20px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
            font-size: 14px;
            resize: vertical;
            transition: border-color 0.3s ease;
            background: #fafafa;
        }
        
        textarea:focus { 
            border-color: #3498db; 
            outline: none;
            background: white;
            box-shadow: 0 0 0 3px rgba(52,152,219,0.1);
        }
        
        .btn { 
            background: linear-gradient(135deg, #3498db, #2980b9); 
            color: white; 
            padding: 16px 40px; 
            border: none; 
            border-radius: 50px;
            cursor: pointer; 
            font-size: 18px;
            font-weight: 600;
            transition: all 0.3s ease;
            display: block;
            margin: 30px auto;
            box-shadow: 0 4px 15px rgba(52,152,219,0.3);
        }
        
        .btn:hover { 
            transform: translateY(-3px); 
            box-shadow: 0 8px 25px rgba(52,152,219,0.4);
        }
        
        .btn:disabled { 
            background: #bdc3c7; 
            cursor: not-allowed; 
            transform: none;
            box-shadow: none;
        }
        
        .result { 
            background: #f8f9fa; 
            padding: 25px; 
            margin: 25px 0; 
            border-left: 5px solid #3498db; 
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .error { 
            border-left-color: #e74c3c; 
            background: #fce4ec;
        }
        
        .success { 
            border-left-color: #27ae60; 
            background: #e8f5e8;
        }
        
        .warning { 
            border-left-color: #f39c12; 
            background: #fff3e0;
        }
        
        .high-severity {
            border-left-color: #e74c3c;
            background: #ffebee;
        }
        
        .medium-severity {
            border-left-color: #ff9800;
            background: #fff3e0;
        }
        
        .low-severity {
            border-left-color: #ffc107;
            background: #fffde7;
        }
        
        .info-severity {
            border-left-color: #2196f3;
            background: #e3f2fd;
        }
        
        pre { 
            background: #2c3e50; 
            color: #ecf0f1; 
            padding: 20px; 
            border-radius: 10px; 
            overflow-x: auto;
            font-size: 14px;
            line-height: 1.5;
            margin: 15px 0;
            white-space: pre-wrap;
        }
        
        .loading { 
            text-align: center; 
            color: #3498db;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        
        .file-info { 
            background: linear-gradient(135deg, #e3f2fd, #bbdefb); 
            padding: 15px; 
            border-radius: 10px; 
            margin: 15px 0;
            font-size: 14px;
            border-left: 4px solid #2196f3;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #7f8c8d;
            border-top: 1px solid #e0e0e0;
        }
        
        .info-box {
            background: #e3f2fd;
            border: 1px solid #2196f3;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
        }
        
        .severity-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin: 2px;
        }
        
        .severity-high { background: #ffcdd2; color: #b71c1c; }
        .severity-medium { background: #ffe0b2; color: #e65100; }
        .severity-low { background: #fff9c4; color: #f57f17; }
        .severity-info { background: #bbdefb; color: #0d47a1; }
        
        .finding {
            margin: 15px 0;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 8px;
            border-left: 4px solid #ddd;
        }
        
        .finding h4 {
            margin: 0 0 10px 0;
            color: #333;
        }
        
        .finding p {
            margin: 5px 0;
            color: #666;
        }
        
        .finding code {
            background: #e0e0e0;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Slither Smart Contract Analyzer</h1>
            <p>Static analysis framework for Solidity smart contracts</p>
        </div>
        
        <div class="content">
            <div class="info-box">
                <strong>ℹ️ About Slither:</strong> Slither is a static analysis framework for Solidity that detects vulnerabilities, 
                provides code insights, and helps ensure smart contract security. It can identify common issues like reentrancy, 
                unchecked calls, and gas optimization opportunities.
            </div>
            
            <form id="uploadForm">
                <div class="upload-area" id="uploadArea">
                    <input type="file" id="fileInput" accept=".sol" style="display: none;">
                    <div class="upload-icon">📁</div>
                    <div>
                        <strong>Click to upload .sol file</strong><br>
                        <small style="color: #7f8c8d;">or drag & drop here</small>
                    </div>
                </div>
                
                <div id="fileInfo" class="file-info" style="display: none;"></div>
                
                <textarea 
                    id="codeArea" 
                    placeholder="Or paste your Solidity code here...

Example:
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleStorage {
    uint256 private storedData;
    
    function set(uint256 x) public {
        storedData = x;
    }
    
    function get() public view returns (uint256) {
        return storedData;
    }
}"
                ></textarea>
                
                <button type="submit" class="btn" id="auditBtn">
                    🔍 Analyze Contract
                </button>
            </form>
            
            <div id="results"></div>
        </div>
        
        <div class="footer">
            <p>Powered by <a href="https://github.com/crytic/slither" target="_blank">Slither</a> by Trail of Bits</p>
        </div>
    </div>

    <script>
        const fileInput = document.getElementById('fileInput');
        const codeArea = document.getElementById('codeArea');
        const uploadForm = document.getElementById('uploadForm');
        const uploadArea = document.getElementById('uploadArea');
        const results = document.getElementById('results');
        const auditBtn = document.getElementById('auditBtn');
        const fileInfo = document.getElementById('fileInfo');

        // File upload handling
        uploadArea.addEventListener('click', () => fileInput.click());
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });

        function handleFile(file) {
            if (!file.name.endsWith('.sol')) {
                alert('Please upload a .sol file');
                return;
            }
            
            fileInfo.style.display = 'block';
            fileInfo.innerHTML = `
                <strong>📄 ${file.name}</strong> 
                <span style="color: #666; margin-left: 10px;">${(file.size/1024).toFixed(1)} KB</span>
            `;
            
            const reader = new FileReader();
            reader.onload = (e) => {
                codeArea.value = e.target.result;
            };
            reader.readAsText(file);
        }

        // Form submission
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const code = codeArea.value.trim();
            
            if (!code) {
                alert('Please provide Solidity code to analyze');
                return;
            }

            auditBtn.disabled = true;
            auditBtn.innerHTML = '⏳ Analyzing contract...';
            
            results.innerHTML = `
                <div class="result loading">
                    <h3>🔄 Running Slither Analysis...</h3>
                    <p>Scanning for vulnerabilities and code quality issues...</p>
                </div>
            `;

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({code: code})
                });
                
                const result = await response.json();
                displayResults(result);
                
            } catch (error) {
                results.innerHTML = `
                    <div class="result error">
                        <h3>❌ Network Error</h3>
                        <p>${error.message}</p>
                    </div>
                `;
            } finally {
                auditBtn.disabled = false;
                auditBtn.innerHTML = '🔍 Analyze Contract';
            }
        });
        
        function displayResults(result) {
            if (!result.success) {
                results.innerHTML = `
                    <div class="result error">
                        <h3>❌ Analysis Error</h3>
                        <pre>${result.error}</pre>
                    </div>
                `;
                return;
            }
            
            // Display the Slither output
            if (result.output) {
                // Check for findings
                const hasFindings = result.output.includes('Impact:') || 
                                   result.output.includes('Reference:') ||
                                   result.output.includes('found');
                
                const hasHighSeverity = result.output.includes('Impact: High');
                const hasMediumSeverity = result.output.includes('Impact: Medium');
                const hasLowSeverity = result.output.includes('Impact: Low');
                const hasInfoSeverity = result.output.includes('Impact: Informational');
                
                let resultClass = 'success';
                let resultTitle = '✅ Analysis Complete';
                
                if (hasHighSeverity) {
                    resultClass = 'high-severity';
                    resultTitle = '🚨 High Severity Issues Found';
                } else if (hasMediumSeverity) {
                    resultClass = 'medium-severity';
                    resultTitle = '⚠️ Medium Severity Issues Found';
                } else if (hasLowSeverity) {
                    resultClass = 'low-severity';
                    resultTitle = '📋 Low Severity Issues Found';
                } else if (hasInfoSeverity) {
                    resultClass = 'info-severity';
                    resultTitle = 'ℹ️ Informational Findings';
                } else if (!hasFindings) {
                    resultTitle = '✅ No Issues Found';
                }
                
                results.innerHTML = `
                    <div class="result ${resultClass}">
                        <h3>${resultTitle}</h3>
                        <pre>${result.output}</pre>
                    </div>
                `;
            } else {
                results.innerHTML = `
                    <div class="result success">
                        <h3>✅ Analysis Complete</h3>
                        <p>Slither analysis completed successfully. No issues found.</p>
                    </div>
                `;
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        solidity_code = data['code']
        
        # Create a temporary directory for the contract
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create a temporary file for the Solidity code
            contract_file = os.path.join(temp_dir, 'Contract.sol')
            with open(contract_file, 'w') as f:
                f.write(solidity_code)
            
            # Run slither with JSON output
            result = subprocess.run(
                ['slither', contract_file, '--json', '-'],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=temp_dir
            )
            
            # Parse the JSON output
            output_text = ""
            if result.stdout:
                try:
                    json_data = json.loads(result.stdout)
                    output_text = format_slither_output(json_data)
                except json.JSONDecodeError:
                    # If JSON parsing fails, try human-readable format
                    result_human = subprocess.run(
                        ['slither', contract_file],
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=temp_dir
                    )
                    output_text = result_human.stdout if result_human.stdout else result.stdout
            
            if not output_text and result.stderr:
                output_text = result.stderr
            
            # Return the formatted output
            return jsonify({
                'success': True,
                'output': output_text,
                'returncode': result.returncode
            })
            
        finally:
            # Clean up temp directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Analysis timed out after 60 seconds'
        })
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'slither not found. Please ensure slither-analyzer is installed.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error running slither: {str(e)}'
        })

def format_slither_output(json_data):
    """Format Slither JSON output into readable text"""
    output_lines = []
    
    if not json_data.get('success'):
        return "Analysis failed: " + json_data.get('error', 'Unknown error')
    
    results = json_data.get('results', {})
    detectors = results.get('detectors', [])
    
    if not detectors:
        return "✅ No issues found! Your contract appears to be secure."
    
    # Group findings by severity
    severity_groups = {
        'High': [],
        'Medium': [],
        'Low': [],
        'Informational': []
    }
    
    for detector in detectors:
        impact = detector.get('impact', 'Unknown')
        severity_groups[impact].append(detector)
    
    # Format output
    output_lines.append(f"🔍 Slither Analysis Results")
    output_lines.append(f"{'='*60}")
    output_lines.append(f"Found {len(detectors)} issue(s)\n")
    
    # Display findings by severity
    for severity in ['High', 'Medium', 'Low', 'Informational']:
        findings = severity_groups[severity]
        if findings:
            output_lines.append(f"\n{get_severity_emoji(severity)} {severity.upper()} SEVERITY ({len(findings)} issue(s))")
            output_lines.append(f"{'-'*60}")
            
            for i, finding in enumerate(findings, 1):
                output_lines.append(f"\nIssue #{i}:")
                output_lines.append(f"Type: {finding.get('check', 'Unknown')}")
                output_lines.append(f"Confidence: {finding.get('confidence', 'Unknown')}")
                
                # Clean up the description
                description = finding.get('description', '').strip()
                description = description.replace('\n\t', '\n  • ')
                output_lines.append(f"\nDescription:")
                output_lines.append(description)
                
                # Add location info if available
                if finding.get('elements'):
                    output_lines.append(f"\nLocation:")
                    for element in finding['elements']:
                        if element.get('source_mapping'):
                            lines = element['source_mapping'].get('lines', [])
                            name = element.get('name', 'Unknown')
                            elem_type = element.get('type', 'Unknown')
                            if lines:
                                output_lines.append(f"  • {elem_type} '{name}' at lines {lines[0]}-{lines[-1]}")
                
                output_lines.append(f"\n{'-'*40}")
    
    output_lines.append(f"\n{'='*60}")
    output_lines.append("📊 Summary:")
    output_lines.append(f"  • High: {len(severity_groups['High'])}")
    output_lines.append(f"  • Medium: {len(severity_groups['Medium'])}")
    output_lines.append(f"  • Low: {len(severity_groups['Low'])}")
    output_lines.append(f"  • Informational: {len(severity_groups['Informational'])}")
    
    return '\n'.join(output_lines)

def get_severity_emoji(severity):
    """Get emoji for severity level"""
    emojis = {
        'High': '🚨',
        'Medium': '⚠️',
        'Low': '📋',
        'Informational': 'ℹ️'
    }
    return emojis.get(severity, '📌')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
