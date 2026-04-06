import tkinter as tk
from tkinter import scrolledtext, messagebox
from tkinter import ttk
import socket
import requests
import whois
import ssl
import threading
import dns.resolver
import os
from datetime import datetime
import re

class CyberRecon(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CyberRecon - Advanced OSINT Tool")
        self.geometry("1100x800")
        self.configure(bg="#0a0f1a")

        self.build_ui()

        if not os.path.exists("Reports"):
            os.makedirs("Reports")

    def build_ui(self):
        title = tk.Label(self, text="⚡ CyberRecon - Advanced OSINT Recon Tool",
                         font=("Consolas", 22, "bold"),
                         fg="cyan", bg="#0a0f1a")
        title.pack(pady=15)

        self.target_entry = tk.Entry(self, width=65, font=("Segoe UI", 14))
        self.target_entry.pack(pady=8)
        self.target_entry.insert(0, "example.com")

        self.scan_btn = tk.Button(self, text="🚀 START SCAN",
                                  command=self.start_scan,
                                  bg="cyan", fg="black",
                                  font=("Segoe UI", 14, "bold"),
                                  width=22)
        self.scan_btn.pack(pady=8)

        self.status_label = tk.Label(self, text="Status: Idle",
                                     fg="white", bg="#0a0f1a",
                                     font=("Segoe UI", 12))
        self.status_label.pack(pady=6)

        self.progress = ttk.Progressbar(self, orient="horizontal",
                                        length=450, mode="indeterminate")
        self.progress.pack(pady=8)

        self.output = scrolledtext.ScrolledText(self, width=135, height=34,
                                                bg="black", fg="lime",
                                                font=("Consolas", 11))
        self.output.pack(padx=12, pady=12)

    def log(self, text):
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        if hasattr(self, 'report_file'):
            self.report_file.write(text + "\n")

    def clean_target(self, target):
        target = target.replace("https://", "").replace("http://", "")
        return target.split("/")[0]

    def start_scan(self):
        target = self.target_entry.get().strip()
        if not target:
            messagebox.showwarning("Warning", "Enter a valid domain")
            return

        target = self.clean_target(target)

        self.output.delete(1.0, tk.END)

        self.scan_btn.config(state="disabled")
        self.status_label.config(text="Status: Scanning...")
        self.progress.start(10)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"Reports/{target}_{timestamp}.txt"
        self.report_file = open(report_filename, "w", encoding="utf-8")

        threading.Thread(target=self.scan, args=(target,), daemon=True).start()

    def finish_scan_ui(self):
        self.progress.stop()
        self.scan_btn.config(state="normal")
        self.status_label.config(text="Status: Completed ✅")

    def get_ip_info(self, ip):
        try:
            return requests.get(f"https://ipinfo.io/{ip}/json", timeout=5).json()
        except:
            return {}

    def extract_emails(self, text):
        return set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text))

    def security_header_check(self, headers):
        self.log("\n[+] HTTP Security Headers Check:")

        security_headers = [
            "Content-Security-Policy",
            "Strict-Transport-Security",
            "X-Frame-Options",
            "X-Content-Type-Options",
            "X-XSS-Protection",
            "Referrer-Policy",
            "Permissions-Policy"
        ]

        for header in security_headers:
            if header in headers:
                self.log(f"✅ {header}: PRESENT")
            else:
                self.log(f"❌ {header}: MISSING")

    # 🔥 ADVANCED PORT SCAN
    def port_scan(self, target):
        self.log("\n[+] Common Ports Scan:")

        ports = [
            21,22,23,25,53,80,110,135,139,143,443,445,
            1433,1521,2049,3306,3389,5432,5900,6379,
            8080,8443,8888,9000
        ]

        for port in ports:
            try:
                s = socket.socket()
                s.settimeout(1)
                if s.connect_ex((target, port)) == 0:
                    self.log(f"OPEN PORT: {port}")
                s.close()
            except:
                pass

    # 🔥 ADVANCED SUBDOMAIN ENUMERATION
    def subdomain_scan(self, target):
        self.log("\n[+] Subdomain Enumeration:")

        subdomains = [
            "www","mail","ftp","dev","test","api","admin","blog",
            "shop","secure","portal","staging","vpn","web","app",
            "beta","dashboard","support","m","mobile"
        ]

        found = []

        for sub in subdomains:
            domain = f"{sub}.{target}"
            try:
                socket.gethostbyname(domain)
                self.log(f"FOUND: {domain}")
                found.append(domain)
            except:
                pass

        if not found:
            self.log("No subdomains found.")

    def scan(self, target):
        try:
            self.log("="*80)
            self.log(f"Scanning Target: {target}")
            self.log("="*80)

            ip = socket.gethostbyname(target)
            self.log(f"[+] IP Address: {ip}")

            # IP Info
            self.log("\n[+] IP Location Info:")
            ip_info = self.get_ip_info(ip)
            for k in ["city","region","country","org"]:
                self.log(f"{k}: {ip_info.get(k,'N/A')}")

            # WHOIS
            self.log("\n[+] WHOIS Info:")
            try:
                d = whois.whois(target)
                self.log(f"Registrar: {d.registrar}")
                self.log(f"Creation: {d.creation_date}")
            except Exception as e:
                self.log(f"WHOIS Error: {e}")

            # DNS
            self.log("\n[+] DNS Records:")
            for rtype in ["A","MX","NS","TXT","CNAME"]:
                try:
                    answers = dns.resolver.resolve(target, rtype)
                    for r in answers:
                        self.log(f"{rtype}: {r}")
                except:
                    pass

            # Website Info
            self.log("\n[+] Website Info:")
            try:
                r = requests.get(f"http://{target}", timeout=5)
                self.log(f"Status Code: {r.status_code}")

                # Security headers
                self.security_header_check(r.headers)

                emails = self.extract_emails(r.text)
                if emails:
                    self.log("\n[+] Emails Found:")
                    for e in emails:
                        self.log(e)

                self.log("\n[+] Headers:")
                for k,v in r.headers.items():
                    self.log(f"{k}: {v}")

            except Exception as e:
                self.log(f"HTTP Error: {e}")

            # SSL Info
            self.log("\n[+] SSL Info:")
            try:
                ctx = ssl.create_default_context()
                with socket.create_connection((target,443)) as sock:
                    with ctx.wrap_socket(sock, server_hostname=target) as ssock:
                        cert = ssock.getpeercert()
                        self.log(f"Issuer: {cert['issuer']}")
            except Exception as e:
                self.log(f"SSL Error: {e}")

            # 🔥 PORT SCAN
            self.port_scan(target)

            # 🔥 SUBDOMAIN SCAN
            self.subdomain_scan(target)

            self.log("\nScan Completed ✅")
            self.report_file.close()
            self.after(0, self.finish_scan_ui)

        except Exception as e:
            self.log(f"[ERROR] {e}")
            try:
                self.report_file.close()
            except:
                pass
            self.after(0, self.finish_scan_ui)


if __name__ == "__main__":
    app = CyberRecon()
    app.mainloop()