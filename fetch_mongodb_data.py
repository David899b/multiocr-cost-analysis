#!/usr/bin/env python3
"""
MongoDB Data Fetcher for MultiOCR Analysis
Connects to MongoDB to fetch real FormConfig schemas and token consumption logs.
"""

import json
import os
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime, timedelta

# Try to import pymongo
try:
    from pymongo import MongoClient
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    print("Warning: pymongo not installed. Install with: pip install pymongo")


class MongoDBFetcher:
    """Fetches data from MultiOCR MongoDB database"""
    
    def __init__(self, connection_string: str, database_name: str = "IAGroupMultiOCRTool"):
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None
    
    def connect(self) -> bool:
        """Connect to MongoDB"""
        if not PYMONGO_AVAILABLE:
            print("Cannot connect: pymongo not installed")
            return False
        
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            print(f"Connected to MongoDB: {self.database_name}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def fetch_form_configs(self, limit: int = None) -> List[Dict]:
        """Fetch FormConfig documents (schemas)"""
        if not self.db:
            print("Not connected to database")
            return []
        
        try:
            collection = self.db.formconfigs
            query = {}
            cursor = collection.find(query)
            
            if limit:
                cursor = cursor.limit(limit)
            
            configs = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            for config in configs:
                if '_id' in config:
                    config['_id'] = str(config['_id'])
            
            print(f"Fetched {len(configs)} FormConfig documents")
            return configs
            
        except Exception as e:
            print(f"Error fetching FormConfigs: {e}")
            return []
    
    def fetch_api_logs(self, days: int = 30, limit: int = None) -> List[Dict]:
        """Fetch ApiLog documents (token consumption logs)"""
        if not self.db:
            print("Not connected to database")
            return []
        
        try:
            collection = self.db.apilogs
            
            # Filter by date range
            start_date = datetime.now() - timedelta(days=days)
            query = {"timestamp": {"$gte": start_date.isoformat()}}
            
            cursor = collection.find(query).sort("timestamp", -1)
            
            if limit:
                cursor = cursor.limit(limit)
            
            logs = list(cursor)
            
            # Convert ObjectId to string
            for log in logs:
                if '_id' in log:
                    log['_id'] = str(log['_id'])
            
            print(f"Fetched {len(logs)} ApiLog documents (last {days} days)")
            return logs
            
        except Exception as e:
            print(f"Error fetching ApiLogs: {e}")
            return []
    
    def fetch_ai_logs(self, days: int = 30, limit: int = None) -> List[Dict]:
        """Fetch AiLog documents (detailed AI processing logs)"""
        if not self.db:
            print("Not connected to database")
            return []
        
        try:
            collection = self.db.ailogs
            
            # Filter by date range
            start_date = datetime.now() - timedelta(days=days)
            query = {"timestamp": {"$gte": start_date.isoformat()}}
            
            cursor = collection.find(query).sort("timestamp", -1)
            
            if limit:
                cursor = cursor.limit(limit)
            
            logs = list(cursor)
            
            # Convert ObjectId to string
            for log in logs:
                if '_id' in log:
                    log['_id'] = str(log['_id'])
            
            print(f"Fetched {len(logs)} AiLog documents (last {days} days)")
            return logs
            
        except Exception as e:
            print(f"Error fetching AiLogs: {e}")
            return []
    
    def fetch_token_prices(self) -> List[Dict]:
        """Fetch TokenPrice documents (pricing configuration)"""
        if not self.db:
            print("Not connected to database")
            return []
        
        try:
            collection = self.db.tokenprices
            cursor = collection.find()
            prices = list(cursor)
            
            # Convert ObjectId to string
            for price in prices:
                if '_id' in price:
                    price['_id'] = str(price['_id'])
            
            print(f"Fetched {len(prices)} TokenPrice documents")
            return prices
            
        except Exception as e:
            print(f"Error fetching TokenPrices: {e}")
            return []
    
    def fetch_api_keys(self) -> List[Dict]:
        """Fetch ApiKey documents (client configurations)"""
        if not self.db:
            print("Not connected to database")
            return []
        
        try:
            collection = self.db.apikeys
            cursor = collection.find()
            keys = list(cursor)
            
            # Convert ObjectId to string and mask secrets
            for key in keys:
                if '_id' in key:
                    key['_id'] = str(key['_id'])
                # Don't expose secrets in analysis
                if 'apiSecret' in key:
                    key['apiSecret'] = "***MASKED***"
            
            print(f"Fetched {len(keys)} ApiKey documents")
            return keys
            
        except Exception as e:
            print(f"Error fetching ApiKeys: {e}")
            return []
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        if not self.db:
            return {}
        
        try:
            stats = {}
            stats['database'] = self.database_name
            
            # Get collection stats
            collections = self.db.list_collection_names()
            stats['collections'] = collections
            
            for coll_name in collections:
                coll = self.db[coll_name]
                stats[f'{coll_name}_count'] = coll.count_documents({})
            
            return stats
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
    
    def export_all_data(self, output_dir: str):
        """Export all relevant data to JSON files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print("\nExporting data from MongoDB...")
        
        # Export FormConfigs
        configs = self.fetch_form_configs()
        if configs:
            configs_path = output_path / "formconfigs.json"
            with open(configs_path, 'w', encoding='utf-8') as f:
                json.dump(configs, f, indent=2, ensure_ascii=False, default=str)
            print(f"  Exported {len(configs)} FormConfigs to {configs_path}")
        
        # Export ApiLogs
        api_logs = self.fetch_api_logs(days=90)
        if api_logs:
            api_logs_path = output_path / "apilogs.json"
            with open(api_logs_path, 'w', encoding='utf-8') as f:
                json.dump(api_logs, f, indent=2, ensure_ascii=False, default=str)
            print(f"  Exported {len(api_logs)} ApiLogs to {api_logs_path}")
        
        # Export AiLogs
        ai_logs = self.fetch_ai_logs(days=90)
        if ai_logs:
            ai_logs_path = output_path / "ailogs.json"
            with open(ai_logs_path, 'w', encoding='utf-8') as f:
                json.dump(ai_logs, f, indent=2, ensure_ascii=False, default=str)
            print(f"  Exported {len(ai_logs)} AiLogs to {ai_logs_path}")
        
        # Export TokenPrices
        prices = self.fetch_token_prices()
        if prices:
            prices_path = output_path / "tokenprices.json"
            with open(prices_path, 'w', encoding='utf-8') as f:
                json.dump(prices, f, indent=2, ensure_ascii=False, default=str)
            print(f"  Exported {len(prices)} TokenPrices to {prices_path}")
        
        # Export ApiKeys
        keys = self.fetch_api_keys()
        if keys:
            keys_path = output_path / "apikeys.json"
            with open(keys_path, 'w', encoding='utf-8') as f:
                json.dump(keys, f, indent=2, ensure_ascii=False, default=str)
            print(f"  Exported {len(keys)} ApiKeys to {keys_path}")
        
        # Export stats
        stats = self.get_database_stats()
        stats_path = output_path / "database_stats.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        print(f"  Exported database stats to {stats_path}")
        
        print(f"\nAll data exported to: {output_path}")


def main():
    """Main function to fetch data from MongoDB"""
    # Connection string
    MONGODB_URI = "mongodb://n8n_user:IAGroupAdmin123@31.97.91.87:27017/IAGroupMultiOCRTool?authSource=admin&directConnection=true&tls=false"
    
    # Initialize fetcher
    fetcher = MongoDBFetcher(MONGODB_URI)
    
    # Connect to database
    if not fetcher.connect():
        print("Failed to connect to MongoDB. Exiting.")
        return
    
    # Export all data
    output_dir = Path(__file__).parent / "production_data"
    fetcher.export_all_data(str(output_dir))
    
    # Print summary
    stats = fetcher.get_database_stats()
    print("\nDatabase Statistics:")
    print("-" * 40)
    for key, value in stats.items():
        if key != 'collections':
            print(f"  {key}: {value}")
    
    print("\nData collection complete!")
    print(f"Next step: Run 'python3 run_analysis.py' to analyze the production data")


if __name__ == "__main__":
    main()
