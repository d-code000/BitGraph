import os
import subprocess
from concurrent.futures import ProcessPoolExecutor


def run_command(command: list[str]) -> tuple[str, str]:
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        return result.stdout, result.stderr
    except Exception as e:
        return "", str(e)


if __name__ == '__main__':
    ui_dir = 'ui'
    output_dir = 'ui/migration'

    if not os.path.exists(ui_dir):
        print(f"Ошибка: Каталог '{ui_dir}' не существует.")
        exit(1)

    os.makedirs(output_dir, exist_ok=True)

    commands = []
    for file in os.listdir(ui_dir):
        if file.endswith('.ui'):
            name = os.path.splitext(file)[0]
            commands.append(['pyside6-uic', f'{ui_dir}/{file}', '-o', f'{output_dir}/{name}.py'])

    # Обработка команд в пуле процессов
    with ProcessPoolExecutor() as executor:
        results = executor.map(run_command, commands)
        for i, (stdout, stderr) in enumerate(results):
            if stdout:
                print(f"Команда {i+1} завершилась с выводом:\n{stdout}")
            if stderr:
                print(f"Команда {i+1} завершилась с ошибкой:\n{stderr}")

    print('Миграция UI завершена.')
