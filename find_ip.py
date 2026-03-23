import socket
import concurrent.futures
import sys

# --- Настройки ---
TARGET_IP = '84.201.129.1'        # УКАЖИ СЮДА СВОЙ ЦЕЛЕВОЙ IP
INPUT_FILE = 'whitelist.txt'   # Файл со списком доменов
MIN_MATCH_OCTETS = 1         # Минимальное количество совпадающих октетов (от 1 до 4)
MAX_WORKERS = 30             # Количество одновременных потоков
# -----------------

def get_match_score(target_ip, resolved_ip):
    """Возвращает количество совпавших октетов слева направо."""
    if not resolved_ip:
        return 0
    
    target_octets = target_ip.split('.')
    resolved_octets = resolved_ip.split('.')
    print("target", target_ip)
    print("resolved", resolved_ip)

    score = 0
    for t, r in zip(target_octets, resolved_octets):
        if t == r:
            score += 1
        else:
            break # Прерываем, так как важна последовательность (подсеть)
            
    return score

def resolve_and_compare(domain, target_ip):
    domain = domain.strip()
    if not domain:
        return None
        
    try:
        # Получаем IPv4 адрес домена
        resolved_ip = socket.gethostbyname(domain)
        score = get_match_score(target_ip, resolved_ip)
        
        return {
            'domain': domain,
            'ip': resolved_ip,
            'score': score
        }
    except socket.gaierror:
        # Если домен не резолвится
        return {
            'domain': domain,
            'ip': None,
            'score': 0
        }

def main():
    try:
        with open(INPUT_FILE, 'r') as f:
            domains = f.readlines()
    except FileNotFoundError:
        print(f"Ошибка: Файл {INPUT_FILE} не найден.")
        sys.exit(1)

    print(f"Поиск совпадений с IP: {TARGET_IP}")
    print(f"Проверка {len(domains)} доменов...\n")
    
    results = []

    # Многопоточный резолв
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(resolve_and_compare, domain, TARGET_IP): domain for domain in domains}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                results.append(res)
                # Опционально: можно выводить прогресс в консоль
                # print(f"Проверен: {res['domain']} -> {res['ip']}")

    # Фильтруем те, что подходят под минимальные требования
    valid_matches = [r for r in results if r['score'] >= MIN_MATCH_OCTETS]
    
    # Сортируем результаты: сначала те, у которых больше совпадений
    valid_matches.sort(key=lambda x: x['score'], reverse=True)

    print("="*50)
    if not valid_matches:
        print(f"Не найдено доменов, у которых совпадает хотя бы {MIN_MATCH_OCTETS} октета.")
    else:
        print(f"🏆 НАЙДЕНО ДОМЕНОВ: {len(valid_matches)}")
        print("="*50)
        for match in valid_matches:
            # Форматируем вывод в зависимости от уровня совпадения
            score_bar = "🟢" * match['score'] + "⚪" * (4 - match['score'])
            print(f"[{score_bar}] {match['domain'].ljust(30)} -> {match['ip']}")
    print("="*50)

if __name__ == '__main__':
    main()