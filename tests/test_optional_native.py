from pathlib import Path
from lupa.luajit20 import LuaRuntime
P=Path(__file__).resolve().parent.parent/'gamedata/scripts/gamma_opt_native_reads.script'
count=0
for vision,device,wrapped in ((True,False,False),(False,True,False),(True,True,False),(True,False,True),(True,True,True),(False,False,False)):
 l=LuaRuntime(unpack_returned_tuples=True);l.execute(P.read_text())
 l.execute(r'''
 function make_original(file,line)
  return assert(loadstring(string.rep('\n',line-1)..'return function() return 17 end','@'..file..'.script'))()
 end
 replacement=function()return 23 end
 -- Test initializer routing independently of the separately verified replacement bodies.
 bind_body=function(old,body)return replacement end
 ''')
 if vision:
  l.execute("original=make_original('visual_memory_manager',28);visual_memory_manager={get_visible_value=original}")
  if wrapped:
   l.execute("local code=string.rep('\\n',18)..'local orig=original;return function()return orig() end';outer=assert(loadstring(code,'@xrr_patch_stealth.script'))();visual_memory_manager.get_visible_value=outer")
 if device:l.execute("item_device={device_binder={update=make_original('item_device',700)}}")
 v=l.eval('start_vision')()[0];d=l.eval('start_device')()[0]
 assert v==vision and d==device,(vision,device,wrapped,v,d)
 if vision:
  assert l.eval('visual_memory_manager.get_visible_value()')==23
  if wrapped:assert l.eval('visual_memory_manager.get_visible_value==outer')
  assert l.eval('start_vision')()[0]
 if device:assert l.eval('item_device.device_binder.update==replacement') and l.eval('start_device')()[0]
 count+=1
print(count,'independent visibility/device initializer scenarios passed, including preserved multiplayer wrapper')
