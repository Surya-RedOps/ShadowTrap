import time

class AdaptiveDeception:
    def __init__(self, vfs):
        self.vfs = vfs
        self.users = ["admin", "devops", "backup", "security"]
        self.baits = [
            ("/home/devops/aws_keys.txt", "AKIAIOSFODNN7EXAMPLE:wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"),
            ("/root/db_password.txt", "POSTGRES_PWD=supersecret!"),
            ("/var/backups/backup.sql", "-- SQL Dump\nCREATE TABLE users..."),
            ("/etc/shadow.bak", "root:$6$.....:18498:0:99999:7:::")
        ]

    def deploy_baits(self):
        """Add fake users and bait files to the VFS."""
        # Add users to /etc/passwd
        passwd_content = self.vfs.get_file_content("/etc/passwd")
        for user in self.users:
            if user not in passwd_content:
                passwd_content += f"\n{user}:x:100{self.users.index(user)+1}:100{self.users.index(user)+1}:{user}:/home/{user}:/bin/bash"
                self.vfs.mk_dir(f"/home/{user}")
        self.vfs.write_file("/etc/passwd", passwd_content)

        # Write bait files
        for path, content in self.baits:
            parent = "/".join(path.split("/")[:-1])
            if not self.vfs.exists(parent):
                self.vfs.mk_dir(parent)
            self.vfs.write_file(path, content)

    def get_dynamic_ps(self, username):
        """Generate realistic ps output."""
        output = "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\n"
        output += "root         1  0.0  0.1 168000 12000 ?        Ss   Feb13   0:05 /sbin/init\n"
        output += "root       852  0.0  0.1  12340  5000 ?        Ss   Feb13   0:00 /usr/sbin/sshd -D\n"
        output += f"root      1337  0.0  0.2  24500  8200 pts/0    Ss+  {time.strftime('%H:%M')}   0:00 -bash\n"
        output += f"root      1402  0.0  0.1  18000  3200 pts/0    R+   {time.strftime('%H:%M')}   0:00 ps aux\n"
        return output

    def get_dynamic_netstat(self):
        """Generate realistic netstat output."""
        output = "Active Internet connections (w/o servers)\n"
        output += "Proto Recv-Q Send-Q Local Address           Foreign Address         State      \n"
        output += "tcp        0      0 192.168.1.10:22         1.2.3.4:56789           ESTABLISHED\n"
        output += "tcp        0      0 127.0.0.1:5432          0.0.0.0:*               LISTEN     \n"
        return output
