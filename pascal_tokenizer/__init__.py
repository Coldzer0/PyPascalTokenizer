#
# PyPascalTokenizer
# Author: Artem Gavrilov (@Artem3213212)
# License: MPL 2.0
#

SYMS1 = ['(',')','[',']','/','|','\\','@','#','=','>','<',':',';',',','.','$','+','-','*']
SYMS2 = ['>=','<=','<>',':=','..']
SPACES = ['\f','\n','\r','\t','\v',' ']
NO_NAME_SYMS = SYMS1 + SPACES + ['{','}']

def is_comment(s):
    return (s[0]=='{' and s[-1]=='}') or (s[:2]=='(*' and s[-2:]=='*)') or s[:2]=='//'

def is_name(s):
    if not(s[0] in '&abcdefghijklmnopqrstuvwxyz_'):
        return False
    for i in s[1:].lower():
        if not (i in 'abcdefghijklmnopqrstuvwxyz0123456789_'):
            return False
    return True

class PasTokenizer():
    def __init__(self, s):
        self.s, self.i0, self.i1, self.ended = s, 0, 0, False
        self._do_readable_()

    def _do_readable_(self):
        if self._is_readable_:
            if self.i0+1 == len(self.s):
                self.ended = True
            else:
                self.i0+=1
                self.i1=0
                while not self.s[self.i0]:
                    if self.i0+1 == len(self.s):
                        self.ended = True
                        break
                    self.i0+=1

    def _is_readable_(self):
        return len(self.s[self.i0])<=self.i1

    def _next_readable_(self):
        self.i1=+1
        if self._is_readable_():
            if self.i0+1 == len(self.s):
                self.ended = True
            else:
                self.i0+=1
                self.i1=0
                while not self.s[self.i0]:
                    if self.i0+1 == len(self.s):
                        self.ended = True
                        break
                    self.i0+=1
            return True
        else:
            return False

    def _skip_spaces_(self):
        while self.s[self.i0][self.i1] in SPACES:
            self._next_readable_()

    def _getpos_(self):
        return self.i0, self.i1

    def get_next(self):
        self._skip_spaces_()
        begin_pos = self._getpos_()
        ml, ss, f = '', '', True
        str_changed = False
        while f:
            line = self.s[self.i0]
            now_sym = line[self.i1]
            l = len(line)
            if self.i1+1 != l:
                next_sym = line[self.i1+1]
            else:
                next_sym = ''
            if ml == '':
                if now_sym == '/':
                    if next_sym == '/':
                        ss = line[self.i1:]
                        self.i1 = l
                        break
                elif now_sym == '{':
                    ml = '}'
                    ss=[str_changed]
                    last_i0 = self.i0
                elif now_sym == '(':
                    if next_sym == '*':
                        ml = ')'
                        self.i1+=1
                        last_i0 = self.i0
                        ss = [now_sym+next_sym]
                    else:
                        ss = '('
                        self.i1+=1
                        break
                else:
                    if now_sym in SYMS1:
                        ss = now_sym
                        if now_sym + next_sym in SYMS2:
                            self.i1+=2
                            ss = ss + next_sym
                        break
                    elif now_sym=="'":
                        ss="'"
                        self.i1+=1
                        if next_sym!='':
                            ss = ss + next_sym
                            while line[self.i1]!="'":
                                self.i1+=1
                                if not self._is_readable_():
                                    break
                                ss = ss + line[self.i1]
                        break
                    else:
                        while not(line[self.i1] in NO_NAME_SYMS):
                            ss=ss+line[self.i1]
                            self.i1+=1
                            if not self._is_readable_():
                                break
                        break
            else:
                while last_i0!=self.i0:
                    ss.append('')
                ss[-1] = ss[-1] + now_sym
                if now_sym==ml:
                    if ml=='}':
                        ml=''
                    elif self.i1!=0:
                        if line[self.i1-1]=='*':
                            ml=''
            self._next_readable_()
        if len(ss)==1:
            ss=ss[0]
        ss=(ss,begin_pos,self._getpos_(),self.ended)
        self._do_readable_()
        return ss

    def read_next(self):
        i0, i1 = self._getpos_()
        z = self.get_next()
        self.setpos(i0, i1)
        return z

    def setpos(self, i0, i1):
        self.i0, self.i1, self.ended = i0, i1, False
        self._do_readable_()

    def is_ended(self):
        return self.ended

class PasTokenizerStack():
    def __init__(self, s, comments=True):
        self.main = PasTokenizer(s)
        self.stack = []
        if comments:
            self._pop_ = self._get_with_comments_
        else:
            self._pop_ = self._get_without_comments_

    def _get_with_comments_(self):
        return self.main.get_next()

    def _get_without_comments_(self):
        s=(0,'//')
        while is_comment(s[1]):
            return self.main

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

    def push(self, s):
        self.stack.append(s)

