import sys
import argparse
import subprocess
import os
import time
import random
import threading
import re
import random
from urllib.parse import urlsplit


CURSOR_UP_ONE = '\x1b[1A' 
ERASE_LINE = '\x1b[2K'

intervals = (
    ('h', 3600),
    ('m', 60),
    ('s', 1),
    )
def display_time(seconds, granularity=3):
    result = []
    seconds = seconds + 1
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            result.append("{}{}".format(value, name))
    return ' '.join(result[:granularity])


def terminal_size():
    try:
        rows, columns = subprocess.check_output(['stty', 'size']).split()
        return int(columns)
    except subprocess.CalledProcessError as e:
        return int(20)
    


def url_maker(url):
    if not re.match(r'http(s?)\:', url):
        url = 'http://' + url
    parsed = urlsplit(url)
    host = parsed.netloc
    if host.startswith('www.'):
        host = host[4:]
    return host

def check_internet():
    os.system('ping -c1 github.com > rs_net 2>&1')
    if "0% packet loss" in open('rs_net').read():
        val = 1
    else:
        val = 0
    os.system('rm rs_net > /dev/null 2>&1')
    return val



class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    BADFAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    BG_ERR_TXT  = '\033[41m' 
    BG_HEAD_TXT = '\033[100m'
    BG_ENDL_TXT = '\033[46m'
    BG_CRIT_TXT = '\033[45m'
    BG_HIGH_TXT = '\033[41m'
    BG_MED_TXT  = '\033[43m'
    BG_LOW_TXT  = '\033[44m'
    BG_INFO_TXT = '\033[42m'

    BG_SCAN_TXT_START = '\x1b[6;30;42m'
    BG_SCAN_TXT_END   = '\x1b[0m'  


# Classifies the Vulnerability's Severity
def vul_info(val):
    result =''
    if val == 'c':
        result = bcolors.BG_CRIT_TXT+" critical "+bcolors.ENDC
    elif val == 'h':
        result = bcolors.BG_HIGH_TXT+" high "+bcolors.ENDC
    elif val == 'm':
        result = bcolors.BG_MED_TXT+" medium "+bcolors.ENDC
    elif val == 'l':
        result = bcolors.BG_LOW_TXT+" low "+bcolors.ENDC
    else:
        result = bcolors.BG_INFO_TXT+" info "+bcolors.ENDC
    return result

# Legends
proc_high = bcolors.BADFAIL + "●" + bcolors.ENDC
proc_med  = bcolors.WARNING + "●" + bcolors.ENDC
proc_low  = bcolors.OKGREEN + "●" + bcolors.ENDC

# Links the vulnerability with threat level and remediation database
def vul_remed_info(v1,v2,v3):
    print(bcolors.BOLD+"Vulnerability Threat Level"+bcolors.ENDC)
    print("\t"+vul_info(v2)+" "+bcolors.WARNING+str(tool_resp[v1][0])+bcolors.ENDC)
    print(bcolors.BOLD+"Vulnerability Definition"+bcolors.ENDC)
    print("\t"+bcolors.BADFAIL+str(tools_fix[v3-1][1])+bcolors.ENDC)
    print(bcolors.BOLD+"Vulnerability Remediation"+bcolors.ENDC)
    print("\t"+bcolors.OKGREEN+str(tools_fix[v3-1][2])+bcolors.ENDC)


# securify Help Context
def helper():
        print(bcolors.OKBLUE+"Information:"+bcolors.ENDC)
        print("------------")
        print("\t./securify.py example.com: Scans the domain example.com.")
        print(bcolors.OKBLUE+"Legends:"+bcolors.ENDC)
        print("--------")
        print("\t["+proc_high+"]: Scan process may take longer times (not predictable).")
        print("\t["+proc_med+"]: Scan process may take less than 10 minutes.")
        print("\t["+proc_low+"]: Scan process may take less than a minute or two.")
        print(bcolors.OKBLUE+"Vulnerability Information:"+bcolors.ENDC)
        print("--------------------------")
        print("\t"+vul_info('c')+": Requires immediate attention as it may lead to compromise or service unavailability.")
        print("\t"+vul_info('h')+"    : May not lead to an immediate compromise, but there are considerable chances for probability.")
        print("\t"+vul_info('m')+"  : Attacker may correlate multiple vulnerabilities of this type to launch a sophisticated attack.")
        print("\t"+vul_info('l')+"     : Not a serious issue, but it is recommended to tend to the finding.")
        print("\t"+vul_info('i')+"    : Not classified as a vulnerability, simply an useful informational alert to be considered.\n")


# Clears Line
def clear():
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K") 

# securify Logo
def logo():
    print(bcolors.OKBLUE)
    logo_ascii = """
                ███████╗███████╗ ██████╗██╗   ██╗██████╗ ██╗███████╗██╗   ██╗
                ██╔════╝██╔════╝██╔════╝██║   ██║██╔══██╗██║██╔════╝╚██╗ ██╔╝
                ███████╗█████╗  ██║     ██║   ██║██████╔╝██║█████╗   ╚████╔╝ 
                ╚════██║██╔══╝  ██║     ██║   ██║██╔══██╗██║██╔══╝    ╚██╔╝  
                ███████║███████╗╚██████╗╚██████╔╝██║  ██║██║██║        ██║   
                ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝        ╚═╝   
    """
    print(logo_ascii)
    print(bcolors.ENDC)






