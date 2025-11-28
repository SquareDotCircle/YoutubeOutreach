#!/usr/bin/env python3
"""
YouTube Channel Database Manager
Stores channel information in SQLite for easy access and querying
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

DATABASE_FILE = "youtube_channels.db"

class ChannelDatabase:
    def __init__(self, db_file: str = DATABASE_FILE):
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.cursor = self.conn.cursor()
        
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.commit()
            self.conn.close()
            
    def migrate_schema(self):
        """Add new columns to existing database"""
        new_columns = [
            ('avg_views_per_video', 'INTEGER'),
            ('median_views', 'INTEGER'),
            ('engagement_rate', 'REAL'),
            ('view_rate', 'REAL'),
            ('total_video_count', 'INTEGER'),
            ('avg_video_length', 'INTEGER'),
            ('upload_frequency', 'REAL'),
            ('videos_last_30_days', 'INTEGER'),
            ('last_upload_date', 'TEXT'),
            ('consistency_score', 'REAL'),
            ('growth_trend', 'TEXT'),
            ('recent_viral_count', 'INTEGER'),
            ('channel_description', 'TEXT'),
            ('channel_country', 'TEXT'),
            ('channel_join_date', 'TEXT'),
            ('business_email', 'TEXT'),
            ('website_url', 'TEXT'),
            ('instagram_handle', 'TEXT'),
            ('twitter_handle', 'TEXT'),
            ('has_affiliate_store', 'INTEGER DEFAULT 0'),
            ('has_patreon', 'INTEGER DEFAULT 0'),
        ]
        
        # Get existing columns
        self.cursor.execute("PRAGMA table_info(channels)")
        existing_columns = {row[1] for row in self.cursor.fetchall()}
        
        # Add missing columns
        for col_name, col_type in new_columns:
            if col_name not in existing_columns:
                try:
                    self.cursor.execute(f'ALTER TABLE channels ADD COLUMN {col_name} {col_type}')
                    print(f"✓ Added column: {col_name}")
                except sqlite3.OperationalError:
                    pass  # Column already exists
        
        self.conn.commit()
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT UNIQUE NOT NULL,
                channel_name TEXT NOT NULL,
                channel_url TEXT NOT NULL,
                subscriber_count INTEGER,
                view_count INTEGER,
                added_date TEXT,
                last_updated TEXT,
                category TEXT,
                notes TEXT,
                
                -- Enhanced metrics (Tier 1)
                avg_views_per_video INTEGER,
                median_views INTEGER,
                engagement_rate REAL,
                view_rate REAL,
                
                -- Content analysis
                total_video_count INTEGER,
                avg_video_length INTEGER,
                upload_frequency REAL,
                videos_last_30_days INTEGER,
                last_upload_date TEXT,
                consistency_score REAL,
                
                -- Growth indicators
                growth_trend TEXT,
                recent_viral_count INTEGER,
                
                -- Channel description
                channel_description TEXT,
                channel_country TEXT,
                channel_join_date TEXT,
                
                -- Contact info
                business_email TEXT,
                website_url TEXT,
                instagram_handle TEXT,
                twitter_handle TEXT,
                has_affiliate_store INTEGER DEFAULT 0,
                has_patreon INTEGER DEFAULT 0
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT NOT NULL,
                contact_type TEXT NOT NULL,
                contact_value TEXT NOT NULL,
                verified INTEGER DEFAULT 0,
                added_date TEXT,
                FOREIGN KEY (channel_id) REFERENCES channels (channel_id),
                UNIQUE(channel_id, contact_type, contact_value)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT UNIQUE NOT NULL,
                channel_id TEXT NOT NULL,
                video_title TEXT,
                video_url TEXT,
                view_count INTEGER,
                added_date TEXT,
                FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_terms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_term TEXT UNIQUE NOT NULL,
                used_date TEXT,
                results_count INTEGER DEFAULT 0,
                source TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS outreach (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT NOT NULL,
                contact_date TEXT,
                contact_method TEXT,
                response_received INTEGER DEFAULT 0,
                response_date TEXT,
                status TEXT,
                notes TEXT,
                FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
            )
        ''')
        
        self.conn.commit()
        print("✓ Database tables created")
        
    def add_channel(self, channel_data: Dict) -> bool:
        """Add or update a channel in the database with enhanced metrics"""
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO channels 
                (channel_id, channel_name, channel_url, subscriber_count, 
                 view_count, added_date, last_updated, category, notes,
                 avg_views_per_video, median_views, engagement_rate, view_rate,
                 total_video_count, avg_video_length, upload_frequency, 
                 videos_last_30_days, last_upload_date, consistency_score,
                 growth_trend, recent_viral_count, channel_description,
                 channel_country, channel_join_date, business_email,
                 website_url, instagram_handle, twitter_handle,
                 has_affiliate_store, has_patreon)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                channel_data.get('channel_id'),
                channel_data.get('channel_name'),
                channel_data.get('channel_url'),
                channel_data.get('subscriber_count', 0),
                channel_data.get('view_count', 0),
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                channel_data.get('category', 'Unknown'),
                channel_data.get('notes', ''),
                # Enhanced metrics
                channel_data.get('avg_views_per_video'),
                channel_data.get('median_views'),
                channel_data.get('engagement_rate'),
                channel_data.get('view_rate'),
                channel_data.get('total_video_count'),
                channel_data.get('avg_video_length'),
                channel_data.get('upload_frequency'),
                channel_data.get('videos_last_30_days'),
                channel_data.get('last_upload_date'),
                channel_data.get('consistency_score'),
                channel_data.get('growth_trend'),
                channel_data.get('recent_viral_count'),
                channel_data.get('channel_description'),
                channel_data.get('channel_country'),
                channel_data.get('channel_join_date'),
                channel_data.get('business_email'),
                channel_data.get('website_url'),
                channel_data.get('instagram_handle'),
                channel_data.get('twitter_handle'),
                channel_data.get('has_affiliate_store', 0),
                channel_data.get('has_patreon', 0)
            ))
            
            # Also add contact info if present
            if channel_data.get('business_email'):
                self.add_contact(channel_data['channel_id'], 'email', channel_data['business_email'])
            if channel_data.get('instagram_handle'):
                self.add_contact(channel_data['channel_id'], 'instagram', channel_data['instagram_handle'])
            if channel_data.get('twitter_handle'):
                self.add_contact(channel_data['channel_id'], 'twitter', channel_data['twitter_handle'])
            if channel_data.get('website_url'):
                self.add_contact(channel_data['channel_id'], 'website', channel_data['website_url'])
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding channel: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def add_contact(self, channel_id: str, contact_type: str, contact_value: str) -> bool:
        """Add a contact for a channel"""
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO contacts 
                (channel_id, contact_type, contact_value, added_date)
                VALUES (?, ?, ?, ?)
            ''', (channel_id, contact_type, contact_value, datetime.now().isoformat()))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding contact: {e}")
            return False
            
    def add_video(self, video_data: Dict) -> bool:
        """Add a video to the database"""
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO videos 
                (video_id, channel_id, video_title, video_url, view_count, added_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                video_data.get('video_id'),
                video_data.get('channel_id'),
                video_data.get('video_title'),
                video_data.get('video_url'),
                video_data.get('view_count', 0),
                datetime.now().isoformat()
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding video: {e}")
            return False
            
    def get_channel(self, channel_id: str) -> Optional[Dict]:
        """Get a channel by ID"""
        self.cursor.execute('SELECT * FROM channels WHERE channel_id = ?', (channel_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
        
    def get_all_channels(self, category: Optional[str] = None) -> List[Dict]:
        """Get all channels, optionally filtered by category"""
        if category:
            self.cursor.execute('SELECT * FROM channels WHERE category = ? ORDER BY subscriber_count DESC', (category,))
        else:
            self.cursor.execute('SELECT * FROM channels ORDER BY subscriber_count DESC')
        return [dict(row) for row in self.cursor.fetchall()]
        
    def get_contacts(self, channel_id: str) -> List[Dict]:
        """Get all contacts for a channel"""
        self.cursor.execute('SELECT * FROM contacts WHERE channel_id = ?', (channel_id,))
        return [dict(row) for row in self.cursor.fetchall()]
        
    def search_channels(self, query: str) -> List[Dict]:
        """Search channels by name"""
        self.cursor.execute('''
            SELECT * FROM channels 
            WHERE channel_name LIKE ? 
            ORDER BY subscriber_count DESC
        ''', (f'%{query}%',))
        return [dict(row) for row in self.cursor.fetchall()]
        
    def get_channels_by_subscriber_range(self, min_subs: int, max_subs: int) -> List[Dict]:
        """Get channels within a subscriber count range"""
        self.cursor.execute('''
            SELECT * FROM channels 
            WHERE subscriber_count BETWEEN ? AND ?
            ORDER BY subscriber_count DESC
        ''', (min_subs, max_subs))
        return [dict(row) for row in self.cursor.fetchall()]
        
    def add_search_term(self, term: str, source: str = 'manual') -> bool:
        """Add a search term to the database"""
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO search_terms (search_term, used_date, source)
                VALUES (?, ?, ?)
            ''', (term, datetime.now().isoformat(), source))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding search term: {e}")
            return False
            
    def update_search_term_results(self, term: str, count: int):
        """Update the results count for a search term"""
        self.cursor.execute('''
            UPDATE search_terms SET results_count = ? WHERE search_term = ?
        ''', (count, term))
        self.conn.commit()
        
    def get_all_search_terms(self) -> List[Dict]:
        """Get all search terms"""
        self.cursor.execute('SELECT * FROM search_terms ORDER BY used_date DESC')
        return [dict(row) for row in self.cursor.fetchall()]
        
    def add_outreach_record(self, channel_id: str, method: str, notes: str = '') -> bool:
        """Add an outreach record"""
        try:
            self.cursor.execute('''
                INSERT INTO outreach (channel_id, contact_date, contact_method, status, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (channel_id, datetime.now().isoformat(), method, 'contacted', notes))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding outreach record: {e}")
            return False
            
    def export_to_json(self, filename: str = 'channels_export.json'):
        """Export all data to JSON"""
        channels = self.get_all_channels()
        
        # Add contacts to each channel
        for channel in channels:
            channel['contacts'] = self.get_contacts(channel['channel_id'])
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(channels, f, indent=2, ensure_ascii=False)
            
        print(f"✓ Exported {len(channels)} channels to {filename}")
        
    def get_stats(self) -> Dict:
        """Get database statistics"""
        stats = {}
        
        self.cursor.execute('SELECT COUNT(*) FROM channels')
        stats['total_channels'] = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM contacts WHERE contact_type = "email"')
        stats['channels_with_email'] = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(DISTINCT channel_id) FROM contacts WHERE contact_type = "instagram"')
        stats['channels_with_instagram'] = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM channels WHERE category = "prepper"')
        stats['prepper_channels'] = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM channels WHERE subscriber_count BETWEEN 10000 AND 500000')
        stats['target_range_channels'] = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM search_terms')
        stats['total_search_terms'] = self.cursor.fetchone()[0]
        
        return stats


def import_existing_data(db: ChannelDatabase):
    """Import data from existing CSV files"""
    import csv
    
    # Import from creator_contacts.csv
    try:
        with open('creator_contacts.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                channel_data = {
                    'channel_id': row['Channel URL'].split('/')[-1],
                    'channel_name': row['Channel Name'],
                    'channel_url': row['Channel URL'],
                    'subscriber_count': int(row['Subscribers']) if row['Subscribers'].isdigit() else 0,
                    'category': 'prepper' if any(kw in row['Channel Name'].lower() 
                                for kw in ['prepper', 'survival', 'bug out']) else 'other'
                }
                
                if db.add_channel(channel_data):
                    count += 1
                    
                    # Add contacts
                    channel_id = channel_data['channel_id']
                    if row.get('Email'):
                        for email in row['Email'].split(';'):
                            db.add_contact(channel_id, 'email', email.strip())
                    if row.get('Instagram'):
                        for ig in row['Instagram'].split(';'):
                            db.add_contact(channel_id, 'instagram', ig.strip())
                    if row.get('Twitter'):
                        for tw in row['Twitter'].split(';'):
                            db.add_contact(channel_id, 'twitter', tw.strip())
                    if row.get('Facebook'):
                        for fb in row['Facebook'].split(';'):
                            db.add_contact(channel_id, 'facebook', fb.strip())
                            
        print(f"✓ Imported {count} channels from creator_contacts.csv")
    except FileNotFoundError:
        print("⚠ creator_contacts.csv not found")
        
    # Import from discovered_channels.csv
    try:
        with open('discovered_channels.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                channel_data = {
                    'channel_id': row['Channel URL'].split('/')[-1],
                    'channel_name': row['Channel Name'],
                    'channel_url': row['Channel URL'],
                    'subscriber_count': int(row['Subscribers']) if row['Subscribers'].isdigit() else 0,
                    'category': 'discovered'
                }
                
                if db.add_channel(channel_data):
                    count += 1
                    
                # Add sample video
                if row.get('Sample Video URL'):
                    video_data = {
                        'video_id': row['Sample Video URL'].split('=')[-1],
                        'channel_id': channel_data['channel_id'],
                        'video_title': row.get('Sample Video Title', ''),
                        'video_url': row['Sample Video URL']
                    }
                    db.add_video(video_data)
                    
        print(f"✓ Imported {count} channels from discovered_channels.csv")
    except FileNotFoundError:
        print("⚠ discovered_channels.csv not found")


def main():
    """Initialize database and import existing data"""
    print("🗄️ YouTube Channel Database Setup")
    print("=" * 50)
    
    db = ChannelDatabase()
    db.connect()
    db.create_tables()
    
    # Import existing data
    import_existing_data(db)
    
    # Show stats
    print("\n📊 Database Statistics:")
    stats = db.get_stats()
    for key, value in stats.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    # Export to JSON
    db.export_to_json()
    
    db.close()
    print("\n✓ Database setup complete!")
    print(f"✓ Database file: {DATABASE_FILE}")


if __name__ == "__main__":
    main()

