import re
import requests
import os

SOURCE_URL1 = "https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/master/adblock-for-dnsmasq.conf"
SOURCE_URL2 = "https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockdns.txt"
OUTPUT_FILE = "rules-2.txt"

def extract_domains_from_dnsmasq(content):
    """解析第一个源格式：address=/domain/"""
    domains = set()
    for line in content.splitlines():
        if line.startswith('#'):
            continue
        match = re.match(r'address=/(.+)/$', line.strip())
        if match:
            domains.add(match.group(1))
    return domains

def extract_domains_from_adblock(content):
    """解析第二个源格式：||domain^"""
    domains = set()
    for line in content.splitlines():
        if line.startswith(('!', '#')) or '##' in line:
            continue
        match = re.match(r'^\|\|([a-z0-9_.-]+)\^$', line.strip())
        if match:
            domains.add(match.group(1))
    return domains

def merge_rules():
    # 下载第一个规则源
    try:
        response1 = requests.get(SOURCE_URL1, timeout=30)
        response1.raise_for_status()
        domains1 = extract_domains_from_dnsmasq(response1.text)
    except Exception as e:
        print(f"Error downloading source1: {str(e)}")
        domains1 = set()
    
    # 下载第二个规则源
    try:
        response2 = requests.get(SOURCE_URL2, timeout=30)
        response2.raise_for_status()
        domains2 = extract_domains_from_adblock(response2.text)
    except Exception as e:
        print(f"Error downloading source2: {str(e)}")
        domains2 = set()
    
    # 合并并去重
    all_domains = domains1.union(domains2)
    
    # 按域名排序（二级和三级域名分组）
    def domain_key(domain):
        parts = domain.split('.')
        return tuple(reversed(parts)), domain
    
    sorted_domains = sorted(all_domains, key=domain_key)
    
    # 写入结果文件
    with open(OUTPUT_FILE, 'w') as f:
        f.write("# Merged adblock rules from two sources\n")
        f.write(f"# Source1: {SOURCE_URL1}\n")
        f.write(f"# Source2: {SOURCE_URL2}\n")
        f.write(f"# Total unique domains: {len(sorted_domains)}\n\n")
        
        for domain in sorted_domains:
            f.write(f"0.0.0.0 {domain}\n")
    
    return len(sorted_domains)

if __name__ == "__main__":
    count = merge_rules()
    print(f"Generated {count} unique domains in {OUTPUT_FILE}")