tool_names = [
                #1
                ["host","Host - Checks for existence of IPV6 address.","host"],

                #2
                ["aspnet_config_err","ASP.Net Misconfiguration - Checks for ASP.Net Misconfiguration.","wget"],

                #3
                ["wp_check","WordPress Checker - Checks for WordPress Installation.","wget"],

                #4
                ["drp_check", "Drupal Checker - Checks for Drupal Installation.","wget"],

                #5
                ["joom_check", "Joomla Checker - Checks for Joomla Installation.","wget"],

                #6
                ["uniscan","Uniscan - Checks for robots.txt & sitemap.xml","uniscan"],

                #7
                ["wafw00f","Wafw00f - Checks for Application Firewalls.","wafw00f"],

                #8
                ["nmap","Nmap - Fast Scan [Only Few Port Checks]","nmap"],

                #9
                ["theHarvester","The Harvester - Scans for emails using Google's passive search.","theHarvester"],   

                #10
                ["whois","Whois - Checks for Administrator's Contact Information.","whois"],

                #11
                ["nmap_header","Nmap [XSS Filter Check] - Checks if XSS Protection Header is present.","nmap"],

                #12
                ["sslyze_hbleed","SSLyze - Checks only for Heartbleed Vulnerability.","sslyze"],

                #13
                ["nmap_hbleed","Nmap [Heartbleed] - Checks only for Heartbleed Vulnerability.","nmap"],

                #14
                ["nmap_poodle","Nmap [POODLE] - Checks only for Poodle Vulnerability.","nmap"],

                #15
                ["nmap_ccs","Nmap [OpenSSL CCS Injection] - Checks only for CCS Injection.","nmap"],

                #16
                ["nmap_freak","Nmap [FREAK] - Checks only for FREAK Vulnerability.","nmap"],

                #17
                ["nmap_logjam","Nmap [LOGJAM] - Checks for LOGJAM Vulnerability.","nmap"],

                #18
                ["dirb","DirB - Brutes the target for Open Directories.","dirb"],

                #19
                ["xsser","XSSer - Checks for Cross-Site Scripting [XSS] Attacks.","xsser"],


                #20
                ["dnsenum_zone_transfer","DNSEnum - Attempts Zone Transfer.","dnsenum"],

                #21
                ["fierce_brute_subdomains","Fierce Subdomains Bruter - Brute Forces Subdomain Discovery.","fierce"],

                #22
                ["dmitry_email","DMitry - Passively Harvests Emails from the Domain.","dmitry"],

                #23
                ["dmitry_subdomains","DMitry - Passively Harvests Subdomains from the Domain.","dmitry"],

                #24
                ["nmap_telnet","Nmap [TELNET] - Checks if TELNET service is running.","nmap"],

                #25
                ["nmap_ftp","Nmap [FTP] - Checks if FTP service is running.","nmap"],

                #26
                ["nmap_stuxnet","Nmap [STUXNET] - Checks if the host is affected by STUXNET Worm.","nmap"],

                #27
                ["webdav","WebDAV - Checks if WEBDAV enabled on Home directory.","davtest"],

                #28
                ["uniscan_filebrute","Uniscan - Brutes for Filenames on the Domain.","uniscan"],

                #29
                ["uniscan_dirbrute", "Uniscan - Brutes Directories on the Domain.","uniscan"],

                #30
                ["uniscan_ministresser", "Uniscan - Stress Tests the Domain.","uniscan"],

                #31
                ["uniscan_rfi","Uniscan - Checks for LFI, RFI and RCE.","uniscan"],

                #32
                ["uniscan_xss","Uniscan - Checks for XSS, SQLi, BSQLi & Other Checks.","uniscan"],

                #33
                ["nikto_xss","Nikto - Checks for Apache Expect XSS Header.","nikto"],

                #34
                ["nikto_subrute","Nikto - Brutes Subdomains.","nikto"],

                #35
                ["nikto_shellshock","Nikto - Checks for Shellshock Bug.","nikto"],

                #36
                ["nikto_internalip","Nikto - Checks for Internal IP Leak.","nikto"],

                #37
                ["nikto_putdel","Nikto - Checks for HTTP PUT DEL.","nikto"],

                #38
                ["nikto_headers","Nikto - Checks the Domain Headers.","nikto"],

                #39
                ["nikto_ms01070","Nikto - Checks for MS10-070 Vulnerability.","nikto"],

                #40
                ["nikto_servermsgs","Nikto - Checks for Server Issues.","nikto"],

                #41
                ["nikto_outdated","Nikto - Checks if Server is Outdated.","nikto"],

                #42
                ["nikto_httpoptions","Nikto - Checks for HTTP Options on the Domain.","nikto"],

                #43
                ["nikto_cgi","Nikto - Enumerates CGI Directories.","nikto"],

                #44
                ["nikto_ssl","Nikto - Performs SSL Checks.","nikto"],

                #45
                ["nikto_sitefiles","Nikto - Checks for any interesting files on the Domain.","nikto"],

                #46
                ["nikto_paths","Nikto - Checks for Injectable Paths.","nikto"],


                #47
                ["nmap_sqlserver","Nmap - Checks for MS-SQL Server DB","nmap"],

                #48
                ["nmap_mysql", "Nmap - Checks for MySQL DB","nmap"],

                #49
                ["nmap_oracle", "Nmap - Checks for ORACLE DB","nmap"],

                #50
                ["nmap_rdp_udp","Nmap - Checks for Remote Desktop Service over UDP","nmap"],

                #51
                ["nmap_rdp_tcp","Nmap - Checks for Remote Desktop Service over TCP","nmap"],

                #52
                ["nmap_full_ps_tcp","Nmap - Performs a Full TCP Port Scan","nmap"],

                #53
                ["nmap_full_ps_udp","Nmap - Performs a Full UDP Port Scan","nmap"],

                #54
                ["nmap_snmp","Nmap - Checks for SNMP Service","nmap"],

                #55
                ["aspnet_elmah_axd","Checks for ASP.net Elmah Logger","wget"],

                #56
                ["nmap_tcp_smb","Checks for SMB Service over TCP","nmap"],

                #57
                ["nmap_udp_smb","Checks for SMB Service over UDP","nmap"],

                #58
                ["wapiti","Wapiti - Checks for SQLi, RCE, XSS and Other Vulnerabilities","wapiti"],

                #59
                ["nmap_iis","Nmap - Checks for IIS WebDAV","nmap"],

                #60
                ["whatweb","WhatWeb - Checks for X-XSS Protection Header","whatweb"],

          
            ]


