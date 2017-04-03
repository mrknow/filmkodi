# -*- coding: utf-8 -*-

import sys
import pprint

sys.path.append('../plugin.video.fanfilm')
sys.path.append('../tests/lib')

from resources.lib.libraries import control
from resources.lib.libraries import client


i = u"""
<type 'list'>: [u'<ul data-type="LEKTOR_PL"><li class="line" data-ref="58dfa190dcb2ae078cc4c1c2"><div class="leftSide"><a href="/user/kloopdry"><i class="fa fa-user" title="Doda\u0142: kloopdry"></i></a><span class="host">openload</span><span class="quality">Wysoka / 720p</span></div><div class="rightSide"><div style="width: 75px; float: left; margin-left: 10px"><span id="watchBtn">Ogl\u0105daj</span></div></div><div class="clear"></div></li><li class="line" data-ref="58dea0c49f478a1c6b97516c"><div class="leftSide"><a href="/user/Uploader"><i class="fa fa-user" title="Doda\u0142: Uploader"></i></a><span class="host">openload</span><span class="quality">Wysoka / 720p</span></div><div class="rightSide"><div style="width: 75px; float: left; margin-left: 10px"><span id="watchBtn">Ogl\u0105daj</span></div></div><div class="clear"></div></li><li class="line" data-ref="58deb008dcb2ae078cc3c42f"><div class="leftSide"><a href="/user/Firr0"><i class="fa fa-user" title="Doda\u0142: Firr0"></i></a><span class="host">openload</span><span class="quality">Wysoka / 720p</span></div><div class="rightSide"><div style="width: 75px; float: left; margin-left: 10px"><span id="watchBtn">Ogl\u0105daj</span></div></div><div class="clear"></div></li><li class="line" data-ref="58df520c9244fb0deff582eb"><div class="leftSide"><a href="/user/pawelo098"><i class="fa fa-user" title="Doda\u0142: pawelo098"></i></a><span class="host">openload</span><span class="quality">Wysoka / 720p</span></div><div class="rightSide"><div style="width: 75px; float: left; margin-left: 10px"><span id="watchBtn">Ogl\u0105daj</span></div></div><div class="clear"></div></li><li class="line" data-ref="58df60979244fb0deff591f5"><div class="leftSide"><a href="/user/markolo"><i class="fa fa-user" title="Doda\u0142: markolo"></i></a><span class="host">openload</span><span class="quality">Wysoka / 720p</span></div><div class="rightSide"><div style="width: 75px; float: left; margin-left: 10px"><span id="watchBtn">Ogl\u0105daj</span></div></div><div class="clear"></div></li></ul><ul style="display:none" data-type="W_ROOM"><li class="line" data-ref="58e0e83adcb2ae078cc687c6"><div class="leftSide"><a href="/user/docent120"><i class="fa fa-user" title="Doda\u0142: docent120"></i></a><span class="host">openload</span><span class="quality">Lektor polski</span></div><div class="rightSide"><div style="width: 75px; float: left; margin-left: 10px"><span id="watchBtn">Ogl\u0105daj</span></div></div><div class="clear"></div></li><li class="line" data-ref="58e132f79f478a1c6b9a8d65"><div class="leftSide"><a href="/user/vtomogz"><i class="fa fa-user" title="Doda\u0142: vtomogz"></i></a><span class="host">openload</span><span class="quality">Lektor polski</span></div><div class="rightSide"><div style="width: 75px; float: left; margin-left: 10px"><span id="watchBtn">Ogl\u0105daj</span></div></div><div class="clear"></div></li><li class="line" data-ref="58e155369f478a1c6b9ae9dd"><div class="leftSide"><a href="/user/vtomogz"><i class="fa fa-user" title="Doda\u0142: vtomogz"></i></a><span class="host">openload</span><span class="quality">Napisy polskie</span></div><div class="rightSide"><div style="width: 75px; float: left; margin-left: 10px"><span id="watchBtn">Ogl\u0105daj</span></div></div><div class="clear"></div></li></ul>']
"""

print "aaa"
b=[]
b = [client.parseDOM(i, 'ul'), client.parseDOM(i,'ul', ret='data-type')]
pprint.pprint(b)
for x in range(0, len(b[1])):
    print "---"
    print b[1][x]
    print b[0][x]