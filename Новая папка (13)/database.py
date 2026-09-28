
import sqlite3
from pathlib import Path


DB_PATH = Path("bot.db")


# =========================================================
# CONNECTION
# =========================================================

def connect():
    conn = sqlite3.connect(
        DB_PATH,
        timeout=10
    )
    conn.row_factory = sqlite3.Row
    return conn


def _columns(cursor, table):
    return {
        row[1]
        for row in cursor.execute(
            f"PRAGMA table_info({table})"
        ).fetchall()
    }


def _add_column_if_missing(
    cursor,
    table,
    column,
    definition
):
    columns = _columns(cursor, table)

    if column not in columns:
        cursor.execute(
            f"ALTER TABLE {table} "
            f"ADD COLUMN {column} {definition}"
        )


# =========================================================
# INIT DATABASE
# =========================================================

def init_db():
    conn = connect()
    cursor = conn.cursor()

    # =====================================================
    # USERS
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT DEFAULT '',
            first_name TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    _add_column_if_missing(
        cursor,
        "users",
        "username",
        "TEXT DEFAULT ''"
    )

    _add_column_if_missing(
        cursor,
        "users",
        "first_name",
        "TEXT DEFAULT ''"
    )

    _add_column_if_missing(
        cursor,
        "users",
        "created_at",
        "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    )

    _add_column_if_missing(
        cursor,
        "users",
        "last_activity",
        "TIMESTAMP"
    )

    cursor.execute("""
        UPDATE users
        SET last_activity = COALESCE(
            last_activity,
            created_at,
            CURRENT_TIMESTAMP
        )
        WHERE last_activity IS NULL
    """)

    # =====================================================
    # ORDERS
    #
    # get_order():
    #
    # 0  user_id
    # 1  username
    # 2  receiver
    # 3  stars
    # 4  price
    # 5  status
    # 6  created_at
    # 7  product_type
    # 8  premium_months
    # 9  receipt_file_id
    # 10 gram_amount
    # 11 gram_wallet
    #
    # get_all_orders():
    #
    # 0  id
    # 1  user_id
    # 2  username
    # 3  receiver
    # 4  stars
    # 5  price
    # 6  status
    # 7  created_at
    # 8  product_type
    # 9  premium_months
    # 10 receipt_file_id
    # 11 gram_amount
    # 12 gram_wallet
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT DEFAULT '',
            receiver TEXT DEFAULT '',
            stars INTEGER DEFAULT 0,
            price INTEGER NOT NULL,
            status TEXT DEFAULT 'waiting',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            product_type TEXT DEFAULT 'stars',
            premium_months INTEGER DEFAULT 0,
            receipt_file_id TEXT DEFAULT '',
            gram_amount REAL DEFAULT 0,
            gram_wallet TEXT DEFAULT ''
        )
    """)

    _add_column_if_missing(
        cursor,
        "orders",
        "username",
        "TEXT DEFAULT ''"
    )

    _add_column_if_missing(
        cursor,
        "orders",
        "receiver",
        "TEXT DEFAULT ''"
    )

    _add_column_if_missing(
        cursor,
        "orders",
        "stars",
        "INTEGER DEFAULT 0"
    )

    _add_column_if_missing(
        cursor,
        "orders",
        "price",
        "INTEGER DEFAULT 0"
    )

    _add_column_if_missing(
        cursor,
        "orders",
        "status",
        "TEXT DEFAULT 'waiting'"
    )

    _add_column_if_missing(
        cursor,
        "orders",
        "created_at",
        "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    )

    _add_column_if_missing(
        cursor,
        "orders",
        "product_type",
        "TEXT DEFAULT 'stars'"
    )

    _add_column_if_missing(
        cursor,
        "orders",
        "premium_months",
        "INTEGER DEFAULT 0"
    )

    _add_column_if_missing(
        cursor,
        "orders",
        "receipt_file_id",
        "TEXT DEFAULT ''"
    )

    _add_column_if_missing(
        cursor,
        "orders",
        "gram_amount",
        "REAL DEFAULT 0"
    )

    _add_column_if_missing(
        cursor,
        "orders",
        "gram_wallet",
        "TEXT DEFAULT ''"
    )

    # =====================================================
    # STARS PRICES
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            stars INTEGER PRIMARY KEY,
            price INTEGER NOT NULL
        )
    """)

    default_prices = [
        (50, 66),
        (100, 132),
        (250, 330),
        (500, 660),
        (1000, 1320)
    ]

    for stars, price in default_prices:
        cursor.execute("""
            INSERT OR IGNORE INTO prices
            (stars, price)
            VALUES (?, ?)
        """, (
            stars,
            price
        ))

    # =====================================================
    # PREMIUM PRICES
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS premium_prices (
            months INTEGER PRIMARY KEY,
            price INTEGER NOT NULL
        )
    """)

    default_premium = [
        (3, 599),
        (6, 1199),
        (12, 1999)
    ]

    for months, price in default_premium:
        cursor.execute("""
            INSERT OR IGNORE INTO premium_prices
            (months, price)
            VALUES (?, ?)
        """, (
            months,
            price
        ))

    # =====================================================
    # ADMINS
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY
        )
    """)

    # =====================================================
    # SETTINGS
    #
    # Все настройки бота находятся здесь.
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT DEFAULT ''
        )
    """)

    # =====================================================
    # DEFAULT SETTINGS
    # =====================================================

    default_settings = {

        # Stars
        "stars_rate": "1.32",

        # GRAM
        "gram_markup": "5.0",
        "gram_balance": "0",
        "gram_enabled": "0",
        "gram_payment_wallet": "",

        # =================================================
        # PAYMENT DETAILS
        # =================================================

        # Карта для Stars / Premium
        "payment_card": "",

        # Банк
        "payment_bank": "",

        # Получатель
        "payment_name": ""
    }

    for key, value in default_settings.items():
        cursor.execute("""
            INSERT OR IGNORE INTO settings
            (key, value)
            VALUES (?, ?)
        """, (
            key,
            value
        ))

    # =====================================================
    # BUTTON STYLES
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS button_styles (
            button_key TEXT PRIMARY KEY,
            style TEXT DEFAULT 'primary'
        )
    """)

    default_buttons = [
        "stars",
        "premium",
        "gram",
        "reviews",
        "profile",
        "admin"
    ]

    for button_key in default_buttons:
        cursor.execute("""
            INSERT OR IGNORE INTO button_styles
            (button_key, style)
            VALUES (?, 'primary')
        """, (
            button_key,
        ))

    conn.commit()
    conn.close()


