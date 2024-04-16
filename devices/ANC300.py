from pymeasure.instruments.attocube.anc300 import ANC300Controller, Axis
from pymeasure.instruments import Instrument


class ANC300():
    def __init__(self, adress):
        self.device = ANC300Controller(adress)
        
    def serial(self):
        ans = Axis(1, self.device).serial_nr()
        return ans
        
    def close(self):
        pass
        
def main():
    device = ANC300("TCPIP::192.168.1.90::7230::SOCKET")
    try:
        print(device.serial())
    except Exception as ex:
        print(ex)
    finally:
        device.close()
        
if __name__ == '__main__':
    main()