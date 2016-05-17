# -*- coding: utf-8 -*-
"""
App name
~~~~~~

:copyright: (c) 2014 by mrknow
:license: GNU GPL Version 3, see LICENSE for more details.
"""

import urllib



def n98c4d2c(s):
    txtArr = s.split('12326949')
    s = urllib.unquote(txtArr[0])
    t = urllib.unquote(txtArr[1] + '624330')
    tmp=''
    for i in range(0,len(s)-1):
        tmp += chr((int(t[i%len(t)])^ord(s[i]))+-6)
    return urllib.unquote(tmp)

import re


class Unpacker(object):

    """
    Unpacker is a base class to unpack various function based eval packed functions writen in javascript
    """
    param_regex = None

    def unpack():
        raise NotImplemented('unpack method is not implemented')


class WiseUnpacker(Unpacker):
    param_regex = re.compile(
        r";\}\('(?P<param_w>\w+)'[\s,]+'(?P<param_i>\w+)'[\s,]+'(?P<param_s>\w+)'[\s,]+'(?P<param_e>\w+)'\)\);")

    @staticmethod
    def unpack(w, i, s, e):
        """
        function (w, i, s, e) {
          var lIll = 0;
          var ll1I = 0;
          var Il1l = 0;
          var ll1l = [];
          var l1lI = [];
          while (true) {
              if (lIll < 5) l1lI.push(w.charAt(lIll));
              else if (lIll < w.length) ll1l.push(w.charAt(lIll));
              lIll++;
              if (ll1I < 5) l1lI.push(i.charAt(ll1I));
              else if (ll1I < i.length) ll1l.push(i.charAt(ll1I));
              ll1I++;
              if (Il1l < 5) l1lI.push(s.charAt(Il1l));
              else if (Il1l < s.length) ll1l.push(s.charAt(Il1l));
              Il1l++;
              if (w.length + i.length + s.length + e.length == ll1l.length + l1lI.length + e.length) break;
          }
          var lI1l = ll1l.join('');
          var I1lI = l1lI.join('');
          ll1I = 0;
          var l1ll = [];
          for (lIll = 0; lIll < ll1l.length; lIll += 2) {
              var ll11 = -1;
              if (I1lI.charCodeAt(ll1I) % 2) ll11 = 1;
              l1ll.push(String.fromCharCode(parseInt(lI1l.substr(lIll, 2), 36) - ll11));
              ll1I++;
              if (ll1I >= l1lI.length) ll1I = 0;
          }
          return l1ll.join('');
        }
        """

        va = 0
        vb = 0
        vc = 0
        vd = []
        ve = []
        while True:
            if va < 5:
                ve.append(w[va])
            elif va < len(w):
                vd.append(w[va])

            va += 1

            if vb < 5:
                ve.append(i[vb])
            elif vb < len(i):
                vd.append(i[vb])

            vb += 1

            if vc < 5:
                ve.append(s[vc])
            elif vc < len(s):
                vd.append(s[vc])

            vc += 1

            if (len(w) + len(i) + len(s) + len(e)) == (len(vd) + len(ve) + len(e)):
                break

        vf = "".join(vd)  # vf = vd.join('')
        vg = "".join(ve)  # vg = ve.join('')

        vb = 0
        vi = []
        for va in range(0, len(vd), 2):  # (va = 0; va < vd; va += 2)
            vj = -1
            if ord(vg[vb]) % 2:  # (vg.charCodeAt(vb) % 2):
                vj = 1

            # vi.append(String.fromCharCode(parseInt(vf.substr(va, 2), 36) - vj))
            vi.append(chr(int(vf[va:va + 2], 36) - vj))

            vb += 1

            if vb >= len(ve):
                vb = 0

        result = ''.join(vi)  # vi.join('')

        rgx = WiseUnpacker.param_regex
        if re.search(rgx, result):
            w = re.search(rgx, result).group('param_w')
            i = re.search(rgx, result).group('param_i')
            s = re.search(rgx, result).group('param_s')
            e = re.search(rgx, result).group('param_e')

            result = WiseUnpacker.unpack(w, i, s, e)

        return result