import psycopg2
import SETTINGS
import accounts


def create_db():
    # Данные для подключения к базе данных
    dbname = SETTINGS.dbname
    user = SETTINGS.user
    password = SETTINGS.password
    host = SETTINGS.host
    port = SETTINGS.port

    # Определение полей таблицы
    fields = [
        'impressions',
        'reach',
        'frequency',
        'clicks',
        'cost_per_link_click',
        'cpm',
        'ctr',
        'spend',
        'actions',
        'unique_actions',
        'conversions',
        'conversion_values',
        'cost_per_unique_click',
        'cost_per_action_type',
        'cost_per_conversion',
        'purchase_roas',
        'mobile_app_purchase_roas',
        'website_purchase_roas',
        'video_play_actions',
        'video_p100_watched_actions',
        'video_p25_watched_actions',
        'video_p50_watched_actions',
        'video_p75_watched_actions',
        'video_p95_watched_actions',
        'cost_per_video_view'
    ]

    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()

        fields_with_types = ', '.join([f"{field} VARCHAR(500)" for field in fields])
        for _ in accounts.app_id:
            create_table_query = f"CREATE TABLE IF NOT EXISTS {str(_)} ({fields_with_types});"
            cursor.execute(create_table_query)

        conn.commit()

        cursor.close()
        conn.close()

        print("Таблицы успешно созданы.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

