
"""
Z_H_10min - Web Application Testing Tool
Developer: Tamilselvan S
Security Researchers
"""

import argparse
import sys
import time
import urllib3
import warnings
import ssl
import socket
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from colorama import init, Fore, Style
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Suppress insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=UserWarning, module='urllib3')

# Configure requests session with retry strategy
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)
session.verify = False  

# Initialize colorama
init()

class WebTester:
    def __init__(self, headless=False):
        """Initialize the WebTester with Chrome WebDriver"""
        self.headless = headless
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome WebDriver with options"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                chrome_options = Options()
                if self.headless:
                    chrome_options.add_argument('--headless=new')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--window-size=1920,1080')
                
                # Disable automation flags to avoid detection
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                # Try different approaches to initialize the driver
                try:
                    # First try with ChromeDriverManager
                    from webdriver_manager.chrome import ChromeDriverManager
                    from webdriver_manager.core.utils import ChromeType
                    
                    service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                except Exception as e:
                    print(f"{Fore.YELLOW}[!] ChromeDriverManager failed, trying with system Chrome...{Style.RESET_ALL}")
                    # Fallback to system Chrome
                    self.driver = webdriver.Chrome(options=chrome_options)
                
                # Set some additional capabilities
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                self.driver.maximize_window()
                
                print(Fore.GREEN + "[+] WebDriver initialized successfully" + Style.RESET_ALL)
                return
                
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    print(Fore.RED + f"[!] Failed to initialize WebDriver after {max_retries} attempts" + Style.RESET_ALL)
                    print(Fore.RED + f"[!] Error: {str(e)}" + Style.RESET_ALL)
                    print("\nTroubleshooting steps:")
                    print("1. Make sure you have Google Chrome installed")
                    print("2. Try updating Chrome to the latest version")
                    print("3. Run 'pip install --upgrade webdriver-manager'")
                    print("4. Try running without --headless flag first")
                    sys.exit(1)
                
                print(f"{Fore.YELLOW}[!] Retrying WebDriver initialization ({retry_count}/{max_retries})...{Style.RESET_ALL}")
                time.sleep(2)  # Wait before retrying
    
    def test_url(self, url):
        """Test a given URL for basic web application tests"""
        if not hasattr(self, 'driver') or not self.driver:
            self.setup_driver()
            
        print(f"\n{Fore.CYAN}=== Testing URL: {url} ==={Style.RESET_ALL}")
        
        try:
            start_time = time.time()
            
            # Test 1: Check if URL is reachable
            self.test_connection(url)
            
            # Test 2: Open URL in browser
            self.driver.get(url)
            load_time = time.time() - start_time
            print(Fore.GREEN + f"[+] Successfully loaded the URL (took {load_time:.2f} seconds)" + Style.RESET_ALL)
            
            # Test 3: Get page info
            print(f"\n{Fore.YELLOW}=== Page Information ==={Style.RESET_ALL}")
            print(f"Title: {self.driver.title}")
            print(f"Current URL: {self.driver.current_url}")
            
            # Test 4: Check for console errors
            print(f"\n{Fore.YELLOW}=== Console Error Check ==={Style.RESET_ALL}")
            self.check_console_errors()
            
            # Test 5: Check for broken links
            print(f"\n{Fore.YELLOW}=== Link Validation ==={Style.RESET_ALL}")
            self.check_broken_links()
            
            # Test 6: Take screenshot
            print(f"\n{Fore.YELLOW}=== Capturing Screenshot ==={Style.RESET_ALL}")
            self.take_screenshot()
            
            print(f"\n{Fore.GREEN}[✓] Basic testing completed in {time.time() - start_time:.2f} seconds!{Style.RESET_ALL}")
            
        except Exception as e:
            print(Fore.RED + f"[!] Error during testing: {str(e)}" + Style.RESET_ALL)
            raise
    
    def test_connection(self, url):
        """Test if URL is reachable"""
        try:
            # Use the configured session
            response = session.get(url, timeout=10)
            status_msg = f"[+] URL is reachable. Status code: {response.status_code}"
            if response.status_code == 200:
                print(Fore.GREEN + status_msg + Style.RESET_ALL)
            else:
                print(Fore.YELLOW + status_msg + Style.RESET_ALL)
            return response
        except requests.exceptions.SSLError as e:
            print(Fore.YELLOW + f"[!] SSL Certificate verification failed for {url}" + Style.RESET_ALL)
            try:
                # Try with SSL verification disabled
                response = session.get(url, timeout=10, verify=False)
                print(Fore.YELLOW + f"[!] Connected with SSL verification disabled. Status: {response.status_code}" + Style.RESET_ALL)
                return response
            except Exception as e:
                print(Fore.RED + f"[!] Connection failed: {str(e)}" + Style.RESET_ALL)
                return None
        except requests.exceptions.RequestException as e:
            print(Fore.RED + f"[!] Could not connect to {url}: {str(e)}" + Style.RESET_ALL)
            return None
    
    def check_console_errors(self):
        """Check browser console for errors"""
        try:
            logs = self.driver.get_log('browser')
            if logs:
                print(Fore.YELLOW + "[!] Browser console errors found:" + Style.RESET_ALL)
                for log in logs:
                    if log['level'] == 'SEVERE':
                        print(f"- {log['message']}")
            else:
                print(Fore.GREEN + "[+] No browser console errors found" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.YELLOW + f"[!] Could not retrieve browser logs: {str(e)}" + Style.RESET_ALL)
    
    def check_broken_links(self):
        """Check for broken links on the page"""
        try:
            links = self.driver.find_elements(By.TAG_NAME, 'a')
            print(f"Found {len(links)} links on the page")
            
            broken_links = 0
            checked_links = set()  # To avoid checking the same link multiple times
            
            for link in links:
                try:
                    href = link.get_attribute('href')
                    if href and href.startswith(('http://', 'https://')) and href not in checked_links:
                        checked_links.add(href)
                        try:
                            response = session.head(
                                href, 
                                allow_redirects=True, 
                                timeout=5,
                                verify=False  # Disable SSL verification for link checking
                            )
                            if response.status_code >= 400:
                                print(Fore.RED + f"[!] Broken link ({response.status_code}): {href}" + Style.RESET_ALL)
                                broken_links += 1
                            elif response.status_code >= 300:
                                print(Fore.YELLOW + f"[!] Redirect ({response.status_code}): {href} -> {response.url}" + Style.RESET_ALL)
                        except requests.exceptions.SSLError:
                            # Try with GET if HEAD fails due to SSL
                            try:
                                response = session.get(href, timeout=5, verify=False, stream=True)
                                if response.status_code >= 400:
                                    print(Fore.RED + f"[!] Broken link ({response.status_code}): {href}" + Style.RESET_ALL)
                                    broken_links += 1
                            except Exception as e:
                                print(Fore.RED + f"[!] Error checking link {href}: {str(e)[:100]}..." + Style.RESET_ALL)
                                broken_links += 1
                except Exception as e:
                    continue
            
            if broken_links == 0:
                print(Fore.GREEN + "[+] No broken links found" + Style.RESET_ALL)
            
        except Exception as e:
            print(Fore.YELLOW + f"[!] Error checking links: {str(e)}" + Style.RESET_ALL)
    
    def take_screenshot(self):
        """Take a screenshot of the current page"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            self.driver.save_screenshot(filename)
            print(Fore.GREEN + f"[+] Screenshot saved as {filename}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.YELLOW + f"[!] Could not take screenshot: {str(e)}" + Style.RESET_ALL)
    
    def test_security_headers(self, url):
        """Test for important security headers"""
        try:
            print(f"\n{Fore.CYAN}=== Testing Security Headers ==={Style.RESET_ALL}")
            
            response = requests.get(url, verify=False, timeout=10)
            headers = response.headers
            
            security_headers = {
                'X-Content-Type-Options': 'Prevents MIME type sniffing',
                'X-Frame-Options': 'Prevents clickjacking',
                'X-XSS-Protection': 'Cross-site scripting filter',
                'Content-Security-Policy': 'Prevents XSS and data injection',
                'Strict-Transport-Security': 'Enforces HTTPS',
                'Referrer-Policy': 'Controls referrer information',
                'Permissions-Policy': 'Controls browser features',
                'Cross-Origin-Opener-Policy': 'Isolates browsing context',
                'Cross-Origin-Resource-Policy': 'Controls cross-origin requests'
            }
            
            missing_headers = []
            
            for header, description in security_headers.items():
                if header.lower() in (h.lower() for h in headers):
                    print(f"{Fore.GREEN}[✓] {header}: {headers.get(header, 'Present')}" + 
                          f"{Style.DIM} - {description}{Style.RESET_ALL}")
                else:
                    missing_headers.append(header)
                    print(f"{Fore.RED}[!] Missing: {header}{Style.RESET_ALL} {Style.DIM}- {description}{Style.RESET_ALL}")
            
            if missing_headers:
                print(f"\n{Fore.YELLOW}Recommendations:")
                for header in missing_headers:
                    print(f"- Consider adding the {header} header for better security")
                print(Style.RESET_ALL)
            
            return len(missing_headers) == 0
            
        except Exception as e:
            print(Fore.RED + f"[!] Error checking security headers: {str(e)}" + Style.RESET_ALL)
            return False
    
    def test_forms(self):
        """Test all forms on the page"""
        try:
            print(f"\n{Fore.CYAN}=== Form Testing ==={Style.RESET_ALL}")
            forms = self.driver.find_elements(By.TAG_NAME, 'form')
            
            if not forms:
                print("No forms found on the page.")
                return
                
            print(f"Found {len(forms)} form(s) on the page.")
            
            for i, form in enumerate(forms, 1):
                print(f"\n{Fore.YELLOW}Form {i}:{Style.RESET_ALL}")
                
                # Get form attributes
                form_id = form.get_attribute('id') or 'No ID'
                form_action = form.get_attribute('action') or 'No action specified'
                form_method = form.get_attribute('method') or 'GET'
                
                print(f"ID: {form_id}")
                print(f"Action: {form_action}")
                print(f"Method: {form_method}")
                
                # Check for password fields
                password_fields = form.find_elements(By.CSS_SELECTOR, 'input[type="password"]')
                if password_fields:
                    print(f"{Fore.YELLOW}[!] Contains password field(s) - check for HTTPS in form action{Style.RESET_ALL}")
                
                # Check for CSRF token
                csrf_tokens = form.find_elements(By.CSS_SELECTOR, 'input[name*="csrf"], input[name*="CSRF"]')
                if not csrf_tokens:
                    print(f"{Fore.YELLOW}[!] No CSRF token detected - potential security risk{Style.RESET_ALL}")
                
                # List all input fields
                inputs = form.find_elements(By.TAG_NAME, 'input')
                if inputs:
                    print("\nInput fields:")
                    for input_field in inputs:
                        input_type = input_field.get_attribute('type') or 'text'
                        input_name = input_field.get_attribute('name') or 'No name'
                        input_id = input_field.get_attribute('id') or 'No ID'
                        print(f"- {input_type.upper()}: {input_name} (ID: {input_id})")
            
            print(f"\n{Fore.GREEN}[✓] Form testing completed{Style.RESET_ALL}")
            
        except Exception as e:
            print(Fore.RED + f"[!] Error testing forms: {str(e)}" + Style.RESET_ALL)
    
    def test_performance(self, url):
        """Test page load performance"""
        try:
            print(f"\n{Fore.CYAN}=== Performance Testing ==={Style.RESET_ALL}")
            
            # Test initial page load
            start_time = time.time()
            self.driver.get(url)
            load_time = time.time() - start_time
            
            # Get performance metrics
            navigation_start = self.driver.execute_script("return window.performance.timing.navigationStart")
            dom_complete = self.driver.execute_script("return window.performance.timing.domComplete")
            load_event_end = self.driver.execute_script("return window.performance.timing.loadEventEnd")
            
            # Calculate metrics
            dom_loading = (dom_complete - navigation_start) / 1000
            page_load = (load_event_end - navigation_start) / 1000
            
            print(f"Page loaded in {load_time:.2f} seconds")
            print(f"DOM loading time: {dom_loading:.2f} seconds")
            print(f"Full page load time: {page_load:.2f} seconds")
            
            # Check for large resources
            resources = self.driver.execute_script("""
                var resources = window.performance.getEntriesByType('resource');
                return resources.map(function(resource) {
                    return {
                        name: resource.name,
                        type: resource.initiatorType,
                        duration: resource.duration,
                        size: resource.transferSize
                    };
                });
            """)
            
            # Sort resources by size (largest first)
            large_resources = sorted(
                [r for r in resources if r['size'] > 102400],  # > 100KB
                key=lambda x: x['size'],
                reverse=True
            )
            
            if large_resources:
                print(f"\n{Fore.YELLOW}Large resources found (over 100KB):{Style.RESET_ALL}")
                for i, resource in enumerate(large_resources[:5], 1):  # Show top 5
                    size_mb = resource['size'] / (1024 * 1024)
                    print(f"{i}. {resource['name']}")
                    print(f"   Type: {resource['type']}")
                    print(f"   Size: {size_mb:.2f} MB")
                    print(f"   Load time: {resource['duration']:.2f} ms")
            
            print(f"\n{Fore.GREEN}[✓] Performance testing completed{Style.RESET_ALL}")
            
        except Exception as e:
            print(Fore.RED + f"[!] Error during performance testing: {str(e)}" + Style.RESET_ALL)

    def test_accessibility(self):
        """Perform basic accessibility checks"""
        try:
            print(f"\n{Fore.CYAN}=== Accessibility Testing ==={Style.RESET_ALL}")
            
            # Check for images without alt attributes
            images = self.driver.find_elements(By.TAG_NAME, 'img')
            missing_alt = 0
            for img in images:
                if not img.get_attribute('alt'):
                    missing_alt += 1
            
            if missing_alt > 0:
                print(f"{Fore.YELLOW}[!] Found {missing_alt} images without 'alt' text{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}[✓] All images have 'alt' text{Style.RESET_ALL}")

            # Check for input fields without labels
            inputs = self.driver.find_elements(By.TAG_NAME, 'input')
            missing_labels = 0
            for inp in inputs:
                if inp.get_attribute('type') not in ['hidden', 'submit', 'button', 'image']:
                    input_id = inp.get_attribute('id')
                    if input_id:
                        labels = self.driver.find_elements(By.CSS_SELECTOR, f"label[for='{input_id}']")
                        if not labels:
                            missing_labels += 1
                    else:
                        try:
                            parent = inp.find_element(By.XPATH, "..")
                            if parent.tag_name != 'label':
                                missing_labels += 1
                        except:
                            missing_labels += 1
            
            if missing_labels > 0:
                print(f"{Fore.YELLOW}[!] Found {missing_labels} input fields potentially without labels{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}[✓] Input fields appear to have labels{Style.RESET_ALL}")
                
        except Exception as e:
            print(Fore.RED + f"[!] Error during accessibility testing: {str(e)}" + Style.RESET_ALL)

    def test_seo(self):
        """Check for basic SEO elements"""
        try:
            print(f"\n{Fore.CYAN}=== SEO Checks ==={Style.RESET_ALL}")
            
            # Check Title
            title = self.driver.title
            if title:
                print(f"{Fore.GREEN}[✓] Page Title found: {title[:50]}...{Style.RESET_ALL}")
                if len(title) > 60:
                     print(f"{Fore.YELLOW}[!] Title is longer than 60 characters ({len(title)}){Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}[!] Missing Page Title{Style.RESET_ALL}")
            
            # Check Meta Description
            try:
                meta_desc = self.driver.find_element(By.CSS_SELECTOR, "meta[name='description']")
                content = meta_desc.get_attribute('content')
                if content:
                     print(f"{Fore.GREEN}[✓] Meta Description found: {content[:50]}...{Style.RESET_ALL}")
                     if len(content) > 160:
                         print(f"{Fore.YELLOW}[!] Meta description is longer than 160 characters ({len(content)}){Style.RESET_ALL}")
                else:
                     print(f"{Fore.YELLOW}[!] Meta Description tag exists but is empty{Style.RESET_ALL}")
            except:
                print(f"{Fore.RED}[!] Missing Meta Description{Style.RESET_ALL}")
                
            # Check H1
            h1s = self.driver.find_elements(By.TAG_NAME, 'h1')
            if len(h1s) == 1:
                print(f"{Fore.GREEN}[✓] Exactly one H1 tag found: {h1s[0].text[:50]}{Style.RESET_ALL}")
            elif len(h1s) == 0:
                print(f"{Fore.RED}[!] No H1 tag found{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}[!] Multiple H1 tags found ({len(h1s)}){Style.RESET_ALL}")

        except Exception as e:
            print(Fore.RED + f"[!] Error during SEO checks: {str(e)}" + Style.RESET_ALL)

    def test_ssl(self, url):
        """Check SSL certificate details"""
        try:
            print(f"\n{Fore.CYAN}=== SSL Certificate Check ==={Style.RESET_ALL}")
            
            if not url.startswith('https'):
                print(f"{Fore.YELLOW}[!] Not an HTTPS URL, skipping SSL check{Style.RESET_ALL}")
                return

            hostname = url.replace('https://', '').split('/')[0]
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_left = (not_after - datetime.utcnow()).days
                    
                    print(f"Issued To: {dict(x[0] for x in cert['subject'])['commonName']}")
                    print(f"Issued By: {dict(x[0] for x in cert['issuer'])['commonName']}")
                    print(f"Valid Until: {not_after}")
                    
                    if days_left < 0:
                        print(f"{Fore.RED}[!] Certificate EXPIRED {abs(days_left)} days ago{Style.RESET_ALL}")
                    elif days_left < 30:
                        print(f"{Fore.YELLOW}[!] Certificate expires soon ({days_left} days left){Style.RESET_ALL}")
                    else:
                        print(f"{Fore.GREEN}[✓] Certificate is valid ({days_left} days left){Style.RESET_ALL}")
                        
        except Exception as e:
            print(Fore.RED + f"[!] Error checking SSL: {str(e)}" + Style.RESET_ALL)
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
                print(Fore.CYAN + "[i] WebDriver session ended" + Style.RESET_ALL)
            except:
                pass  # Ignore errors during cleanup

def show_banner():
    """Display tool banner"""
    banner = f"""
{Fore.CYAN}

