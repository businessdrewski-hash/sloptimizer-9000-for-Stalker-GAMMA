"""Diagnostics must preserve call results and never silently undo another writer."""
from pathlib import Path
import unittest
from lupa.luajit20 import LuaRuntime

ROOT = Path(__file__).resolve().parent.parent


class DiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute((ROOT / 'gamedata/scripts/sloptimizer_diagnostics.script').read_text(encoding='utf-8'))
        self.lua.execute('''
            now = 0
            function profile_timer()
                local accumulated, started = 0, nil
                return {
                    start = function() started = now end,
                    stop = function() accumulated = accumulated + now - started; started = nil end,
                    time = function() return accumulated end,
                }
            end
            function statistics() return {calls=0,total_us=0,max_us=0,errors=0} end
            function setup_patch()
                example = {run = function() return 'old' end}
                spec = {id='example',switch='example_enabled',targets={'example.run'}}
                reset('test')
                local previous = before(spec)
                example.run = function(...) now=now+7;return ... end
                record(spec,'ACTIVE','test replacement',previous)
            end
        ''')

    def test_nil_arguments_and_multiple_return_values(self):
        self.lua.execute('''
            local stats=statistics()
            local f=timed(function(...) assert(select('#',...)==3);now=now+7;return ... end,profile_timer,stats)
            local a,b,c=f(1,nil,3)
            assert(a==1 and b==nil and c==3)
            assert(select('#',f(nil,nil,nil))==3)
            assert(stats.calls==2 and stats.total_us==14 and stats.max_us==7)
        ''')

    def test_zero_returns_stay_zero(self):
        self.lua.execute("local f=timed(function()end,profile_timer,statistics());assert(select('#',f())==0)")

    def test_errors_preserve_object_and_allow_next_call(self):
        self.lua.execute('''
            local token,stats={},statistics()
            local f=timed(function(fail) now=now+3;if fail then error(token)end;return true end,profile_timer,stats)
            local ok,err=pcall(f,true);assert(not ok and err==token)
            assert(f(false) and stats.errors==1 and stats.calls==2 and stats.total_us==6)
        ''')

    def test_recursive_calls_use_separate_timers(self):
        self.lua.execute('''
            local stats=statistics();local f
            f=timed(function(n)now=now+2;if n>0 then return f(n-1)end;return 5 end,profile_timer,stats)
            assert(f(2)==5 and stats.calls==3 and stats.total_us==12 and stats.max_us==6)
        ''')

    def test_locate_private_upvalue_without_loading_modules(self):
        self.lua.execute('''
            local original=function()return 8 end
            local orig=original;holder={wrapper=function()return orig()end}
            local value,setter=locate('holder.wrapper::orig');assert(value==original)
            setter(function()return 9 end);assert(holder.wrapper()==9)
            assert(locate('missing_mod.function_name')==nil)
        ''')

    def test_ownership_report_detects_later_replacement(self):
        self.lua.execute('''
            setup_patch()
            assert(table.concat(report_lines(),'\n'):find('SAME_AS_AFTER_INSTALL',1,true))
            example.run=function()end
            assert(table.concat(report_lines(),'\n'):find('CHANGED_SINCE_COMPONENT_INIT',1,true))
        '''.replace("'\n'", "'\\n'"))

    def test_no_default_timing_and_explicit_start_stop(self):
        self.lua.execute('''
            setup_patch();local original=example.run
            report_lines();assert(example.run==original)
            assert(start_timing('example.run'));assert(example.run~=original)
            assert(not start_timing('example.run'))
            example.run(nil,2)
            assert(table.concat(report_lines(),'\n'):find('inclusive_total_us=7',1,true))
            assert(stop_timing('example.run'));assert(example.run==original)
        '''.replace("'\n'", "'\\n'"))

    def test_refuses_unknown_target_or_later_writer(self):
        self.lua.execute('''
            setup_patch();assert(not start_timing('unknown.run'))
            assert(start_timing('example.run'))
            local other=function()end;example.run=other
            assert(not stop_timing('example.run') and example.run==other)
        ''')

    def test_unchanged_and_skipped_targets_are_not_instrumented(self):
        self.lua.execute('''
            setup_patch();example.other=function()end
            local s={id='skipped',switch='x',targets={'example.other'}}
            record(s,'SKIPPED','different version',before(s))
            assert(not start_timing('example.other'))
        ''')

    def test_missing_engine_timer_is_reported(self):
        self.lua.execute("setup_patch();profile_timer=nil;assert(not start_timing('example.run'))")

    def test_callable_engine_class_constructor(self):
        self.lua.execute('''
            setup_patch();local construct=profile_timer
            profile_timer=setmetatable({}, {__call=function()return construct()end})
            assert(start_timing('example.run'));example.run();assert(stop_timing('example.run'))
        ''')

    def test_invalid_timer_leaves_function_unchanged(self):
        self.lua.execute('''
            setup_patch();local original=example.run
            profile_timer=function()return {}end
            assert(not start_timing('example.run') and example.run==original)
        ''')

    def test_stop_resolves_current_namespace(self):
        self.lua.execute('''
            setup_patch();local original=example.run
            assert(start_timing('example.run'))
            example={run=example.run}
            assert(stop_timing('example.run') and example.run==original)
        ''')


if __name__ == '__main__':
    unittest.main(verbosity=2)
