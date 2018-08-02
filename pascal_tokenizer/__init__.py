#
# PyPascalTokenizer
# Author: Artem Gavrilov (@Artem3213212)
# License: MPL 2.0
#

SYMS1 = ['(',')','[',']','/','|','\\','@','#','=','>','<',':',';',',','.','$','+','-','*']
SYMS2 = ['>=','<=','<>',':=','..','-=','+=','/=','*=']
SPACES = ['\f','\n','\r','\t','\v',' ']
NO_NAME_SYMS = SYMS1 + SPACES + ['{','}']
CHARS_ID0 = '&abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
CHARS_ID = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'

def is_comment(s):
    if type(s) is list:
        return True
    else:
        return (s[0]=='{' and s[-1]=='}') or (s[:2]=='(*' and s[-2:]=='*)') or s[:2]=='//'

def is_name(s):
    if not (s[0] in CHARS_ID0):
        return False
    for i in s[1:]:
        if not (i in CHARS_ID):
            return False
    return True

def is_string(s):
    return s[0]=="'" and s[-1]=="'"

class PasTokenizer():
    def __init__(self, s):
        self.s, self.y, self.x, self.ended = s, 0, 0, False
        self._do_readable()
        self._skip_spaces()

    def _do_readable(self):
        if self._is_readable:
            if self.y+1 == len(self.s):
                self.ended = True
            else:
                self.y+=1
                self.x=0
                while not self.s[self.y]:
                    if self.y+1 == len(self.s):
                        self.ended = True
                        break
                    self.y+=1

    def _is_readable(self):
        return len(self.s[self.y])<=self.x

    def _next_readable(self):
        self.x=+1
        if self._is_readable():
            if self.y+1 == len(self.s):
                self.ended = True
            else:
                self.y+=1
                self.x=0
                while not self.s[self.y]:
                    if self.y+1 == len(self.s):
                        self.ended = True
                        break
                    self.y+=1
            return True
        else:
            return False

    def _skip_spaces(self):
        while self.s[self.y][self.x] in SPACES:
            self._next_readable()

    def _get_pos(self):
        return self.y, self.x

    def _set_pos(self, i0, i1):
        self.y, self.x, self.ended = i0, i1, False
        self._do_readable()

    def get_next(self):
        begin_pos = self._get_pos()
        ml, ss, f = '', '', True
        str_changed = False
        while f:
            line = self.s[self.y]
            now_sym = line[self.x]
            l = len(line)
            if self.x+1 != l:
                next_sym = line[self.x+1]
            else:
                next_sym = ''
            if ml == '':
                if now_sym == '/':
                    if next_sym == '/':
                        ss = line[self.x:]
                        self.x = l
                        break
                elif now_sym == '{':
                    ml = '}'
                    ss=[str_changed]
                    last_i0 = self.y
                elif now_sym == '(':
                    if next_sym == '*':
                        ml = ')'
                        self.x+=1
                        last_i0 = self.y
                        ss = [now_sym+next_sym]
                    else:
                        ss = '('
                        self.x+=1
                        break
                else:
                    if now_sym in SYMS1:
                        ss = now_sym
                        if now_sym + next_sym in SYMS2:
                            self.x+=2
                            ss = ss + next_sym
                        break
                    elif now_sym=="'":
                        ss="'"
                        self.x+=1
                        if next_sym!='':
                            ss = ss + next_sym
                            while line[self.x]!="'":
                                self.x+=1
                                if not self._is_readable():
                                    break
                                ss = ss + line[self.x]
                        break
                    else:
                        while not(line[self.x] in NO_NAME_SYMS):
                            ss=ss+line[self.x]
                            self.x+=1
                            if not self._is_readable():
                                break
                        break
            else:
                while last_i0!=self.y:
                    ss.append('')
                ss[-1] = ss[-1] + now_sym
                if now_sym==ml:
                    if ml=='}':
                        ml=''
                    elif self.x!=0:
                        if line[self.x-1]=='*':
                            ml=''
            self._next_readable()
        if len(ss)==1:
            ss=ss[0]
        ss=(ss,begin_pos,self._get_pos(),self.ended)
        self._do_readable()
        self._skip_spaces()
        return ss

    def read_next(self):
        i0, i1 = self._get_pos()
        z = self.get_next()
        self._set_pos(i0, i1)
        return z

    def is_ended(self):
        return self.ended

class PasTokenizerStack():
    def __init__(self, s, comments=True):
        self.main = PasTokenizer(s)
        self.stack = []
        if comments:
            self._pop_ = self._get_with_comments
        else:
            self._pop_ = self._get_without_comments

    def _get_with_comments(self):
        return self.main.get_next()

    def _get_without_comments(self):
        s=(0,'//')
        while is_comment(s[1]):
            s = self.main.

    def push(self, s):
        self.stack.append(s)

    def pop(self):
        if self.stack:
            return self.stack.pop()
        else:
            return self._pop_()

    def read_last(self):
        if not self.stack:
            self.stack.append(self._pop_())
        return self.stack[-1]

    def is_ended(self):
        return self.stack or self.main.is_ended()

'''class PasTokenizerParallelStack(PasTokenizerStack):
    def __init__(self,s,comments=True):'''