tool_cmd   = [
                #1
                ["host ",""],

                #2
                ["wget -O /tmp/securify_temp_aspnet_config_err --tries=1 ","/%7C~.aspx"],

                #3
                ["wget -O /tmp/securify_temp_wp_check --tries=1 ","/wp-admin"],

                #4
                ["wget -O /tmp/securify_temp_drp_check --tries=1 ","/user"],

                #5
                ["wget -O /tmp/securify_temp_joom_check --tries=1 ","/administrator"],

                #6
                ["uniscan -e -u ",""],

                #7
                ["wafw00f ",""],

                #8
                ["nmap -F --open -Pn ",""],

                #9
                ["theHarvester -l 50 -b censys -d ",""],


                #10
                ["whois ",""],

                #11
                ["nmap -p80 --script http-security-headers -Pn ",""],


                #12
                ["sslyze --heartbleed ",""],

                #13
                ["nmap -p443 --script ssl-heartbleed -Pn ",""],

                #14
                ["nmap -p443 --script ssl-poodle -Pn ",""],

                #15
                ["nmap -p443 --script ssl-ccs-injection -Pn ",""],

                #16
                ["nmap -p443 --script ssl-enum-ciphers -Pn ",""],

                #17
                ["nmap -p443 --script ssl-dh-params -Pn ",""],

                #18
                ["dirb http://"," -fi"],

                #19
                ["xsser --all=http://",""],

                #20
                ["dnsenum ",""],

                #21
                ["fierce --domain ",""],

                #22
                ["dmitry -e ",""],

                #23
                ["dmitry -s ",""],

                #24
                ["nmap -p23 --open -Pn ",""],

                #25
                ["nmap -p21 --open -Pn ",""],

                #26
                ["nmap --script stuxnet-detect -p445 -Pn ",""],

                #27
                ["davtest -url http://",""],

                #28
                ["uniscan -w -u ",""],

                #29
                ["uniscan -q -u ",""],

                #30
                ["uniscan -r -u ",""],

                #31
                ["uniscan -s -u ",""],

                #32
                ["uniscan -d -u ",""],

                #33
                ["nikto -Plugins 'apache_expect_xss' -host ",""],

                #34
                ["nikto -Plugins 'subdomain' -host ",""],

                #35
                ["nikto -Plugins 'shellshock' -host ",""],

                #36
                ["nikto -Plugins 'cookies' -host ",""],

                #37
                ["nikto -Plugins 'put_del_test' -host ",""],

                #38
                ["nikto -Plugins 'headers' -host ",""],

                #39
                ["nikto -Plugins 'ms10-070' -host ",""],

                #40
                ["nikto -Plugins 'msgs' -host ",""],

                #41
                ["nikto -Plugins 'outdated' -host ",""],

                #42
                ["nikto -Plugins 'httpoptions' -host ",""],

                #43
                ["nikto -Plugins 'cgi' -host ",""],

                #44
                ["nikto -Plugins 'ssl' -host ",""],

                #45
                ["nikto -Plugins 'sitefiles' -host ",""],

                #46
                ["nikto -Plugins 'paths' -host ",""],


                #47
                ["nmap -p1433 --open -Pn ",""],

                #48
                ["nmap -p3306 --open -Pn ",""],

                #49
                ["nmap -p1521 --open -Pn ",""],

                #50
                ["nmap -p3389 --open -sU -Pn ",""],

                #51
                ["nmap -p3389 --open -sT -Pn ",""],

                #52
                ["nmap -p1-65535 --open -Pn ",""],

                #53
                ["nmap -p1-65535 -sU --open -Pn ",""],

                #54
                ["nmap -p161 -sU --open -Pn ",""],

                #55
                ["wget -O /tmp/securify_temp_aspnet_elmah_axd --tries=1 ","/elmah.axd"],

                #56
                ["nmap -p445,137-139 --open -Pn ",""],

                #57
                ["nmap -p137,138 --open -Pn ",""],

                #58
                ["wapiti "," -f txt -o securify_temp_wapiti"],

                #59
                ["nmap -p80 --script=http-iis-webdav-vuln -Pn ",""],
                
                #60
                ["whatweb "," -a 1"],
            ]


tool_resp   = [
                #1
                ["Does not have an IPv6 Address. It is good to have one.","i",1],

                #2
                ["ASP.Net is misconfigured to throw server stack errors on screen.","m",2],

                #3
                ["WordPress Installation Found. Check for vulnerabilities corresponds to that version.","i",3],

                #4
                ["Drupal Installation Found. Check for vulnerabilities corresponds to that version.","i",4],

                #5
                ["Joomla Installation Found. Check for vulnerabilities corresponds to that version.","i",5],

                #6
                ["robots.txt/sitemap.xml found. Check those files for any information.","i",6],

                #7
                ["No Web Application Firewall Detected","m",7],

                #8
                ["Some ports are open. Perform a full-scan manually.","l",8],

                #9
                ["Email Addresses Found.","l",9],

                #10
                ["Whois Information Publicly Available.","i",11],

                #11
                ["XSS Protection Filter is Disabled.","m",12],

                #12
                ["HEARTBLEED Vulnerability Found with SSLyze.","h",14],

                #13
                ["HEARTBLEED Vulnerability Found with Nmap.","h",14],

                #14
                ["POODLE Vulnerability Detected.","h",15],

                #15
                ["OpenSSL CCS Injection Detected.","h",16],

                #16
                ["FREAK Vulnerability Detected.","h",17],

                #17
                ["LOGJAM Vulnerability Detected.","h",18],

                #18
                ["Open Directories Found with DirB.","m",26],

                #19
                ["XSSer found XSS vulnerabilities.","c",28],

                #20
                ["Zone Transfer Successful using DNSEnum. Reconfigure DNS immediately.","h",10],

                #21
                ["Found Subdomains with Fierce.","m",31],

                #22
                ["Email Addresses discovered with DMitry.","l",9],

                #23
                ["Subdomains discovered with DMitry.","m",31],

                #24
                ["Telnet Service Detected.","h",32],

                #25
                ["FTP Service Detected.","c",33],

                #26
                ["Vulnerable to STUXNET.","c",34],

                #27
                ["WebDAV Enabled.","m",35],

                #28
                ["Open Files Found with Uniscan.","m",25],

                #29
                ["Open Directories Found with Uniscan.","m",26],

                #30
                ["Vulnerable to Stress Tests.","h",37],

                #31
                ["Uniscan detected possible LFI, RFI or RCE.","h",38],

                #32
                ["Uniscan detected possible XSS, SQLi, BSQLi.","h",39],

                #33
                ["Apache Expect XSS Header not present.","m",12],

                #34
                ["Found Subdomains with Nikto.","m",31],

                #35
                ["Webserver vulnerable to Shellshock Bug.","c",40],

                #36
                ["Webserver leaks Internal IP.","l",41],

                #37
                ["HTTP PUT DEL Methods Enabled.","m",42],

                #38
                ["Some vulnerable headers exposed.","m",43],

                #39
                ["Webserver vulnerable to MS10-070.","h",44],

                #40
                ["Some issues found on the Webserver.","m",30],

                #41
                ["Webserver is Outdated.","h",45],

                #42
                ["Some issues found with HTTP Options.","l",42],

                #43
                ["CGI Directories Enumerated.","l",26],

                #44
                ["Vulnerabilities reported in SSL Scans.","m",29],

                #45
                ["Interesting Files Detected.","m",25],

                #46
                ["Injectable Paths Detected.","l",46],

                #47
                ["MS-SQL DB Service Detected.","l",47],

                #48
                ["MySQL DB Service Detected.","l",47],

                #49
                ["ORACLE DB Service Detected.","l",47],

                #50
                ["RDP Server Detected over UDP.","h",48],

                #51
                ["RDP Server Detected over TCP.","h",48],

                #52
                ["TCP Ports are Open","l",8],

                #53
                ["UDP Ports are Open","l",8],

                #54
                ["SNMP Service Detected.","m",49],

                #55
                ["Elmah is Configured.","m",50],

                #56
                ["SMB Ports are Open over TCP","m",51],

                #57
                ["SMB Ports are Open over UDP","m",51],

                #58
                ["Wapiti discovered a range of vulnerabilities","h",30],

                #59
                ["IIS WebDAV is Enabled","m",35],

                #60
                ["X-XSS Protection is not Present","m",12],




            ]

# Tool Responses (Ends)