# =========================================================
# USERS
# =========================================================

def add_user(
    user_id: int,
    username: str,
    first_name: str
):
    conn = connect()

    conn.execute("""
        INSERT INTO users (
            user_id,
            username,
            first_name,
            last_activity
        )
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)

        ON CONFLICT(user_id)
        DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name,
            last_activity = CURRENT_TIMESTAMP
    """, (
        user_id,
        username,
        first_name
    ))

    conn.commit()
    conn.close()


def touch_user(user_id: int):
    conn = connect()

    conn.execute("""
        UPDATE users
        SET last_activity = CURRENT_TIMESTAMP
        WHERE user_id = ?
    """, (
        user_id,
    ))

    conn.commit()
    conn.close()


def count_users():
    conn = connect()

    result = conn.execute("""
        SELECT COUNT(*)
        FROM users
    """).fetchone()[0]

    conn.close()

    return result


def count_active_today():
    conn = connect()

    result = conn.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE last_activity >=
        datetime('now', 'start of day')
    """).fetchone()[0]

    conn.close()

    return result


def count_active_week():
    conn = connect()

    result = conn.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE last_activity >=
        datetime('now', '-7 days')
    """).fetchone()[0]

    conn.close()

    return result


def get_all_users():
    conn = connect()

    rows = conn.execute("""
        SELECT
            user_id,
            username,
            first_name,
            last_activity
        FROM users
        ORDER BY last_activity DESC
    """).fetchall()

    conn.close()

    return [
        tuple(row)
        for row in rows
    ]


# =========================================================
# SETTINGS HELPERS
# =========================================================

