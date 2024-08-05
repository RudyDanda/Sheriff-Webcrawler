# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class SheriffScraperPipeline:
    '''
    Pipeline that cleans items before insertion into database, file, etc.
    '''
    def process_item(self, item, spider):
        return item


import psycopg2
import configparser
import os


script_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_dir, '../config.ini')

config = configparser.ConfigParser(interpolation=None)
config.read(config_file_path)



class SaveToPostgreSQLPipeline:
    '''
    Pipeline that inserts items scraped from spider to PostgreSQL db
    
    '''

    def __init__(self):
        
        # db connection access params
        conn_params = {
            'dbname': config['database']['dbname'],
            'user': config['database']['user'],
            'password': config['database']['password'],
            'host': config['database']['host'],
            'port': config['database']['port']
        }


        self.conn = psycopg2.connect(**conn_params)
        self.cur = self.conn.cursor()

        # In case table is not defined
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS auction_items (
            county TEXT,
            start_date TEXT,
            case_number TEXT NOT NULL,
            parcel_id INTEGER,
            property_address TEXT,
            geocode POINT,
            appraised_value MONEY,
            opening_bid MONEY,
            deposit_requirement MONEY,
            PRIMARY KEY (case_number)
        )
        """)
        self.conn.commit()  # Commit the table creation

    # Function that scrapy looks for to process items in the pipeline
    def process_item(self, item, spider):
        try:
            lat, lon = item['geocode']['lat'], item['geocode']['lon']

            # Define the UPSERT statement
            self.cur.execute("""
                INSERT INTO auction_items (
                    county, 
                    start_date, 
                    case_number, 
                    parcel_id, 
                    property_address, 
                    geocode, 
                    appraised_value, 
                    opening_bid, 
                    deposit_requirement
                ) VALUES (
                    %s, 
                    %s, 
                    %s,
                    %s, 
                    %s, 
                    POINT(%s, %s), 
                    %s, 
                    %s, 
                    %s
                )
                ON CONFLICT (case_number)
                DO UPDATE SET
                    county = EXCLUDED.county,
                    start_date = EXCLUDED.start_date,
                    parcel_id = EXCLUDED.parcel_id,
                    property_address = EXCLUDED.property_address,
                    geocode = EXCLUDED.geocode,
                    appraised_value = EXCLUDED.appraised_value,
                    opening_bid = EXCLUDED.opening_bid,
                    deposit_requirement = EXCLUDED.deposit_requirement;
            """, (
                item['county'],
                item['start_date'],
                item['case_number'],
                item['parcel_id'],
                item['property_address'],
                lon,
                lat,
                item['appraised_value'],
                item['opening_bid'],
                item['deposit_requirement']
            ))

            self.conn.commit()  # Commit the transaction if successful

        except Exception as e:
            self.conn.rollback()  # Rollback the transaction on error
            spider.logger.error(f"Error processing item: {e}")

        return item
    
    # Function that scrapy looks for after spider is done
    def close_spider(self, spider):
        # Close cursor and connection to database
        self.cur.close()
        self.conn.close()


