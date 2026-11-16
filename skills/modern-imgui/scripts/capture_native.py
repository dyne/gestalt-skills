# Copyright (c) 2026 Plan-B Foundation
# Copyright (c) 2026 Dyne.org foundation (adaptation)
# SPDX-License-Identifier: MIT
"""Losslessly encode actual PPM readbacks as PNG and inventory native captures."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib
from native_support import evidence_directory,binary_identity


def encode_capture(ppm):
    magic, dimensions, maximum, data = ppm.read_bytes().split(b'\n', 3)
    width, height = map(int, dimensions.split())
    if magic != b'P6' or maximum != b'255' or width<=0 or height<=0 or len(data) != width*height*3:
        raise ValueError('invalid raw framebuffer capture')
    def chunk(name, payload):
        return struct.pack('!I', len(payload))+name+payload+struct.pack('!I', zlib.crc32(name+payload))
    scanlines = b''.join(b'\0'+data[y*width*3:(y+1)*width*3] for y in range(height))
    encoded = b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR', struct.pack('!2I5B', width, height, 8, 2, 0, 0, 0))+chunk(b'IDAT', zlib.compress(scanlines, 6))+chunk(b'IEND', b'')
    png = ppm.with_suffix('.png'); png.write_bytes(encoded)
    return dict(path=png.name, sha256=hashlib.sha256(encoded).hexdigest(), bytes=len(encoded), width=width, height=height,
                rawPath=ppm.name, rawSha256=hashlib.sha256(ppm.read_bytes()).hexdigest(),
                kind='native-window-frame-root-crop' if ppm.stem.endswith('-frame') else 'production-client-OpenGL-framebuffer')

def compare(left,right):
    def pixels(path):
        magic,dimensions,maximum,data=Path(path).read_bytes().split(b'\n',3)
        width,height=map(int,dimensions.split())
        if magic!=b'P6' or maximum!=b'255' or width<=0 or height<=0 or len(data)!=width*height*3:raise ValueError('invalid RGB framebuffer')
        return (width,height),data
    a,x=pixels(left);b,y=pixels(right)
    if a!=b:return dict(passed=False,reason='dimensions differ',changedChannels=None)
    changed=sum(p!=q for p,q in zip(x,y))
    return dict(passed=changed==0,changedChannels=changed)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory',type=Path);p.add_argument('--expected',type=int,required=True)
    p.add_argument('--baseline',type=Path,help='Explicit previously inspected manifest directory; never updated')
    p.add_argument('--binary',type=Path,help='Executable that produced these captures')
    p.add_argument('--input',type=Path,action='append',default=[],help='Font/source/config input to fingerprint; repeat as needed')
    p.add_argument('--accept-baseline',action='store_true',help='Explicitly mark these already inspected captures as a baseline')
    a=p.parse_args()
    if a.expected<=0 or a.baseline and a.accept_baseline:p.error('positive count and distinct capture/compare/accept modes required')
    a.directory=evidence_directory(a.directory)
    if a.baseline and a.baseline.resolve()==a.directory:raise ValueError('candidate and baseline must be separate directories')
    paths=sorted(a.directory.glob('*.ppm'))
    if len(paths)!=a.expected:raise ValueError('actual capture count differs from expected')
    captures=[encode_capture(x) for x in paths]
    result=dict(schema=1,status='candidate',captures=captures,
                binary=binary_identity(a.binary) if a.binary else None,
                inputs=[dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in a.input])
    if a.baseline:
        approved=json.loads((a.baseline/'capture-manifest.json').read_text())
        if approved.get('status')!='inspected-baseline':raise ValueError('baseline is not explicitly inspected')
        old={x['rawPath']:x for x in approved['captures']}
        if set(old)!={x['rawPath'] for x in captures}:raise ValueError('baseline case identities differ')
        comparisons=[]
        for cap in captures:
            prior=a.baseline/cap['rawPath']
            if hashlib.sha256(prior.read_bytes()).hexdigest()!=old[cap['rawPath']]['rawSha256']:raise ValueError('baseline bytes changed')
            comparisons.append(dict(path=cap['rawPath'],**compare(a.directory/cap['rawPath'],prior)))
        result.update(status='passed' if all(x['passed'] for x in comparisons) else 'failed',comparisons=comparisons)
    if a.accept_baseline:result['status']='inspected-baseline'
    (a.directory/'capture-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],captures=len(captures))))
    return 1 if result['status']=='failed' else 0
if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,KeyError) as error:raise SystemExit(str(error))
