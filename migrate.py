# run your db migration scripts here
# see Peewee ORM for complete documentation: http://docs.peewee-orm.com/
from peewee import *
from playhouse.migrate import *
from models import *


# creating tables
print("migrating tables ..")
db.connect()
db.drop_tables([Markets])
db.create_tables([Markets])
#migrator = SqliteMigrator(db)

# add pid in traded pairs
#pid = IntegerField(default=0)
#migrate(
    #migrator.add_column('tradedpairs','pid',pid)
#)