def _get_setting(
    key: str,
    default=None
):
    conn = connect()

    row = conn.execute("""
        SELECT value
        FROM settings
        WHERE key = ?
        LIMIT 1
    """, (
        key,
    )).fetchone()

    conn.close()

    if not row:
        return default

    return row[0]


def _set_setting(
    key: str,
    value
):
    conn = connect()

    conn.execute("""
        INSERT INTO settings
        (key, value)
        VALUES (?, ?)

        ON CONFLICT(key)
        DO UPDATE SET
            value = excluded.value
    """, (
        key,
        str(value)
    ))

    conn.commit()
    conn.close()


# =========================================================
# STARS
# =========================================================

def get_stars_rate():
    value = _get_setting(
        "stars_rate",
        "1.32"
    )

    try:
        return float(value)
    except Exception:
        return 1.32


def set_stars_rate(rate: float):
    _set_setting(
        "stars_rate",
        rate
    )


def get_stars_price(stars: int):
    conn = connect()

    row = conn.execute("""
        SELECT price
        FROM prices
        WHERE stars = ?
        LIMIT 1
    """, (
        stars,
    )).fetchone()

    conn.close()

    if row:
        return int(row[0])

    rate = get_stars_rate()

    return round(
        stars * rate
    )


def get_price(stars: int):
    return get_stars_price(stars)


def set_price(
    stars: int,
    price: int
):
    conn = connect()

    conn.execute("""
        INSERT INTO prices
        (stars, price)
        VALUES (?, ?)

        ON CONFLICT(stars)
        DO UPDATE SET
            price = excluded.price
    """, (
        stars,
        price
    ))

    conn.commit()
    conn.close()


# =========================================================
# PREMIUM
# =========================================================

def get_premium_price(months: int):
    conn = connect()

    row = conn.execute("""
        SELECT price
        FROM premium_prices
        WHERE months = ?
        LIMIT 1
    """, (
        months,
    )).fetchone()

    conn.close()

    if not row:
        return 0

    return int(row[0])


def set_premium_price(
    months: int,
    price: int
):
    conn = connect()

    conn.execute("""
        INSERT INTO premium_prices
        (months, price)
        VALUES (?, ?)

        ON CONFLICT(months)
        DO UPDATE SET
            price = excluded.price
    """, (
        months,
        price
    ))

    conn.commit()
    conn.close()


# =========================================================
# GRAM MARKUP
# =========================================================

def get_gram_markup():
    value = _get_setting(
        "gram_markup",
        "5.0"
    )

    try:
        return float(value)
    except Exception:
        return 5.0


def set_gram_markup(
    markup: float
):
    _set_setting(
        "gram_markup",
        markup
    )


# =========================================================
# GRAM BALANCE
# =========================================================

def get_gram_balance():
    value = _get_setting(
        "gram_balance",
        "0"
    )

    try:
        return float(value)
    except Exception:
        return 0.0


def set_gram_balance(
    balance: float
):
    if balance < 0:
        balance = 0

    _set_setting(
        "gram_balance",
        balance
    )


# =========================================================
# GRAM ENABLED
# =========================================================

def get_gram_enabled():
    value = _get_setting(
        "gram_enabled",
        "0"
    )

    return str(value) == "1"


def set_gram_enabled(
    enabled: bool
):
    _set_setting(
        "gram_enabled",
        "1" if enabled else "0"
    )


# =========================================================
# GRAM PAYMENT WALLET
# =========================================================

def get_gram_payment_wallet():
    return _get_setting(
        "gram_payment_wallet",
        ""
    )


def set_gram_payment_wallet(
    wallet: str
):
    _set_setting(
        "gram_payment_wallet",
        wallet
    )


# =========================================================
# PAYMENT DETAILS
# =========================================================

def get_payment_card():
    return _get_setting(
        "payment_card",
        ""
    )


def set_payment_card(
    card: str
):
    _set_setting(
        "payment_card",
        card
    )


def get_payment_bank():
    return _get_setting(
        "payment_bank",
        ""
    )


def set_payment_bank(
    bank: str
):
    _set_setting(
        "payment_bank",
        bank
    )


def get_payment_name():
    return _get_setting(
        "payment_name",
        ""
    )


