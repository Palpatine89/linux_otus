import subprocess
from collections import Counter
from date import Date


REPORT_SYSTEM = "Отчёт о состоянии системы:"
REPORT_USERS = "Пользователи системы: {}"
REPORT_PROCESS = 'Процессов запущено: {}'
REPORT_USER_PROCESS = 'Пользовательских процессов:'
REPORT_TOTAL_MEMORY = 'Всего памяти используется: {} mb'
REPORT_TOTAL_CPU = 'Всего CPU используется: {}%'
REPORT_MAX_MEMORY = 'Больше всего памяти использует: {}'
REPORT_MAX_CPU = 'Больше всего CPU использует: {}'


def command_parser():
    """Функция парсинга команды 'ps aux'"""
    result = subprocess.run(["ps aux"], shell=True, capture_output=True)
    output = result.stdout
    lines = output.splitlines()

    # Собираем список с данными по каждому пользователю
    datas_list = []
    for line in lines[1:]:
        process_info = line.decode().split()
        info = [float(process_info[index]) if index != 0 else process_info[index] for index in [0, 1, 2, 3]]
        datas_list.append(info)

    # Собираем словарь с суммами по каждому пользователю
    sums_by_users = {}
    process_list = []  # Список процессов
    memory_sum = 0
    cpu_sum = 0

    for data in datas_list:
        user = data[0]
        process_list.append(data[1])
        cpu = data[2]
        memory = data[3]

        cpu_sum += cpu
        memory_sum += memory

        if user in sums_by_users:
            sums_by_users[user][0] += cpu
            sums_by_users[user][1] += memory
        else:
            sums_by_users[user] = [cpu, memory]

    # Получаем список уникальных пользователей
    users_list = [user[0] for user in datas_list]
    count_users = Counter(users_list)
    users_process = [user for user in count_users.items()]

    # Округляем полученные суммы
    round_memory = round(memory_sum, 1)
    round_cpu = round(cpu_sum, 1)
    process_count = len(process_list)

    # Получаем пользователя с максимальным потреблением по памяти и процессору
    max_memory_user = max(sums_by_users, key=lambda x: sums_by_users[x][0])
    max_cpu_user = max(sums_by_users, key=lambda x: sums_by_users[x][1])

    if len(max_memory_user) > 20:
        max_memory_user = max_memory_user[:20]
    else:
        max_memory_user = max_memory_user

    unique_users = ", ".join([str(user[0]) for user in users_process])

    # Формируем отчет в вывод
    print(REPORT_SYSTEM)
    print(REPORT_USERS.format(unique_users))
    print(REPORT_PROCESS.format(process_count))
    print(REPORT_USER_PROCESS)
    for users in users_process:
        print(f"{users[0]}: {users[1]}")
    print(REPORT_TOTAL_MEMORY.format(round_memory))
    print(REPORT_TOTAL_CPU.format(round_cpu))
    print(REPORT_MAX_MEMORY.format(max_memory_user))
    print(REPORT_MAX_CPU.format(max_cpu_user))

    # Формируем отчет в тексовый файл
    report = REPORT_SYSTEM + '\n'
    report += REPORT_USERS.format(unique_users) + '\n'
    report += REPORT_PROCESS.format(process_count) + '\n'
    report += REPORT_USER_PROCESS + '\n'
    for users in users_process:
        report += f"{users[0]}: {users[1]}\n"
    report += REPORT_TOTAL_MEMORY.format(round_memory) + '\n'
    report += REPORT_TOTAL_CPU.format(round_cpu) + '\n'
    report += REPORT_MAX_MEMORY.format(max_memory_user) + '\n'
    report += REPORT_MAX_CPU.format(max_cpu_user) + '\n'

    with open(f"{Date.current_date()}-scan.txt", "w") as file:
        file.write(report)


if __name__ == '__main__':
    command_parser()
