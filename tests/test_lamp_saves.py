from pathlib import Path
from lupa.luajit20 import LuaRuntime
P=Path(__file__).resolve().parent.parent/'gamedata/scripts'
v=LuaRuntime(unpack_returned_tuples=True)
v.execute("""
stores={};history={};inputs={};writes=0
function se_load_var(id) return stores[id] end
function se_save_var(id,unused,key,value)
 stores[id]=value;writes=writes+1;history[#history+1]={id=id,condition=value.condition}
end
hf_obj_manager={}
""")
manager="""local varname = 'hf_data'

-- Soft update
function update_data(id, data)
 local hf_data = se_load_var(id, nil, varname) or {}
 for index, datum in pairs(data) do
  hf_data[index] = datum
 end
 se_save_var(id, nil, varname, hf_data)
end
"""
v.execute("local f=assert(loadstring(...,'@hf_obj_manager.script'));setfenv(f,setmetatable(hf_obj_manager,{__index=_G}));f()",manager)
v.execute("bind_light_furniture={placeable_light_wrapper={}}")
original="\n"*222+"""function placeable_light_wrapper:save_data()
 hf_obj_manager.update_data(self.object:id(), {
  condition = self.fuel
 })
end
"""
v.execute("local f=assert(loadstring(...,'@bind_light_furniture.script'));setfenv(f,setmetatable(bind_light_furniture,{__index=_G}));f()",original)
v.execute((P/'sloptimizer_lamp_save_buffers.script').read_text())
v.execute("""
local old=bind_light_furniture.placeable_light_wrapper.save_data
local ok,why=install();assert(ok,why)
local new=bind_light_furniture.placeable_light_wrapper.save_data
local lamps={};for id=1,2 do lamps[id]={object={id=function()return id end},fuel=1} end
for i=1,1000 do
 local lamp=lamps[i%2+1];lamp.fuel=(i%101)/100
 old(lamp);local expected=history[#history].condition
 new(lamp);assert(history[#history].condition==expected)
end
assert(writes==2000)
-- Earlier snapshots are values, not references to the reused input buffer.
assert(history[1].condition==.01 and history[2].condition==.01)
-- Replacing the manager must take the original path, including fresh tables.
local seen={}
hf_obj_manager.update_data=function(id,data) assert(not seen[data]);seen[data]=true end
new(lamps[1]);new(lamps[1])
""")
print('1,000 lamp saves matched original writes; snapshot isolation and replaced-manager fallback passed')
