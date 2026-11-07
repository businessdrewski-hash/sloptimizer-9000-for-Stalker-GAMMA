from pathlib import Path
from lupa.luajit20 import LuaRuntime
P=Path(__file__).resolve().parent.parent/'gamedata/scripts'
v=LuaRuntime(unpack_returned_tuples=True)
v.execute("""
function load_module(name,source)
 local e=setmetatable({},{__index=_G});local f=assert(loadstring(source,'@'..name..'.script'));setfenv(f,e);f();_G[name]=e;return e
end
""")
for n in ('sloptimizer_function_binding','sloptimizer_visibility','sloptimizer_light_flicker'):
 v.globals().load_module(n,(P/(n+'.script')).read_text(encoding='utf-8'))
text=(P/'sloptimizer_light_flicker.script').read_text(encoding='utf-8')
reference=text.split('local reference_body = [====[\n',1)[1].split('\n]====]',1)[0]
def upstream(body):
 source="local psi_influence_clsid={[1]=true};local switch=false\n"+'\n'*31+body.replace('function(lamp_obj)','function need_flicker(lamp_obj)',1)+"\nfunction set_state(k,s)psi_influence_clsid=k;switch=s end"
 v.execute("local e=setmetatable({},{__index=_G});local f=assert(loadstring(...,'@bind_light_furniture.script'));setfenv(f,e);f();bind_light_furniture=e",source)
v.execute("""
emission=false;events={};objects={};fail=false;reenter=false
level_environment={get_light_flicker=function()return emission end}
lamp={position=function()return 1 end}
level={iterate_nearest=function(pos,rad,visit)
 assert(pos==1 and rad==15);events[#events+1]='scan'
 if fail then fail=false;error('scan failure')end
 if reenter then reenter=false;bind_light_furniture.need_flicker(lamp)end
 for _,o in ipairs(objects)do local result=visit(o);events[#events+1]=tostring(result)end
end}
function obj(kind,alive)return {clsid=function()events[#events+1]='class';return kind end,alive=function()events[#events+1]='alive';return alive end}end
""")
upstream(reference)
v.execute("original=bind_light_furniture.need_flicker;local ok,why=sloptimizer_light_flicker.install();assert(ok,why);optimized=bind_light_furniture.need_flicker")
v.execute("""
for i=1,1000 do
 emission=i%13==0
 bind_light_furniture.set_state(i%3==0 and {[2]=true} or {[1]=true},i%2==0)
 objects={obj(i%3,i%5~=0),obj(1,true),obj(2,false)}
 events={};local a=original(lamp);local ae=table.concat(events,',')
 events={};local b=optimized(lamp);local be=table.concat(events,',')
 assert(a==b and ae==be)
end
emission=false;fail=true;assert(not pcall(optimized,lamp));assert(pcall(optimized,lamp))
reenter=true;assert(pcall(optimized,lamp))
""")
# Same source lines but a changed radius must be rejected, without replacing the original.
v.globals().load_module('sloptimizer_light_flicker',text)
upstream(reference.replace(', 15,',', 14,'))
v.execute("local original=bind_light_furniture.need_flicker;local ok=sloptimizer_light_flicker.install();assert(not ok);assert(bind_light_furniture.need_flicker==original)")
# Strict matching must reject a modified visibility constant, even at the accepted source line.
text=(P/'sloptimizer_visibility.script').read_text(encoding='utf-8')
body=text.split('local reference_body = [====[\n',1)[1].split('\n]====]',1)[0]
v.execute("candidate=assert(loadstring('return '.. ...))()",body.replace('/ 3.02','/ 3.03'))
v.execute("assert(sloptimizer_visibility.matching_body(candidate)==nil)")
v.execute("local original=require;require=function()error('jit.util unavailable')end;assert(sloptimizer_visibility.matching_body(candidate)==nil);require=original")
print('1,000 live lamp scans matched decisions and read sequence; state replacement, errors, re-entry and unknown-body rejection passed')
