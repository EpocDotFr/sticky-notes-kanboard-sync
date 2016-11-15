import sys

class RtfException(Exception):
    pass

plaintext = 1
control = 2
argument = 3
backslash = 4
escapedChar = 5

class RtfParser(object):

    def __init__(self,unicode=False):
        self.state = plaintext
        self.arg = ''
        self.token = ''
        self.unicode = unicode

    def getChar(self,code):
        """ called when an escaped char is found """
        return chr(code)

    def getNonBreakingSpace(self):
        return " "

    def pushState(self):
        pass

    def popState(self):
        pass

    def putChar(self):
        pass

    def doControl(self,token,arg):
        pass

    def feed(self,txt):
        for c in txt:
            self.feedChar(c)

    def feedChar(self,char):
        if self.state == plaintext: #this is just normal user content
            if char == '\\':
                self.state = backslash
            elif char == '{':
                self.pushState()
            elif char == '}':
                self.popState()
            else:
                self.putChar(char)
        elif self.state == backslash: #something special like a command or escape
            if char == '\\' or char == '{' or char == '}':
                self.putChar(char)
                self.state = plaintext
            else:
                if char.isalpha() or char in ('*','-','|'):
                    self.state = control
                    self.token = char
                elif char == "'":
                    self.state = escapedChar
                    self.escapedChar = ''
                elif char in ['\\','{','}']:
                    self.putChar(char)
                    self.state = plaintext
                elif char == "~": #non breking space
                    self.putChar(self.getNonBreakingSpace())
                    self.state = plaintext
                else:
                    raise RtfException('unexpected {} after \\'.format(char))
        elif self.state == escapedChar:
            self.escapedChar = self.escapedChar + char
            if len(self.escapedChar) == 2:
                char = self.getChar(int(self.escapedChar,16))
                self.putChar(char)
                self.state = plaintext
        elif self.state == control: #collecting the command token
            if char.isalpha():
                self.token = self.token + char
            elif char.isdigit() or char== '-':
                self.state = argument
                self.arg = char
            else:
                self.doControl(self.token,self.arg)
                self.state = plaintext
                if char == '\\':
                    self.state = backslash
                elif char == '{':
                    self.pushState()
                elif char == '}':
                    self.popState()
                else:
                    if not char.isspace():
                        self.putChar(char)
        elif self.state == argument: #collecting the optional command argument
            if char.isdigit():
                self.arg = self.arg + char
            else:
                self.state = plaintext
                self.doControl(self.token,self.arg)
                if char == '\\':
                    self.state = backslash
                elif char == '{':
                    self.pushState()
                elif char == '}':
                    self.popState()
                else:
                    if not char.isspace():
                        self.putChar(char)


class RtfTester(RtfParser):
    def __init__(self):
        RtfParser.__init__(self)
        self.level = 0
    
    def pushState(self):
        print(self.level,'pushState',self.level + 1)
        self.level = self.level + 1

    def popState(self):
        print(self.level,'popState',self.level - 1)
        self.level = self.level - 1

    def putChar(self,ch):
        print(self.level,'putChar',ch)

    def doControl(self,token,arg):
        print(self.level,'doControl',token,arg)