⠠⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠘⢷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿
⠀⠀⢸⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿
⠀⠀⠀⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿
⠀⠀⠀⣿⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿
⠀⠀⠀⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⣀⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⡿⣏⣿
⠀⠀⠀⢻⣿⣿⣿⣿⣷⣦⣀⠀⠀⠀⠀⣀⣤⣴⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣦⣄⣀⠀⠀⠀⣀⣼⣿⣿⣿⣿⣿⣾⡟⠃⠀
⠀⠀⠀⠸⣿⣿⣿⣿⣿⣿⣿⣿⣶⣤⣝⣛⡻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣙⣭⣥⣶⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀
⠀⠀⠀⠀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠀⠀⠀⠀
⠀⠀⠀⠀⠈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢈⢿⣿⣿⣿⣿⣿⣿⣿⣿⢟⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣌⢿⣿⣿⣿⣿⣿⣿⣿⡿⢣⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢠⣿⣦⣽⣛⣻⠿⠿⣟⣛⣵⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣭⣛⣛⣛⣛⣻⣭⣶⣿⣧⠀⠀⠀⠀
⠀⠀⠀⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀
⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡸⣿⡏⢿⣿⣿⣿⡟⣼⣿⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀
⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠹⣿⡈⢿⣿⠟⢰⣿⢃⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀
⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠹⣷⡀⠉⢠⣿⠏⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀
⠀⠀⠀⠀⣿⣿⣿⣿⣯⣍⡛⠻⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠀⣿⣷⣶⣿⡟⠀⢿⣿⣿⣿⣿⣿⣿⣿⠿⠿⠛⢋⣩⣵⣾⣿⣿⣿⡟⠀⠀⠀
⠀⠀⠀⠀⣿⣿⣜⢿⣿⣿⣿⣿⣶⣶⣤⣤⣤⣉⣉⣉⣁⣀⣠⣴⣿⣿⣿⣿⣿⣤⣄⣀⣀⣀⣠⣤⣤⣴⣶⣾⣿⣿⣿⣿⡿⢋⣾⣿⣇⠀⠀⠀
⠀⠀⠀⢰⣿⣿⣿⣷⣮⡝⠻⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠟⠛⢩⣾⣿⣿⣿⡿⣄⠀⠀
⠀⠀⢰⡏⠘⢿⣿⣿⣿⣇⠀⠀⠀⠀⠉⢭⣭⣽⡟⠛⠛⠛⠋⢁⣿⣿⣿⣿⣷⡈⠉⠉⠉⠉⢭⣭⣭⠵⠀⠀⠀⠀⠀⣼⣿⣿⣿⠟⠀⣽⠀⠀
⠀⠀⠀⢿⣄⠀⠻⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⣿⣿⣿⣿⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⣿⡿⠃⢀⣾⡟⠀⠀
⠀⠀⠀⠘⣿⣷⣤⣈⠛⠿⣿⣷⣦⣄⡀⠀⠀⠀⠀⠀⣀⣤⣾⡿⢸⣿⣿⣿⡇⢿⣷⣤⣀⡀⠀⠀⠀⢀⣀⣤⣶⣿⡿⠟⣉⣤⣴⣿⡿⠀⠀⠀
⠀⠀⠀⠀⠸⣿⣿⣿⣿⣷⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢃⣾⣿⣿⣿⣷⡈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣾⣿⣿⣿⣿⡿⠁⠀⠀⠀
⠀⠀⠀⠀⠀⢹⣿⣭⡻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣾⣿⣿⣿⣿⣿⣷⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣫⣶⣶⡇⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣸⣿⣿⡟⢈⣭⣟⣛⠿⠿⣿⣿⣿⠟⣩⣤⣬⣝⢿⣿⣿⣿⣿⣿⣿⣫⣥⣶⣌⠙⠿⡿⠿⠿⣛⣫⣭⣧⣄⢹⣿⣿⣇⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣿⣿⣿⣇⣿⣿⢛⣯⣟⢿⣶⣶⣶⡇⣿⣿⣿⣿⣾⣿⣿⣿⣿⣿⣷⣿⣿⣿⣿⢸⣿⣾⣿⢟⣯⣭⣝⢻⣿⣼⣿⣿⡿⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢸⣿⣿⣿⡿⣵⣿⣿⣿⣷⢹⣿⣿⣇⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣸⣿⣿⡏⣾⣿⣿⣿⣧⡹⣿⣿⣿⠇⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢿⡿⢋⣾⣿⣿⣿⣿⠟⢈⢿⣿⣿⣷⣤⣉⠙⠿⣿⣿⣿⣿⣿⠿⠛⣉⣤⣾⣿⣿⡿⡁⠙⢿⣿⣿⣿⣿⣌⠻⡿⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⣨⣶⣿⣿⡿⢟⠋⠀⠀⢸⡎⠻⣿⣿⣿⣿⣿⣶⣮⣭⣿⣯⣵⣶⣿⣿⣿⣿⡿⢟⠱⡇⠀⠀⠈⣙⡻⠿⣿⣿⣦⣄⡀⠀⠀⠀
⠀⠀⠀⠀⠒⠛⠛⠉⣽⣶⣾⣿⣧⠀⠀⠈⠃⣿⣶⣶⢰⣮⡝⣛⣻⢿⣿⣿⢿⣛⡫⣵⣶⢲⣾⣿⠀⠃⠀⠀⣸⣿⣿⣿⣶⠂⠈⠉⠉⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⡄⠀⠀⠀⢿⡿⠁⠈⠛⠷⠿⠿⠿⠿⠿⠸⠿⠇⠛⠁⠀⢹⣿⠀⠀⠀⠀⠈⣿⣿⣿⢿⠃⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⡇⠀⠀⠀⠘⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠋⠀⠀⠀⠀⠀⣾⣿⣿⡿⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⣿⡇⣠⣶⠀⠀⠀⠀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡀⠀⠀⢰⣦⠀⠀⢠⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿⡙⠇⣰⡇⢰⣿⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣽⣷⢀⣀⡜⢋⣶⣿⣿⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⣿⣇⢿⠗⣿⣿⣷⡄⣴⣶⣴⡆⣶⡆⣶⣰⣶⡄⣾⣿⣿⡞⢿⣣⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣿⣿⣷⣧⡻⡿⢟⣣⣛⣣⠻⣃⡻⣣⣛⣣⣛⣡⣛⡻⡿⣱⣷⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣷⣾⣿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⣿⣶⣿⣿⣿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⢿⣿⣿⣭⣶⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣶⣽⣿⣿⠟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠿⠛⠋⠉⠁⠀⠀⠀⠀⠈⠉⠙⠛⠛⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
╔════════════════════════════════════════════════╗
║         Z_H_10min - Web Testing Tool           ║
║         Developer: Tamilselvan S               ║
║         Security Researchers                   ║
╚════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def get_test_options():
    """Display test options and get user choice"""
    print(f"\n{Fore.YELLOW}Select an option:{Style.RESET_ALL}")
    print("1. Basic Testing (URL reachability, page load, links)")
    print("2. Full Testing (All available tests)")
    print("3. Security Headers Check")
    print("4. Form Testing")
    print("5. Performance Testing")
    print("6. SEO Check")
    print("7. Accessibility Check")
    print("8. SSL Certificate Check")
    print(f"9. {Fore.RED}Exit{Style.RESET_ALL}")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-9): "))
            if 1 <= choice <= 9:
                return choice
            print(f"{Fore.RED}Please enter a number between 1 and 9{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")

