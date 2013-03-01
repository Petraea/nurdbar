from ConfigParser import SafeConfigParser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base,Member,Item,Transaction
from decimal import Decimal

class NurdBar(object):
    def __init__(self,configfile='nurdbar.cfg'):
        self.config=NurdBar.read_config(configfile)
        self.engine,self.metadata,self.session=NurdBar.setupModel(self.config)

    @staticmethod
    def setupModel(config):
        engine=create_engine(config.get('db','uri'))
        Session = sessionmaker(bind=engine)
        metadata=Base.metadata
        metadata.bind=engine
        session = Session()
        return (engine,metadata,session)

    @staticmethod
    def read_config(configfile):
        config=SafeConfigParser()
        config.readfp(open(configfile,'r'))
        return config

    def giveItem(self,member_barcode,item_barcode,amount=1):
        item=self.getItemByBarcode(item_barcode)
        member=self.getMemberByBarcode(member_barcode)
        return self.addTransaction(item,member,amount)

    def takeItem(self,member_barcode,item_barcode,amount=1):
        item=self.getItemByBarcode(item_barcode)
        member=self.getMemberByBarcode(member_barcode)
        return self.addTransaction(item,member,-amount)

    def fill_tables(self):
        payment_item=self.addItem(1010101010,0.01)

    def create_tables(self):
        self.metadata.create_all()

    def drop_tables(self):
        self.metadata.drop_all()

    def getMemberByBarcode(self,barcode):
        return self.session.query(Member).filter_by(barcode=barcode).first()

    def getMemberByNick(self,nick):
        return self.session.query(Member).filter_by(nick=nick).first()

    def addMember(self,barcode,nick):
        member=Member(barcode,nick)
        self.session.add(member)
        self.session.commit()
        self.session.flush()
        return member

    def getItemByBarcode(self,barcode):
        return self.session.query(Item).filter_by(barcode=barcode).first()

    def getBalance(self,member):
        return member.balance

    def getTransactions(self,member):
        return member.transactions

    def payAmount(self,member,amount):
        payment_item=self.getItemByBarcode(1010101010)
        self.addTransaction(payment_item,member,int(amount*100))

    def addTransaction(self,item,member,count):
        trans=Transaction()
        self.session.add(trans)
        trans.item=item
        trans.member=member
        self.session.commit()
        self.session.flush()
        trans.count=count
        self.session.commit()
        self.session.flush()
        return trans

    def addItem(self,barcode,price):
        item=Item(barcode,price)
        self.session.add(item)
        self.session.commit()
        self.session.flush()
        return item
