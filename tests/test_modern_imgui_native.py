"""Native helper contracts; real Linux process tests are explicitly opt-in."""
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
import types

SCRIPTS=Path(__file__).resolve().parents[1]/'skills/modern-imgui/scripts'
# Load checked-in helpers without writing bytecode into packaged skill content.
support=types.ModuleType('native_support');support.__file__=str(SCRIPTS/'native_support.py')
exec(compile(Path(support.__file__).read_bytes(),support.__file__,'exec'),support.__dict__)
previous=sys.modules.get('native_support');sys.modules['native_support']=support
capture=types.ModuleType('capture_native');capture.__file__=str(SCRIPTS/'capture_native.py')
exec(compile(Path(capture.__file__).read_bytes(),capture.__file__,'exec'),capture.__dict__)
if previous is None:sys.modules.pop('native_support',None)
else:sys.modules['native_support']=previous
encode_capture,compare=capture.encode_capture,capture.compare
evidence_directory=support.evidence_directory

class Captures(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
    def ppm(self,name,data=b'\x01\x02\x03\x04\x05\x06'):
        p=self.root/name;p.write_bytes(b'P6\n2 1\n255\n'+data);return p
    def invoke(self,*args):
        return subprocess.run([sys.executable,'-B',str(SCRIPTS/'capture_native.py'),*map(str,args)],capture_output=True,text=True,timeout=10)
    def test_lossless_png_preserves_exact_rgb(self):
        p=self.ppm('frame.ppm');r=encode_capture(p);data=p.with_suffix('.png').read_bytes();self.assertEqual(data[:8],b'\x89PNG\r\n\x1a\n');offset=8;compressed=b''
        while offset<len(data):
            count=struct.unpack('!I',data[offset:offset+4])[0];name=data[offset+4:offset+8];payload=data[offset+8:offset+8+count]
            self.assertEqual(struct.unpack('!I',data[offset+8+count:offset+12+count])[0],zlib.crc32(name+payload))
            if name==b'IDAT':compressed+=payload
            offset+=12+count
        self.assertEqual(zlib.decompress(compressed),b'\0'+p.read_bytes().split(b'\n',3)[3]);self.assertEqual((r['width'],r['height']),(2,1))
    def test_malformed_or_empty_frame_rejected(self):
        for value in [b'P6\n0 0\n255\n',b'P6\n2 1\n255\nx',b'P3\n1 1\n255\nabc']:
            p=self.root/'bad.ppm';p.write_bytes(value)
            with self.assertRaises(ValueError):encode_capture(p)
    def test_exact_comparison_and_wrong_pixels(self):
        a=self.ppm('a.ppm');b=self.ppm('b.ppm');self.assertTrue(compare(a,b)['passed']);b.write_bytes(b.read_bytes()[:-1]+b'x');self.assertEqual(compare(a,b)['changedChannels'],1)
    def test_missing_capture_and_wrong_count_fail(self):
        self.assertNotEqual(self.invoke(self.root,'--expected',1).returncode,0);self.ppm('a.ppm');self.assertNotEqual(self.invoke(self.root,'--expected',2).returncode,0)
    def test_candidate_not_automatically_approved(self):
        self.ppm('a.ppm');r=self.invoke(self.root,'--expected',1);self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(json.loads((self.root/'capture-manifest.json').read_text())['status'],'candidate')
    def test_explicit_baseline_approval_compare_and_drift(self):
        self.ppm('a.ppm');candidate=self.root/'candidate';candidate.mkdir();shutil.copy2(self.root/'a.ppm',candidate/'a.ppm')
        self.assertEqual(self.invoke(self.root,'--expected',1).returncode,0)
        self.assertNotEqual(self.invoke(candidate,'--expected',1,'--baseline',self.root).returncode,0)
        self.assertEqual(self.invoke(self.root,'--expected',1,'--accept-baseline').returncode,0)
        self.assertEqual(self.invoke(candidate,'--expected',1,'--baseline',self.root).returncode,0)
        p=self.root/'a.ppm';p.write_bytes(p.read_bytes()[:-1]+b'x');self.assertNotEqual(self.invoke(candidate,'--expected',1,'--baseline',self.root).returncode,0)
    def test_comparison_never_overwrites_own_baseline(self):
        self.ppm('a.ppm');self.assertEqual(self.invoke(self.root,'--expected',1,'--accept-baseline').returncode,0);before=(self.root/'capture-manifest.json').read_bytes();self.assertNotEqual(self.invoke(self.root,'--expected',1,'--baseline',self.root).returncode,0);self.assertEqual((self.root/'capture-manifest.json').read_bytes(),before)
    def test_installed_skill_is_not_an_artifact_destination(self):
        with self.assertRaises(ValueError):evidence_directory(SCRIPTS/'must-not-be-created')
    def test_prerequisite_probe_does_not_create_output(self):
        output=self.root/'absent';r=subprocess.run([sys.executable,'-B',str(SCRIPTS/'run_owned_display.py'),'--probe','--output',str(output)],capture_output=True,text=True,timeout=10);self.assertIn(r.returncode,[0,2]);self.assertFalse(output.exists());self.assertIn('available',json.loads(r.stdout))

@unittest.skipUnless(os.environ.get('MODERN_IMGUI_NATIVE_TESTS')=='1','real owned Linux display tests explicitly opt-in')
class NativeProcessContracts(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
    def run_child(self,code,*args):
        r=subprocess.run([sys.executable,'-B',str(SCRIPTS/'run_owned_display.py'),'--output',str(self.root),*args,'--',sys.executable,'-c',code],capture_output=True,text=True,timeout=30)
        paths=list(self.root.glob('run-*/processes.json'));self.assertEqual(len(paths),1,r.stderr);receipt=json.loads(paths[0].read_text())
        self.assertTrue(all(p.get('settled') and not p.get('remainingLiveGroupMembers') for p in receipt['processes']),receipt)
        if 'child' in receipt:self.assertTrue(receipt['child']['settled']);self.assertFalse(receipt['child'].get('remainingLiveGroupMembers'))
        return r,receipt,paths[0].parent
    def test_failed_child_and_descendant_are_settled(self):
        r,p,_=self.run_child("import subprocess,sys;subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)']);sys.exit(7)")
        self.assertEqual(r.returncode,7,r.stderr);self.assertEqual(p['child']['exit'],7)
    def test_outer_timeout_enters_child_and_cleans_processes(self):
        r,p,out=self.run_child("import time;print('ENTERED',flush=True);time.sleep(30)",'--timeout','.2');self.assertNotEqual(r.returncode,0);self.assertTrue(p['timedOut']);self.assertIn('ENTERED',(out/'command.log').read_text())
    def test_window_manager_readiness_failure_cleans_server(self):
        r,p,_=self.run_child('pass','--wm-command',json.dumps([sys.executable,'-c','raise SystemExit(3)']));self.assertNotEqual(r.returncode,0);self.assertNotIn('child',p)
    @unittest.skipUnless(os.environ.get('MODERN_IMGUI_NATIVE_BINARY'),'native entry executable supplied separately')
    def test_actual_entry_failure_reports_counts_and_cleans_app(self):
        r=subprocess.run([sys.executable,'-B',str(SCRIPTS/'run_owned_display.py'),'--output',str(self.root),'--',sys.executable,'-B',str(SCRIPTS/'smoke_native_entry.py'),'--binary',os.environ['MODERN_IMGUI_NATIVE_BINARY'],'--output','{output}/entry','--inject-failure'],capture_output=True,text=True,timeout=30)
        self.assertEqual(r.returncode,1,r.stderr)
        folder=next(self.root.glob('run-*'));result=json.loads((folder/'entry/result.json').read_text());processes=json.loads((folder/'processes.json').read_text())
        self.assertEqual(result['executed'],result['passed']+result['failed']);self.assertEqual(result['failed'],1);self.assertTrue(result['appSettled']);self.assertTrue(processes['child']['settled']);self.assertFalse(processes['child']['remainingLiveGroupMembers'])

if __name__=='__main__':unittest.main()
