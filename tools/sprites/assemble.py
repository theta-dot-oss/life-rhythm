import json,os,sys
from PIL import Image
out=sys.argv[1]; man=json.load(open(os.path.join(out,'manifest.json')))
gap,pad=40,20
for m in man:
    imgs=[Image.open(os.path.join(out,'svg',f"{m['name']}-{k}.png")).convert('RGBA') for k in range(m['frames'])]
    n=len(imgs); W=pad*2+n*320+(n-1)*gap
    sheet=Image.new('RGBA',(W,320+pad*2),(0,0,0,0))
    for i,im in enumerate(imgs): sheet.paste(im,(pad+i*(320+gap),pad),im)
    sheet.save(os.path.join(out,m['file']),optimize=True); print(m['file'],n)
files=[os.path.join(out,m['file']) for m in man]
W=max(Image.open(f).width for f in files); H=sum(Image.open(f).height for f in files)
c=Image.new('RGBA',(W,H),(214,236,250,255)); y=0
for f in files:
    im=Image.open(f); c.paste(im,(0,y),im); y+=im.height
c.resize((W//2,H//2)).save(os.path.join(out,'preview.png'))
