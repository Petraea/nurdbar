from _basetest import BaseTest
from nurdbar import NurdBar, BarcodeTypes, model
from decimal import Decimal

class TestBar(BaseTest):

    def setUp(self):
        super(TestBar,self).setUp()
        self.member=self.bar.addMember(133713371337,'SmokeyD')
        self.item=self.bar.addItem(12312893712938,0.50)

    def test_barcodeType(self):
        self.assertEqual(self.bar.getBarcodeType(self.item.barcode),BarcodeTypes.ITEMBARCODE)
        self.assertEqual(self.bar.getBarcodeType(self.member.barcode),BarcodeTypes.MEMBERBARCODE)
        self.assertNotEqual(self.bar.getBarcodeType(self.member.barcode),BarcodeTypes.ITEMBARCODE)
        self.assertNotEqual(self.bar.getBarcodeType(self.item.barcode),BarcodeTypes.MEMBERBARCODE)

    def test_filled_tables(self):
        payment_item=self.bar.getItemByBarcode(1010101010)
        self.assertAlmostEqual(payment_item.price,Decimal(0.01))

    def test_item(self):
        item=self.bar.getItemByBarcode(12312893712938)
        self.assertEqual(item.price,0.50)

    def test_member(self):
        member=self.bar.getMemberByNick('SmokeyD')
        self.assertEqual(member.barcode,133713371337)

    def test_duplicateItemBarcode(self):
        item2=self.bar.addItem(12312893712938,0.25)
        item=self.bar.getItemByBarcode(12312893712938)
        self.assertEqual(item.price,0.50)

    def test_transaction(self):
        self.bar.addTransaction(self.item,self.member,10) #add beer
        self.assertEqual(self.member.balance,5)
        self.assertEqual(self.item.stock,10)
        self.bar.addTransaction(self.item,self.member,-1) #take a beer
        self.assertEqual(self.item.stock,9)
        self.assertEqual(self.member.balance,4.50)
        self.bar.addTransaction(self.item,self.member,-1) #take a beer
        self.assertEqual(self.item.stock,8)
        self.assertEqual(self.member.balance,4)
        self.bar.addTransaction(self.item,self.member,-1) #take a beer
        self.assertEqual(self.item.stock,7)
        self.assertEqual(self.member.balance,3.50)
        self.bar.addTransaction(self.item,self.member,-8) #take 7 beer
        self.assertEqual(self.item.stock,-1)
        self.assertEqual(self.member.balance,-0.50)

    def test_giveItem(self):
        with self.assertRaises(ValueError):
            self.bar.giveItem('133713371338',self.item.barcode,0.10) #give a beer, should fail since member is unkown
        trans=self.bar.giveItem(self.member.barcode,self.item.barcode,0.50,10) #add 10 beer
        trans2=self.bar.giveItem(self.member.barcode,self.item.barcode,0.25,10) #add 10 non-existing beers, which should be added as items
        self.assertEqual(self.bar.session.query(model.Item).filter_by(barcode=self.item.barcode).count(),2)
        self.assertEqual(self.item.stock,10)
        self.assertEqual(trans2.item.stock,10)
        self.assertEqual(self.member.balance,7.50)

    def test_takeItem(self):
        with self.assertRaises(ValueError):
            self.bar.takeItem(self.member.barcode,self.item.barcode) #take a beer, should fail since no stock present
        self.bar.giveItem(self.member.barcode,self.item.barcode,0.50,10) #add 10 beer
        with self.assertRaises(ValueError):
            self.bar.takeItem('133713371338',self.item.barcode) #take a beer, should fail since member is unkown
        self.bar.takeItem(self.member.barcode,self.item.barcode) #take a beer
        self.assertEqual(self.item.stock,9)
        self.assertEqual(self.member.balance,4.50)
        self.bar.takeItem(self.member.barcode,self.item.barcode,3) #take 3 beer
        self.assertEqual(self.item.stock,6)
        self.assertEqual(self.member.balance,3.00)
        trans=self.bar.giveItem(self.member.barcode,self.item.barcode,0.25,10) #add 10 cheaper beer
        self.bar.takeItem(self.member.barcode,self.item.barcode,8) #take 8 beer (6 expenise ones, 2 cheap ones)
        self.assertEqual(self.item.stock,0)
        self.assertEqual(trans.item.stock,8)
        self.assertEqual(self.member.balance,2.00)

    def test_payment(self):
        self.bar.addTransaction(self.item,self.member,-10) #take 10 beer
        self.assertEqual(self.member.balance,-5)
        self.bar.payAmount(self.member,6.50) #pay 6.50 euro
        self.assertEqual(self.member.balance,1.5)
        self.fail("Test correct items are paid and archive transactions")