def set_payment_name(
    name: str
):
    _set_setting(
        "payment_name",
        name
    )


def get_payment_details():
    return {
        "card": get_payment_card(),
        "bank": get_payment_bank(),
        "name": get_payment_name(),
        "gram_wallet": get_gram_payment_wallet()
    }


# =========================================================
# BUTTON STYLES
# =========================================================

VALID_BUTTON_STYLES = {
    "primary",
    "success",
    "danger"
}


def get_button_style(
    button_key: str
):
    conn = connect()

    row = conn.execute("""
        SELECT style
        FROM button_styles
        WHERE button_key = ?
        LIMIT 1
    """, (
        button_key,
    )).fetchone()

    conn.close()

    if not row:
        return "primary"

    style = row[0]

    if style not in VALID_BUTTON_STYLES:
        return "primary"

    return style


def set_button_style(
    button_key: str,
    style: str
):
    if style not in VALID_BUTTON_STYLES:
        style = "primary"

    conn = connect()

    conn.execute("""
        INSERT INTO button_styles
        (button_key, style)
        VALUES (?, ?)

        ON CONFLICT(button_key)
        DO UPDATE SET
            style = excluded.style
    """, (
        button_key,
        style
    ))

    conn.commit()
    conn.close()


# =========================================================
# ORDERS
# =========================================================

def create_order(
    user_id,
    username,
    receiver,
    stars,
    price,
    product_type="stars",
    premium_months=0,
    gram_amount=0,
    gram_wallet=""
):
    conn = connect()

    try:
        cursor = conn.cursor()

        # =================================================
        # GRAM RESERVATION
        # =================================================

        if product_type == "gram":

            amount = float(
                gram_amount or 0
            )

            if amount <= 0:
                conn.rollback()
                return None

            row = cursor.execute("""
                SELECT value
                FROM settings
                WHERE key = 'gram_balance'
                LIMIT 1
            """).fetchone()

            current_balance = (
                float(row[0])
                if row
                else 0.0
            )

            if amount > current_balance:
                conn.rollback()
                return None

            new_balance = (
                current_balance - amount
            )

            cursor.execute("""
                UPDATE settings
                SET value = ?
                WHERE key = 'gram_balance'
            """, (
                str(new_balance),
            ))

            if new_balance <= 0:
                cursor.execute("""
                    UPDATE settings
                    SET value = '0'
                    WHERE key = 'gram_enabled'
                """)

        # =================================================
        # CREATE ORDER
        # =================================================

        cursor.execute("""
            INSERT INTO orders (
                user_id,
                username,
                receiver,
                stars,
                price,
                status,
                product_type,
                premium_months,
                receipt_file_id,
                gram_amount,
                gram_wallet
            )
            VALUES (
                ?, ?, ?, ?, ?,
                'waiting',
                ?, ?, '',
                ?, ?
            )
        """, (
            user_id,
            username,
            receiver,
            stars,
            price,
            product_type,
            premium_months,
            float(gram_amount or 0),
            gram_wallet or ""
        ))

        order_id = cursor.lastrowid

        conn.commit()

        return order_id

    except Exception:
        conn.rollback()
        return None

    finally:
        conn.close()


# =========================================================
# GET ORDER
# =========================================================

def get_order(
    order_id: int
):
    conn = connect()

    row = conn.execute("""
        SELECT
            user_id,
            username,
            receiver,
            stars,
            price,
            status,
            created_at,
            product_type,
            premium_months,
            receipt_file_id,
            gram_amount,
            gram_wallet
        FROM orders
        WHERE id = ?
    """, (
        order_id,
    )).fetchone()

    conn.close()

    if not row:
        return None

    return tuple(row)


# =========================================================
# GET ALL ORDERS
# =========================================================