# Tool Status (Response Data + Response Code (if status check fails and you still got to push it + Legends + Approx Time + Tool Identification + Bad Responses)
tool_status = [
                #1
                ["has IPv6",1,proc_low," < 15s","ipv6",["not found","has IPv6"]],

                #2
                ["Server Error",0,proc_low," < 30s","asp.netmisconf",["unable to resolve host address","Connection timed out"]],

                #3
                ["wp-login",0,proc_low," < 30s","wpcheck",["unable to resolve host address","Connection timed out"]],

                #4
                ["drupal",0,proc_low," < 30s","drupalcheck",["unable to resolve host address","Connection timed out"]],

                #5
                ["joomla",0,proc_low," < 30s","joomlacheck",["unable to resolve host address","Connection timed out"]],

                #6
                ["[+]",0,proc_low," < 40s","robotscheck",["Use of uninitialized value in unpack at"]],

                #7
                ["No WAF",0,proc_low," < 45s","wafcheck",["appears to be down"]],

                #8
                ["tcp open",0,proc_med," <  2m","nmapopen",["Failed to resolve"]],

                #9
                ["No emails found",1,proc_med," <  3m","harvester",["No hosts found","No emails found"]],

             

                #10
                ["Admin Email:",0,proc_low," < 25s","whois",["No match for domain"]],

                #11
                ["XSS filter is disabled",0,proc_low," < 20s","nmapxssh",["Failed to resolve"]],


                #12
                ["Server is vulnerable to Heartbleed",0,proc_low," < 40s","sslyzehb",["Could not resolve hostname"]],

                #13
                ["VULNERABLE",0,proc_low," < 30s","nmap1",["Failed to resolve"]],

                #14
                ["VULNERABLE",0,proc_low," < 35s","nmap2",["Failed to resolve"]],

                #15
                ["VULNERABLE",0,proc_low," < 35s","nmap3",["Failed to resolve"]],

                #16
                ["VULNERABLE",0,proc_low," < 30s","nmap4",["Failed to resolve"]],

                #17
                ["VULNERABLE",0,proc_low," < 35s","nmap5",["Failed to resolve"]],


                #18
                ["FOUND: 0",1,proc_high," < 35m","dirb",["COULDNT RESOLVE HOST","FOUND: 0"]],

                #19
                ["Could not find any vulnerability!",1,proc_med," <  4m","xsser",["XSSer is not working propertly!","Could not find any vulnerability!"]],

                #20
                ["AXFR record query failed:",1,proc_low," < 45s","dnsenumzt",["NS record query failed:","AXFR record query failed","no NS record for"]],

                #21
                ["Found 0 entries",1,proc_high," < 75m","fierce2",["Found 0 entries","is gimp"]],

                #22
                ["Found 0 E-Mail(s)",1,proc_low," < 30s","dmitry1",["Unable to locate Host IP addr","Found 0 E-Mail(s)"]],

                #23
                ["Found 0 possible subdomain(s)",1,proc_low," < 35s","dmitry2",["Unable to locate Host IP addr","Found 0 possible subdomain(s)"]],

                #24
                ["open",0,proc_low," < 15s","nmaptelnet",["Failed to resolve"]],

                #25
                ["open",0,proc_low," < 15s","nmapftp",["Failed to resolve"]],

                #26
                ["open",0,proc_low," < 20s","nmapstux",["Failed to resolve"]],

                #27
                ["SUCCEED",0,proc_low," < 30s","webdav",["is not DAV enabled or not accessible."]],

                #28
                ["[+]",0,proc_med," <  2m","uniscan2",["Use of uninitialized value in unpack at"]],

                #29
                ["[+]",0,proc_med," <  5m","uniscan3",["Use of uninitialized value in unpack at"]],

                #30
                ["[+]",0,proc_med," <  9m","uniscan4",["Use of uninitialized value in unpack at"]],

                #31
                ["[+]",0,proc_med," <  8m","uniscan5",["Use of uninitialized value in unpack at"]],

                #32
                ["[+]",0,proc_med," <  9m","uniscan6",["Use of uninitialized value in unpack at"]],

                #33
                ["0 item(s) reported",1,proc_low," < 35s","nikto1",["ERROR: Cannot resolve hostname","0 item(s) reported","No web server found","0 host(s) tested"]],

                #34
                ["0 item(s) reported",1,proc_low," < 35s","nikto2",["ERROR: Cannot resolve hostname","0 item(s) reported","No web server found","0 host(s) tested"]],

                #35
                ["0 item(s) reported",1,proc_low," < 35s","nikto3",["ERROR: Cannot resolve hostname","0 item(s) reported","No web server found","0 host(s) tested"]],

                #36
                ["0 item(s) reported",1,proc_low," < 35s","nikto4",["ERROR: Cannot resolve hostname","0 item(s) reported","No web server found","0 host(s) tested"]],

                #37
                ["0 item(s) reported",1,proc_low," < 35s","nikto5",["ERROR: Cannot resolve hostname","0 item(s) reported","No web server found","0 host(s) tested"]],

                #38
                ["0 item(s) reported",1,proc_low," < 35s","nikto6",["ERROR: Cannot resolve hostname","0 item(s) reported","No web server found","0 host(s) tested"]],

                #39
                ["0 item(s) reported",1,proc_low," < 35s","nikto7",["ERROR: Cannot resolve hostname","0 item(s) reported","No web server found","0 host(s) tested"]],

                #40
                ["0 item(s) reported",1,proc_low," < 35s","nikto8",["ERROR: Cannot resolve hostname","0 item(s) reported","No web server found","0 host(s) tested"]],

                #41
                ["0 item(s) reported",1,proc_low," < 35s","nikto9",["ERROR: Cannot resolve hostname","0 item(s) reported","No web server found","0 host(s) tested"]],

                #42
                ["0 item(s) reported",1,proc_low," < 35s","nikto10",["ERROR: Cannot resolve hostname","0 item(s) reported","No web server found","0 host(s) tested"]],

                #43
                ["0 item(s) reported",1,proc_low," < 35s","nikto11",["ERROR: Cannot resolve hostname","0 item(s) reported","No web server found","0 host(s) tested"]],

                #44
                ["0 item(s) reported",1,proc_low," < 35s","nikto12",["ERROR: Cannot resolve hostname","0 item(s) reported","No web server found","0 host(s) tested"]],

                #45
                ["0 item(s) reported",1,proc_low," < 35s","nikto13",["ERROR: Cannot resolve hostname","0 item(s) reported","No web server found","0 host(s) tested"]],

                #46
                ["0 item(s) reported",1,proc_low," < 35s","nikto14","ERROR: Cannot resolve hostname , 0 item(s) reported"],

                #47
                ["open",0,proc_low," < 15s","nmapmssql",["Failed to resolve"]],

                #48
                ["open",0,proc_low," < 15s","nmapmysql",["Failed to resolve"]],

                #49
                ["open",0,proc_low," < 15s","nmaporacle",["Failed to resolve"]],

                #50
                ["open",0,proc_low," < 15s","nmapudprdp",["Failed to resolve"]],

                #51
                ["open",0,proc_low," < 15s","nmaptcprdp",["Failed to resolve"]],

                #52
                ["open",0,proc_high," > 50m","nmapfulltcp",["Failed to resolve"]],

                #53
                ["open",0,proc_high," > 75m","nmapfulludp",["Failed to resolve"]],

                #54
                ["open",0,proc_low," < 30s","nmapsnmp",["Failed to resolve"]],

                #55
                ["Microsoft SQL Server Error Log",0,proc_low," < 30s","elmahxd",["unable to resolve host address","Connection timed out"]],

                #56
                ["open",0,proc_low," < 20s","nmaptcpsmb",["Failed to resolve"]],

                #57
                ["open",0,proc_low," < 20s","nmapudpsmb",["Failed to resolve"]],

                #58
                ["Host:",0,proc_med," < 5m","wapiti",["none"]],

                #59
                ["WebDAV is ENABLED",0,proc_low," < 40s","nmapwebdaviis",["Failed to resolve"]],

                #60
                ["X-XSS-Protection[1",1,proc_med," < 3m","whatweb",["Timed out","Socket error","X-XSS-Protection[1"]],
            ]

