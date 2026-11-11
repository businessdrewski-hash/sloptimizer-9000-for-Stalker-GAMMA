from pathlib import Path
import json,unittest
from lupa.luajit20 import LuaRuntime,LuaError
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT.parent/'Sloptimizer-9000-2.10.2-readable'

COMMON='''
function object(id,section)
 local o={ident=id,sec=section,valid=true}
 local function check(self)assert(self.valid,'expired native-object stand-in')end
 function o:id()check(self);return self.ident end
 function o:section()check(self);return self.sec end
 function o:condition()check(self);return .5 end
 function o:get_remaining_uses()check(self);return 3 end
 function o:parent()check(self);return nil end
 return o
end
old=object(1,'old');new=object(2,'new');self={object=old,first_update=true,no_rad=true}
object_binder={update=function()end}
function swap()old.valid=false;self.object=new end
'''
def vm(folder,name):
 l=LuaRuntime(unpack_returned_tuples=True);l.execute(COMMON);l.execute((folder/'gamedata/scripts'/('sloptimizer_'+name+'.script')).read_text(encoding='utf-8'));return l

class Tests(unittest.TestCase):
 def lifetime(self,folder,kind):
  l=vm(folder,kind)
  if kind=='item_updates':
   l.execute('item_uses={};item_condition={};self.multiuse=true;f=assert(make_tracked(function()end,_G));f(self,1)')
  elif kind=='artifact_updates':
   l.execute('''cond_t={[1]=.5,[2]=.5};dist_t={};function SYS_GetParam()return 'other'end
db={actor={position=function()return {distance_to_sqr=function()return 10 end}end}}
function old:position()return 0 end;function new:position()return 0 end
function pr()end;function r(v)return v end
f=make_artifact(_G,function()return false end,1,1);f(self,1)''')
  else:
   l.execute("dev_condition={};f=assert(loadstring('return '..replacement_source()))();f(self,1)")
  l.globals().swap();l.globals().f(l.globals().self,1)
  if kind=='item_updates':self.assertEqual(l.globals().item_uses[2],3)
  if kind=='device_updates':self.assertEqual(l.globals().dev_condition[2],.5)
  if kind=='artifact_updates':self.assertEqual(l.globals().dist_t['new'],10)
 def test_reproduce_cached_object_failure(self):
  for kind in ('item_updates','artifact_updates','device_updates'):
   with self.subTest(kind=kind),self.assertRaisesRegex(LuaError,'expired native-object'):
    self.lifetime(BASE,kind)
 def test_local_fix_reads_current_object(self):
  for kind in ('item_updates','artifact_updates','device_updates'):
   with self.subTest(kind=kind):self.lifetime(ROOT,kind)
 def radiation(self,folder,missing):
  l=vm(folder,'radiation_display');l.execute('''
function time_global()return 5 end;faster_refresh_rate=true;db={actor={radiation=.1}}
label={IsShown=function()return true end,GetText=function()return ''end,SetText=function(self,v)self.written=v end}
icon={IsShown=function()return true end}
self={_tmr=10,slot={{icon_f=icon,xcvb_time=label}}}
f=make_radiation(function()end,true,1)
''')
  if missing:l.globals().self.slot[1][missing]=None
  l.globals().f(l.globals().self,False)
  return l.globals().label.written
 def test_reproduce_missing_hud_failure(self):
  for missing in ('xcvb_time','icon_f'):
   with self.subTest(missing=missing),self.assertRaises(LuaError):self.radiation(BASE,missing)
 def test_missing_hud_is_skipped(self):
  for missing in ('xcvb_time','icon_f'):self.assertIsNone(self.radiation(ROOT,missing))
 def test_normal_hud_unchanged(self):
  self.assertEqual(self.radiation(BASE,None),self.radiation(ROOT,None))
 def test_line_only_guard_accepts_changed_body(self):
  l=vm(BASE,'item_updates');l.execute(r'''
body=string.rep('\n',151)..'return function(self, delta) CUSTOM_BEHAVIOR=true end'
-- return-function declaration stays on the same reviewed line.
changed=assert(loadstring(body,'@bind_item.script'))()
bind_item={item_binder={update=changed}}
''')
  ok,why=l.globals().install();self.assertTrue(ok,why)
  l.globals().bind_item.item_binder.update(l.globals().self,1)
  self.assertIsNone(l.globals().CUSTOM_BEHAVIOR)
 def test_compile(self):
  l=LuaRuntime(unpack_returned_tuples=True);check=l.eval('function(s)local f,e=loadstring(s);return f~=nil,e end')
  for p in (ROOT/'gamedata/scripts').glob('*.script'):
   ok,e=check(p.read_text(encoding='utf-8'));self.assertTrue(ok,(p.name,e))
 def test_item_guard_rejects_changed_accepts_reviewed(self):
  l=vm(ROOT,'item_updates')
  binding=(ROOT/'gamedata/scripts/sloptimizer_function_binding.script').read_text()
  l.execute('sloptimizer_function_binding=(function()\n'+binding+'\nreturn {bind_body=bind_body,same_implementation=same_implementation} end)()')
  l.execute(r"changed=assert(loadstring(string.rep('\n',151)..'return function(self, delta) CUSTOM_BEHAVIOR=true end','@bind_item.script'))();bind_item={item_binder={update=changed}}")
  ok,why=l.globals().install();self.assertFalse(ok,why)
  self.assertTrue(l.eval('bind_item.item_binder.update == changed'))
  source=(ROOT/'gamedata/scripts/sloptimizer_item_updates.script').read_text()
  body=source.split('local reference_body = [====[\n',1)[1].split('\n]====]',1)[0]
  l.eval(r"function(s) local f=assert(loadstring(string.rep('\n',151)..'return '..s,'@bind_item.script'));bind_item.item_binder.update=f() end")(body)
  ok,why=l.globals().install();self.assertTrue(ok,why)

if __name__=='__main__':unittest.main(verbosity=2)
