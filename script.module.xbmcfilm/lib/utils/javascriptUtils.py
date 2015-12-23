# -*- coding: utf-8 -*-

import re
import urllib
import base64
import unpack95High
from string import join
import traceback, sys

class JsFunctions:
    
    def hp_d01(self, s):
        ar=[]
        os=""
        for i in range(0,len(s)-1):
            c = ord(s[i])
            if c < 128:
                c = c^2
            os += chr(c)
            if len(os) > 80:
                ar.append(os)
                os = ""
        o = join(ar,'') + os
        return o
    
    def o61a2a8f(self, s):
        r = "";
        tmp = s.split("18267506");
        s = urllib.unquote(tmp[0]);
        k = urllib.unquote(tmp[1] + "511382");
        for i in range(0,len(s)-1):
            r += chr((int(k[i%len(k)])^ord(s[i]))+1);
        return r;
    
    def n98c4d2c(self, s):
        txtArr = s.split('18234663')
        s = urllib.unquote(txtArr[0])
        t = urllib.unquote(txtArr[1] + '549351')
        tmp=''
        for i in range(0,len(s)-1):
            tmp += chr((int(t[i%len(t)])^ord(s[i]))+-6)
        return urllib.unquote(tmp)
    
    def RrRrRrRr(self, teaabb):
        tttmmm=""
        l=len(teaabb)
        www = hhhhffff = int(round(l/2))
        if l<2*www:
            hhhhffff -= 1
        for i in range(0,hhhhffff-1):
            tttmmm = tttmmm + teaabb[i] + teaabb[i+hhhhffff]
        if l<2*www :
            tttmmm = tttmmm + teaabb[l-1]
        return tttmmm
    
    def ew_dc(self, s):
        d=''
        a=[]
        for i in range(0, len(s)-1):
            c = ord(s[i])
            if (c<128):
                c = c^5
            d += chr(c)
            if (i+1) % 99 == 0:
                a.append(d)
                d=''
        r = join(a,'') + d
        return r
    
    def pbbfa0(self, s):
        r = ""
        tmp = s.split("17753326")
        s = urllib.unquote(tmp[0])
        k = urllib.unquote(tmp[1] + "527117")
        for i in range(0,len(s)):
            r += chr((int(k[i%len(k)])^ord(s[i]))+7)
        return r

class JsUnpacker:

    def unpackAll(self, data):
        sPattern = '(eval\(function\(p,a,c,k,e,d\)\{while.*?)\s*</script>'
        return re.sub(sPattern, lambda match: self.unpack(match.group(1)), data)
    
    def containsPacked(self, data):
        return 'p,a,c,k,e,d' in data
        
    def unpack(self, sJavascript):
        aSplit = sJavascript.split(";',")
        p = str(aSplit[0])
        aSplit = aSplit[1].split(",")
        a = int(aSplit[0])
        c = int(aSplit[1])
        k = aSplit[2].split(".")[0].replace("'", '').split('|')
        e = ''
        d = ''
        sUnpacked = str(self.__unpack(p, a, c, k, e, d))
        return sUnpacked.replace('\\', '')
    
    def __unpack(self, p, a, c, k, e, d):
        while (c > 1):
            c = c -1
            if (k[c]):
                p = re.sub('\\b' + str(self.__itoa(c, a)) +'\\b', k[c], p)
        return p
    
    def __itoa(self, num, radix):
        result = ""
        while num > 0:
            result = "0123456789abcdefghijklmnopqrstuvwxyz"[num % radix] + result
            num /= radix
        return result
        
