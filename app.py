from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import subprocess
import whois
import os
import platform
from telegram_bot import send_message

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev_key_change_in_production!')
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')
app.config['DEBUG'] = False if app.config['ENV'] == 'production' else True

# Configure SocketIO for production
socketio = SocketIO(
    app,
    async_mode='eventlet',  # Use eventlet for better WebSocket performance
    cors_allowed_origins="*",  # Adjust this in production to your domain
    ping_timeout=30,
    ping_interval=25
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ping')
def ping():
    return render_template('ping.html')

@app.route('/whois')
def whoisdomain():
    return render_template('whois.html')

@app.route('/ip_lookup')
def iplookup():
    return render_template('ip_lookup.html')

@app.route('/certificate_search')
def crtsh():
    return render_template('certificate_search.html')

@app.route('/open_ports')
def openports():
    return render_template('open_ports.html')

@app.route('/recon')
def recon():
    return render_template('recon.html')

""" @socketio.on('start_ping')
def start_ping(data):
    domain = data['domain']
    send_message(f"📱 Ping scan started for: {domain}")
    try:
        with subprocess.Popen(['ping', '-c', '4', domain], stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
            for line in p.stdout:
                emit('ping_update', {'data': line.strip()})
    except Exception as e:
        error_msg = f"❌ Ping scan failed for {domain}: {e}"
        emit('ping_update', {'data': error_msg})
        send_message(error_msg)
        return
    emit('ping_update', {'data': '✅ Ping Finished'})
    send_message(f"✅ Ping scan finished for: {domain}") """

@socketio.on('start_ping')
def start_ping(data):
    domain = data.get('domain')
    if not domain:
        emit('ping_update', {'data': '❌ No domain provided'})
        return

    send_message(f"📱 Ping scan started for: {domain}")

    # Select ping command based on OS
    if platform.system().lower() == "windows":
        cmd = ['ping', '-n', '4', domain]  # Windows flag
    else:
        cmd = ['ping', '-c', '4', domain]  # Linux/macOS flag

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,  # same as universal_newlines=True in newer Python
            bufsize=1
        )

        if process.stdout is None:
            raise RuntimeError("No output stream from ping command")

        # Stream output line-by-line
        for line in process.stdout:
            emit('ping_update', {'data': line.strip()})

        process.stdout.close()
        process.wait()

    except Exception as e:
        error_msg = f"❌ Ping scan failed for {domain}: {e}"
        emit('ping_update', {'data': error_msg})
        send_message(error_msg)
        return

    emit('ping_update', {'data': '✅ Ping Finished'})
    send_message(f"✅ Ping scan finished for: {domain}")

@socketio.on('start_iplookup')
def start_iplookup(data):
    ipAddress = data['ipAddress']
    result = subprocess.run(['curl', f'http://ip-api.com/json/{ipAddress}'], stdout=subprocess.PIPE, text=True)
    send_message(f"📊 IP Lookup for {ipAddress} done")
    emit('iplookup_update', {'data': result.stdout})

@socketio.on('start_whois')
def start_whois(data):
    domain = data['domain']
    try:
        domain_info = whois.whois(domain)
        result = str(domain_info)
        send_message(f"📄 Whois data fetched for {domain}")
    except Exception as e:
        result = f"Error: {e}"
        send_message(result)
    emit('whois_update', {'data': result})

@socketio.on('start_crtsh')
def start_crtsh(data):
    domain = data['domain']
    result = subprocess.run(['curl', f'https://crt.sh/?q=%.{domain}&output=json'], stdout=subprocess.PIPE, text=True)
    send_message(f"🔍 Certificate transparency scan done for {domain}")
    emit('crtsh_update', {'data': result.stdout})

@socketio.on('start_openports')
def start_openports(data):
    domain = data['domain']
    result = subprocess.run(['nmap', '-F', domain], stdout=subprocess.PIPE, text=True)
    send_message(f"🚧 Open ports scan done for {domain}")
    emit('openports_update', {'data': result.stdout})

@socketio.on('start_recon')
def start_recon(data):
    org_name = data['org_name']
    domains = data['domains']
    recon_folder = 'recon'
    os.makedirs(recon_folder, exist_ok=True)
    orgs_file_path = os.path.join(recon_folder, 'orgs.txt')
    if not os.path.exists(orgs_file_path):
        with open(orgs_file_path, 'w') as f:
            pass
    with open(orgs_file_path, 'r') as orgs_file:
        existing_orgs = orgs_file.read().splitlines()
    if org_name in existing_orgs:
        org_folder = os.path.join(recon_folder, org_name)
        domains_file_path = os.path.join(org_folder, 'domains.txt')
        if os.path.exists(domains_file_path):
            with open(domains_file_path, 'r') as domains_file:
                existing_domains = domains_file.read().splitlines()
            for domain in domains:
                if domain not in existing_domains:
                    with open(domains_file_path, 'a') as f:
                        f.write(domain + '\n')
                    emit('recon_update', {'data': f'Domain {domain} added to {org_name}'})
                else:
                    emit('recon_update', {'data': f'Domain {domain} already exists in {org_name}'})
        else:
            os.makedirs(org_folder, exist_ok=True)
            with open(domains_file_path, 'a') as f:
                for domain in domains:
                    f.write(domain + '\n')
            emit('recon_update', {'data': f'Domains added to {org_name}'})
    else:
        with open(orgs_file_path, 'a') as f:
            f.write(org_name + '\n')
        org_folder = os.path.join(recon_folder, org_name)
        os.makedirs(org_folder, exist_ok=True)
        domains_file_path = os.path.join(org_folder, 'domains.txt')
        with open(domains_file_path, 'a') as f:
            for domain in domains:
                f.write(domain + '\n')
        emit('recon_update', {'data': f'Domains added to {org_name}'})
    send_message(f"🔎 Recon setup complete for {org_name} with domains: {', '.join(domains)}")

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG'],
        allow_unsafe_werkzeug=not app.config['ENV'] == 'production'
    )