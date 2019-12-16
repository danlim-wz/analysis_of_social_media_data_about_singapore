from instaloader import Instaloader
from time import sleep
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from credentials import credentials

#import passwords
credential = Credentials()

engine = create_engine(credential.psql_endpoint)

metadata = MetaData()
insta = Table('instagram_captions', metadata,
        Column('id', Integer, primary_key=True),
        Column('date', String),
        Column('user', String),
        Column('caption', String),
)
metadata.create_all(engine)

L = Instaloader(sleep=True, quiet=False, user_agent=None, dirname_pattern=None, filename_pattern=None,
                download_pictures=False, download_videos=False, download_video_thumbnails=False,
                download_geotags=False, download_comments=False, save_metadata=False, compress_json=False,
                post_metadata_txt_pattern=None, storyitem_metadata_txt_pattern=None, max_connection_attempts=0,
                commit_mode=False)

while True:
    try:
        for post in L.get_hashtag_posts('singapore'):
            try:
                query = insta.insert().values(date=post.date_local, user=post.owner_username, caption=post.caption)
                conn = engine.connect()
                conn.execute(query)
            except:
                pass
    except:
        sleep(60*10)