def get_all_orders():
    conn = connect()

    rows = conn.execute("""
        SELECT
            id,
            user_id,
            username,
            receiver,
            stars,
            price,
            status,
            created_at,
            product_type,
            premium_months,
            receipt_file_id,
            gram_amount,
            gram_wallet
        FROM orders
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return [
        tuple(row)
        for row in rows
    ]


# =========================================================
# RECEIPT
# =========================================================

def set_receipt(
    order_id: int,
    file_id: str
):
    conn = connect()

    conn.execute("""
        UPDATE orders
        SET receipt_file_id = ?
        WHERE id = ?
    """, (
        file_id,
        order_id
    ))

    conn.commit()
    conn.close()


# =========================================================
# COMPLETE ORDER
# =========================================================

def complete_order(
    order_id: int
):
    conn = connect()

    conn.execute("""
        UPDATE orders
        SET status = 'completed'
        WHERE id = ?
        AND status = 'waiting'
    """, (
        order_id,
    ))

    conn.commit()
    conn.close()


# =========================================================
# CANCEL ORDER
# =========================================================

def cancel_order(
    order_id: int
):
    conn = connect()

    try:
        cursor = conn.cursor()

        order = cursor.execute("""
            SELECT
                product_type,
                gram_amount,
                status
            FROM orders
            WHERE id = ?
        """, (
            order_id,
        )).fetchone()

        if not order:
            conn.rollback()
            return

        product_type = order[0]
        gram_amount = float(
            order[1] or 0
        )
        status = order[2]

        if status != "waiting":
            conn.rollback()
            return

        # =================================================
        # RETURN GRAM
        # =================================================

        if (
            product_type == "gram"
            and gram_amount > 0
        ):

            row = cursor.execute("""
                SELECT value
                FROM settings
                WHERE key = 'gram_balance'
                LIMIT 1
            """).fetchone()

            current_balance = (
                float(row[0])
                if row
                else 0.0
            )

            new_balance = (
                current_balance
                + gram_amount
            )

            cursor.execute("""
                INSERT INTO settings
                (key, value)
                VALUES ('gram_balance', ?)

                ON CONFLICT(key)
                DO UPDATE SET
                    value = excluded.value
            """, (
                str(new_balance),
            ))

            if new_balance > 0:
                cursor.execute("""
                    INSERT INTO settings
                    (key, value)
                    VALUES ('gram_enabled', '1')

                    ON CONFLICT(key)
                    DO UPDATE SET
                        value = '1'
                """)

        # =================================================
        # CANCEL ORDER
        # =================================================

        cursor.execute("""
            UPDATE orders
            SET status = 'cancelled'
            WHERE id = ?
            AND status = 'waiting'
        """, (
            order_id,
        ))

        conn.commit()

    except Exception:
        conn.rollback()

    finally:
        conn.close()


# =========================================================
# ORDER STATISTICS
# =========================================================

def count_orders():
    conn = connect()

    result = conn.execute("""
        SELECT COUNT(*)
        FROM orders
    """).fetchone()[0]

    conn.close()

    return result


def count_completed_orders():
    conn = connect()

    result = conn.execute("""
        SELECT COUNT(*)
        FROM orders
        WHERE status = 'completed'
    """).fetchone()[0]

    conn.close()

    return result


# =========================================================
# ADMINS
# =========================================================

def add_admin(
    user_id: int
):
    conn = connect()

    conn.execute("""
        INSERT OR IGNORE INTO admins
        (user_id)
        VALUES (?)
    """, (
        user_id,
    ))

    conn.commit()
    conn.close()


def remove_admin(
    user_id: int
):
    conn = connect()

    conn.execute("""
        DELETE FROM admins
        WHERE user_id = ?
    """, (
        user_id,
    ))

    conn.commit()
    conn.close()


def get_admins():
    conn = connect()

    rows = conn.execute("""
        SELECT user_id
        FROM admins
        ORDER BY user_id
    """).fetchall()

    conn.close()

    return [
        row[0]
        for row in rows
    ]


def is_admin(
    user_id: int
):
    conn = connect()

    result = conn.execute("""
        SELECT 1
        FROM admins
        WHERE user_id = ?
        LIMIT 1
    """, (
        user_id,
    )).fetchone()

    conn.close()

    return result is not None


# =========================================================
# INIT
# =========================================================

init_db()


# =========================================================
# OWNER
# =========================================================

try:
    from config import ADMIN_ID

    if ADMIN_ID:
        add_admin(
            ADMIN_ID
        )

except Exception as error:
    print(
        f"Ошибка добавления владельца: {error}"
    )