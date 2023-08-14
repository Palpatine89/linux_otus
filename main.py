import subprocess
from collections import Counter
from datetime import datetime

DATE_FORMAT = "%d-%m-%Y-%H:%M"


REPORT_SYSTEM = "Отчёт о состоянии системы:"
REPORT_USERS = "Пользователи системы: {}"
REPORT_PROCESS = 'Процессов запущено: {}'
REPORT_USER_PROCESS = 'Пользовательских процессов:'
REPORT_TOTAL_MEMORY = 'Всего памяти используется: {} mb'
REPORT_TOTAL_CPU = 'Всего CPU используется: {}%'
REPORT_MAX_MEMORY = 'Больше всего памяти использует: {}'
REPORT_MAX_CPU = 'Больше всего CPU использует: {}'


def current_date():
    """Функция получения текущей даты и времени"""
    date = datetime.now()
    return date.strftime(DATE_FORMAT)


def get_correct_process_name(process_name):
    """Функция полученния имени процесса с длинной не более 20 символов"""
    if len(process_name) > 20:
        correct_process_name = process_name[:20]
    else:
        correct_process_name = process_name

    return correct_process_name


def command_parser():
    """Функция парсинга команды 'ps aux'"""
    result = subprocess.run(["ps aux"], shell=True, capture_output=True)
    output = result.stdout
    lines = output.splitlines()

    # Собираем список с данными по каждому пользователю
    datas_list = []
    for line in lines[1:]:
        user, pid, cpu, mem, *_, ps_name = line.decode().split()
        pid, cpu, mem = int(pid), float(cpu), float(mem)
        datas_list.append((user, pid, cpu, mem, ps_name))

    # Собираем словарь с суммами по каждому пользователю
    sums_by_users = {}
    process_param = []
    memory_sum = 0
    cpu_sum = 0

    for data in datas_list:
        user, pid, cpu, mem, ps_name = data

        cpu_sum += cpu
        memory_sum += mem

        sums_by_users.setdefault(user, [0, 0])
        sums_by_users[user][0] += cpu
        sums_by_users[user][1] += mem

        process_param.append({'pid': pid, 'cpu': cpu, 'mem': mem, 'ps_name': ps_name})

    # Получаем список уникальных пользователей
    users_list = [user[0] for user in datas_list]
    count_users = Counter(users_list)
    users_process = [user for user in count_users.items()]

    # Округляем полученные суммы
    round_memory = round(memory_sum, 1)
    round_cpu = round(cpu_sum, 1)
    process_count = len(process_param)

    # Получаем процесс с максимальным потреблением по памяти
    max_memory_process_name = max(process_param, key=lambda x: x['mem'])['ps_name']

    # Получаем процесс с максимальным потреблением по процессору
    max_cpu_process_name = max(process_param, key=lambda x: x['cpu'])['ps_name']

    unique_users = ", ".join([str(user[0]) for user in users_process])

    # Формируем отчет в тексовый файл и в консоль
    report = []
    report.append(REPORT_SYSTEM)
    report.append(REPORT_USERS.format(unique_users))
    report.append(REPORT_PROCESS.format(process_count))
    report.append(REPORT_USER_PROCESS)
    for users in users_process:
        report.append(f"{users[0]}: {users[1]}")
    report.append(REPORT_TOTAL_MEMORY.format(round_memory))
    report.append(REPORT_TOTAL_CPU.format(round_cpu))
    report.append(REPORT_MAX_MEMORY.format(get_correct_process_name(max_memory_process_name)))
    report.append(REPORT_MAX_CPU.format(get_correct_process_name(max_cpu_process_name)))

    with open(f"{current_date()}-scan.txt", "w") as file:
        for line in report:
            file.write(line + '\n')
            print(line)


if __name__ == '__main__':
    command_parser()
