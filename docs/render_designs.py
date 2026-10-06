"""Render current desktop design reference images (not runtime screenshots)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from parking_core import slot_name
ROOT = Path(__file__).resolve().parents[1]
BG, PANEL, HEADER, CARD, YELLOW, WHITE, MUTED = '#4a495b', '#2c2e43', '#24273a', '#393c52', '#ffc800', '#ececf2', '#aeb1c4'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def font(size, bold=False): return ImageFont.truetype(BOLD if bold else FONT, size)
def text(d, xy, value, size=14, color=WHITE, bold=False, anchor=None): d.text(xy, value, font=font(size,bold), fill=color, anchor=anchor, spacing=7)

def base(admin=False, page='Home'):
 im=Image.new('RGB',(1280,730),BG);d=ImageDraw.Draw(im)
 d.rectangle((0,0,1280,81),fill=HEADER);d.rectangle((0,81,265,730),fill=PANEL)
 logo=Image.open(ROOT/'Gambar/assets/logo.png').resize((45,55));im.paste(logo,(20,12),logo)
 text(d,(77,18),'E-PARKING',23,WHITE,True);text(d,(77,49),'Park with ease, no need to wheeze',10,YELLOW)
 text(d,(1138,33),'Hi, Demo',14,WHITE,True);d.ellipse((1233,19,1271,57),fill=YELLOW)
 nav=['Home','Find Car','Transaction'] if admin else ['Home','Start Parking','Find My Car','Transaction']
 for i,n in enumerate(nav):
  y=111+i*55;d.rounded_rectangle((24,y,241,y+42),8,fill='#4a4734' if n==page else CARD,outline=YELLOW if n==page else '#53566b')
  text(d,(40,y+13),n,14,YELLOW,True)
 d.line((24,350,241,350),fill='#56596d');text(d,(24,372),'Account',18,WHITE,True)
 for i,(k,v) in enumerate([('Name','Demo Admin' if admin else 'Demo Driver'),('Email','demo@example.test'),('Role','Admin' if admin else 'User')]):
  text(d,(24,416+i*55),k,11,MUTED);text(d,(24,435+i*55),v,14)
 d.line((24,646,241,646),fill='#56596d');text(d,(24,664),'Date                         Time',11,MUTED);text(d,(24,687),'07 Oct 2026           08:30:00',11)
 return im,d

def banner(im,d,kind):
 asset=Image.open(ROOT/f'Gambar/assets/banner-{kind}-hd.webp').convert('RGB').resize((960,185),Image.Resampling.LANCZOS)
 im.paste(asset,(290,110))
 if kind=='home':text(d,(505,155),'WELCOME TO\nE-PARKING',29,YELLOW,True,'ma')
 elif kind=='parking':text(d,(770,162),'Start Parking',28,YELLOW,True,'ma');text(d,(770,203),'Park your car here',13,PANEL,False,'ma')
 elif kind=='find':text(d,(495,136),'FIND\nMY CAR',30,YELLOW,True,'ma')
 else:
  d.rectangle((505,135,1130,186),fill='#e5ff00');text(d,(817,160),'WELCOME TO PAYMENT',26,'#000000',True,'mm')
  text(d,(954,235),'NO CASH NO PROBLEM',22,'#e5ff00',False,'mm');text(d,(954,263),'PAY QUICKLY AND EASY, SECURELY WITH QRIS',9,WHITE,True,'mm')

def overview():
 im,d=base(True);d.rounded_rectangle((290,110,1250,710),18,fill=PANEL)
 text(d,(320,136),'E-PARKING',11,YELLOW,True);text(d,(320,160),'Parking Overview',29,WHITE,True);text(d,(320,208),"Monitor today's parking activity and availability.",14,MUTED)
 d.rounded_rectangle((1095,149,1219,179),15,fill='#414536',outline='#747449');text(d,(1157,164),'Live Overview',11,YELLOW,False,'mm')
 for i,(name,val) in enumerate([('Cars Parked','3'),('Available Spaces','57'),("Today's Transactions",'2'),("Today's Revenue",'Rp45.000')]):
  x=320+i*226;d.rounded_rectangle((x,250,x+210,352),12,fill=CARD,outline='#55586b');text(d,(x+16,268),name,12,MUTED);text(d,(x+16,300),val,29 if i<3 else 25,YELLOW,True)
 text(d,(320,377),'Floor Availability',17,WHITE,True)
 for i,n in enumerate([1,1,1]):
  x=320+i*304;d.rounded_rectangle((x,414,x+286,509),10,fill=CARD);text(d,(x+16,430),f'Floor {i+1}',14,WHITE,True);text(d,(x+239,431),'1/20',12,MUTED)
  d.rounded_rectangle((x+16,460,x+269,467),4,fill=HEADER);d.rounded_rectangle((x+16,460,x+30,467),4,fill=YELLOW);text(d,(x+16,481),'1 occupied · 19 available',12,MUTED)
 text(d,(320,534),'Recent Transactions',17,WHITE,True);d.rectangle((320,568,1220,600),fill=CARD)
 for x,title in [(335,'License Plate'),(655,'Exit Time'),(1045,'Total Payment')]:text(d,(x,578),title,12,MUTED)
 for y,plate,dt,total in [(616,'B 2026 XYZ','07 Oct 2026 08:10','Rp25.000'),(656,'L 1234 AB','07 Oct 2026 07:45','Rp20.000')]:
  text(d,(335,y),plate,13);text(d,(655,y),dt,13);text(d,(1098,y),total,13);d.line((320,y+25,1220,y+25),fill='#46495e')
 return im

def home():
 im,d=base();banner(im,d,'home');d.rounded_rectangle((290,329,1250,710),18,fill=PANEL)
 text(d,(770,393),'Find your space and enjoy easier parking.\nChoose an available spot across three floors,\nlocate your vehicle on the map, and review your parking fee.',18,WHITE,False,'ma')
 d.rounded_rectangle((655,548,885,591),20,fill=YELLOW);text(d,(770,569),'Start Parking',16,HEADER,True,'mm');return im

def parking(floor=1,find=False):
 im,d=base(False,'Find My Car' if find else 'Start Parking');banner(im,d,'find' if find else 'parking');d.rounded_rectangle((290,329,1250,710),18,fill=PANEL)
 sx=960/633
 for row,(x,y) in enumerate([(104,181),(44,21),(294,21),(354,181)]):
  for col in range(5):
   n=(floor-1)*20+row*5+col+1;xx=290+(x+col*35)*sx;yy=329+y
   color='#16ff00' if find and col==1 and row==1 else '#4a495b' if col==1 and row==1 else YELLOW
   d.rectangle((xx,yy,xx+27*sx,yy+40),fill=color);text(d,(xx+13.5*sx,yy+20),slot_name(n),12,'#000000' if color!=BG else MUTED,False,'mm')
   d.line((xx,yy-6,xx,yy+47),fill=WHITE)
  d.line((290+x*sx,329+y+47 if row in (0,3) else 329+y-6,290+(x+175)*sx,329+y+47 if row in (0,3) else 329+y-6),fill=WHITE)
 for x in [25,175,362,525]:
  xx=290+x*sx;d.line((xx,454,xx+28*sx,454),fill=WHITE,width=3);d.polygon([(xx+28*sx,454),(xx+22*sx,449),(xx+22*sx,459)],fill=WHITE)
 if floor==1:
  d.rectangle((290,538,348,628),fill='#00ef00');text(d,(319,581),'E\nN\nT\nE\nR',10,'#101510',True,'mm');d.rectangle((1050,329,1185,367),fill='#ed1020');text(d,(1117,348),'EXIT',13,'#101510',True,'mm')
 else:
  d.rectangle((290,538,348,628),fill=WHITE);label=Image.new('RGB',(90,58),WHITE);ld=ImageDraw.Draw(label);text(ld,(45,29),f'FLOOR {floor-1}',12,'#101510',True,'mm');im.paste(label.rotate(90,expand=True),(290,538))
  if floor==2:d.rectangle((1050,329,1185,367),fill=WHITE);text(d,(1117,348),'FLOOR 3',13,'#101510',True,'mm')
 text(d,(560,669),f'Your car is in space {slot_name((floor-1)*20+7)}' if find else 'Select a space, then confirm your license plate.',13,MUTED,False,'mm')
 for f in [1,2,3]:
  xx=965+(f-1)*72;d.rounded_rectangle((xx,651,xx+55,689),7,fill=YELLOW if f==floor else CARD,outline=WHITE if f==floor else MUTED);text(d,(xx+27,670),str(f),15,HEADER if f==floor else WHITE,True,'mm')
 return im

def payment():
 im,d=base(False,'Transaction');banner(im,d,'payment');d.rounded_rectangle((290,329,1250,710),18,fill=PANEL)
 text(d,(318,353),'PARKING APPS',11,YELLOW,True);text(d,(318,396),'BILLING TO:   Demo Driver',13,WHITE,True);text(d,(318,428),'Kampus Ketintang\nJl. Ketintang, Surabaya 60231',10)
 d.rectangle((290,494,1250,528),fill=YELLOW);text(d,(620,511),'DESCRIPTION',12,WHITE,True,'mm');text(d,(1100,511),'QUANTITY',12,WHITE,True,'mm')
 for y,k,v in [(547,'License Plate','B 2026 XYZ'),(586,'Parking Duration','1 Hours'),(625,'Total Payment','Rp25.000')]:text(d,(410,y),k,13);text(d,(1070,y),v,13);d.line((350,y+28,1190,y+28),fill='#c9ad27')
 d.rounded_rectangle((705,668,840,702),16,fill=YELLOW);text(d,(772,685),'Done',14,WHITE,True,'mm');return im

def auth(login=False):
 im=Image.open(ROOT/'Gambar/assets/auth-hd.webp').convert('RGB').resize((1280,730));d=ImageDraw.Draw(im)
 d.rounded_rectangle((115,75,615,670),18,fill=PANEL);text(d,(145,107),'E-PARKING',30,WHITE,True);text(d,(145,150),'Park with ease, no need to wheeze',12,YELLOW)
 text(d,(145,209),'Login to your account' if login else 'Create New Account',26,WHITE,True)
 text(d,(145,255),'Don’t have an account yet? Sign up' if login else 'Already have an account? Log in',13,MUTED)
 labels=['Email','Password'] if login else ['First Name','Last Name','Email','Role','Password','Confirm Password']
 for i,name in enumerate(labels):
  x=145 if login else 145+(i%2)*230;y=310+i*80 if login else 310+(i//2)*80
  text(d,(x,y),name,12);d.rectangle((x,y+28,x+(430 if login else 200),y+59),fill='#5d5f70')
 d.rounded_rectangle((145,login and 518 or 595,575,login and 560 or 637),15,fill=YELLOW);text(d,(360,login and 539 or 616),'Login' if login else 'Create Account',16,WHITE,True,'mm');return im

def main():
 images={'home-user':home(),'home-admin':overview(),'payment':payment(),'signup':auth(),'login':auth(True)}
 for f in (1,2,3):images[f'parking-floor-{f}']=parking(f);images[f'find-floor-{f}']=parking(f,True)
 for name,im in images.items():im.save(ROOT/f'docs/{name}.png',optimize=True)
 mapping={'dashboard.jpg':'home-user','transaksi page.jpg':'payment','Bg dasar.jpg':'signup','start park bg.jpg':'parking-floor-1','start park2 bg.jpg':'parking-floor-2','start park3 bg.jpg':'parking-floor-3','find my car.jpg':'find-floor-1','find my car2.jpg':'find-floor-2','find my car3.jpg':'find-floor-3'}
 for filename,name in mapping.items():images[name].save(ROOT/'Gambar'/filename,quality=95,subsampling=0)
 labels={'Create Account.png':'Create Account','Home button.jpg':'Home','Home button1.jpg':'Home','Start Parking.png':'Start Parking','Done.png':'Done','login.png':'Login','transaksi.jpg':'Transaction','transaksi1.jpg':'Transaction','start parkir icon.jpg':'Start Parking','start parkir icon1.jpg':'Start Parking','mobil.jpg':'Find My Car','mobil1.jpg':'Find My Car','mobil.png':'Find My Car','show.png':'Show','hide.png':'Hide','Parking spot.jpg':'P'}
 for name,label in labels.items():
  im=Image.new('RGB',(480,120),PANEL);d=ImageDraw.Draw(im);d.rounded_rectangle((8,8,472,112),22,fill=YELLOW if name.endswith('.png') and label not in ('Show','Hide') else CARD,outline=YELLOW,width=2);text(d,(240,60),label,30,HEADER if name.endswith('.png') and label not in ('Show','Hide') else YELLOW,True,'mm');im.save(ROOT/'Gambar'/name)
if __name__=='__main__':main()
