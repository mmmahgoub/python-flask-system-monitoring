from flask import Flask, render_template, jsonify
import psutil

app = Flask(__name__)

def get_open_ports():
    ports_info = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'LISTEN' and conn.laddr:
            pid = conn.pid
            try:
                proc = psutil.Process(pid)
                ports_info.append({
                    'port': conn.laddr.port,
                    'service': proc.name(),
                    'pid': pid
                })
            except Exception:
                continue
    return ports_info

def get_top_network_services():
    stats = {}
    for conn in psutil.net_connections(kind='inet'):
        pid = conn.pid
        if pid:
            try:
                proc = psutil.Process(pid)
                name = proc.name()
                stats[name] = stats.get(name, 0) + 1
            except:
                continue
    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    return [{'service': name, 'connections': count} for name, count in sorted_stats[:5]]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/metrics')
def metrics():
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    open_ports = get_open_ports()
    net_services = get_top_network_services()

    return jsonify({
        'cpu': cpu,
        'mem': mem,
        'disk': disk,
        'open_ports': open_ports,
        'network_services': net_services
    })

if __name__ == '__main__':
    app.run(debug=True)
