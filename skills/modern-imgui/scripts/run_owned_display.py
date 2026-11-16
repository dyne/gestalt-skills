# Copyright (c) 2026 Plan-B Foundation
# Copyright (c) 2026 Dyne.org foundation (adaptation)
# SPDX-License-Identifier: MIT
"""Authenticated child-owned Linux display; no installation or user config."""
import sys
sys.dont_write_bytecode=True
import argparse
import ctypes
import json
import os
from pathlib import Path
import secrets
import shutil
import ctypes.util
import signal
import struct
import subprocess
import tempfile
import time
from datetime import datetime,timezone

from native_support import validated_scratch,evidence_directory


def main():
    def interrupted(*_):raise RuntimeError('owned display interrupted')
    signal.signal(signal.SIGTERM,interrupted)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--probe', action='store_true', help='Read-only prerequisite check; starts no display')
    parser.add_argument('--wm-command', default='["marco","--sm-disable","--no-composite"]', help='JSON argv; launched inside a private D-Bus session')
    parser.add_argument('--timeout', type=float, default=120)
    parser.add_argument('--display-start', type=int, default=811)
    parser.add_argument('--dpi', type=int, default=96)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command and args.command[0] == '--' else args.command
    try: wm_command=json.loads(args.wm_command)
    except json.JSONDecodeError: parser.error('--wm-command must be a JSON argv array')
    if not isinstance(wm_command,list) or not wm_command or any(not isinstance(x,str) or not x for x in wm_command):parser.error('invalid window-manager argv')
    if not 0<args.timeout<=3600 or not 1<=args.dpi<=768 or not 1<=args.display_start<=60000:parser.error('invalid timeout, DPI or display range')
    missing=[name for name in ['Xvfb','xrdb','dbus-run-session',wm_command[0]] if not shutil.which(name)]
    missing += [name for name in ['X11','GL','Xtst'] if not ctypes.util.find_library(name)]
    if args.probe:
        print(json.dumps(dict(available=not missing,missing=missing,wm=wm_command,scope='prerequisites only; no runtime/rendering qualification')))
        return 2 if missing else 0
    if not command or args.output is None:parser.error('--output and a command after -- are required')
    if missing:
        args.output=evidence_directory(args.output)
        (args.output/'processes.json').write_text(json.dumps(dict(status='unavailable',missing=missing,processes=[],result=2))+'\n')
        print(json.dumps(dict(status='unavailable',missing=missing)))
        return 2
    args.output=Path(tempfile.mkdtemp(prefix='run-',dir=evidence_directory(args.output)))
    command=[value.replace('{output}',str(args.output)) for value in command]
    xlib = ctypes.CDLL('libX11.so.6')
    xlib.XOpenDisplay.argtypes = [ctypes.c_char_p]; xlib.XOpenDisplay.restype = ctypes.c_void_p
    xlib.XDefaultRootWindow.argtypes = [ctypes.c_void_p]; xlib.XDefaultRootWindow.restype = ctypes.c_ulong
    xlib.XInternAtom.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]; xlib.XInternAtom.restype = ctypes.c_ulong
    xlib.XGetWindowProperty.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_long, ctypes.c_long, ctypes.c_int, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_void_p)]
    xlib.XCloseDisplay.argtypes = [ctypes.c_void_p]; xlib.XFree.argtypes = [ctypes.c_void_p]
    record = {'command': command, 'dpi': args.dpi, 'processes': [], 'result': None,'startUTC':datetime.now(timezone.utc).isoformat()}
    scratch_root=validated_scratch()
    literal=os.environ.get('TMPDIR')
    if literal and Path(literal).resolve()==scratch_root:scratch_root=literal
    with tempfile.TemporaryDirectory(prefix='imgui-native-', dir=scratch_root) as scratch:
        folder = Path(scratch)
        for number in range(args.display_start, args.display_start+100):
            socket = Path('/tmp/.X11-unix')/('X'+str(number))
            if not socket.exists() and not Path('/tmp/.X'+str(number)+'-lock').exists(): break
        else: raise RuntimeError('no free owned display')
        auth = folder/'Xauthority'
        def field(value): return struct.pack('!H', len(value))+value
        auth.write_bytes(struct.pack('!H', 65535)+field(b'')+field(str(number).encode())+field(b'MIT-MAGIC-COOKIE-1')+field(secrets.token_bytes(16)))
        auth.chmod(0o600)
        env = os.environ | {'DISPLAY': ':'+str(number), 'XAUTHORITY': str(auth),
            'MODERN_IMGUI_OWNED_DISPLAY': ':'+str(number), 'LIBGL_ALWAYS_SOFTWARE': '1',
            'GSETTINGS_BACKEND': 'memory', 'NO_AT_BRIDGE': '1',
            'XDG_CONFIG_HOME': str(folder/'config'), 'XDG_CACHE_HOME': str(folder/'cache'),
            'XDG_DATA_HOME': str(folder/'data'), 'XDG_RUNTIME_DIR': str(folder/'runtime')}
        for name in ['config', 'cache', 'data', 'runtime']: (folder/name).mkdir(mode=0o700)
        logs = [(args.output/n).open('wb') for n in ['xvfb.log', 'wm.log', 'command.log']]
        server = wm = child = None
        try:
            argv = ['Xvfb', ':'+str(number), '-screen', '0', '3200x2200x24', '-nolisten', 'tcp', '-noreset', '-auth', str(auth), '-dpi', str(args.dpi)]
            server = subprocess.Popen(argv, env=env, stdout=logs[0], stderr=subprocess.STDOUT)
            record['processes'].append({'kind': 'Xvfb', 'pid': server.pid, 'argv': argv})
            deadline = time.monotonic()+10
            while not socket.exists():
                if server.poll() is not None or time.monotonic() > deadline: raise RuntimeError('owned display failed readiness')
                time.sleep(.02)
            subprocess.run(['xrdb', '-load'], input=f'Xft.dpi: {args.dpi}\n', env=env, text=True, check=True)
            argv = ['dbus-run-session', '--']+wm_command
            wm = subprocess.Popen(argv, env=env, stdout=logs[1], stderr=subprocess.STDOUT, start_new_session=True)
            record['processes'].append({'kind': 'WM/private-D-Bus', 'pid': wm.pid, 'pgid': wm.pid, 'argv': argv})
            # Use a separate authenticated connection without changing this process's environment.
            saved_auth = os.environ.get('XAUTHORITY')
            os.environ['XAUTHORITY'] = str(auth)
            try: display = xlib.XOpenDisplay(env['DISPLAY'].encode())
            finally:
                if saved_auth is None: os.environ.pop('XAUTHORITY', None)
                else: os.environ['XAUTHORITY'] = saved_auth
            if not display: raise RuntimeError('owned display authentication failed')
            try:
                atom = xlib.XInternAtom(display, b'_NET_SUPPORTING_WM_CHECK', 0)
                deadline = time.monotonic()+10
                while True:
                    actual = ctypes.c_ulong(); fmt = ctypes.c_int(); count = ctypes.c_ulong(); remaining = ctypes.c_ulong(); data = ctypes.c_void_p()
                    xlib.XGetWindowProperty(display, xlib.XDefaultRootWindow(display), atom, 0, 1, 0, 0, ctypes.byref(actual), ctypes.byref(fmt), ctypes.byref(count), ctypes.byref(remaining), ctypes.byref(data))
                    ready = count.value == 1
                    if data: xlib.XFree(data)
                    if ready: break
                    if wm.poll() is not None or time.monotonic() > deadline: raise RuntimeError('real WM failed readiness')
                    time.sleep(.02)
            finally: xlib.XCloseDisplay(display)
            child=subprocess.Popen(command,env=env,stdout=logs[2],stderr=subprocess.STDOUT,start_new_session=True)
            try:child.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid,signal.SIGKILL);child.wait(timeout=5);record['timedOut']=True
            record['result']=child.returncode
            record['child']={'pid':child.pid,'exit':child.returncode,'settled':child.poll() is not None}
        finally:
            if child:
                if child.poll() is None:
                    os.killpg(child.pid,signal.SIGTERM)
                    try:child.wait(timeout=5)
                    except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait(timeout=5)
                record['child']={'pid':child.pid,'exit':child.returncode,'settled':child.poll() is not None}
                if record['result'] is None:record['result']=1
            if wm:
                try: os.killpg(wm.pid, signal.SIGTERM)
                except ProcessLookupError: pass
                try: wm.wait(timeout=5)
                except subprocess.TimeoutExpired: os.killpg(wm.pid, signal.SIGKILL); wm.wait(timeout=5)
                record['processes'][1].update(exit=wm.returncode, settled=wm.poll() is not None)
                def live_members():
                    members = []
                    for status in Path('/proc').glob('[0-9]*/stat'):
                        try:
                            fields = status.read_text().rsplit(')', 1)[1].split()
                            if int(fields[2]) == wm.pid and fields[0] != 'Z': members.append(int(status.parent.name))
                        except (OSError, ValueError, IndexError): pass
                    return members
                deadline = time.monotonic()+2
                while (live := live_members()) and time.monotonic() < deadline: time.sleep(.02)
                if live:
                    os.killpg(wm.pid, signal.SIGKILL)
                    deadline = time.monotonic()+2
                    while (live := live_members()) and time.monotonic() < deadline: time.sleep(.02)
                record['processes'][1]['remainingLiveGroupMembers'] = live
                if live: record['result'] = 1
            if server:
                server.terminate()
                try: server.wait(timeout=5)
                except subprocess.TimeoutExpired: server.kill(); server.wait(timeout=5)
                record['processes'][0].update(exit=server.returncode, settled=server.poll() is not None)
            for log in logs: log.close()
            if child:
                # The leader may have exited while a descendant stayed alive.
                try:os.killpg(child.pid,signal.SIGTERM)
                except ProcessLookupError:pass
                deadline=time.monotonic()+2
                def command_members():
                    found=[]
                    for stat in Path('/proc').glob('[0-9]*/stat'):
                        try:
                            fields=stat.read_text().rsplit(')',1)[1].split()
                            if int(fields[2])==child.pid and fields[0]!='Z':found.append(int(stat.parent.name))
                        except (OSError,ValueError,IndexError):pass
                    return found
                while command_members() and time.monotonic()<deadline:time.sleep(.02)
                live=command_members()
                if live:
                    try:os.killpg(child.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    deadline=time.monotonic()+2
                    while command_members() and time.monotonic()<deadline:time.sleep(.02)
                record['child']['remainingLiveGroupMembers']=command_members()
                if record['child']['remainingLiveGroupMembers']:record['result']=1
            if record['result'] is None:record['result']=1
            record['auth'] = 'ephemeral local test cookie removed with owned scratch; no cookie logged'
            record['display'] = env['DISPLAY']
            record['endUTC']=datetime.now(timezone.utc).isoformat()
            (args.output/'processes.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(dict(output=str(args.output),exit=record['result'],timedOut=record.get('timedOut',False))))
    return record['result'] if isinstance(record['result'],int) and record['result']>=0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