class JsUnpackerV2:

    def unpackAll(self, data):
        try:
            in_data=data
            sPattern = '(eval\\(function\\(p,a,c,k,e,d.*)'
            enc_data=re.compile(sPattern).findall(in_data)
            #print 'enc_data',enc_data, len(enc_data)
            if len(enc_data)==0:
                sPattern = '(eval\\(function\\(p,a,c,k,e,r.*)'
                enc_data=re.compile(sPattern).findall(in_data)
                #print 'enc_data packer...',enc_data

            for enc_val in enc_data:
                unpack_val=self.unpack(enc_val)
                in_data=in_data.replace(enc_val,unpack_val)
            return in_data
        except: 
            traceback.print_exc(file=sys.stdout)
            return data
        
        
    def containsPacked(self, data):
        return 'p,a,c,k,e,d' in data or 'p,a,c,k,e,r' in data
        
    def unpack(self,sJavascript,iteration=1, totaliterations=1  ):

        aSplit = sJavascript.split("rn p}('")

        p1,a1,c1,k1=('','0','0','')
        ss="p1,a1,c1,k1=(\'"+aSplit[1].split(".spli")[0]+')' 
        exec(ss)
        
        k1=k1.split('|')
        aSplit = aSplit[1].split("))'")
        e = ''
        d = ''#32823
        sUnpacked1 = str(self.__unpack(p1, a1, c1, k1, e, d,iteration))
        if iteration>=totaliterations:
            return sUnpacked1
        else:
            return self.unpack(sUnpacked1,iteration+1)

    def __unpack(self,p, a, c, k, e, d, iteration,v=1):
        while (c >= 1):
            c = c -1
            if (k[c]):
                aa=str(self.__itoaNew(c, a))
                p=re.sub('\\b' + aa +'\\b', k[c], p)# THIS IS Bloody slow!
        return p

    def __itoa(self,num, radix):

        result = ""
        if num==0: return '0'
        while num > 0:
            result = "0123456789abcdefghijklmnopqrstuvwxyz"[num % radix] + result
            num /= radix
        return result
        
    def __itoaNew(self,cc, a):
        aa="" if cc < a else self.__itoaNew(int(cc / a),a) 
        cc = (cc % a)
        bb=chr(cc + 29) if cc> 35 else str(self.__itoa(cc,36))
        return aa+bb
          

class JsUnpacker95High:

    def unpackAll(self, data):
        try:
            in_data=data
            sPattern = '(eval\\(function\\(p,a,c,k,e,d.*)'
            enc_data=re.compile(sPattern).findall(in_data)
            if len(enc_data)==0:
                sPattern = '(eval\\(function\\(p,a,c,k,e,r.*)'
                enc_data=re.compile(sPattern).findall(in_data)
                

            for enc_val in enc_data:
                unpack_val=unpack95High.unpack(enc_val)
                in_data=in_data.replace(enc_val,unpack_val)
                in_data=in_data.replace('\\\'','\'')
            return in_data
        except: 
            traceback.print_exc(file=sys.stdout)
            return data
        
        
    def containsPacked(self, data):
        return 'p,a,c,k,e,d' in data or 'p,a,c,k,e,r' in data
    
    

class JsUnIonCube:
    def ionX(self, x, arrayX):
        r = []
        s = 0
        w = 0
        
        for d in x:
            w |= int(arrayX[ord(d)-48]) << s
            if (s):
                r.append(chr(165 ^ w & 255))
                w >>= 8
                s -= 2
            else:
                s = 6

        r = ''.join(r)
        return r

    def unIonALL(self,data):
        in_data=data
        sPattern = 'c="(.*?)";eval\\(unescape\\(".*"\\)\\);x\\("(.*?)"\\)'
        undc_data=re.compile(sPattern).findall(in_data)
        c = undc_data[0][0]
        x = undc_data[0][1]

        l = list(c)
        for i in range(0, len(c), 3):
            l[i]='%'

        c = ''.join(l)
        c = urllib.unquote_plus(c)

        arrayPattern = 't=Array\\((.*?)\\)'
        arrayData = re.compile(arrayPattern).findall(c)
        ionArray = arrayData[0].split(',')
        data=self.ionX(x,ionArray)

        return data

    def containsIon(self,data):
        return 'eval(unescape("d="";' in data

