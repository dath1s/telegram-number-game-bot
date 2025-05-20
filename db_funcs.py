import sqlite3


def create_database(db_name="game.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            bot_score INTEGER DEFAULT 0,
            player_score INTEGER DEFAULT 0,
            round_number INTEGER DEFAULT 1,
            score INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()
    print(f"База данных '{db_name}' и таблица 'game_stats' успешно созданы или уже существуют.")


def reset_or_create_user(user_id, db_name="game.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Проверяем, есть ли пользователь в БД
    cursor.execute("SELECT id FROM game_stats WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result:
        # Если пользователь существует — обнуляем счет и раунд
        cursor.execute('''
            UPDATE game_stats 
            SET bot_score = 0, player_score = 0, round_number = 1, score = 0
            WHERE user_id = ?
        ''', (user_id,))
        print(f"Счет и раунд для пользователя {user_id} обнулены.")
    else:
        # Если не существует — создаем новую запись
        cursor.execute('''
            INSERT INTO game_stats (user_id, bot_score, player_score, round_number, score)
            VALUES (?, 0, 0, 1, 0)
        ''', (user_id,))
        print(f"Пользователь {user_id} добавлен в базу данных.")

    conn.commit()
    conn.close()


def update_total_score(user_id, x, db_name="game.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE game_stats 
        SET score = score + ?
        WHERE user_id = ?
    ''', (x, user_id))

    conn.commit()
    conn.close()
    print(f"Общий счёт пользователя {user_id} увеличен на {x}.")


def increment_score_and_next_round(user_id, winner='player', db_name="game.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    if winner == 'player':
        cursor.execute('''
            UPDATE game_stats 
            SET player_score = player_score + 1,
                round_number = round_number + 1
            WHERE user_id = ?
        ''', (user_id,))
    elif winner == 'bot':
        cursor.execute('''
            UPDATE game_stats 
            SET bot_score = bot_score + 1,
                round_number = round_number + 1
            WHERE user_id = ?
        ''', (user_id,))
    else:
        print("Неверный параметр winner. Используйте 'player' или 'bot'.")
        return

    conn.commit()
    conn.close()
    print(f"Счет {winner} увеличен на 1. Раунд увеличен.")


def get_current_round(user_id, db_name="game.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT round_number FROM game_stats
        WHERE user_id = ?
    ''', (user_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        print("Пользователь не найден.")
        return None


def get_current_score(user_id, db_name="game.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT score FROM game_stats
        WHERE user_id = ?
    ''', (user_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        print("Пользователь не найден.")
        return None
