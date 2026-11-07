from pathlib import Path
import hashlib, json, random, math
from lupa.luajit20 import LuaRuntime

ROOT=Path(__file__).resolve().parent.parent
PACK=ROOT
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--mods-root',type=Path,required=True)
parser.add_argument('--output',type=Path,default=Path('ai-audit-results.json'))
args=parser.parse_args()
MODS=args.mods_root
SOURCE=MODS/'290- Atmospherics Shaders Weathers and Reshade Latest - Hippobot/gamedata/scripts/visual_memory_manager.script'
WRAPPER=MODS/'xrRazom Co-op/gamedata/scripts/xrr_patch_stealth.script'
original='\n'.join(SOURCE.read_text(encoding='utf-8-sig').splitlines()[:211])
setup=r'''
c={}; events={}; reads=0
function get_console_cmd() return 'renderer_r2' end
function clamp(x,a,b) return math.max(a,math.min(x,b)) end
function time_global() return c.now end
function IsMoveState(s) return s=='mcCrouch' and c.crouch or s=='mcAccel' and c.accel end
function IsStalker(o) return o and (o.kind=='stalker' or avatar_mode and o.kind=='avatar') end
function IsMonster(o) return o and o.kind=='monster' end
stealth_mcm={get_config=function(k) if k=='debugx' then return c.debug elseif k=='michiko_patch' then return c.michiko elseif k=='crouch' then return .7 elseif k=='low_crouch' then return .4 else return 1 end end}
level={get_time_hours=function() return c.hour end,get_time_minutes=function() return c.minute end,get_target_obj=function() return c.debug_target and npc or nil end}
camp_lum={}; level_weathers={get_weather_manager=function()return {get_curr_weather_preset=function()return 'test'end}end}
weather={get_value_vector=function(k) local v=k=='sun_color' and c.sun or c.hemi; return {x=v,y=v,z=v} end}
function emit(...) local t={...};for i=1,select('#',...) do local x=select(i,...);t[i]=type(x)=='table' and 'object' or tostring(x)end;events[#events+1]=table.concat(t,'|')end
printf=emit;strformat=string.format;round_idp=function(x)return x end
news_manager={send_tip=emit};actor_menu={set_msg=emit}
function object(id,kind)
 return {kind=kind,id=function()return id end,get_luminocity=function()return c.lum end,
 object=function() reads=reads+1;return c.npc_torch_exists and {attachable_item_enabled=function()return c.npc_torch_on end} or nil end,
 alive=function()return id==2 and c.npc_alive or id~=2 and c.target_alive end,
 see=function()return c.sees end,memory_time=function()return c.now-c.memory_age end,visibility_threshold=function()return c.threshold end,
 item_in_slot=function(self,slot) reads=reads+1;if slot==10 then return c.torch_exists and {torch_enabled=function()return c.torch_on end} or nil end; return c.flash_exists and {section=function()return c.flash_section end} or nil end,
 active_detector=function()return c.detector end,get_total_weight=function()return c.weight_value end}
end
function configure(t)
 c=t;events={};reads=0
 actor=object(1,'stalker');npc=object(2,c.npc_kind);if c.no_npc then npc=nil end
 who=c.target_kind=='actor' and actor or object(3,c.target_kind)
 db={actor=actor,storage=c.storage and {[2]={active_scheme=c.scheme}} or {}}
 camp_lum.luminocity_inc=c.camp;level_weathers.bLevelUnderground=c.underground
end
function change_upvalue(fn,name,value)
 for i=1,100 do local n=debug.getupvalue(fn,i);if not n then break end;if n==name then debug.setupvalue(fn,i,value);return end end
end
function state(fn)
 local t={};for i=1,100 do local n,v=debug.getupvalue(fn,i);if not n then break end
 if n=='vision_memory' then for a,b in pairs(v) do for k,x in pairs(b)do t[#t+1]='memory:'..a..':'..k..':'..tostring(x)end end
 elseif n=='actor_marked' or n=='summ' then t[#t+1]=n..':'..tostring(v) end end
 table.sort(t);return table.concat(t,';')
end
function reset(fn)
 change_upvalue(fn,'vision_memory',{});change_upvalue(fn,'marked',{});change_upvalue(fn,'actor_marked',0);change_upvalue(fn,'summ',0)
end
function set_live(fn)
 change_upvalue(fn,'is_r1',c.r1);change_upvalue(fn,'jacketmult',c.jacket);change_upvalue(fn,'pewpewmult',c.shot)
 change_upvalue(fn,'get_camo_k',c.camo);change_upvalue(fn,'marked',c.mark and {[2]=true} or {})
end
function invoke(fn)
 return fn(npc,who,.016,c.quant,c.input_lum,c.velocity_factor,c.speed,c.range,c.object_distance,1)
end
function XrrPlayers()return {IsPlayerDummy=function(self,id)return id==3 and c.target_kind=='avatar'end}end
function XrrAvatarAwareCall(fn,...)
 wrapper_calls=wrapper_calls+1
 if c.wrapper_fail then return false,nil end
 avatar_mode=true;local ok,result=pcall(fn,...);avatar_mode=false;return ok,result
end
function log()end
'''

