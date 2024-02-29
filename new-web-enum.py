import requests
import dns.resolver
import argparse
import concurrent.futures
import time

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['dir', 'dns'], help='Specify action: dir or dns')
    parser.add_argument('-u', dest='url', help='Target URL')
    parser.add_argument('-w', dest='wordlist', help='Wordlist file')
    args = parser.parse_args()
    return args

def check_status_code(url):
    try:
        response = requests.get(url)
        return response.status_code
    except requests.exceptions.RequestException:
        return "Connection Error"

def get_directories(target, wordlist):
    with open(wordlist, 'r') as f:
        items = f.readlines()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Capture both URL and status code in a tuple
        results = executor.map(lambda item: (f"{target if target.startswith(('http://', 'https://')) else 'http://' + target}/{item.strip()}", check_status_code(f"{target if target.startswith(('http://', 'https://')) else 'http://' + target}/{item.strip()}")), items)

        # Print and filter results based on status code
        for url, status_code in results:
            if status_code != 404:
                print(f"{url} - {status_code}")

def enumerate_subdomains(target, wordlist):
    with open(wordlist, 'r') as f:
        subdomains = f.readlines()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(resolve_subdomain, f"{subdomain.strip()}.{target}") for subdomain in subdomains]
        results = [f"{future.result()[0]} - {future.result()[1]}" for future in concurrent.futures.as_completed(futures) if future.result()[1]]
    print(*results, sep='\n')
    return results

def resolve_subdomain(full_domain):
    try:
        answers = dns.resolver.resolve(full_domain, 'A')
        return full_domain, ' '.join(answer.address for answer in answers)
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return full_domain, None

def main():
    args = get_args()
    start_time = time.time()
    # target_url = args.url.split('://')[-1]
    if args.action == 'dir':
        get_directories(args.url, args.wordlist)
    elif args.action == 'dns':
        enumerate_subdomains(args.url, args.wordlist)
    
    execution_time = time.time() - start_time
    print(f"\nExecution time: {execution_time:.2f} seconds")

main()


