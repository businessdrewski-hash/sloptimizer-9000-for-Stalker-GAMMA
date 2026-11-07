"""Exercise the split modules through their real public API."""
from pathlib import Path
from lupa.luajit20 import LuaRuntime
ROOT=Path(__file__).resolve().parent.parent
vm=LuaRuntime(unpack_returned_tuples=True)
vm.execute("""
function load_module(name,source)
 local env=setmetatable({},{__index=_G});env._G=_G
 local chunk=assert(loadstring(source,'@'..name..'.script'));setfenv(chunk,env);chunk();_G[name]=env;return env
end
""")
def load(name):return vm.globals().load_module(name,(ROOT/'gamedata/scripts'/(name+'.script')).read_text(encoding='utf-8'))
binding=load('sloptimizer_function_binding')
vm.execute("""
local state=1
local old=function()state=state+1;return state end
local new=assert(sloptimizer_function_binding.bind_body(old,'function()state=state+2;return state end','@test'))
assert(new()==3 and old()==4 and new()==6)
""")
load('sloptimizer_device_clock')
load('sloptimizer_light_flicker')
load('sloptimizer_party_session')
load('sloptimizer_visibility')
load('sloptimizer_device_updates')
vm.execute("""
assert(type(sloptimizer_light_flicker.install)=='function')
assert(type(sloptimizer_party_session.install)=='function')
assert(sloptimizer_visibility.replacement_source():find('function',1,true))
assert(sloptimizer_device_updates.replacement_source():find('function',1,true))
local tick=7;function time_global()return tick end
local clock=sloptimizer_device_clock.make_clock();assert(clock()==7);tick=19;assert(clock()==19)
""")
print('Split-module loading, live-clock fallback and shared mutable upvalues passed')