def vm(optimized,wrapped):
    v=LuaRuntime(unpack_returned_tuples=True)
    v.execute(setup)
    # Update private state through ordinary Lua closures, as gameplay callbacks do.
    # debug.setupvalue writes after JIT compilation are not a faithful gameplay fixture.
    state_access='''
function reset() vision_memory={};marked={};actor_marked=0;summ=0 end
function set_live() is_r1=c.r1;jacketmult=c.jacket;pewpewmult=c.shot;get_camo_k=c.camo;marked=c.mark and {[2]=true} or {} end
'''
    v.execute("assert(loadstring(...,'@visual_memory_manager.script'))()",original+state_access)
    v.execute('original_fn=get_visible_value;visual_memory_manager=_G;wrapper_calls=0')
    if wrapped:
        v.execute("assert(loadstring(...,'@xrr_patch_stealth.script'))()",WRAPPER.read_text(encoding='utf-8-sig'))
        v.execute('on_game_start()')
    if optimized:
        v.execute('sloptimizer_function_binding={};local e=setmetatable(sloptimizer_function_binding,{__index=_G});local f=assert(loadstring(...));setfenv(f,e);f()', (PACK/'gamedata/scripts/sloptimizer_function_binding.script').read_text())
        v.execute('sloptimizer_visibility={};local e=setmetatable(sloptimizer_visibility,{__index=_G});local f=assert(loadstring(...));setfenv(f,e);f();local ok,why=e.install();assert(ok,why)',(PACK/'gamedata/scripts/sloptimizer_visibility.script').read_text())
    return v

r=random.Random(901734)
cases=[]
for i in range(2500):
    cases.append(dict(hour=r.choice([0,3,4,5,12,20,21,22,23]),minute=r.choice([0,1,30,59]),sun=r.random(),hemi=r.random(),lum=r.random(),input_lum=r.choice([0,.1,.8]),michiko=r.choice([True,False]),r1=r.choice([True,False]),underground=r.choice([True,False]),camp=r.choice([0,.1,.5]),crouch=r.choice([True,False]),accel=r.choice([True,False]),torch_exists=r.choice([True,False]),torch_on=r.choice([True,False]),flash_exists=r.choice([True,False]),flash_section=r.choice(['device_flashlight','other']),detector=r.choice([True,False]),npc_torch_exists=r.choice([True,False]),npc_torch_on=r.choice([True,False]),npc_kind=r.choice(['stalker','monster','other']),target_kind=r.choice(['actor','stalker','monster','avatar']),no_npc=i%13==0,npc_alive=i%7!=0,target_alive=i%11!=0,sees=True,storage=r.choice([True,False]),scheme=r.choice(['guard','sniper','combat']),weight_value=r.choice([0,20,70,150]),jacket=r.choice([1,2,4.5]),shot=r.choice([0,7]),camo=r.choice([0,1,10]),mark=i%17==0,now=100000,memory_age=r.choice([1,1000,10000,80000]),threshold=35,quant=r.choice([.008,.016,.1]),velocity_factor=r.random(),speed=r.choice([0,.1,4]),range=r.choice([-1,0,50,90,90.01,100]),object_distance=r.choice([.01,10,24.99,25,25.01,29.99,30,30.01,100]),debug=i%19==0,debug_target=i%38==0,wrapper_fail=i%23==0))

