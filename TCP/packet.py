class Header:
    def __init__(self, source, destination, sqNumber=0, AckFlag=0):
        self.Source = source
        self.Destination = destination
        self.AckFlag = AckFlag
        self.SqNumber = sqNumber


class Packet:
    def __init__(self, header, payload):
        self.Header = header
        self.Payload = payload

    def ToJSON(self):
        x = {
            'Source': self.Header.Source,
            'Destination': self.Header.Destination,
            'AckFlag': self.Header.AckFlag,
            'SqNumber': self.Header.SqNumber,
            'Payload': self.Payload
        }
        return x

    def ToString(self):
        x = 'Source:' + self.Header.Source
        x += '_Destination:' + self.Header.Destination
        x += '_AckFlag:' + str(self.Header.AckFlag)
        x += '_SqNumber:' + str(self.Header.SqNumber)
        x += '_Payload:' + self.Payload
        '''
        x = {
            'Source': self.Header.Source,
            'Destination': self.Header.Destination,
            'AckFlag': self.Header.AckFlag,
            'SqNumber': self.Header.SqNumber,
            'Payload': self.Payload
        }
        '''
        return x