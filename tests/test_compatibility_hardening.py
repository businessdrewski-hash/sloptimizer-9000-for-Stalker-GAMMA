from pathlib import Path
import re,unittest,os
from lupa.luajit20 import LuaRuntime
ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'gamedata/scripts'
GAME=Path(os.environ.get("GAMMA_SCRIPTS", "upstream/gamedata/scripts"))
def runtime():
 l=LuaRuntime(unpack_returned_tuples=True)
 l.execute('''function module(n,s)local e=setmetatable({},{__index=_G});local f=assert(loadstring(s,'@'..n..'.script'));setfenv(f,e);f();_G[n]=e;return e end
function source(s,n)assert(loadstring(s,'@'..n..'.script'))()end''')
 l.globals().module('sloptimizer_function_binding',(P/'sloptimizer_function_binding.script').read_text())
 return l
def load(l,name):return l.globals().module('sloptimizer_'+name,(P/('sloptimizer_'+name+'.script')).read_text())
def ref(name):return (P/('sloptimizer_'+name+'.script')).read_text().split('local reference_body = [====[\n',1)[1].split('\n]====]',1)[0]
class Tests(unittest.TestCase):
 def test_binder_guards(self):
  for name,line,filename,setup,assign in [
   ('device_updates',700,'item_device','local dev_condition={};local dev_type={};local dev_consumption={};local dev_critical={};local dev_slot={};local device_npc_pda={};local nv_glitch_state=false','item_device={device_binder={update=target}}'),
   ('artifact_updates',129,'zz_item_artefact','local in_actor_ruck=function()return false end;local rad_tg_step=1;local rad_factor=1','item_artefact={artefact_binder={update=target}}')]:
   for changed in (False,True):
    l=runtime();m=load(l,name);body=ref(name)
    if changed:body=body.replace('object_binder.update(self, delta)','object_binder.update(self, delta + 1)',1)
    l.globals().source(setup+'\n'*(line-1)+'target='+body+'\n'+assign,filename)
    ok,why=m.install();self.assertEqual(ok,not changed,(name,why))
    if changed:self.assertTrue(l.eval(('item_device.device_binder' if name=='device_updates' else 'item_artefact.artefact_binder')+'.update==target'))
 def callbacks(self,change=None):
  l=runtime();m=load(l,'callback_dispatch')
  lines=(GAME/'_g_patches.script').read_text(encoding='utf-8',errors='replace').splitlines()
  selected=['']*1066;selected[0]='local math_floor=math.floor;function nil_func()end'
  for start,end in [(413,415),(752,872),(1060,1066)]:selected[start-1:end]=lines[start-1:end]
  source='\n'.join(selected)
  if change=='sift':source=source.replace('math_floor(end_idx / 2)','math_floor(end_idx / 3)',1)
  if change=='order':source=source.replace('t[a] < t[b]','t[a] > t[b]',1)
  l.globals().source(source,'_g_patches')
  dispatch='\n'.join((GAME/'axr_main.script').read_text(encoding='utf-8',errors='replace').splitlines()[279:293])
  l.globals().source('local intercepts={}\n'+'\n'*278+dispatch+'\naxr_main={make_callback=make_callback};original=make_callback','axr_main')
  return l,m
 def test_dispatch_guard_original_and_mutated_helpers(self):
  for change in (None,'sift','order'):
   l,m=self.callbacks(change);ok,why=m.install();self.assertEqual(ok,change is None,(change,why))
   if change:self.assertTrue(l.eval('axr_main.make_callback==original'))
 def test_optional_comparison_support_fails_closed(self):
  l=runtime();b=l.globals().sloptimizer_function_binding
  l.execute("function original()return 1 end;require=function()error('unavailable')end")
  self.assertFalse(b.matches_body(l.globals().original,'function()return 1 end'))
 def test_later_sort_replacement_uses_original(self):
  l,m=self.callbacks();ok,why=m.install();self.assertTrue(ok,why)
  l.execute('''local registry
for i=1,20 do local n,v=debug.getupvalue(original,i);if n=='intercepts' then registry=v end end
calls=0;registry.tick={[function()calls=calls+1 end]=1}
axr_main.make_callback('tick');assert(calls==1)
custom_calls=0
spairs=function(t,order)custom_calls=custom_calls+1;return function()end end
axr_main.make_callback('tick');assert(custom_calls==1 and calls==1)
''')
 def test_rebuilt_widget_receives_unchanged_value(self):
  l=runtime();m=load(l,'party_fields');l.execute('slot={};a={calls=0};b={calls=0};function a:SetText(v)self.calls=self.calls+1 end;b.SetText=a.SetText')
  g=l.globals();m.set_field(g.slot,'name',g.a,'SetText','same');m.set_field(g.slot,'name',g.a,'SetText','same');m.set_field(g.slot,'name',g.b,'SetText','same')
  self.assertEqual(g.a.calls,1);self.assertEqual(g.b.calls,1)
  l.execute("a=nil;b=nil;collectgarbage('collect');collectgarbage('collect');assert(slot.gamma_opt_widgets.name==nil)")
 def test_party_renderer_temporarily_absent(self):
  l=runtime();l.execute('''now=0;db={actor={}};function device()return {time_global=function()return now end}end
function XrrIsHosted()return false end;function XrrIsConnected()return false end
hud=nil;function get_hud()return hud end;panel={calls=0,Update=function(self)self.calls=self.calls+1 end};mod={HUD=panel}''')
  load(l,'device_clock');m=load(l,'party_session');poll=m.make_peer_poller(l.globals().mod);poll();self.assertEqual(l.globals().panel.calls,0)
  l.execute('now=501;removed=0;hud={RemoveDialogToRender=function()removed=removed+1 end}')
  poll();self.assertEqual(l.globals().panel.calls,1);self.assertEqual(l.globals().removed,1)
if __name__=='__main__':unittest.main(verbosity=2)
