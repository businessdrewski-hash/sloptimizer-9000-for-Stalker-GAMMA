from pathlib import Path
import unittest
from lupa.luajit20 import LuaRuntime
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT.parent/'Sloptimizer-9000-2.10.2-readable'
FIXTURE=r'''
tick=100;frame=1;full=0;positions=0;project_x=20;hud=true;pda=false;device_calls=0
D={time_global=function()return tick end}
function device()device_calls=device_calls+1;return D end
function time_global()return tick end
function vector()return {set=function(self,x,y,z)self.x=x;self.y=y;self.z=z;return self end}end
vector2=vector
function clamp(v,a,b)return math.min(b,math.max(a,v))end
game={world2ui=function(v)return {x=project_x,y=30}end}
function main_hud_shown()return hud end
axr_main={};item_device={is_pda_active=function()return pda end};CUIScriptWnd={Update=function()end}
utils_catspaw_hudmarks={marker_is_offscreen=assert(loadstring(string.rep('\n',1737)..'return function(m)full=full+1;return m.is_offscreen end','@utils_catspaw_hudmarks.script'))()}
m={preset='dotmark',skip_hint=true,skip_dist=true,args={},update_int=20,offscreen_interval=200,is_shown=true,last_pos={x=1,y=2,z=3},marker={SetWndPos=function(self,v)positions=positions+1;last_x=v.x end}}
function m:HideAll()self.is_shown=false end
function step(i)
 tick=tick+7;D.frame=i
 if i%11==0 then tick=0 end
 hud=i%13~=0;pda=i%17==0;project_x=i%19==0 and -9999 or i
 m.is_shown=i%23~=0;m.actor_taking=i%29==0
 local a=utils_catspaw_hudmarks.marker_is_offscreen(m)
 local b=utils_catspaw_hudmarks.marker_is_offscreen(m)
 return table.concat({tostring(a),tostring(b),full,positions,tostring(last_x),tostring(m.is_shown)},'|')
end
'''
class Tests(unittest.TestCase):
 def test_clock_live_and_one_wrapper(self):
  for name in ('device_clock','live_clock'):
   l=LuaRuntime(unpack_returned_tuples=True);l.execute(FIXTURE)
   l.execute((ROOT/'gamedata/scripts'/('sloptimizer_'+name+'.script')).read_text())
   l.execute('clock=make_clock('+('device()' if name=='live_clock' else '')+')')
   for value in (100,100,107,0,500):
    l.globals().tick=value;self.assertEqual(l.globals().clock(),value)
   self.assertEqual(l.globals().device_calls,1)
 def test_marker_behavior_matches(self):
  engines=[]
  for folder in (BASE,ROOT):
   l=LuaRuntime(unpack_returned_tuples=True);l.execute(FIXTURE)
   l.execute((folder/'gamedata/scripts/sloptimizer_marker_updates.script').read_text())
   ok,why=l.globals().install();self.assertTrue(ok,why);engines.append(l)
  for i in range(1,501):self.assertEqual(engines[0].globals().step(i),engines[1].globals().step(i),i)
  for l in engines:self.assertEqual(l.globals().device_calls,1)
if __name__=='__main__':unittest.main(verbosity=2)
