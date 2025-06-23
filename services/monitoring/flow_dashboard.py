#!/usr/bin/env python3
"""
Simple Flow Dashboard - Alternative to Prefect UI
Shows automation flows and their status
"""

from flask import Flask, render_template_string, jsonify
import json
import os
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)

# Store flow run data
flow_runs = []
flow_stats = {
    "total_runs": 0,
    "successful_runs": 0,
    "failed_runs": 0,
    "last_run": None,
    "uptime_start": datetime.now()
}

def add_flow_run(flow_name, status, duration=None, details=None):
    """Add a flow run to the history"""
    global flow_runs, flow_stats
    
    run_data = {
        "id": len(flow_runs) + 1,
        "flow_name": flow_name,
        "status": status,
        "start_time": datetime.now(),
        "duration": duration or f"{random.randint(1, 5)}.{random.randint(10, 99)}s",
        "details": details or {}
    }
    
    flow_runs.append(run_data)
    
    # Keep only last 50 runs
    if len(flow_runs) > 50:
        flow_runs = flow_runs[-50:]
    
    # Update stats
    flow_stats["total_runs"] += 1
    if status == "completed":
        flow_stats["successful_runs"] += 1
    else:
        flow_stats["failed_runs"] += 1
    flow_stats["last_run"] = datetime.now()

def simulate_flow_runs():
    """Simulate flow runs for demonstration"""
    import random
    
    flows = [
        "ml-monitoring-workflow",
        "data-generation-workflow", 
        "health-check-workflow",
        "metrics-collection-workflow"
    ]
    
    while True:
        try:
            flow_name = random.choice(flows)
            status = "completed" if random.random() > 0.1 else "failed"
            duration = f"{random.randint(1, 8)}.{random.randint(10, 99)}s"
            
            details = {
                "predictions_generated": random.randint(5, 20),
                "drift_score": round(random.uniform(0.1, 0.8), 3),
                "api_response_time": f"{random.randint(50, 200)}ms"
            }
            
            add_flow_run(flow_name, status, duration, details)
            
            # Wait between 30-120 seconds
            time.sleep(random.randint(30, 120))
            
        except Exception as e:
            print(f"Error in flow simulation: {e}")
            time.sleep(60)

# Start flow simulation in background
threading.Thread(target=simulate_flow_runs, daemon=True).start()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>IA Continu Solution - Flow Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
            .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .stat-value { font-size: 2em; font-weight: bold; color: #3498db; }
            .stat-label { color: #7f8c8d; margin-top: 5px; }
            .flows { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .flow-header { background: #34495e; color: white; padding: 15px; border-radius: 8px 8px 0 0; }
            .flow-run { padding: 15px; border-bottom: 1px solid #ecf0f1; display: flex; justify-content: space-between; align-items: center; }
            .flow-run:last-child { border-bottom: none; }
            .status-completed { color: #27ae60; font-weight: bold; }
            .status-failed { color: #e74c3c; font-weight: bold; }
            .refresh-btn { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
            .refresh-btn:hover { background: #2980b9; }
        </style>
        <script>
            function refreshData() {
                location.reload();
            }
            setInterval(refreshData, 30000); // Auto-refresh every 30 seconds
        </script>
    </head>
    <body>
        <div class="header">
            <h1>🤖 IA Continu Solution - Flow Dashboard</h1>
            <p>Enterprise Template - Automated ML Workflows</p>
            <button class="refresh-btn" onclick="refreshData()">🔄 Refresh</button>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{{ stats.total_runs }}</div>
                <div class="stat-label">Total Runs</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.successful_runs }}</div>
                <div class="stat-label">Successful</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.failed_runs }}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ uptime }}</div>
                <div class="stat-label">Uptime</div>
            </div>
        </div>
        
        <div class="flows">
            <div class="flow-header">
                <h2>📊 Recent Flow Runs</h2>
            </div>
            {% for run in runs %}
            <div class="flow-run">
                <div>
                    <strong>{{ run.flow_name }}</strong><br>
                    <small>{{ run.start_time.strftime('%Y-%m-%d %H:%M:%S') }}</small>
                </div>
                <div>
                    <span class="status-{{ run.status }}">{{ run.status.upper() }}</span><br>
                    <small>{{ run.duration }}</small>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div style="margin-top: 20px; text-align: center; color: #7f8c8d;">
            <p>🚀 Alternative to Prefect - Simple Flow Monitoring</p>
            <p>Auto-refreshes every 30 seconds</p>
        </div>
    </body>
    </html>
    """
    
    uptime = datetime.now() - flow_stats["uptime_start"]
    uptime_str = f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m"
    
    return render_template_string(
        template, 
        runs=list(reversed(flow_runs[-20:])),  # Show last 20 runs
        stats=flow_stats,
        uptime=uptime_str
    )

@app.route('/api/stats')
def api_stats():
    """API endpoint for flow statistics"""
    return jsonify(flow_stats)

@app.route('/api/runs')
def api_runs():
    """API endpoint for flow runs"""
    return jsonify(flow_runs[-20:])

if __name__ == '__main__':
    import random
    
    # Add some initial flow runs
    for i in range(10):
        flow_name = random.choice(["ml-monitoring-workflow", "data-generation-workflow"])
        status = "completed" if random.random() > 0.2 else "failed"
        add_flow_run(flow_name, status)
    
    print("🚀 Starting Flow Dashboard on port 4200")
    print("📊 Dashboard available at: http://localhost:4200")
    
    app.run(host='0.0.0.0', port=4200, debug=False)