# Vulnerabilities and Remediation
tools_fix = [
                    [1, "Not a vulnerability, just an informational alert. The host does not have IPv6 support. IPv6 provides more security as IPSec (responsible for CIA - Confidentiality, Integrity and Availablity) is incorporated into this model. So it is good to have IPv6 Support.",
                            "It is recommended to implement IPv6. More information on how to implement IPv6 can be found from this resource. https://www.cisco.com/c/en/us/solutions/collateral/enterprise/cisco-on-cisco/IPv6-Implementation_CS.html"],
                    [2, "Sensitive Information Leakage Detected. The ASP.Net application does not filter out illegal characters in the URL. The attacker injects a special character (%7C~.aspx) to make the application spit sensitive information about the server stack.",
                            "It is recommended to filter out special charaters in the URL and set a custom error page on such situations instead of showing default error messages. This resource helps you in setting up a custom error page on a Microsoft .Net Application. https://docs.microsoft.com/en-us/aspnet/web-forms/overview/older-versions-getting-started/deploying-web-site-projects/displaying-a-custom-error-page-cs"],
                    [3, "It is not bad to have a CMS in WordPress. There are chances that the version may contain vulnerabilities or any third party scripts associated with it may possess vulnerabilities",
                            "It is recommended to conceal the version of WordPress. This resource contains more information on how to secure your WordPress Blog. https://codex.wordpress.org/Hardening_WordPress"],
                    [4, "It is not bad to have a CMS in Drupal. There are chances that the version may contain vulnerabilities or any third party scripts associated with it may possess vulnerabilities",
                            "It is recommended to conceal the version of Drupal. This resource contains more information on how to secure your Drupal Blog. https://www.drupal.org/docs/7/site-building-best-practices/ensure-that-your-site-is-secure"],
                    [5, "It is not bad to have a CMS in Joomla. There are chances that the version may contain vulnerabilities or any third party scripts associated with it may possess vulnerabilities",
                            "It is recommended to conceal the version of Joomla. This resource contains more information on how to secure your Joomla Blog. https://www.incapsula.com/blog/10-tips-to-improve-your-joomla-website-security.html"],
                    [6, "Sometimes robots.txt or sitemap.xml may contain rules such that certain links that are not supposed to be accessed/indexed by crawlers and search engines. Search engines may skip those links but attackers will be able to access it directly.",
                            "It is a good practice not to include sensitive links in the robots or sitemap files."],
                    [7, "Without a Web Application Firewall, An attacker may try to inject various attack patterns either manually or using automated scanners. An automated scanner may send hordes of attack vectors and patterns to validate an attack, there are also chances for the application to get DoS`ed (Denial of Service)",
                            "Web Application Firewalls offer great protection against common web attacks like XSS, SQLi, etc. They also provide an additional line of defense to your security infrastructure. This resource contains information on web application firewalls that could suit your application. https://www.gartner.com/reviews/market/web-application-firewall"],
                    [8, "Open Ports give attackers a hint to exploit the services. Attackers try to retrieve banner information through the ports and understand what type of service the host is running",
                            "It is recommended to close the ports of unused services and use a firewall to filter the ports wherever necessary. This resource may give more insights. https://security.stackexchange.com/a/145781/6137"],
                    [9, "Chances are very less to compromise a target with email addresses. However, attackers use this as a supporting data to gather information around the target. An attacker may make use of the username on the email address and perform brute-force attacks on not just email servers, but also on other legitimate panels like SSH, CMS, etc with a password list as they have a legitimate name. This is however a shoot in the dark scenario, the attacker may or may not be successful depending on the level of interest",
                            "Since the chances of exploitation is feeble there is no need to take action. Perfect remediation would be choosing different usernames for different services will be more thoughtful."],
                    [10, "Zone Transfer reveals critical topological information about the target. The attacker will be able to query all records and will have more or less complete knowledge about your host.",
                            "Good practice is to restrict the Zone Transfer by telling the Master which are the IPs of the slaves that can be given access for the query. This SANS resource  provides more information. https://www.sans.org/reading-room/whitepapers/dns/securing-dns-zone-transfer-868"],
                    [11, "The email address of the administrator and other information (address, phone, etc) is available publicly. An attacker may use these information to leverage an attack. This may not be used to carry out a direct attack as this is not a vulnerability. However, an attacker makes use of these data to build information about the target.",
                            "Some administrators intentionally would have made this information public, in this case it can be ignored. If not, it is recommended to mask the information. This resource provides information on this fix. http://www.name.com/blog/how-tos/tutorial-2/2013/06/protect-your-personal-information-with-whois-privacy/"],
                    [12, "As the target is lacking this header, older browsers will be prone to Reflected XSS attacks.",
                            "Modern browsers does not face any issues with this vulnerability (missing headers). However, older browsers are strongly recommended to be upgraded."],
                    [13, "This attack works by opening multiple simultaneous connections to the web server and it keeps them alive as long as possible by continously sending partial HTTP requests, which never gets completed. They easily slip through IDS by sending partial requests.",
                            "If you are using Apache Module, `mod_antiloris` would help. For other setup you can find more detailed remediation on this resource. https://www.acunetix.com/blog/articles/slow-http-dos-attacks-mitigate-apache-http-server/"],
                    [14, "This vulnerability seriously leaks private information of your host. An attacker can keep the TLS connection alive and can retrieve a maximum of 64K of data per heartbeat.",
                            "PFS (Perfect Forward Secrecy) can be implemented to make decryption difficult. Complete remediation and resource information is available here. http://heartbleed.com/"],
                    [15, "By exploiting this vulnerability, an attacker will be able gain access to sensitive data in a n encrypted session such as session ids, cookies and with those data obtained, will be able to impersonate that particular user.",
                            "This is a flaw in the SSL 3.0 Protocol. A better remediation would be to disable using the SSL 3.0 protocol. For more information, check this resource. https://www.us-cert.gov/ncas/alerts/TA14-290A"],
                    [16, "This attacks takes place in the SSL Negotiation (Handshake) which makes the client unaware of the attack. By successfully altering the handshake, the attacker will be able to pry on all the information that is sent from the client to server and vice-versa",
                            "Upgrading OpenSSL to latest versions will mitigate this issue. This resource gives more information about the vulnerability and the associated remediation. http://ccsinjection.lepidum.co.jp/"],
                    [17, "With this vulnerability the attacker will be able to perform a MiTM attack and thus compromising the confidentiality factor.",
                            "Upgrading OpenSSL to latest version will mitigate this issue. Versions prior to 1.1.0 is prone to this vulnerability. More information can be found in this resource. https://bobcares.com/blog/how-to-fix-sweet32-birthday-attacks-vulnerability-cve-2016-2183/"],
                    [18, "With the LogJam attack, the attacker will be able to downgrade the TLS connection which allows the attacker to read and modify any data passed over the connection.",
                            "Make sure any TLS libraries you use are up-to-date, that servers you maintain use 2048-bit or larger primes, and that clients you maintain reject Diffie-Hellman primes smaller than 1024-bit. More information can be found in this resource. https://weakdh.org/"],
                    [19, "Allows remote attackers to cause a denial of service (crash), and possibly obtain sensitive information in applications that use OpenSSL, via a malformed ClientHello handshake message that triggers an out-of-bounds memory access.",
                            " OpenSSL versions 0.9.8h through 0.9.8q and 1.0.0 through 1.0.0c are vulnerable. It is recommended to upgrade the OpenSSL version. More resource and information can be found here. https://www.openssl.org/news/secadv/20110208.txt"],
                    [20, "Otherwise termed as BREACH atack, exploits the compression in the underlying HTTP protocol. An attacker will be able to obtain email addresses, session tokens, etc from the TLS encrypted web traffic.",
                            "Turning off TLS compression does not mitigate this vulnerability. First step to mitigation is to disable Zlib compression followed by other measures mentioned in this resource. http://breachattack.com/"],
                    [21, "Otherwise termed as Plain-Text Injection attack, which allows MiTM attackers to insert data into HTTPS sessions, and possibly other types of sessions protected by TLS or SSL, by sending an unauthenticated request that is processed retroactively by a server in a post-renegotiation context.",
                            "Detailed steps of remediation can be found from these resources. https://securingtomorrow.mcafee.com/technical-how-to/tips-securing-ssl-renegotiation/ https://www.digicert.com/news/2011-06-03-ssl-renego/ "],
                    [22, "This vulnerability allows attackers to steal existing TLS sessions from users.",
                            "Better advice is to disable session resumption. To harden session resumption, follow this resource that has some considerable information. https://wiki.crashtest-security.com/display/KB/Harden+TLS+Session+Resumption"],
                    [23, "This has nothing to do with security risks, however attackers may use this unavailability of load balancers as an advantage to leverage a denial of service attack on certain services or on the whole application itself.",
                            "Load-Balancers are highly encouraged for any web application. They improve performance times as well as data availability on during times of server outage. To know more information on load balancers and setup, check this resource. https://www.digitalocean.com/community/tutorials/what-is-load-balancing"],
                    [24, "An attacker can forwarded requests that comes to the legitimate URL or web application to a third party address or to the attacker's location that can serve malware and affect the end user's machine.",
                            "It is highly recommended to deploy DNSSec on the host target. Full deployment of DNSSEC will ensure the end user is connecting to the actual web site or other service corresponding to a particular domain name. For more information, check this resource. https://www.cloudflare.com/dns/dnssec/how-dnssec-works/"],
                    [25, "Attackers may find considerable amount of information from these files. There are even chances attackers may get access to critical information from these files.",
                            "It is recommended to block or restrict access to these files unless necessary."],
                    [26, "Attackers may find considerable amount of information from these directories. There are even chances attackers may get access to critical information from these directories.",
                            "It is recommended to block or restrict access to these directories unless necessary."],
                    [27, "May not be SQLi vulnerable. An attacker will be able to know that the host is using a backend for operation.",
                            "Banner Grabbing should be restricted and access to the services from outside would should be made minimum."],
                    [28, "An attacker will be able to steal cookies, deface web application or redirect to any third party address that can serve malware.",
                            "Input validation and Output Sanitization can completely prevent Cross Site Scripting (XSS) attacks. XSS attacks can be mitigated in future by properly following a secure coding methodology. The following comprehensive resource provides detailed information on fixing this vulnerability. https://www.owasp.org/index.php/XSS_(Cross_Site_Scripting)_Prevention_Cheat_Sheet"],
                    [29, "SSL related vulnerabilities breaks the confidentiality factor. An attacker may perform a MiTM attack, intrepret and eavesdrop the communication.",
                            "Proper implementation and upgraded version of SSL and TLS libraries are very critical when it comes to blocking SSL related vulnerabilities."],
                    [30, "Particular Scanner found multiple vulnerabilities that an attacker may try to exploit the target.",
                            "Refer to RS-Vulnerability-Report to view the complete information of the vulnerability, once the scan gets completed."],
                    [31, "Attackers may gather more information from subdomains relating to the parent domain. Attackers may even find other services from the subdomains and try to learn the architecture of the target. There are even chances for the attacker to find vulnerabilities as the attack surface gets larger with more subdomains discovered.",
                            "It is sometimes wise to block sub domains like development, staging to the outside world, as it gives more information to the attacker about the tech stack. Complex naming practices also help in reducing the attack surface as attackers find hard to perform subdomain bruteforcing through dictionaries and wordlists."],
                    [32, "Through this deprecated protocol, an attacker may be able to perform MiTM and other complicated attacks.",
                            "It is highly recommended to stop using this service and it is far outdated. SSH can be used to replace TELNET. For more information, check this resource https://www.ssh.com/ssh/telnet"],
                    [33, "This protocol does not support secure communication and there are likely high chances for the attacker to eavesdrop the communication. Also, many FTP programs have exploits available in the web such that an attacker can directly crash the application or either get a SHELL access to that target.",
                            "Proper suggested fix is use an SSH protocol instead of FTP. It supports secure communication and chances for MiTM attacks are quite rare."],
                    [34, "The StuxNet is level-3 worm that exposes critical information of the target organization. It was a cyber weapon that was designed to thwart the nuclear intelligence of Iran. Seriously wonder how it got here? Hope this isn't a false positive Nmap ;)",
                            "It is highly recommended to perform a complete rootkit scan on the host. For more information refer to this resource. https://www.symantec.com/security_response/writeup.jsp?docid=2010-071400-3123-99&tabid=3"],
                    [35, "WebDAV is supposed to contain multiple vulnerabilities. In some case, an attacker may hide a malicious DLL file in the WebDAV share however, and upon convincing the user to open a perfectly harmless and legitimate file, execute code under the context of that user",
                            "It is recommended to disable WebDAV. Some critical resource regarding disbling WebDAV can be found on this URL. https://www.networkworld.com/article/2202909/network-security/-webdav-is-bad---says-security-researcher.html"],
                    [36, "Attackers always do a fingerprint of any server before they launch an attack. Fingerprinting gives them information about the server type, content- they are serving, last modification times etc, this gives an attacker to learn more information about the target",
                            "A good practice is to obfuscate the information to outside world. Doing so, the attackers will have tough time understanding the server's tech stack and therefore leverage an attack."],
                    [37, "Attackers mostly try to render web applications or service useless by flooding the target, such that blocking access to legitimate users. This may affect the business of a company or organization as well as the reputation",
                            "By ensuring proper load balancers in place, configuring rate limits and multiple connection restrictions, such attacks can be drastically mitigated."],
                    [38, "Intruders will be able to remotely include shell files and will be able to access the core file system or they will be able to read all the files as well. There are even higher chances for the attacker to remote execute code on the file system.",
                            "Secure code practices will mostly prevent LFI, RFI and RCE attacks. The following resource gives a detailed insight on secure coding practices. https://wiki.sei.cmu.edu/confluence/display/seccode/Top+10+Secure+Coding+Practices"],
                    [39, "Hackers will be able to steal data from the backend and also they can authenticate themselves to the website and can impersonate as any user since they have total control over the backend. They can even wipe out the entire database. Attackers can also steal cookie information of an authenticated user and they can even redirect the target to any malicious address or totally deface the application.",
                            "Proper input validation has to be done prior to directly querying the database information. A developer should remember not to trust an end-user's input. By following a secure coding methodology attacks like SQLi, XSS and BSQLi. The following resource guides on how to implement secure coding methodology on application development. https://wiki.sei.cmu.edu/confluence/display/seccode/Top+10+Secure+Coding+Practices"],
                    [40, "Attackers exploit the vulnerability in BASH to perform remote code execution on the target. An experienced attacker can easily take over the target system and access the internal sources of the machine",
                            "This vulnerability can be mitigated by patching the version of BASH. The following resource gives an indepth analysis of the vulnerability and how to mitigate it. https://www.symantec.com/connect/blogs/shellshock-all-you-need-know-about-bash-bug-vulnerability https://www.digitalocean.com/community/tutorials/how-to-protect-your-server-against-the-shellshock-bash-vulnerability"],
                    [41, "Gives attacker an idea on how the address scheming is done internally on the organizational network. Discovering the private addresses used within an organization can help attackers in carrying out network-layer attacks aiming to penetrate the organization's internal infrastructure.",
                            "Restrict the banner information to the outside world from the disclosing service. More information on mitigating this vulnerability can be found here. https://portswigger.net/kb/issues/00600300_private-ip-addresses-disclosed"],
                    [42, "There are chances for an attacker to manipulate files on the webserver.",
                            "It is recommended to disable the HTTP PUT and DEL methods incase if you don't use any REST API Services. Following resources helps you how to disable these methods. http://www.techstacks.com/howto/disable-http-methods-in-tomcat.html https://docs.oracle.com/cd/E19857-01/820-5627/gghwc/index.html https://developer.ibm.com/answers/questions/321629/how-to-disable-http-methods-head-put-delete-option/"],
                    [43, "Attackers try to learn more about the target from the amount of information exposed in the headers. An attacker may know what type of tech stack a web application is emphasizing and many other information.",
                            "Banner Grabbing should be restricted and access to the services from outside would should be made minimum."],
                    [44, "An attacker who successfully exploited this vulnerability could read data, such as the view state, which was encrypted by the server. This vulnerability can also be used for data tampering, which, if successfully exploited, could be used to decrypt and tamper with the data encrypted by the server.",
                            "Microsoft has released a set of patches on their website to mitigate this issue. The information required to fix this vulnerability can be inferred from this resource. https://docs.microsoft.com/en-us/security-updates/securitybulletins/2010/ms10-070"],
                    [45, "Any outdated web server may contain multiple vulnerabilities as their support would've been ended. An attacker may make use of such an opportunity to leverage attacks.",
                            "It is highly recommended to upgrade the web server to the available latest version."],
                    [46, "Hackers will be able to manipulate the URLs easily through a GET/POST request. They will be able to inject multiple attack vectors in the URL with ease and able to monitor the response as well",
                            "By ensuring proper sanitization techniques and employing secure coding practices it will be impossible for the attacker to penetrate through. The following resource gives a detailed insight on secure coding practices. https://wiki.sei.cmu.edu/confluence/display/seccode/Top+10+Secure+Coding+Practices"],
                    [47, "Since the attacker has knowledge about the particular type of backend the target is running, they will be able to launch a targetted exploit for the particular version. They may also try to authenticate with default credentials to get themselves through.",
                            "Timely security patches for the backend has to be installed. Default credentials has to be changed. If possible, the banner information can be changed to mislead the attacker. The following resource gives more information on how to secure your backend. http://kb.bodhost.com/secure-database-server/"],
                    [48, "Attackers may launch remote exploits to either crash the service or tools like ncrack to try brute-forcing the password on the target.",
                            "It is recommended to block the service to outside world and made the service accessible only through the a set of allowed IPs only really neccessary. The following resource provides insights on the risks and as well as the steps to block the service. https://www.perspectiverisk.com/remote-desktop-service-vulnerabilities/"],
                    [49, "Hackers will be able to read community strings through the service and enumerate quite a bit of information from the target. Also, there are multiple Remote Code Execution and Denial of Service vulnerabilities related to SNMP services.",
                            "Use a firewall to block the ports from the outside world. The following article gives wide insight on locking down SNMP service. https://www.techrepublic.com/article/lock-it-down-dont-allow-snmp-to-compromise-network-security/"],
                    [50, "Attackers will be able to find the logs and error information generated by the application. They will also be able to see the status codes that was generated on the application. By combining all these information, the attacker will be able to leverage an attack.",
                            "By restricting access to the logger application from the outside world will be more than enough to mitigate this weakness."],
                    [51, "Cyber Criminals mainly target this service as it is very easier for them to perform a remote attack by running exploits. WannaCry Ransomware is one such example.",
                            "Exposing SMB Service to the outside world is a bad idea, it is recommended to install latest patches for the service in order not to get compromised. The following resource provides a detailed information on SMB Hardening concepts. https://kb.iweb.com/hc/en-us/articles/115000274491-Securing-Windows-SMB-and-NetBios-NetBT-Services"]
            ]

