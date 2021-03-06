from _basetest import BaseTest
from nurdbar import NurdBar, model
from decimal import Decimal
import datetime
import sqlalchemy.exc
import traceback
import logging

class TestModel(BaseTest):

    def setUp(self):
        super(TestModel,self).setUp()
        self.session=self.bar.session
        self.log=logging.getLogger(__name__)

    def _commit(self):
        try:
            self.session.commit()
            self.session.flush()
        except Exception:
            self.log.error("Error occured during commit:\n%s"%traceback.format_exc())
            self.session.rollback()
            raise

    def _addObject(self,obj):
        self.session.add(obj)
        self._commit()
        return obj

    def test_uniqueItem(self):
        item=self._addObject(model.Item('123456789',0.50))
        item=self._addObject(model.Item('123456789',0.25))
        self.assertEqual(self.session.query(model.Item).filter_by(barcode='123456789').count(),2)
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            item=self._addObject(model.Item('123456789',0.50))

    def test_uniqueMember(self):
        member=self._addObject(model.Member('133713371337','SmokeyD'))
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
           self._addObject(model.Member('133713371337','SmokeyD'))

    def test_memberTransactions(self):
        item=self._addObject(model.Item('123456789',0.50))
        member=self._addObject(model.Member('133713371337','SmokeyD'))
        trans = self._addObject(model.Transaction())
        trans.member=member
        trans.item=item
        trans.transaction_price=-10*item.sell_price
        self._commit()
        self.assertEqual(member.transactions,[trans])
        self.assertEqual(member.allTransactions,[trans])
        self.assertEqual(member.negativeTransactions,[trans])
        self.assertEqual(member.positiveTransactions,[])
        trans.archived=True
        self._commit()
        self.assertEqual(member.transactions,[])
        self.assertEqual(member.allTransactions,[trans])
        self.assertEqual(member.negativeTransactions,[])
        self.assertEqual(member.positiveTransactions,[])

    def test_creationDateTime(self):
        item=self._addObject(model.Item('123456789',0.50))
        now=datetime.datetime.now().timetuple()[:5]
        self.assertEqual(item.creationDateTime.timetuple()[:5],now)
        member=self._addObject(model.Member('133713371337','SmokeyD'))
        now=datetime.datetime.now().timetuple()[:5]
        self.assertEqual(member.creationDateTime.timetuple()[:5],now)

    def test_lastModifiedDateTime(self):
        item=self._addObject(model.Item('123456789',0.50))
        self.assertEqual(item.creationDateTime.timetuple()[:6],item.lastModifiedDateTime.timetuple()[:6])
        member=self._addObject(model.Member('133713371337','SmokeyD'))
        self.assertEqual(member.creationDateTime.timetuple()[:6],member.lastModifiedDateTime.timetuple()[:6])
        item.price=0.75
        member.nick='smokeyD'
        self._commit()
        self.assertTrue(item.lastModifiedDateTime>item.creationDateTime)
        self.assertTrue(member.lastModifiedDateTime>member.creationDateTime)
