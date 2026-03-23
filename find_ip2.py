import socket
import concurrent.futures

INPUT_FILE = 'whitelist.txt'
OUTPUT_FILE = 'resolved.txt'
MAX_WORKERS = 50  # Оптимально для стандартных библиотек

def resolve(domain):
    domain = domain.strip()
    if not domain:
        return None
    try:
        # Получаем все IP-адреса (IPv4) для домена
        # getaddrinfo возвращает список кортежей, вытягиваем только IP
        infos = socket.getaddrinfo(domain, None, family=socket.AF_INET)
        ips = list(set([info[4][0] for info in infos]))
        return f"{domain} - {', '.join(ips)}"
    except Exception:
        return f"{domain} - No IP found"

def main():
    try:
        with open(INPUT_FILE, 'r') as f:
            domains = f.readlines()
    except FileNotFoundError:
        print(f"Файл {INPUT_FILE} не найден.")
        return

    print(f"Резолвим {len(domains)} доменов через ThreadPool...")
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(resolve, domains))

    with open(OUTPUT_FILE, 'w') as f:
        for res in results:
            if res:
                f.write(res + '\n')

    print(f"Готово! Проверь файл {OUTPUT_FILE}")

if __name__ == '__main__':
    main()