class JsUnwiser:
    def unwiseAll(self, data):
        try:
            in_data=data
            sPattern = 'eval\\(function\\(w,i,s,e\\).*?}\\((.*?)\\)'
            wise_data=re.compile(sPattern).findall(in_data)
            for wise_val in wise_data:
                unpack_val=self.unwise(wise_val)
                #print '\nunpack_val',unpack_val
                in_data=in_data.replace(wise_val,unpack_val)
            return re.sub("eval\(function\(w,i,s,e\).*?join\(''\);}", "", in_data, count=1, flags=re.DOTALL)
        except: 
            traceback.print_exc(file=sys.stdout)
            return data
        
    def containsWise(self, data):
        return 'w,i,s,e' in data
        
    def unwise(self, sJavascript):
        #print 'sJavascript',sJavascript
        page_value=""
        try:        
            ss="w,i,s,e=("+sJavascript+')' 
            exec (ss)
            page_value=self.__unpack(w,i,s,e)
        except: traceback.print_exc(file=sys.stdout)
        return page_value
        
    def __unpack( self,w, i, s, e):
        lIll = 0;
        ll1I = 0;
        Il1l = 0;
        ll1l = [];
        l1lI = [];
        while True:
            if (lIll < 5):
                l1lI.append(w[lIll])
            elif (lIll < len(w)):
                ll1l.append(w[lIll]);
            lIll+=1;
            if (ll1I < 5):
                l1lI.append(i[ll1I])
            elif (ll1I < len(i)):
                ll1l.append(i[ll1I])
            ll1I+=1;
            if (Il1l < 5):
                l1lI.append(s[Il1l])
            elif (Il1l < len(s)):
                ll1l.append(s[Il1l]);
            Il1l+=1;
            if (len(w) + len(i) + len(s) + len(e) == len(ll1l) + len(l1lI) + len(e)):
                break;
            
        lI1l = ''.join(ll1l)#.join('');
        I1lI = ''.join(l1lI)#.join('');
        ll1I = 0;
        l1ll = [];
        for lIll in range(0,len(ll1l),2):
            #print 'array i',lIll,len(ll1l)
            ll11 = -1;
            if ( ord(I1lI[ll1I]) % 2):
                ll11 = 1;
            #print 'val is ', lI1l[lIll: lIll+2]
            l1ll.append(chr(    int(lI1l[lIll: lIll+2], 36) - ll11));
            ll1I+=1;
            if (ll1I >= len(l1lI)):
                ll1I = 0;
        ret=''.join(l1ll)
        if 'eval(function(w,i,s,e)' in ret:
            ret=re.compile('eval\(function\(w,i,s,e\).*}\((.*?)\)').findall(ret)[0] 
            return self.unwise(ret)
        else:
            return ret

class JsUnFunc:
    def unFuncALL(self,data):
        in_data = data
        dec_data = ''
        sPattern = r"var\s*tmp\s*=\s*s.split\(\"([^\"]+)\"\)"
        kPattern = r"unescape\(tmp\[1\]\s*\+\s*\"([^\"]+)\"\)"
        dataPattern = r"document.write\(\w+\(\'\'\)\s*\+\s*\'([^\']+)"
        modPattern = r"charCodeAt\(i\)\)\+\s*([^\)]+)\)"
        
        s_data = re.compile(sPattern).findall(in_data)
        k_data = re.compile(kPattern).findall(in_data)
        undc_data = re.compile(dataPattern).findall(in_data)
        mod_data = re.compile(modPattern).findall(in_data)

        sDelimiter = s_data[0]
        s = undc_data[0]
        tmp = urllib.unquote(s).split(sDelimiter)
        k = tmp[1] + k_data[0]
        mod = int(mod_data[0])
        encData = tmp[0]
        
        for i,d in enumerate(encData):
            dec_data += chr((int(k[i % len(k)]) ^ ord(d)) + mod)
            
        data = re.sub("eval\(unescape\('function.*?unescape\(''\)\);'\)\);", dec_data, in_data, count=1, flags=re.DOTALL)
        return data
    
    def cointainUnFunc(self,data):
        return 'String.fromCharCode((parseInt' in data
    
class JsUnPP:
    def UnPPAll(self,data):
        def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)
        
        in_data = data
        tPattern = r"var\s*t=['\"](\w+)['\"]\s*;\s*for"
        
        t_data = re.compile(tPattern).findall(in_data)
        
        for i in t_data:
            out_data = removeNonAscii(str(base64.b16decode(i.upper())))
            data = re.sub(r"var\s*t[^}]+}", out_data, data)
                
        return data
    def containUnPP(self,data):
        return 'parseInt(t.substr' in data

class JsUnPush:
    def UnPush(self,data):
        in_data = data
        varPattern = '(var\s*\w+\s*=\s*new.*?\.push\(\'\'\);)'
        var_data = re.compile(varPattern).findall(in_data)
        
        charPattern = '\(\'([%0-9a-fA-F])\'\)'
        
        chars = re.compile(charPattern).findall(var_data[0])
        res = urllib.unquote(''.join(chars))
        out_data=in_data.replace(var_data[0],res)
        return out_data
        
    def containUnPush(self,data):
        return '.push(\'%\')' in data

