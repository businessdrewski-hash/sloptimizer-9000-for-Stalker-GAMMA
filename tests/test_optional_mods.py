from pathlib import Path
import json
from lupa.luajit20 import LuaRuntime
R=Path(__file__).resolve().parent.parent;P=R/'gamedata/scripts'
entries=json.loads((R/'tests/optional_components.json').read_text(encoding='utf-8'))
all_deps=sorted({d for e in entries for d in e[4]})
def runtime(missing=(),error_module=None,real=False,shipping_defaults=False):
 l=LuaRuntime(unpack_returned_tuples=True)
 l.execute('''now=0;db={actor={}};calls={};lines={};missing={};writes=0
 function time_global()return now end
 function printf(...)end
 function RegisterScriptCallback(n,f) registered=f end
 function getFS()return {exist=function(self,root,name)return not missing[name]end,update_path=function()return ''end}end
 io={open=function()return {write=function(self,...)writes=writes+1 end,close=function()end}end}
 function load_module(name,source)
  local env=setmetatable({},{__index=_G});env._G=_G
  local f=assert(loadstring(source,'@'..name..'.script'));setfenv(f,env);f();_G[name]=env;return env
 end
 ''')
 for d in missing:l.globals().missing[d+'.script']=True
 l.eval('load_module')('sloptimizer_config',(P/'sloptimizer_config.script').read_text(encoding='utf-8'))
 if not shipping_defaults:
  for key in ('light_scan_cache','vision_light_frame','visibility_reads'):l.globals().sloptimizer_config[key]=True
 for core in ('sloptimizer_registry','sloptimizer_diagnostics','sloptimizer_device_clock','sloptimizer_function_binding'):l.eval('load_module')(core,(P/(core+'.script')).read_text(encoding='utf-8'))
 if real:
  for p in P.glob('*.script'):
   if p.stem not in ('sloptimizer_config','sloptimizer_bootstrap'):l.eval('load_module')(p.stem,p.read_text(encoding='utf-8'))
 else:
  for _,_,module,method,_,_ in entries:
   if not l.globals()[module]:l.globals()[module]=l.table()
   source="function() calls['"+module+'.'+method+"']=(calls['"+module+'.'+method+"'] or 0)+1; return true,'ok' end"
   if error_module==module:source="function() error('intentional initializer failure') end"
   l.globals()[module][method]=l.eval(source)
  # Only the marker prerequisite's signature check is simulated.
  l.execute("utils_catspaw_hudmarks={marker_is_offscreen=function()end}; local old=debug.getinfo; debug.getinfo=function(f,...) if f==utils_catspaw_hudmarks.marker_is_offscreen then return {source='@utils_catspaw_hudmarks.script',linedefined=1738}end;return old(f,...)end")
  if 'utils_catspaw_hudmarks' in missing:l.globals().utils_catspaw_hudmarks=None
 pack=l.eval('load_module')('sloptimizer_bootstrap',(P/'sloptimizer_bootstrap.script').read_text(encoding='utf-8'))
 return l,pack

count=0
for missing in [[],all_deps,['utils_catspaw_hudmarks','ui_hud_dotmarks']]+[[d] for d in all_deps]:
 l,p=runtime(missing)
 p.actor_on_update();assert l.globals().writes==0
 l.globals().now=5000;p.actor_on_update()
 result=list(p.start().values());assert len(result)==len(entries)
 for e,line in zip(entries,result):
  expected='SKIPPED' if any(d in missing for d in e[4]) else 'ACTIVE'
  assert ': '+expected+' - ' in line,(missing,e,line)
 writes=l.globals().writes;p.actor_on_update();p.start();assert l.globals().writes==writes
 count+=1
for module in sorted({e[2] for e in entries}):
 l,p=runtime(error_module=module);result=list(p.start().values())
 assert len(result)==len(entries)
 for e,line in zip(entries,result):assert (': ERROR - ' if e[2]==module else ': ACTIVE - ') in line,(e,line)
 count+=1
# Actually load each released initializer, with every optional script absent.
l,p=runtime(all_deps,real=True);result=list(p.start().values())
assert len(result)==len(entries) and all(': SKIPPED - ' in x for x in result),result
count+=1
# Dots present but disabled/no markers: no whole-pack wait.
l,p=runtime();l.execute('ui_hud_dotmarks={scanning=false,cfg={markers={}}}')
p.actor_on_update();l.globals().now=5000;p.actor_on_update();assert l.globals().writes>0
count+=1
# Unsupported but present optional scripts must not block others.
l,p=runtime(real=True)
for d in all_deps:l.globals()[d]=l.table()
result=list(p.start().values());assert len(result)==len(entries)
assert not any(': ERROR - ' in x for x in result),result
count+=1
print(count,'optional-mod scenarios passed: missing individually/all together, disabled dots, unsupported variants, initializer fault isolation, one-time startup')

# Each registry ID can be disabled independently, including the two native-read components.
for entry in json.loads((R/'tests/components.json').read_text(encoding='utf-8')):
 l,p=runtime();l.globals().sloptimizer_config.disabled_components[entry['id']]=True
 result=list(p.start().values())
 assert sum(': DISABLED - ' in x for x in result)==1,entry
 assert sum(': ACTIVE - ' in x for x in result)==len(entries)-1,entry
print('19 independent component-disable scenarios passed')

# Shipping defaults must leave all three gameplay-facing targets untouched.
l,p=runtime(real=True,shipping_defaults=True)
l.execute("""
local original=function()return 11 end
local wrapper=function(...)return original(...)end
visual_memory_manager={get_visible_value=wrapper,lights_lum=function()return .5 end}
bind_light_furniture={need_flicker=function()return false end}
before_wrapper=wrapper;before_original=original
before_light=visual_memory_manager.lights_lum;before_flicker=bind_light_furniture.need_flicker
""")
result=list(p.start().values())
assert sum(': DISABLED - ' in x for x in result)==3,result
l.execute("""
assert(visual_memory_manager.get_visible_value==before_wrapper)
local name,value=debug.getupvalue(before_wrapper,1);assert(value==before_original)
assert(visual_memory_manager.lights_lum==before_light)
assert(bind_light_furniture.need_flicker==before_flicker)
""")
print('Shipping defaults preserve visibility, wrapper upvalue, world lighting and lamp query identities')