tools_precheck = [
                    ["wapiti"], ["whatweb"], ["nmap"], ["golismero"], ["host"], ["wget"], ["uniscan"], ["wafw00f"], ["dirb"], ["davtest"], ["theHarvester"], ["xsser"], ["dnsrecon"],["fierce"], ["dnswalk"], ["whois"], ["sslyze"], ["lbd"], ["golismero"], ["dnsenum"],["dmitry"], ["davtest"], ["nikto"], ["dnsmap"], ["amass"]
                 ]

def get_parser():

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='store_true', help='Show help message and exit.')
    parser.add_argument('target', nargs='?', metavar='URL', help='URL to scan.', default='', type=str)
    return parser



tool_checks = len(tool_cmd)  # 

tool = 0


runTest = 1

# For accessing list/dictionary elements
arg1 = 0
arg2 = 1
arg3 = 2
arg4 = 3
arg5 = 4
arg6 = 5

# Detected Vulnerabilities [will be dynamically populated]
rs_vul_list = list()
rs_vul_num = 0
rs_vul = 0

# Total Time Elapsed
rs_total_elapsed = 0

# Tool Pre Checker
rs_avail_tools = 0


if len(sys.argv) == 1:
    logo()
    helper()
    sys.exit(1)

args_namespace = get_parser().parse_args()


