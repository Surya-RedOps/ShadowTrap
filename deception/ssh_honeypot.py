import asyncssh
import asyncio
import os
import shlex
import time

from database.db import SessionLocal
from database.models import SSHSession
from intelligence.threat_score import calculate_score
from intelligence.telegram_alert import send_telegram_alert
from dashboard.live_ws import manager
from deception.filesystem import VirtualFileSystem
from intelligence.behavior import behavior_engine
from intelligence.mitre import get_mitre_info
from config.settings import NODE_ID

# New Imports
import uuid
from deception.fake_network import FakeNetwork
from intelligence.malware_analysis import malware_engine
from intelligence.attack_patterns import pattern_engine
from intelligence.threat_scoring import threat_engine
from intelligence.geoip_engine import geoip_engine
from intelligence.honeytoken_monitor import token_monitor
from intelligence.session_replay import replay_engine
from deception.adaptive_engine import AdaptiveDeception

# Handle each attacker session
async def handle_client(process: asyncssh.SSHServerProcess):
    ip = process.get_extra_info("peername")[0]
    username = process.get_extra_info("username")
    password = "unknown" # Password capture handled in auth callback
    print(f"DEBUG: New client connected: {ip} user={username}")

    process.stdout.write("Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 5.15.0-91-generic x86_64)\n\n")
    process.stdout.write(" * Documentation:  https://help.ubuntu.com\n")
    process.stdout.write(" * Management:     https://landscape.canonical.com\n")
    process.stdout.write(" * Support:        https://ubuntu.com/advantage\n\n")
    process.stdout.write("  System information as of " + time.strftime("%a %d %b %Y %H:%M:%S %Z") + "\n\n")
    process.stdout.write("  System load:  0.08               Processes:             102\n")
    process.stdout.write("  Usage of /:   12.3% of 38.60GB   Users logged in:       0\n")
    process.stdout.write("  Memory usage: 14%                IPv4 address for eth0: 192.168.1.10\n")
    process.stdout.write("  Swap usage:   0%\n\n")
    process.stdout.write("0 updates can be applied immediately.\n\n") 
    process.stdout.write("The programs included with the Ubuntu system are free software;\n")
    process.stdout.write("the exact distribution terms for each program are described in the\n")
    process.stdout.write("individual files in /usr/share/doc/*/copyright.\n\n")
    process.stdout.write("Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by\n")
    process.stdout.write("applicable law.\n\n")

    # Initialize session ID and metadata
    session_id = str(uuid.uuid4())
    location = geoip_engine.get_location(ip)
    
    # Initialize Virtual Filesystem for this session
    vfs = VirtualFileSystem()
    fake_net = FakeNetwork(vfs)
    adaptive = AdaptiveDeception(vfs)
    adaptive.deploy_baits()
    
    db = SessionLocal()
    session_history = []

    try:
        while not process.stdin.at_eof():
            try:
                line = await process.stdin.readline()
                if not line:
                    break
                command_line = line.strip()
                if not command_line:
                    process.stdout.write(f"root@ubuntu-server:{vfs.cwd if vfs.cwd == '/' else vfs.cwd.replace('/root', '~')}# ")
                    continue
            except Exception:
                break

            # Basic parsing using shlex to handle quotes
            try:
                parts = shlex.split(command_line)
            except ValueError:
                parts = command_line.split() # Fallback

            if not parts:
                continue

            cmd = parts[0]
            args = parts[1:]

            # --- Advanced Intelligence ---
            risk = calculate_score(command_line)
            analysis = behavior_engine.analyze(ip, command_line)
            mitre_data = get_mitre_info(command_line)
            tactic = mitre_data['tactic'] if mitre_data else "None"
            
            # Threat Scoring
            threat_engine.calculate_risk(ip, tactic)
            
            # Honeytoken Monitoring
            await token_monitor.check_command(ip, command_line)
            
            # Pattern Detection
            session_history.append(cmd)
            detected_patterns = pattern_engine.detect_patterns(session_history)
            
            # Log for Session Replay
            replay_engine.log_event(session_id, ip, "COMMAND", {"cmd": command_line, "cwd": vfs.cwd})

            # Save to DB
            db_session = SSHSession(
                session_id=session_id,
                ip_address=ip,
                username=username,
                password=password,
                command=command_line,
                risk_score=risk,
                attacker_type=analysis['attacker_type'],
                mitre_tactic=tactic
            )
            db.add(db_session)
            db.commit()

            # Live broadcast to dashboard
            await manager.broadcast({
                "session_id": session_id,
                "node_id": NODE_ID,
                "ip": ip,
                "location": location,
                "user": username,
                "command": command_line,
                "risk_score": risk,
                "attacker_type": analysis['attacker_type'],
                "mitre_tactic": tactic,
                "mitre_id": mitre_data['id'] if mitre_data else "",
                "patterns": detected_patterns
            })

            # Telegram Alert for high risk or patterns
            if risk >= 70 or detected_patterns:
                alert_msg = (
                    f"⚠️ *ShadowTrap High Risk Event*\n\n"
                    f"*IP:* `{ip}`\n"
                    f"*Location:* {location.get('city', 'Unknown')}, {location.get('code', 'XX')}\n"
                    f"*User:* `{username}`\n"
                    f"*Cmd:* `{command_line}`\n"
                    f"*Risk:* `{risk}`\n"
                    f"*Tactic:* `{tactic}`\n"
                    f"*Patterns:* {', '.join(detected_patterns) if detected_patterns else 'None'}"
                )
                send_telegram_alert(alert_msg)

            # --- Command Handling ---
            
            if cmd == "exit":
                process.exit(0)
                break

            elif cmd == "pwd":
                process.stdout.write(f"{vfs.cwd}\n")

            elif cmd == "ls":
                path = vfs.cwd
                show_hidden = False
                long_format = False
                
                # Simple flag parsing
                clean_args = []
                for arg in args:
                    if arg.startswith("-"):
                        if "a" in arg: show_hidden = True
                        if "l" in arg: long_format = True
                    else:
                        clean_args.append(arg)
                
                if clean_args:
                    path = clean_args[0]

                if vfs.is_dir(path):
                    contents = vfs.list_dir(path)
                    if contents is not None:
                        # Filter hidden if not -a
                        if not show_hidden:
                            contents = [c for c in contents if not c.startswith(".")]
                        
                        if long_format:
                            output = "\n".join([f"-rw-r--r-- 1 root root 1024 Feb 15 10:00 {c}" for c in contents]) # Fake stats
                        else:
                            output = "  ".join(contents)
                        process.stdout.write(f"{output}\n")
                    else:
                         process.stdout.write(f"ls: cannot access '{path}': No such file or directory\n")
                elif vfs.is_file(path):
                     process.stdout.write(f"{path}\n")
                else:
                    process.stdout.write(f"ls: cannot access '{path}': No such file or directory\n")

            elif cmd == "cd":
                path = args[0] if args else "/root"
                if vfs.change_dir(path):
                    pass
                else:
                    process.stdout.write(f"bash: cd: {path}: No such file or directory\n")

            elif cmd == "cat":
                if not args:
                    process.stdout.write("")
                else:
                    for filename in args:
                         content = vfs.get_file_content(filename)
                         if content is not None:
                             process.stdout.write(f"{content}\n")
                         else:
                             process.stdout.write(f"cat: {filename}: No such file or directory\n")

            elif cmd == "whoami":
                process.stdout.write("root\n")

            elif cmd == "id":
                process.stdout.write("uid=0(root) gid=0(root) groups=0(root)\n")

            elif cmd == "uname":
                if "-a" in args:
                    process.stdout.write("Linux ubuntu-server 5.15.0-91-generic #101-Ubuntu SMP Tue Nov 14 13:30:08 UTC 2023 x86_64 x86_64 x86_64 GNU/Linux\n")
                else:
                    process.stdout.write("Linux\n")

            elif cmd == "w":
                process.stdout.write(" 21:58:11 up 2 days, 10:30,  1 user,  load average: 0.05, 0.03, 0.00\n")
                process.stdout.write("USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT\n")
                process.stdout.write(f"{username}     pts/0    {ip}    21:58    0.00s  0.03s  0.00s w\n")

            elif cmd == "ps":
                process.stdout.write(adaptive.get_dynamic_ps(username))

            elif cmd == "netstat":
                process.stdout.write(adaptive.get_dynamic_netstat())

            elif cmd == "ping":
                host = args[0] if args else None
                await fake_net.simulate_ping(host, process)

            elif cmd == "wget":
                url = args[0] if args else None
                result = await fake_net.simulate_wget(url, args, process)
                if result:
                    malware_engine.capture_sample(ip, result['filename'], result['content'])
            
            elif cmd == "curl":
                url = args[-1] if args else None
                result = await fake_net.simulate_curl(url, args, process)
                if result and result.get('content'):
                    malware_engine.capture_sample(ip, result['filename'], result['content'])

            elif cmd == "apt" or cmd == "apt-get":
                await fake_net.simulate_apt(args, process)

            elif cmd == "mkdir":
                if args:
                    for arg in args:
                         success, msg = vfs.mk_dir(arg)
                         if not success:
                              process.stdout.write(f"mkdir: cannot create directory ‘{arg}’: {msg}\n")
                else:
                     process.stdout.write("mkdir: missing operand\n")

            elif cmd == "touch":
                 if args:
                      for arg in args:
                           vfs.write_file(arg, "")
                 else:
                      process.stdout.write("touch: missing file operand\n")

            elif cmd == "rm":
                 # Minimal rm implementation
                 recursive = "-r" in args or "-rf" in args
                 files = [a for a in args if not a.startswith("-")]
                 if files:
                      for f in files:
                           vfs.remove(f, recursive=recursive)

            elif cmd == "cp":
                 if len(args) >= 2:
                      src = args[0]
                      dest = args[1]
                      vfs.copy(src, dest)
            
            elif cmd == "mv":
                 if len(args) >= 2:
                      src = args[0]
                      dest = args[1]
                      vfs.move(src, dest)

            elif cmd == "grep":
                 process.stdout.write("") # Silent grep if no output matched (fake)

            elif cmd == "tar":
                if "-x" in args or "-xvf" in args or "xvf" in args[0]:
                    process.stdout.write("xmrig\nconfig.json\nstart.sh\n")
                    vfs.write_file("xmrig", "Fake Miner Binary")
                    vfs.write_file("config.json", "{}")
                    vfs.write_file("start.sh", "#!/bin/bash\n./xmrig")
                else:
                    process.stdout.write("tar: must specify action\n")

            elif cmd == "chmod":
                # Silent success
                pass

            elif cmd == "sudo":
                if args:
                    # Simulate password prompt then success
                    process.stdout.write(f"[sudo] password for {username}: ")
                    # In a real shell we'd mask input, here we just simulate the prompt line
                    # But since we can't easily capture the next line without complex state,
                    # we'll just pretend they typed it and it worked, or fail if we want.
                    # For simplicity in this non-interactive block:
                    process.stdout.write("\n")
                    # Execute the command as root (simulated)
                    # We Just recurse or handle 'su'? 
                    # Simpler: Just say "Sorry, try again." to annoy them?
                    # Or run the command. Let's run the command if it's simple.
                    subcmd = args[0]
                    if subcmd == "su":
                         process.stdout.write("root@ubuntu-server:/root# ")
                    else:
                         process.stdout.write(f"{subcmd}: command executed as root\n")
                else:
                    process.stdout.write("usage: sudo -h | -K | -k | -V\n")
                    process.stdout.write("usage: sudo -v [-AknS] [-g group] [-h host] [-p prompt] [-u user]\n")

            elif cmd == "crontab":
                if "-e" in args:
                    process.stdout.write("no crontab for root - using an empty one\n")
                    process.stdout.write("Select an editor.  To change later, run 'select-editor'.\n")
                    process.stdout.write("  1. /bin/nano        <---- easiest\n")
                    process.stdout.write("  2. /usr/bin/vim.basic\n")
                    process.stdout.write("  3. /usr/bin/vim.tiny\n")
                    process.stdout.write("  4. /bin/ed\n")
                    process.stdout.write("Choose 1-4 [1]: 1\n")
                    process.stdout.write("crontab: installing new crontab\n")
                elif "-l" in args:
                    process.stdout.write("no crontab for root\n")


            elif cmd == "history":
                  content = vfs.get_file_content("/root/.bash_history")
                  if content:
                       process.stdout.write(f"{content}\n")

            elif cmd.startswith("./") or cmd.endswith(".sh"):
                process.stdout.write(f"Starting {cmd}...\n")
                process.stdout.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]  net      use pool pool.supportxmr.com:3333  127.0.0.1\n")
                process.stdout.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]  net      new job from pool.supportxmr.com:3333 diff 100000 algo rx/0\n")
                await asyncio.sleep(1) 
                process.stdout.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]  cpu      ACCEPTED (1/0) diff 100000 (123 ms)\n")
            
            elif cmd == "help":
                process.stdout.write("GNU bash, version 5.1.16(1)-release (x86_64-pc-linux-gnu)\n")
                process.stdout.write("These shell commands are defined correctly.  Type 'help' to see this list.\n")

            else:
                process.stdout.write(f"{cmd}: command not found\n")

            # Emulate prompt
            display_cwd = vfs.cwd if vfs.cwd == '/' else vfs.cwd.replace("/root", "~")
            process.stdout.write(f"root@ubuntu-server:{display_cwd}# ")

    finally:
        replay_engine.finalize_session(session_id)
        db.close()

class HoneyPotSSHServer(asyncssh.SSHServer):
    def __init__(self, process_factory=None):
        self._process_factory = process_factory

    def connection_made(self, conn):
        print(f"SSH connection received from {conn.get_extra_info('peername')[0]}")

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        print(f"Login attempt: {username}:{password}")
        return True

    def session_requested(self):
        return asyncssh.SSHServerProcess(
            self._process_factory,
            sftp_factory=None,
            sftp_version=0,
            allow_scp=False
        )

# Start SSH honeypot server
async def start_ssh_honeypot():
    await asyncssh.create_server(
        lambda: HoneyPotSSHServer(process_factory=handle_client),
        "",
        2222,
        server_host_keys=["deception/host_key"],
    )

    # Keep running forever
    await asyncio.Future()