reports=[]
for source in (MODS/'G.A.M.M.A. Stealth Crash Fix/gamedata/scripts/visual_memory_manager.script',SOURCE):
 original='\n'.join(source.read_text(encoding='utf-8-sig').splitlines()[:211])
 comparisons=0;mismatches=0;material=0;first_difference=None
 for wrapped in (False,True):
    a,b=vm(False,wrapped),vm(True,wrapped)
    for idx,c in enumerate(cases):
        for v in (a,b):v.globals().reset(v.globals().original_fn)
        # Live transitions exercise shared upvalues and vision-memory accumulation.
        for step in range(6):
            d=dict(c,sees=step in (0,3),torch_on=step%2==0,detector=step%2!=0,shot=7 if step==2 else 0,now=100000+step*100,memory_age=c['memory_age']+step*100)
            values=[]
            for v in (a,b):
                v.globals().configure(v.table_from(d));v.globals().set_live(v.globals().original_fn)
                result=v.globals().invoke(v.globals().get_visible_value)
                values.append((result,v.globals().state(v.globals().original_fn),v.eval("table.concat(events,'\\n')"),v.globals().wrapper_calls))
            if values[0]!=values[1]:
                mismatches+=1
                if not math.isclose(values[0][0],values[1][0],rel_tol=1e-12,abs_tol=1e-12) or values[0][1:]!=values[1][1:]:material+=1
                if first_difference is None:first_difference={'case':idx,'step':step,'wrapped':wrapped,'original':values[0][0],'replacement':values[1][0]}
            comparisons+=1
 reports.append({'source':source.parent.parent.parent.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'comparisons':comparisons,'exact_mismatches':mismatches,'material_mismatches':material,'first_difference':first_difference})

# Exercise the actual cache factory with the real world-light helper.
v=vm(False,False)
v.execute((PACK/'gamedata/scripts/sloptimizer_world_lighting.script').read_text())
v.globals().configure(v.table_from(cases[0]))
v.execute('frame=1;cached=make_cache(lights_lum,function()return frame end)')
v.execute('c.sun=.1;c.hemi=.1')
first=v.globals().cached()
v.execute('c.sun=.9;c.hemi=.9')
stale=v.globals().cached();live=v.globals().lights_lum()
assert stale==first and live!=stale
# Use those values in actual detection code to establish whether the discrepancy matters.
v.execute('live_light=lights_lum;lights_lum=cached;c.r1=false;c.npc_alive=true;c.target_alive=true;c.no_npc=false;c.target_kind="actor";c.object_distance=10;c.range=100;c.sees=false;c.shot=0;c.mark=false;c.hour=12;configure(c);set_live(original_fn)')
cached_detection=v.globals().invoke(v.globals().get_visible_value)
v.execute('lights_lum=live_light')
live_detection=v.globals().invoke(v.globals().get_visible_value)
assert cached_detection!=live_detection
v.execute('frame=2');assert v.globals().cached()==live
v.execute('frame=nil;c.sun=.2;c.hemi=.2');assert v.globals().cached()==v.globals().lights_lum()

v.execute('clock=0;psi=false;emission=false;device=function()return {time_global=function()return clock end}end;level_environment={get_light_flicker=function()return emission end};sloptimizer_device_clock={}')
v.execute('local f=assert(loadstring(...));setfenv(f,setmetatable(sloptimizer_device_clock,{__index=_G}));f()', (PACK/'gamedata/scripts/sloptimizer_device_clock.script').read_text())
v.execute((PACK/'gamedata/scripts/sloptimizer_light_flicker.script').read_text())
v.execute('lamp={};original_flicker=function()return psi end;cached_flicker=make_light_cache(original_flicker,100);assert(cached_flicker(lamp)==false);clock=50;psi=true;assert(original_flicker(lamp)==true and cached_flicker(lamp)==false);emission=true;assert(cached_flicker(lamp)==true);emission=false;clock=100;assert(cached_flicker(lamp)==true)')
report={'visibility':reports,'wrapper_sha256':hashlib.sha256(WRAPPER.read_bytes()).hexdigest(),'world_cache_same_frame_counterexample':{'cached_light':stale,'live_light':live,'cached_detection':cached_detection,'live_detection':live_detection},'lamp_cache':'A change from no psi influence to psi influence at 50 ms remains cached false until 100 ms; emission bypass works. This changes lamp-animation timing; downstream AI effect not measured.','scope':'Deterministic Lua differential tests with mocked engine inputs. Not live combat validation.'}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