if args_namespace.help or (not args_namespace.target):
    logo()
    helper()
elif args_namespace.target:

    target = url_maker(args_namespace.target)
    os.system('rm /tmp/securify* > /dev/null 2>&1') # Clearing previous scan files
    os.system('clear')
    os.system('setterm -cursor off')
    logo()
    

    while (rs_avail_tools < len(tools_precheck)):
        precmd = str(tools_precheck[rs_avail_tools][arg1])
        try:
            p = subprocess.Popen([precmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
            output, err = p.communicate()
            val = output + err
        except:
            sys.exit(1)
        
        rs_avail_tools = rs_avail_tools + 1
        
    
   
    
    print(bcolors.BG_HEAD_TXT+"[ Preliminary Scan Phase Initiated... Loaded "+str(tool_checks)+" vulnerability checks. ]"+bcolors.ENDC)
 
    while(tool < len(tool_names)):
        print("["+tool_status[tool][arg3]+tool_status[tool][arg4]+"] Deploying "+str(tool+1)+"/"+str(tool_checks)+" | "+bcolors.OKBLUE+tool_names[tool][arg2]+bcolors.ENDC,)
        scan_start = time.time()
        temp_file = "/tmp/securify_temp_"+tool_names[tool][arg1]
        cmd = tool_cmd[tool][arg1]+target+tool_cmd[tool][arg2]+" > "+temp_file+" 2>&1"

        
        try:
            subprocess.check_output(cmd, shell=True)
        except KeyboardInterrupt:
            runTest = 0
        except:
            runTest = 1

        if runTest == 1:
   
                scan_stop = time.time()
                elapsed = scan_stop - scan_start
                rs_total_elapsed = rs_total_elapsed + elapsed
                sys.stdout.write(ERASE_LINE)
                print(bcolors.OKBLUE+"\nScan Completed in "+display_time(int(elapsed))+bcolors.ENDC, end='\r', flush=True)
                print("\n")
                rs_tool_output_file = open(temp_file).read()
                if tool_status[tool][arg2] == 0:
                    if tool_status[tool][arg1].lower() in rs_tool_output_file.lower():
                        vul_remed_info(tool,tool_resp[tool][arg2],tool_resp[tool][arg3])
                        rs_vul_list.append(tool_names[tool][arg1]+"*"+tool_names[tool][arg2])
                else:
                    if any(i in rs_tool_output_file for i in tool_status[tool][arg6]):
                        m = 1 
                    else:
                        vul_remed_info(tool,tool_resp[tool][arg2],tool_resp[tool][arg3])
                        rs_vul_list.append(tool_names[tool][arg1]+"*"+tool_names[tool][arg2])
        else:
                runTest = 1
                scan_stop = time.time()
                elapsed = scan_stop - scan_start
                rs_total_elapsed = rs_total_elapsed + elapsed
                sys.stdout.write(ERASE_LINE)

        tool=tool+1

    print("\n")

    #################### Report & Documentation Phase ###########################

    debuglog = "Securify.dbg.%s" % (target)
    vulreport = "Securify.vuln.%s" % (target)
    print(bcolors.BG_HEAD_TXT+"[ Report Generation Phase Initiated. ]"+bcolors.ENDC)
    if len(rs_vul_list)==0:
        print("\t"+bcolors.OKGREEN+"No Vulnerabilities Detected."+bcolors.ENDC)
    else:
        with open(vulreport, "a") as report:
            while(rs_vul < len(rs_vul_list)):
                vuln_info = rs_vul_list[rs_vul].split('*')
                report.write(vuln_info[arg2])
                report.write("\n------------------------\n\n")
                temp_report_name = "/tmp/securify_temp_"+vuln_info[arg1]
                with open(temp_report_name, 'r') as temp_report:
                    data = temp_report.read()
                    report.write(data)
                    report.write("\n\n")
                temp_report.close()
                rs_vul = rs_vul + 1

            print("\tComplete Vulnerability Report for "+bcolors.OKBLUE+target+bcolors.ENDC+" named "+bcolors.OKGREEN+vulreport+bcolors.ENDC+" is available under the same directory securify resides.")

        report.close()
    # Writing all scan files output into RS-Debug-ScanLog for debugging purposes.
    for file_index, file_name in enumerate(tool_names):
        with open(debuglog, "a") as report:
            try:
                with open("/tmp/securify_temp_"+file_name[arg1], 'r') as temp_report:
                        data = temp_report.read()
                        report.write(file_name[arg2])
                        report.write("\n------------------------\n\n")
                        report.write(data)
                        report.write("\n\n")
                temp_report.close()
            except:
                break
        report.close()

    print("\tTotal Number of Vulnerability Checks        : "+bcolors.BOLD+bcolors.OKGREEN+str(len(tool_names))+bcolors.ENDC)
    print("\tTotal Number of Vulnerabilities Detected    : "+bcolors.BOLD+bcolors.BADFAIL+str(len(rs_vul_list))+bcolors.ENDC)
    print("\tTotal Time Elapsed for the Scan             : "+bcolors.BOLD+bcolors.OKBLUE+display_time(int(rs_total_elapsed))+bcolors.ENDC)
    print("\n")
    print("\tFor Debugging Purposes, You can view the complete output generated by all the tools named "+bcolors.OKBLUE+debuglog+bcolors.ENDC+" under the same directory.")

    os.system('setterm -cursor on')
    os.system('rm /tmp/securify_te* > /dev/null 2>&1')
