from twisted.protocols import basic
from twisted.internet import protocol, reactor, serialport
from nurdbar.plugins.api import *
from nurdbar.events import BarcodeScannedEvent, OutOfStockEvent, MemberBarcodeScannedEvent
from nurdbar import exceptions
import traceback
import logging
log=logging.getLogger(__name__)


class BarcodeProtocol(basic.LineReceiver):

    def __init__(self,bar):
        self.bar=bar

    def connectionLost(self,reason):
        print('connection Lost')
        BarcodeScannedEvent.unregister(self.printBarcode)
        OutOfStockEvent.unregister(self.printOutOfStockEvent)

    def connectionMade(self):
        print('connection Made')
        BarcodeScannedEvent.register(self.printBarcode)
        OutOfStockEvent.register(self.printOutOfStockEvent)
        MemberBarcodeScannedEvent.register(self.printMember)

    def printMember(self,event):
        member=event.attributes['member']
        print("Found member %s"%member.member_id)

    def printOutOfStockEvent(self,event):
        item=event.attributes['item']
        print('Item %s is out of stock'%item.item_id)

    def printBarcode(self,event):
        barcode=event.attributes['barcode']
        print('Scanned the following barcode: %s'%barcode)

    def lineReceived(self, barcode):
        barcode=BarcodeScannedEvent.fire(barcode)
        try:
            self.bar.handleBarcode(barcode)
        except exceptions.ItemOutOfStockError:
            log.warn('Item out of stock')
            self.bar.reset_handlestate()
        except Exception:
            self.bar.resetHandleState()
            log.error(traceback.format_exc())


@TransportInterfacePlugin
def getLocalInterfacePlugin(bar,reactor):
    log.info('Starting barcode monitor')
    port=bar.config.get('scanner','port')
    log.debug('Using serial port %s'%port)
    baudrate=bar.config.get('scanner','baudrate')
    serialport.SerialPort(BarcodeProtocol(bar),port,reactor, baudrate=baudrate)
