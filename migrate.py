# run your db migration scripts here
# see Peewee ORM for complete documentation: http://docs.peewee-orm.com/
from peewee import *
from playhouse.migrate import *
from models import *


# creating tables
print("migrating tables ..")
db.connect()
#db.drop_tables([Markets])
#db.create_tables([Markets])
migrator = SqliteMigrator(db)

# add pid in traded pairs
agg = DecimalField(default=0.0)
updated = DateTimeField(default=datetime.datetime.now)
trxid = CharField(null=True)
price = DecimalField(default=0.0)
qty = DecimalField(default=0.0)
migrate(
    #migrator.add_column('markets','agg',agg)
    #migrator.add_column('markets','updated',updated)
    #migrator.add_column('transaction','trxid',trxid)
    migrator.add_column('transaction','price',price),
    migrator.add_column('transaction','qty',qty)
)