def get_url_input():
    """Get URL input from user"""
    while True:
        url = input("\nEnter URL to test (include http:// or https://): ").strip()
        if url:
            if not url.startswith(('http://', 'https://')):
                print(f"{Fore.YELLOW}Warning: URL should start with http:// or https://{Style.RESET_ALL}")
                url = 'http://' + url
            return url
        print(f"{Fore.RED}URL cannot be empty{Style.RESET_ALL}")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Z_H_10min - Web Application Testing Tool')
    parser.add_argument('url', nargs='?', help='URL to test')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--auto', action='store_true', help='Run all tests automatically')
    return parser.parse_args()

def main():
    """Main function"""
    show_banner()
    args = parse_arguments()
    
    # Get URL
    url = args.url if args.url else get_url_input()
    
    # Initialize tester
    tester = WebTester(headless=args.headless)
    
    if args.auto:
        # Run all tests in automated mode
        print(f"\n{Fore.CYAN}=== Running Automated Test Suite ==={Style.RESET_ALL}")
        tester.test_url(url)
        tester.test_security_headers(url)
        tester.test_forms()
        tester.test_performance(url)
        tester.test_seo()
        tester.test_accessibility()
        tester.test_ssl(url)
    else:
        # Interactive mode
        while True:
            choice = get_test_options()
            
            if choice == 1:
                print(f"\n{Fore.CYAN}=== Running Basic Tests ==={Style.RESET_ALL}")
                tester.test_url(url)
            elif choice == 2:
                print(f"\n{Fore.CYAN}=== Running Full Test Suite ==={Style.RESET_ALL}")
                tester.test_url(url)
                tester.test_security_headers(url)
                tester.test_forms()
                tester.test_performance(url)
                tester.test_seo()
                tester.test_accessibility()
                tester.test_ssl(url)
            elif choice == 3:
                print(f"\n{Fore.CYAN}=== Testing Security Headers ==={Style.RESET_ALL}")
                tester.test_security_headers(url)
            elif choice == 4:
                print(f"\n{Fore.CYAN}=== Testing Forms ==={Style.RESET_ALL}")
                tester.test_forms()
            elif choice == 5:
                print(f"\n{Fore.CYAN}=== Performance Testing ==={Style.RESET_ALL}")
                tester.test_performance(url)
            elif choice == 6:
                tester.test_seo()
            elif choice == 7:
                tester.test_accessibility()
            elif choice == 8:
                tester.test_ssl(url)
            elif choice == 9:
                print(f"\n{Fore.GREEN}Thank you for using Z_H_10min!{Style.RESET_ALL}")
                break
            
            if not input("\nPress Enter to continue or 'q' to quit: ").lower() == 'q':
                continue
            break

if __name__ == "__main__":
    main()
