import os
import time

class VirtualFileSystem:
    def __init__(self):
        # Structure: {path: {'type': 'file'/'dir', 'content': str/list, 'owner': 'root', 'perm': 'rw-r--r--'}}
        self.fs = {
            "/": {"type": "dir", "content": ["bin", "boot", "dev", "etc", "home", "lib", "media", "mnt", "opt", "proc", "root", "run", "sbin", "srv", "sys", "tmp", "usr", "var"], "owner": "root", "perm": "drwxr-xr-x"},
            "/root": {"type": "dir", "content": ["passwords.txt", "notes", ".bash_history", ".ssh"], "owner": "root", "perm": "drwx------"},
            "/root/passwords.txt": {"type": "file", "content": "facebook: admin123\ngmail: hunter2\naws_access_key_id: AKIAIOSFODNN7EXAMPLE\naws_secret_access_key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", "owner": "root", "perm": "-rw-------"},
            "/root/notes": {"type": "file", "content": "TODO: Hack the planet\n1. Scan network\n2. Exploit SMB\n3. Profit", "owner": "root", "perm": "-rw-r--r--"},
            "/root/.bash_history": {"type": "file", "content": "nmap 192.168.1.1\nssh root@10.0.0.1\nscp payload.sh user@10.0.0.5:/tmp\n./payload.sh", "owner": "root", "perm": "-rw-------"},
            "/root/.ssh": {"type": "dir", "content": ["id_rsa", "id_rsa.pub", "authorized_keys"], "owner": "root", "perm": "drwx------"},
            "/root/.ssh/id_rsa": {"type": "file", "content": "-----BEGIN OPENSSH PRIVATE KEY-----\nb3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn\nExamplePrivateKeyContent...\n-----END OPENSSH PRIVATE KEY-----", "owner": "root", "perm": "-rw-------"},
            "/root/.ssh/id_rsa.pub": {"type": "file", "content": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC... root@ubuntu-server", "owner": "root", "perm": "-rw-r--r--"},
            "/etc": {"type": "dir", "content": ["passwd", "shadow", "hostname", "issue", "os-release"], "owner": "root", "perm": "drwxr-xr-x"},
            "/etc/passwd": {"type": "file", "content": "root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\nbin:x:2:2:bin:/bin:/usr/sbin/nologin\nsys:x:3:3:sys:/dev:/usr/sbin/nologin\nsync:x:4:65534:sync:/bin:/bin/sync\ngames:x:5:60:games:/usr/games:/usr/sbin/nologin\nman:x:6:12:man:/var/cache/man:/usr/sbin/nologin\nlp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin\nmail:x:8:8:mail:/var/mail:/usr/sbin/nologin\nnews:x:9:9:news:/var/spool/news:/usr/sbin/nologin\nuucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin\nproxy:x:13:13:proxy:/bin:/usr/sbin/nologin\nwww-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\nbackup:x:34:34:backup:/var/backups:/usr/sbin/nologin\nlist:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin\nirc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin\ngnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin\nnobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin\nsystemd-network:x:100:102:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin\nsystemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin\nsystemd-timesync:x:102:104:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin\nmessagebus:x:103:106::/nonexistent:/usr/sbin/nologin\nsyslog:x:104:110::/home/syslog:/usr/sbin/nologin\n_apt:x:105:65534::/nonexistent:/usr/sbin/nologin\ntss:x:106:111:TPM2 software stack,,,:/var/lib/tpm:/bin/false\nuuidd:x:107:112::/run/uuidd:/usr/sbin/nologin\ntcpdump:x:108:113::/nonexistent:/usr/sbin/nologin\nsshd:x:109:65534::/run/sshd:/usr/sbin/nologin\nuser:x:1000:1000:user:/home/user:/bin/bash", "owner": "root", "perm": "-rw-r--r--"},
            "/etc/shadow": {"type": "file", "content": "root:$6$.....:18498:0:99999:7:::\nuser:$6$.....:18498:0:99999:7:::", "owner": "root", "perm": "-rw-r-----"},
            "/etc/hostname": {"type": "file", "content": "ubuntu-server", "owner": "root", "perm": "-rw-r--r--"},
            "/etc/issue": {"type": "file", "content": "Ubuntu 22.04.3 LTS \\n \\l\n", "owner": "root", "perm": "-rw-r--r--"},
            "/etc/os-release": {"type": "file", "content": "PRETTY_NAME=\"Ubuntu 22.04.3 LTS\"\nNAME=\"Ubuntu\"\nVERSION_ID=\"22.04\"\nVERSION=\"22.04.3 LTS (Jammy Jellyfish)\"\nID=ubuntu", "owner": "root", "perm": "-rw-r--r--"},
            "/proc": {"type": "dir", "content": ["cpuinfo", "meminfo", "version", "uptime"], "owner": "root", "perm": "dr-xr-xr-x"},
            "/proc/cpuinfo": {"type": "file", "content": "processor\t: 0\nvendor_id\t: GenuineIntel\ncpu family\t: 6\nmodel\t\t: 85\nmodel name\t: Intel(R) Xeon(R) CPU @ 2.20GHz\nstepping\t: 7\nmicrocode\t: 0x5003003\ncpu MHz\t\t: 2200.000\ncache size\t: 39424 KB\nphysical id\t: 0\nsiblings\t: 2\ncore id\t\t: 0\ncpu cores\t: 1\napicid\t\t: 0\ninitial apicid\t: 0\nfpu\t\t: yes\nfpu_exception\t: yes\ncpuid level\t: 22\nwp\t\t: yes\nflags\t\t: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss ht syscall nx pdpe1gb rdtscp lm constant_tsc rep_good nopl xtopology nonstop_tsc cpuid tsc_known_freq pni pclmulqdq ssse3 fma cx16 pcid sse4_1 sse4_2 x2apic movbe popcnt aes xsave avx f16c rdrand hypervisor lahf_lm abm 3dnowprefetch invpcid_single ssbd ibrs ibpb stibp ibrs_enhanced fsgsbase tsc_adjust bmi1 hle avx2 smep bmi2 erms invpcid rtm mpx avx512f avx512dq rdseed adx smap clflushopt clwb avx512cd avx512bw avx512vl xsaveopt xsavec xgetbv1 xsaves arat avx512_vnni md_clear arch_capabilities\nbugs\t\t: spectre_v1 spectre_v2 spec_store_bypass swapgs taa itlb_multihit srbds mmio_stale_data retbleed gds\nbogomips\t: 4400.00\nclflush size\t: 64\ncache_alignment\t: 64\naddress sizes\t: 46 bits physical, 48 bits virtual\npower management:\n", "owner": "root", "perm": "-r--r--r--"},
            "/proc/meminfo": {"type": "file", "content": "MemTotal:        8167848 kB\nMemFree:         323456 kB\nMemAvailable:    6543210 kB\nBuffers:          12345 kB\nCached:          234567 kB\nSwapTotal:       2097148 kB\nSwapFree:        2097148 kB", "owner": "root", "perm": "-r--r--r--"},
            "/proc/version": {"type": "file", "content": "Linux version 5.15.0-91-generic (buildd@lcy02-amd64-001) (gcc (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0, GNU ld (GNU Binutils for Ubuntu) 2.38) #101-Ubuntu SMP Tue Nov 14 13:30:08 UTC 2023", "owner": "root", "perm": "-r--r--r--"},
            "/proc/uptime": {"type": "file", "content": "12345.67 23456.78", "owner": "root", "perm": "-r--r--r--"},
            "/tmp": {"type": "dir", "content": [], "owner": "root", "perm": "drwxrwxrwt"},
            "/home": {"type": "dir", "content": ["user"], "owner": "root", "perm": "drwxr-xr-x"},
            "/home/user": {"type": "dir", "content": ["user.txt", ".bashrc", ".profile"], "owner": "user", "perm": "drwxr-xr-x"},
            "/home/user/user.txt": {"type": "file", "content": "User data here", "owner": "user", "perm": "-rw-r--r--"},
            "/var": {"type": "dir", "content": ["log", "www", "lib", "cache"], "owner": "root", "perm": "drwxr-xr-x"},
            "/var/log": {"type": "dir", "content": ["syslog", "auth.log", "kern.log", "dpkg.log", "bootstrap.log", "alternatives.log"], "owner": "root", "perm": "drwxr-xr-x"},
            "/var/log/syslog": {"type": "file", "content": "Feb 15 12:00:01 ubuntu-server systemd[1]: Started Session 1 of user root.\nFeb 15 12:05:00 ubuntu-server CRON[123]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)", "owner": "syslog", "perm": "-rw-r-----"},
            "/var/log/auth.log": {"type": "file", "content": "Feb 15 12:00:01 ubuntu-server sshd[1234]: Accepted password for root from 192.168.1.100 port 55555 ssh2\nFeb 15 12:00:01 ubuntu-server systemd-logind[900]: New session 1 of user root.", "owner": "syslog", "perm": "-rw-r-----"},
            "/var/www": {"type": "dir", "content": ["html"], "owner": "www-data", "perm": "drwxr-xr-x"},
            "/var/www/html": {"type": "dir", "content": ["index.html"], "owner": "www-data", "perm": "drwxr-xr-x"},
            "/var/www/html/index.html": {"type": "file", "content": "<!DOCTYPE html>\n<html>\n<head>\n<title>Welcome to nginx!</title>\n</head>\n<body>\n<h1>Welcome to nginx!</h1>\n<p>If you see this page, the nginx web server is successfully installed and working.</p>\n</body>\n</html>", "owner": "www-data", "perm": "-rw-r--r--"},
            "/bin": {"type": "dir", "content": ["bash", "ls", "cat", "cp", "mv", "rm", "ps", "grep", "wget", "curl", "tar", "chmod", "chown", "mkdir", "touch", "id", "whoami", "uname", "pwd", "echo"], "owner": "root", "perm": "drwxr-xr-x"},
            "/usr": {"type": "dir", "content": ["bin", "sbin", "lib", "local", "share", "include"], "owner": "root", "perm": "drwxr-xr-x"},
            "/usr/bin": {"type": "dir", "content": ["python3", "perl", "gcc", "make", "git", "vim", "nano", "sudo"], "owner": "root", "perm": "drwxr-xr-x"},
        }
        self.cwd = "/root"

    def resolve_path(self, path):
        if path == "/":
            return "/"
        elif path.startswith("/"):
            parts = path.split("/")
            clean_parts = [p for p in parts if p and p != "."]
            
            # Handle ..
            final_parts = []
            for p in clean_parts:
                if p == "..":
                    if final_parts:
                        final_parts.pop()
                else:
                    final_parts.append(p)
            
            return "/" + "/".join(final_parts)
        else:
            # Relative path
            if self.cwd == "/":
                return self.resolve_path(f"/{path}")
            else:
                return self.resolve_path(f"{self.cwd}/{path}")

    def get_parent_dir(self, path):
        resolved = self.resolve_path(path)
        if resolved == "/":
            return "/"
        return "/".join(resolved.split("/")[:-1]) or "/"

    def get_name(self, path):
        resolved = self.resolve_path(path)
        if resolved == "/":
            return ""
        return resolved.split("/")[-1]

    def exists(self, path):
        return self.resolve_path(path) in self.fs

    def is_dir(self, path):
        resolved = self.resolve_path(path)
        return resolved in self.fs and self.fs[resolved]["type"] == "dir"

    def is_file(self, path):
        resolved = self.resolve_path(path)
        return resolved in self.fs and self.fs[resolved]["type"] == "file"

    def list_dir(self, path):
        resolved = self.resolve_path(path)
        if self.is_dir(resolved):
            return self.fs[resolved]["content"]
        return None

    def get_file_content(self, path):
        resolved = self.resolve_path(path)
        if self.is_file(resolved):
            return self.fs[resolved]["content"]
        return None

    def change_dir(self, path):
        resolved = self.resolve_path(path)
        if self.is_dir(resolved):
            self.cwd = resolved
            return True
        return False

    def mk_dir(self, path):
        resolved = self.resolve_path(path)
        if self.exists(resolved):
            return False, "File exists"
        
        parent = self.get_parent_dir(resolved)
        name = self.get_name(resolved)
        
        if not self.is_dir(parent):
            return False, "No such file or directory"
        
        # Add to parent content
        self.fs[parent]["content"].append(name)
        
        # Create dir entry
        self.fs[resolved] = {
            "type": "dir",
            "content": [],
            "owner": "root",
            "perm": "drwxr-xr-x"
        }
        return True, ""

    def write_file(self, path, content, append=False):
        resolved = self.resolve_path(path)
        parent = self.get_parent_dir(resolved)
        name = self.get_name(resolved)
        
        if not self.is_dir(parent):
            return False, "No such file or directory"

        if self.exists(resolved):
            if self.is_dir(resolved):
                 return False, "Is a directory"
            if append:
                self.fs[resolved]["content"] += content
            else:
                self.fs[resolved]["content"] = content
        else:
            # Create new file
            self.fs[parent]["content"].append(name)
            self.fs[resolved] = {
                "type": "file",
                "content": content,
                "owner": "root",
                "perm": "-rw-r--r--"
            }
        return True, ""
    
    def remove(self, path, recursive=False):
        resolved = self.resolve_path(path)
        if not self.exists(resolved):
            return False, "No such file or directory"
        
        if self.is_dir(resolved):
            if not recursive:
                 # Check if empty
                 if self.fs[resolved]["content"]:
                      return False, "Directory not empty"
        
        # Remove from parent
        parent = self.get_parent_dir(resolved)
        name = self.get_name(resolved)
        if name in self.fs[parent]["content"]:
             self.fs[parent]["content"].remove(name)
        
        # Remove entry (and children if recursive - simplistic implementation)
        # For a full recursive remove we'd need to walk children, but for a honeypot,
        # simply removing the keys starting with the path is often enough or we can leave them orphaned
        # as they won't be reachable via directory traversal from root.
        del self.fs[resolved]
        
        # Cleanup orphaned children (simple)
        keys_to_remove = [k for k in self.fs.keys() if k.startswith(resolved + "/")]
        for k in keys_to_remove:
            del self.fs[k]
            
        return True, ""

    def copy(self, src, dest, recursive=False):
        src_resolved = self.resolve_path(src)
        dest_resolved = self.resolve_path(dest)
        
        if not self.exists(src_resolved):
            return False, f"cp: cannot stat '{src}': No such file or directory"
            
        if self.is_dir(src_resolved) and not recursive:
             return False, f"cp: -r not specified; omitting directory '{src}'"
        
        # If dest is dir, append src name
        if self.is_dir(dest_resolved):
            dest_resolved = self.resolve_path(os.path.join(dest, self.get_name(src_resolved)))
        
        # Simple file copy
        if self.is_file(src_resolved):
            content = self.fs[src_resolved]["content"]
            result, msg = self.write_file(dest_resolved, content)
            if not result:
                return False, f"cp: {msg}"
            return True, ""
            
        # Recursive dir copy (simplified: just one level for demo or basic recursion)
        # TODO: Implement full recursion if needed.
        return True, ""
        
    def move(self, src, dest):
        # Implementation of mv is similar to copy+remove
        if self.copy(src, dest, recursive=True):
             self.remove(src, recursive=True)
             return True, ""
        return False, "Move failed"
