import re
import requests

SOURCE_URL = "https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/master/adblock-for-dnsmasq.conf"
OUTPUT_FILE = "rules-1.txt"

def convert_rules():
    try:
        # 下载规则文件
        response = requests.get(SOURCE_URL, timeout=30)
        response.raise_for_status()
        
        # 处理内容
        hosts_entries = []
        for line in response.text.splitlines():
            if line.startswith('#'):  # 跳过注释行
                continue
            match = re.match(r'address=/(.+)/$', line.strip())
            if match:
                hosts_entries.append(f"0.0.0.0 {match.group(1)}")
        
        # 写入文件
        with open(OUTPUT_FILE, 'w') as f:
            f.write("# Generated hosts rules from anti-AD\n")
            f.write(f"# Total domains: {len(hosts_entries)}\n\n")
            f.write("\n".join(hosts_entries))
            
        return len(hosts_entries)
    except Exception as e:
        print(f"Error: {str(e)}")
        return 0

if __name__ == "__main__":
    count = convert_rules()
    print(f"Generated {count} rules in {OUTPUT_FILE}")
