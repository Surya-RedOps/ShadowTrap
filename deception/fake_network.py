import time
import random
import hashlib

class FakeNetwork:
    def __init__(self, vfs):
        self.vfs = vfs

    async def simulate_ping(self, host, process):
        """Simulate the ping command."""
        if not host:
            process.stdout.write("ping: usage error: Destination address required\n")
            return

        process.stdout.write(f"PING {host} ({self._get_fake_ip(host)}) 56(84) bytes of data.\n")
        
        for i in range(4):
            await time_sleep(1)
            time_ms = round(random.uniform(10, 50), 3)
            process.stdout.write(f"64 bytes from {host} ({self._get_fake_ip(host)}): icmp_seq={i+1} ttl=64 time={time_ms} ms\n")
        
        process.stdout.write(f"\n--- {host} ping statistics ---\n")
        process.stdout.write(f"4 packets transmitted, 4 received, 0% packet loss, time 3004ms\n")
        process.stdout.write(f"rtt min/avg/max/mdev = 10.123/25.456/49.789/10.123 ms\n")

    async def simulate_wget(self, url, args, process):
        """Simulate wget and capture the 'malware'."""
        if not url:
            process.stdout.write("wget: missing URL\n")
            return

        filename = url.split("/")[-1] or "index.html"
        # Check if output document is specified
        if "-O" in args:
            try:
                filename = args[args.index("-O") + 1]
            except IndexError:
                pass

        process.stdout.write(f"--{time.strftime('%Y-%m-%d %H:%M:%S')}--  {url}\n")
        process.stdout.write(f"Resolving {url.split('/')[2] if '//' in url else url}... {self._get_fake_ip(url)}\n")
        process.stdout.write(f"Connecting to {url.split('/')[2] if '//' in url else url}|{self._get_fake_ip(url)}|:80... connected.\n")
        process.stdout.write("HTTP request sent, awaiting response... 200 OK\n")
        
        size = random.randint(10000, 2000000)
        process.stdout.write(f"Length: {size} ({size//1024}K) [application/octet-stream]\n")
        process.stdout.write(f"Saving to: ‘{filename}’\n\n")
        
        # Simulate progress bar
        process.stdout.write(f"{filename}        100%[===================>]   {size//1024}K  --.-KB/s    in 0.1s\n\n")
        process.stdout.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} ({size//1024} KB/s) - ‘{filename}’ saved [{size}/{size}]\n")
        
        # Content creation (simulated binary)
        content = f"FAKE_MALWARE_DATA_FROM_{url}_{time.time()}"
        self.vfs.write_file(filename, content)
        
        return {
            "url": url,
            "filename": filename,
            "size": size,
            "content": content
        }

    async def simulate_curl(self, url, args, process):
        """Simulate curl."""
        if not url:
            process.stdout.write("curl: try 'curl --help' for more information\n")
            return

        if "-O" in args or "-o" in args:
             # Similar to wget
             return await self.simulate_wget(url, args, process)
        else:
            # Just output text
            process.stdout.write(f"<html><body><h1>Resource Moved</h1><p>The document has moved <a href='{url}'>here</a>.</p></body></html>\n")
            return None

    async def simulate_apt(self, args, process):
        """Simulate apt-get install."""
        if "install" in args:
            pkg = args[args.index("install") + 1] if len(args) > args.index("install") + 1 else "package"
            process.stdout.write(f"Reading package lists... Done\n")
            process.stdout.write(f"Building dependency tree... Done\n")
            process.stdout.write(f"Reading state information... Done\n")
            process.stdout.write(f"The following NEW packages will be installed:\n  {pkg}\n")
            process.stdout.write(f"0 upgraded, 1 newly installed, 0 to remove and 42 not upgraded.\n")
            process.stdout.write(f"Need to get 1234 kB of archives.\n")
            process.stdout.write(f"After this operation, 5678 kB of additional disk space will be used.\n")
            process.stdout.write(f"Get:1 http://archive.ubuntu.com/ubuntu jammy/main amd64 {pkg} [1234 kB]\n")
            process.stdout.write(f"Fetched 1234 kB in 0s (0 B/s)\n")
            process.stdout.write(f"Selecting previously unselected package {pkg}.\n(Reading database ... 123456 files and directories currently installed.)\n")
            process.stdout.write(f"Preparing to unpack .../{pkg}_1.2.3_amd64.deb ...\n")
            process.stdout.write(f"Unpacking {pkg} (1.2.3) ...\n")
            process.stdout.write(f"Setting up {pkg} (1.2.3) ...\n")
        elif "update" in args:
             process.stdout.write("Hit:1 http://archive.ubuntu.com/ubuntu jammy InRelease\n")
             process.stdout.write("Reading package lists... Done\n")
        else:
            process.stdout.write("apt 2.4.11 (amd64)\nUsage: apt [options] command\n")

    def _get_fake_ip(self, host):
        """Deterministically generate a fake IP for a host."""
        h = hashlib.md5(host.encode()).hexdigest()
        return f"{int(h[:2], 16)}.{int(h[2:4], 16)}.{int(h[4:6], 16)}.{int(h[6:8], 16)}"

async def time_sleep(seconds):
    await asyncio.sleep(seconds)

import asyncio
