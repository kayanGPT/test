import psycopg2
from psycopg2 import sql
import os

class DatabaseManager:
    def __init__(self, database_url):
        self.database_url = database_url
        self.conn = None
        self.cur = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.cur = self.conn.cursor()
        except (Exception, psycopg2.Error) as error:
            print(f"Error while connecting to PostgreSQL: {error}")

    def disconnect(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def get_user_by_username(self, username):
        try:
            self.connect()
            self.cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = self.cur.fetchone()
            if user:
                columns = [desc[0] for desc in self.cur.description]
                return dict(zip(columns, user))
            return None
        except Exception as e:
            print(f"Error fetching user by username: {e}")
            return None
        finally:
            self.disconnect()

    def create_user(self, username, email, password):
        try:
            self.connect()
            self.cur.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, password)
            )
            self.conn.commit()
        except Exception as e:
            print(f"Error creating user: {e}")
            self.conn.rollback()
        finally:
            self.disconnect()

    def get_user_videos(self, user_id):
        try:
            self.connect()
            self.cur.execute("""
                SELECT id, title
                FROM videos
                WHERE user_id = %s
                ORDER BY id DESC
            """, (user_id,))
            columns = [desc[0] for desc in self.cur.description]
            results = [dict(zip(columns, row)) for row in self.cur.fetchall()]
            return results
        except Exception as e:
            print(f"Error fetching user videos: {e}")
            return []
        finally:
            self.disconnect()

    def get_user_projects(self, user_id):
        try:
            self.connect()
            self.cur.execute("""
                SELECT id, title, status, shorts_status, merge_status, transcription_status, social_media_status
                FROM projects
                WHERE user_id = %s
                ORDER BY id DESC
            """, (user_id,))
            columns = [desc[0] for desc in self.cur.description]
            results = [dict(zip(columns, row)) for row in self.cur.fetchall()]
            return results
        except Exception as e:
            print(f"Error fetching user projects: {e}")
            return []
        finally:
            self.disconnect()

    def get_calendar_events(self, user_id):
        try:
            self.connect()
            self.cur.execute("""
                SELECT ce.id, v.title, ce.platform, ce.scheduled_time, ce.status
                FROM calendar_events ce
                JOIN videos v ON ce.video_id = v.id
                WHERE v.user_id = %s
                ORDER BY ce.scheduled_time
            """, (user_id,))
            columns = [desc[0] for desc in self.cur.description]
            results = [dict(zip(columns, row)) for row in self.cur.fetchall()]
            return results
        except Exception as e:
            print(f"Error fetching calendar events: {e}")
            return []
        finally:
            self.disconnect()

    def add_calendar_event(self, user_id, video_id, platform, scheduled_time):
        try:
            self.connect()
            self.cur.execute("""
                INSERT INTO calendar_events (video_id, platform, scheduled_time, status)
                VALUES (%s, %s, %s, 'Scheduled')
            """, (video_id, platform, scheduled_time))
            self.conn.commit()
        except Exception as e:
            print(f"Error adding calendar event: {e}")
            self.conn.rollback()
        finally:
            self.disconnect()

    def update_calendar_event(self, event_id, platform, scheduled_time, status):
        try:
            self.connect()
            self.cur.execute("""
                UPDATE calendar_events
                SET platform = %s, scheduled_time = %s, status = %s
                WHERE id = %s
            """, (platform, scheduled_time, status, event_id))
            self.conn.commit()
        except Exception as e:
            print(f"Error updating calendar event: {e}")
            self.conn.rollback()
        finally:
            self.disconnect()

    def delete_calendar_event(self, event_id):
        try:
            self.connect()
            self.cur.execute("DELETE FROM calendar_events WHERE id = %s", (event_id,))
            self.conn.commit()
        except Exception as e:
            print(f"Error deleting calendar event: {e}")
            self.conn.rollback()
        finally:
            self.disconnect()

    def create_tables(self):
        try:
            self.connect()
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL
                )
            """)
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    title VARCHAR(255) NOT NULL,
                    url VARCHAR(255) NOT NULL
                )
            """)
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    video_id INTEGER REFERENCES videos(id),
                    title VARCHAR(255) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    shorts_status VARCHAR(50),
                    merge_status VARCHAR(50),
                    transcription_status VARCHAR(50),
                    social_media_status VARCHAR(50)
                )
            """)
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS calendar_events (
                    id SERIAL PRIMARY KEY,
                    video_id INTEGER REFERENCES videos(id),
                    platform VARCHAR(50) NOT NULL,
                    scheduled_time TIMESTAMP NOT NULL,
                    status VARCHAR(50) NOT NULL
                )
            """)
            self.conn.commit()
            print("Tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")
            self.conn.rollback()
        finally:
            self.disconnect()
