"""
Computer Diagnostics Script

Run comprehensive diagnostics on your computer.
"""

import json
from jarvis.skills.computer_diagnostics import ComputerDiagnosticsSkill


def print_section(title: str):
    """Print section header."""
    print()
    print("="*60)
    print(f"  {title}")
    print("="*60)
    print()


def format_bytes_to_gb(bytes_val):
    """Convert bytes to GB."""
    return round(bytes_val / (1024**3), 2)


def main():
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║                                                          ║")
    print("║         JARVIS Computer Diagnostics Report              ║")
    print("║                                                          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    skill = ComputerDiagnosticsSkill()
    
    # Run full diagnostic scan
    print()
    print("🔍 Running comprehensive system scan...")
    print()
    
    result = skill.execute(scan_type="full")
    
    if not result.success:
        print(f"❌ Diagnostic scan failed: {result.error_message}")
        return
    
    data = result.result
    
    # System Information
    print_section("💻 SYSTEM INFORMATION")
    sys_info = data.get("system", {})
    print(f"  Operating System:  {sys_info.get('os')} {sys_info.get('os_release')}")
    print(f"  OS Version:        {sys_info.get('os_version')}")
    print(f"  Architecture:      {sys_info.get('architecture')}")
    print(f"  Hostname:          {sys_info.get('hostname')}")
    print(f"  Python Version:    {sys_info.get('python_version')}")
    
    # CPU Information
    print_section("🖥️  CPU INFORMATION")
    cpu_info = data.get("cpu", {})
    print(f"  Processor:         {sys_info.get('processor')}")
    print(f"  CPU Cores:         {cpu_info.get('cores')}")
    if cpu_info.get('details'):
        print(f"\n  Details:")
        for line in cpu_info['details'].split('\n')[:3]:
            if line.strip():
                print(f"    {line.strip()}")
    
    # Memory Information
    print_section("💾 MEMORY INFORMATION")
    mem_info = data.get("memory", {})
    if mem_info:
        print(f"  Total RAM:         {mem_info.get('total_gb', 'N/A')} GB")
        print(f"  Used RAM:          {mem_info.get('used_gb', 'N/A')} GB")
        print(f"  Free RAM:          {mem_info.get('free_gb', 'N/A')} GB")
        print(f"  Usage:             {mem_info.get('usage_percent', 'N/A')}%")
        
        # Visual bar
        if 'usage_percent' in mem_info:
            usage = mem_info['usage_percent']
            bar_length = 40
            filled = int((usage / 100) * bar_length)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"  [{bar}] {usage}%")
    else:
        print("  Memory information not available")
    
    # Disk Information
    print_section("💿 DISK INFORMATION")
    disk_info = data.get("disk", {})
    disks = disk_info.get("disks", [])
    if disks:
        for disk in disks:
            print(f"  Drive {disk['drive']}")
            print(f"    Filesystem:      {disk['filesystem']}")
            print(f"    Total:           {disk['total_gb']} GB")
            print(f"    Used:            {disk['used_gb']} GB")
            print(f"    Free:            {disk['free_gb']} GB")
            print(f"    Usage:           {disk['usage_percent']}%")
            
            # Visual bar
            usage = disk['usage_percent']
            bar_length = 40
            filled = int((usage / 100) * bar_length)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            # Color based on usage
            if usage > 90:
                status = "🔴 CRITICAL"
            elif usage > 75:
                status = "🟡 WARNING"
            else:
                status = "🟢 HEALTHY"
            
            print(f"    [{bar}] {status}")
            print()
    else:
        print("  No disk information available")
    
    # GPU Information
    print_section("🎮 GPU INFORMATION")
    gpu_info = data.get("gpu", {})
    if gpu_info.get('nvidia'):
        print(f"  NVIDIA GPU:        {gpu_info['nvidia']}")
    elif gpu_info.get('details'):
        print("  GPU Details:")
        for line in gpu_info['details'].split('\n')[:3]:
            if line.strip():
                print(f"    {line.strip()}")
    else:
        print("  No dedicated GPU detected")
    
    # Network Information
    print_section("🌐 NETWORK STATUS")
    net_info = data.get("network", {})
    internet = net_info.get("internet_connected", False)
    dns = net_info.get("dns_working", False)
    
    print(f"  Internet:          {'🟢 Connected' if internet else '🔴 Disconnected'}")
    print(f"  DNS:               {'🟢 Working' if dns else '🔴 Not Working'}")
    
    # Performance Metrics
    print_section("⚡ PERFORMANCE METRICS")
    perf_info = data.get("performance", {})
    if perf_info:
        if 'cpu_usage_percent' in perf_info:
            cpu_usage = perf_info['cpu_usage_percent']
            print(f"  CPU Usage:         {cpu_usage}%")
            
            # Visual bar
            bar_length = 40
            filled = int((cpu_usage / 100) * bar_length)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"  [{bar}]")
        
        if 'process_count' in perf_info:
            print(f"  Running Processes: {perf_info['process_count']}")
    else:
        print("  Performance metrics not available")
    
    # Security Status
    print_section("🔒 SECURITY STATUS")
    sec_info = data.get("security", {})
    if sec_info:
        antivirus = sec_info.get("antivirus", "unknown")
        firewall = sec_info.get("firewall", "unknown")
        
        av_status = "🟢 Enabled" if antivirus == "enabled" else "🔴 Disabled"
        fw_status = "🟢 Enabled" if firewall == "enabled" else "🔴 Disabled"
        
        print(f"  Antivirus:         {av_status}")
        print(f"  Firewall:          {fw_status}")
    else:
        print("  Security status not available")
    
    # Software Information
    print_section("📦 INSTALLED SOFTWARE")
    soft_info = data.get("software", {})
    installed = soft_info.get("installed", [])
    count = soft_info.get("count", 0)
    
    if installed:
        print(f"  Total Programs:    {count}")
        print()
        print("  Recent installations:")
        for i, prog in enumerate(installed[:5], 1):
            print(f"    {i}. {prog}")
    else:
        print("  Software list not available")
    
    # Summary
    print_section("📊 HEALTH SUMMARY")
    
    # Calculate health score
    health_score = 100
    issues = []
    
    # Check memory usage
    if mem_info.get('usage_percent', 0) > 90:
        health_score -= 15
        issues.append("High memory usage (>90%)")
    elif mem_info.get('usage_percent', 0) > 75:
        health_score -= 5
        issues.append("Elevated memory usage (>75%)")
    
    # Check disk usage
    for disk in disks:
        if disk['usage_percent'] > 90:
            health_score -= 15
            issues.append(f"Disk {disk['drive']} critically full (>90%)")
        elif disk['usage_percent'] > 75:
            health_score -= 5
            issues.append(f"Disk {disk['drive']} getting full (>75%)")
    
    # Check internet
    if not internet:
        health_score -= 10
        issues.append("No internet connection")
    
    # Check security
    if sec_info.get("antivirus") == "disabled":
        health_score -= 20
        issues.append("Antivirus is disabled")
    if sec_info.get("firewall") == "disabled":
        health_score -= 10
        issues.append("Firewall is disabled")
    
    # Display health score
    if health_score >= 90:
        status = "🟢 EXCELLENT"
        emoji = "😊"
    elif health_score >= 75:
        status = "🟡 GOOD"
        emoji = "🙂"
    elif health_score >= 60:
        status = "🟠 FAIR"
        emoji = "😐"
    else:
        status = "🔴 NEEDS ATTENTION"
        emoji = "😟"
    
    print(f"  Overall Health:    {health_score}/100 {status} {emoji}")
    print()
    
    if issues:
        print("  Issues Found:")
        for issue in issues:
            print(f"    ⚠️  {issue}")
    else:
        print("  ✅ No issues detected!")
    
    print()
    print("="*60)
    print(f"  Scan completed in {result.execution_time_ms}ms")
    print("="*60)
    print()
    
    # Save report
    report_file = "jarvis_output/diagnostics_report.json"
    import os
    os.makedirs("jarvis_output", exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"📄 Full report saved to: {report_file}")
    print()


if __name__ == "__main__":
    main()
