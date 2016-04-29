
import sys

z,x,y= "}{|}A|k{|kA|}=BE1)|BF}))|$}:~pI~/;@Go{H%{&A?|if }:~pJ"\
       "IJ-1~#>=0:GoAG@HG;o{G;%-I&{?|m,kJ,j=C?;/@~o{~D:Gl[c]("\
       ")?","G$p:%~;%~;el!]':p%break~;![':p%#<len(j):~%\n\t\t"\
       "%if c=='%while o%\n%m[k]%+=1%\t%if not %c=j[o]%-=1%sy"\
       "s.std%[0]*64000,0,0,u%if l.has"\
       "_key(c)%in.read(%out.write(chr(%=1%,o".split('%'),"HG"\
       "&%/~!#?}{;$@ABCDEFIJ"

for i in range(len(x)):z=z.replace(y[i],x[i])
z=z.split('|')
for o in range(9):
    exec("def %c():\n\tglobal k,m,o,j\n\t%s\n"%(chr(97+o),z[o]))
l={'>':c,'<':d,'-': b,'+':a,',':e,'.':f,'[':g,']':h}

s="""
import sys

z,x,y= "}{|}A|k{|kA|}=BE1)|BF}))|$}:~pI~/;@Go{H%{&A?|if }:~pJ"\\
       "IJ-1~#>=0:GoAG@HG;o{G;%-I&{?|m,kJ,j=C?;/@~o{~D:Gl[c]("\\
       ")?","G$p:%~;%~;el!]':p%break~;![':p%#<len(j):~%\\n\\t\\t"\\
       "%if c=='%while o%\\n%m[k]%+=1%\\t%if not %c=j[o]%-=1%sy"\\
       "s.std%[0]*64000,0,0,u%if l.has"\\
       "_key(c)%in.read(%out.write(chr(%=1%,o".split('%'),"HG"\\
       "&%/~!#?}{;$@ABCDEFIJ"

for i in range(len(x)):z=z.replace(y[i],x[i])
z=z.split('|')
for o in range(9):
    exec("def %c():\\n\\tglobal k,m,o,j\\n\\t%s\\n"%(chr(97+o),z[o]))
l={'>':c,'<':d,'-': b,'+':a,',':e,'.':f,'[':g,']':h}

u=""
for c in s[:604]+'s='+3*'"'+s.replace(chr(92),chr(92)*2)+3*'"'+s[-118:]:
    u += '+'*ord(c)+'.'+'-'*ord(c)
i()
"""
u=""
for c in s[:604]+'s='+3*'"'+s.replace(chr(92),chr(92)*2)+3*'"'+s[-118:]:
    u += '+'*ord(c)+'.'+'-'*ord(c)
i()
