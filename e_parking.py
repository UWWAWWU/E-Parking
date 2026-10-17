"""E-Parking desktop interface, matching the current web experience."""
from pathlib import Path
from datetime import datetime
import time
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk, ImageOps
from parking_core import ParkingStore, normalize_plate, slot_name, floor_of, price

ROOT = Path(__file__).resolve().parent
BG, PANEL, HEADER, CARD, YELLOW, WHITE, MUTED = '#4a495b', '#2c2e43', '#24273a', '#393c52', '#ffc800', '#ececf2', '#aeb1c4'
TRANSLATIONS = {
    'Home': 'Beranda', 'Start Parking': 'Mulai Parkir', 'Find My Car': 'Cari Mobil Saya', 'Find Car': 'Cari Mobil',
    'Transaction': 'Transaksi', 'Account': 'Akun', 'Name': 'Nama', 'Email': 'Email', 'Role': 'Peran', 'User': 'Pengguna',
    'License Plate': 'Plat Nomor', 'Parking Duration': 'Durasi Parkir', 'Total Payment': 'Total Pembayaran',
    'Description': 'Deskripsi', 'Quantity': 'Jumlah', 'Billing To': 'Tagihan Untuk', 'Search': 'Cari', 'Done': 'Selesai',
    'Close': 'Tutup', 'Cancel': 'Batal', 'Confirm Parking': 'Konfirmasi Parkir', 'Floor': 'Lantai',
    'Parking Overview': 'Ringkasan Parkir', 'Cars Parked': 'Mobil sedang parkir', 'Available Spaces': 'Slot tersedia',
    "Today's Transactions": 'Transaksi hari ini', "Today's Revenue": 'Pendapatan hari ini',
    'Floor Availability': 'Ketersediaan per lantai', 'Recent Transactions': 'Transaksi Terbaru', 'Exit Time': 'Waktu Keluar',
    'Entry Time': 'Waktu Masuk', 'Parking Space': 'Tempat Parkir', 'Duration': 'Durasi', 'Vehicle Information': 'Informasi Kendaraan',
    'Upload / change photo': 'Upload / ganti foto', 'Language': 'Bahasa', 'Log out': 'Keluar', 'Download Invoice': 'Unduh Invoice',
    'Date': 'Tanggal', 'Time': 'Waktu', 'Live Overview': 'Status terkini', 'Invoice': 'Invoice',
    'Monitor today\'s parking activity and availability.': 'Pantau aktivitas dan ketersediaan parkir hari ini.',
    'Enter a license plate to view the vehicle transaction.': 'Masukkan plat nomor untuk melihat transaksi kendaraan.',
    'Click an occupied space to view vehicle information.': 'Klik slot terisi untuk melihat informasi kendaraan.',
    'No completed transactions yet.': 'Belum ada transaksi selesai.',
    'License plate not found.': 'Plat nomor tidak ditemukan.', 'Choose a parking space first.': 'Pilih tempat parkir terlebih dahulu.',
    'No active parking session.': 'Belum ada sesi parkir.', 'You already have an active parking session.': 'Anda sudah parkir.',
    'Enter a valid plate, for example B 2026 XYZ.': 'Isi plat nomor yang valid, misalnya B 2026 XYZ.',
    'This vehicle is already parked.': 'Kendaraan ini sudah parkir.', 'This parking space is occupied.': 'Slot parkir sudah digunakan.',
    'Parking confirmed. Please park in the selected space.': 'Parkir dikonfirmasi. Silakan parkir di slot yang dipilih.',
    'Profile photo updated.': 'Foto profil diperbarui.', 'PAYMENT COMPLETED': 'TRANSAKSI SELESAI',
    'E-Parking simulated transaction receipt.': 'Bukti transaksi simulasi E-Parking.', 'Invoice saved.': 'Invoice tersimpan.',
}


def rupiah(value):
    return 'Rp' + f'{value:,}'.replace(',', '.')


class EParkingApp:
    def __init__(self, root, store=None):
        self.root, self.store = root, store or ParkingStore()
        root.title('E-Parking')
        root.geometry('1280x730')
        root.minsize(1100, 700)
        root.configure(bg=BG)
        self.user, self.target, self.selected = None, None, None
        self.page, self.language, self.floor = 'signup', 'en', 1
        self.images, self.profile, self.overlay, self.notice = [], None, None, None
        self.notice_timer = None
        self.root.bind('<Button-1>', self.outside_profile, add='+')
        self.root.bind('<Escape>', self.escape)
        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure('Parking.Horizontal.TProgressbar', troughcolor=HEADER, background=YELLOW, bordercolor=HEADER, lightcolor=YELLOW, darkcolor=YELLOW)
        self.render()
        self.tick()

    def t(self, value):
        return TRANSLATIONS.get(value, value) if self.user and self.language == 'id' else value

    def label(self, parent, text, size=14, color=WHITE, bold=False, bg=None, **kw):
        widget = tk.Label(parent, text=text, font=('Arial', size, 'bold' if bold else 'normal'), fg=color, bg=bg or parent.cget('bg'), **kw)
        if 'image' in kw: widget.image = kw['image']
        return widget

    def button(self, parent, text, command, primary=False, **kw):
        return tk.Button(parent, text=self.t(text), command=command, font=('Arial', 13, 'bold'), bg=YELLOW if primary else CARD,
                         fg=HEADER if primary else WHITE, activebackground='#ffe36b' if primary else '#50546b', activeforeground=HEADER if primary else WHITE,
                         relief='flat', bd=0, cursor='hand2', padx=16, pady=8, **kw)

    def image(self, path, size):
        im = Image.open(path).convert('RGBA').resize(size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(im)
        self.images.append(photo)
        return photo

    def notify(self, message):
        if self.notice_timer:
            self.root.after_cancel(self.notice_timer)
        if self.notice and self.notice.winfo_exists():
            self.notice.destroy()
        self.notice = tk.Label(self.root, text=self.t(message), bg=HEADER, fg=YELLOW, font=('Arial', 12), padx=18, pady=10, relief='solid', bd=1, wraplength=650)
        self.notice.place(relx=.60 if self.user else .50, y=85, anchor='n')
        self.notice.lift()
        self.notice_timer = self.root.after(3000, self.clear_notice)

    def clear_notice(self):
        if self.notice and self.notice.winfo_exists():
            self.notice.destroy()
        self.notice, self.notice_timer = None, None

    def brand(self, parent):
        frame = tk.Frame(parent, bg=parent.cget('bg'))
        self.label(frame, '', image=self.image(ROOT / 'Gambar/assets/logo.png', (45, 55))).pack(side='left', padx=(0, 10))
        copy = tk.Frame(frame, bg=frame.cget('bg'))
        copy.pack(side='left')
        self.label(copy, 'E-PARKING', 23, WHITE, True).pack(anchor='w')
        self.label(copy, 'Park with ease, no need to wheeze', 10, YELLOW).pack(anchor='w')
        return frame

    def render(self):
        self.clear_notice()
        self.images = []
        for child in self.root.winfo_children():
            child.destroy()
        self.profile, self.overlay = None, None
        if not self.user:
            self.auth()
            return
        header = tk.Frame(self.root, bg=HEADER, height=81)
        header.pack(fill='x')
        header.pack_propagate(False)
        self.brand(header).pack(side='left', padx=20)
        self.button(header, f"Hi, {self.user['first']}  ▾", self.open_profile).pack(side='right', padx=24, pady=16)
        shell = tk.Frame(self.root, bg=BG)
        shell.pack(fill='both', expand=True)
        self.sidebar = tk.Frame(shell, bg=PANEL, width=265)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)
        admin = self.user['role'] == 'Admin'
        nav = [('home', '⌂  Home'), ('find', '⌖  Find Car'), ('payment', '▤  Transaction')] if admin else [('home', '⌂  Home'), ('parking', 'Ⓟ  Start Parking'), ('find', '⌖  Find My Car'), ('payment', '▤  Transaction')]
        for action, title in nav:
            icon, title = title.split('  ', 1)
            b = self.button(self.sidebar, title, lambda a=action: self.navigate(a))
            b.configure(text=icon + '  ' + self.t(title), anchor='w', fg=YELLOW, bg='#4a4734' if self.page == action else CARD,
                        highlightbackground=YELLOW if self.page == action else '#53566b', highlightthickness=1, width=21)
            b.pack(fill='x', padx=24, pady=(24 if action == 'home' else 8, 0))
        account = tk.Frame(self.sidebar, bg=PANEL, highlightbackground='#56596d', highlightthickness=1)
        account.pack(fill='x', padx=24, pady=35)
        self.label(account, self.t('Account'), 18, bold=True).pack(anchor='w', pady=(12, 10))
        fields = [('Name', f"{self.user['first']} {self.user['last']}"), ('Email', self.user['email']), ('Role', self.t(self.user['role']))]
        if self.user['slot']:
            fields.append(('License Plate', self.user['plate']))
        for key, value in fields:
            self.label(account, self.t(key), 10, MUTED).pack(anchor='w', pady=(5, 0))
            self.label(account, value, 12, wraplength=200, justify='left').pack(anchor='w', pady=(0, 6))
        clock = tk.Frame(self.sidebar, bg=PANEL)
        clock.pack(side='bottom', fill='x', padx=24, pady=20)
        self.clock = self.label(clock, '', 11)
        self.clock.pack(anchor='w')
        self.main = tk.Frame(shell, bg=BG)
        self.main.pack(side='left', fill='both', expand=True, padx=25, pady=25)
        if self.page == 'home' and admin:
            self.admin_home()
        else:
            self.banner('payment' if self.page == 'payment' else 'find' if self.page == 'find' else 'parking' if self.page == 'parking' else 'home')
            if self.page == 'home': self.user_home()
            elif self.page in ('find', 'parking'): self.parking_map()
            else: self.payment()

    def auth(self):
        self.auth_background = tk.Label(self.root, image=self.image(ROOT / 'Gambar/assets/auth-hd.webp', (1280, 730)))
        self.auth_background.place(x=0, y=0, relwidth=1, relheight=1)
        form = tk.Frame(self.root, bg=PANEL, padx=30, pady=22)
        form.place(relx=.10, rely=.12)
        self.brand(form).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 28))
        signup = self.page == 'signup'
        self.label(form, 'Create New Account' if signup else 'Login to your account', 26, bold=True).grid(row=1, column=0, columnspan=2, sticky='w')
        self.button(form, 'Already have an account? Log in' if signup else 'Don’t have an account yet? Sign up', lambda: self.auth_switch()).grid(row=2, column=0, columnspan=2, sticky='w', pady=(6, 16))
        self.auth_fields = {}
        names = ['First Name', 'Last Name', 'Email', 'Role', 'Password', 'Confirm Password'] if signup else ['Email', 'Password']
        for i, name in enumerate(names):
            row, col = (3 + i // 2 * 2, i % 2) if signup else (3 + i * 2, 0)
            self.label(form, name, 12).grid(row=row, column=col, sticky='w', padx=(0, 16), pady=(8, 5))
            holder = tk.Frame(form, bg=PANEL)
            holder.grid(row=row + 1, column=col, sticky='w', padx=(0, 16))
            var = tk.StringVar()
            self.auth_fields[name] = var
            if name == 'Role':
                ttk.Combobox(holder, textvariable=var, values=['User', 'Admin'], state='readonly', width=22).pack()
            else:
                entry = tk.Entry(holder, textvariable=var, width=24 if signup else 43, font=('Arial', 12), bg='#5d5f70', fg=WHITE, insertbackground=WHITE, relief='flat', show='•' if 'Password' in name else '')
                entry.pack(side='left', ipady=4)
                if 'Password' in name:
                    tk.Button(holder, text='◉', command=lambda e=entry: e.configure(show='' if e.cget('show') else '•'), bg='#5d5f70', fg=WHITE, relief='flat').pack(side='left')
        self.button(form, 'Create Account' if signup else 'Login', self.submit_auth, True).grid(row=10, column=0, columnspan=2, sticky='ew', pady=(25, 0))
        self.auth_fields[names[0]].set('')
        self.root.bind('<Return>', lambda e: self.submit_auth())

    def auth_switch(self):
        self.page = 'login' if self.page == 'signup' else 'signup'
        self.render()

    def submit_auth(self):
        values = {k: v.get() for k, v in self.auth_fields.items()}
        try:
            if self.page == 'signup':
                self.store.register(values['First Name'], values['Last Name'], values['Email'], values['Role'], values['Password'], values['Confirm Password'])
                self.page = 'login'
                self.render()
                self.notify('Account created. Please log in.')
            else:
                self.user = self.store.login(values['Email'], values['Password'])
                self.language = self.user.get('language', 'en')
                self.page = 'home'
                self.root.unbind('<Return>')
                self.render()
        except ValueError as exc:
            self.notify(str(exc))

    def banner(self, kind):
        frame = tk.Frame(self.main, bg=PANEL, height=185)
        frame.pack(fill='x', pady=(0, 20))
        frame.pack_propagate(False)
        background = tk.Label(frame, bg=PANEL)
        background.place(relwidth=1, relheight=1)
        def resize(event):
            if event.width > 1:
                photo = self.image(ROOT / f'Gambar/assets/banner-{kind}-hd.webp', (event.width, 185))
                background.configure(image=photo)
                background.image = photo
                self.images = self.images[-30:]
        frame.bind('<Configure>', resize)
        if kind == 'payment':
            self.label(frame, 'WELCOME TO PAYMENT', 25, '#000000', True, '#e5ff00', padx=18, pady=7).place(relx=.5, y=24, anchor='n')
            self.label(frame, 'NO CASH NO PROBLEM', 19, '#e5ff00', bg='#15171b').place(relx=.68, y=122, anchor='n')
            self.label(frame, 'PAY QUICKLY AND EASY, SECURELY WITH QRIS', 8, bg='#15171b').place(relx=.68, y=151, anchor='n')
        elif kind == 'home':
            self.label(frame, 'WELCOME TO\nE-PARKING', 29, YELLOW, True, '#30323c').place(relx=.24, y=38, anchor='n')
        elif kind == 'find':
            self.label(frame, 'FIND\nCAR' if self.user['role'] == 'Admin' else 'FIND\nMY CAR', 27, YELLOW, True, '#30323c').place(relx=.22, y=24, anchor='n')
        else:
            self.label(frame, self.t('Start Parking'), 26, YELLOW, True, '#ece5d4').place(relx=.5, y=54, anchor='n')
            self.label(frame, 'Park your car here' if self.language == 'en' else 'Parkirkan mobil Anda di sini', 12, PANEL, bg='#ece5d4').place(relx=.5, y=91, anchor='n')
            self.label(frame, '■ Available   ■ Unavailable' if self.language == 'en' else '■ Tersedia   ■ Terisi', 10, PANEL, bg='#ece5d4').place(relx=.5, y=154, anchor='n')

    def user_home(self):
        panel = tk.Frame(self.main, bg=PANEL)
        panel.pack(fill='both', expand=True)
        self.label(panel, 'Find your space and enjoy easier parking.\nChoose an available spot across three floors,\nlocate your vehicle on the map, and review your parking fee.' if self.language == 'en' else 'Temukan tempat dan nikmati parkir yang lebih mudah.\nPilih slot kosong di tiga lantai, temukan kendaraan pada peta,\ndan lihat durasi serta biaya parkir Anda.', 17, wraplength=760, justify='center').pack(pady=(65, 30))
        self.button(panel, 'Start Parking', lambda: self.navigate('parking'), True).pack()

    def navigate(self, page):
        if self.user['role'] != 'Admin' and page in ('find', 'payment') and not self.user['slot']:
            return self.notify('No active parking session.')
        self.target, self.selected = None, None
        self.floor = floor_of(self.user['slot']) if page == 'find' and self.user['role'] != 'Admin' else 1
        self.page = page
        self.render()

    def admin_home(self):
        data = self.store.overview()
        frame = tk.Frame(self.main, bg=PANEL, padx=25, pady=22)
        frame.pack(fill='both', expand=True)
        self.label(frame, 'E-PARKING', 10, YELLOW, True).pack(anchor='w')
        self.label(frame, self.t('Parking Overview'), 27, bold=True).pack(anchor='w', pady=(6, 5))
        self.label(frame, self.t("Monitor today's parking activity and availability."), 12, MUTED).pack(anchor='w')
        metrics = tk.Frame(frame, bg=PANEL)
        metrics.pack(fill='x', pady=22)
        cards = [('Cars Parked', data['parked']), ('Available Spaces', data['available']), ("Today's Transactions", data['transactions']), ("Today's Revenue", rupiah(data['revenue']))]
        for i, (name, value) in enumerate(cards):
            metrics.columnconfigure(i, weight=1, uniform='metrics')
            card = tk.Frame(metrics, bg=CARD, padx=15, pady=18)
            card.grid(row=0, column=i, sticky='nsew', padx=(0, 10 if i < 3 else 0))
            self.label(card, self.t(name), 10, MUTED, wraplength=170, anchor='w').pack(anchor='w')
            self.label(card, str(value), 25 if i < 3 else 20, YELLOW, True).pack(anchor='w', pady=(10, 0))
        self.label(frame, self.t('Floor Availability'), 16, bold=True).pack(anchor='w')
        floors = tk.Frame(frame, bg=PANEL)
        floors.pack(fill='x', pady=(14, 23))
        for i, used in enumerate(data['floors']):
            floors.columnconfigure(i, weight=1, uniform='floors')
            card = tk.Frame(floors, bg=CARD, padx=16, pady=14)
            card.grid(row=0, column=i, sticky='nsew', padx=(0, 12 if i < 2 else 0))
            heading = tk.Frame(card, bg=CARD)
            heading.pack(fill='x')
            self.label(heading, f"{self.t('Floor')} {i + 1}", 12, bold=True).pack(side='left')
            self.label(heading, f'{used}/20', 11, MUTED).pack(side='right')
            ttk.Progressbar(card, value=used, maximum=20, style='Parking.Horizontal.TProgressbar').pack(fill='x', pady=12)
            self.label(card, f'{used} occupied · {20-used} available' if self.language == 'en' else f'{used} terisi · {20-used} tersedia', 10, MUTED).pack(anchor='w')
        self.label(frame, self.t('Recent Transactions'), 16, bold=True).pack(anchor='w', pady=(0, 12))
        history = tk.Frame(frame, bg=PANEL)
        history.pack(fill='both', expand=True)
        for i, title in enumerate(['License Plate', 'Exit Time', 'Total Payment']):
            history.columnconfigure(i, weight=1)
            self.label(history, self.t(title), 11, MUTED, bg=CARD, anchor='w', padx=12, pady=9).grid(row=0, column=i, sticky='ew')
        if not self.store.history:
            self.label(history, self.t('No completed transactions yet.'), 12, MUTED).grid(row=1, column=0, columnspan=3, pady=25)
        for row, record in enumerate(self.store.history[:5], 1):
            for col, value in enumerate([record['plate'], datetime.fromtimestamp(record['end']).strftime('%d %b %Y %H:%M'), rupiah(record['total'])]):
                self.label(history, value, 11, anchor='w', padx=12, pady=8).grid(row=row, column=col, sticky='ew')

    def parking_map(self):
        frame = tk.Frame(self.main, bg=PANEL)
        frame.pack(fill='both', expand=True)
        canvas = tk.Canvas(frame, bg=PANEL, highlightthickness=0, height=260)
        canvas.pack(fill='both', expand=True, padx=14, pady=12)
        self.map_canvas = canvas
        self.slot_boxes = {}
        def draw(event=None):
            canvas.delete('all')
            w, h = max(canvas.winfo_width(), 760), max(canvas.winfo_height(), 240)
            sx, sy = w / 633, h / 300
            self.slot_boxes = {}
            for row, (x, y) in enumerate([(104, 181), (44, 21), (294, 21), (354, 181)]):
                for col in range(5):
                    n = (self.floor - 1) * 20 + row * 5 + col + 1
                    record = next((a for a in self.store.accounts if a['slot'] == n), None)
                    own = self.page == 'find' and self.user['role'] != 'Admin' and record == self.user
                    color = '#16ff00' if own else '#4a495b' if record else YELLOW
                    x1, y1 = (x + col * 35) * sx, y * sy
                    x2, y2 = x1 + 27 * sx, y1 + 40 * sy
                    self.slot_boxes[n] = (x1, y1, x2, y2)
                    canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=WHITE if self.selected == n else color, width=2)
                    canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=slot_name(n), fill='#000' if not record or own else MUTED, font=('Arial', 11))
                    canvas.create_line((x + col * 35) * sx, (y - 6) * sy, (x + col * 35) * sx, (y + 47) * sy, fill=WHITE)
                canvas.create_line(x * sx, (y + 47 if row in (0, 3) else y - 6) * sy, (x + 175) * sx, (y + 47 if row in (0, 3) else y - 6) * sy, fill=WHITE)
            for x in (25, 175, 362, 525):
                canvas.create_line(x*sx, 125*sy, (x+28)*sx, 125*sy, fill=WHITE, width=3, arrow='last')
                if self.floor > 1:
                    canvas.create_line((x+28)*sx, 141*sy, x*sx, 141*sy, fill=WHITE, width=3, arrow='last')
            if self.floor == 1:
                canvas.create_rectangle(0, 195*sy, 32*sx, 272*sy, fill='#00ef00', outline='')
                canvas.create_text(16*sx, 233*sy, text='E\nN\nT\nE\nR', fill='#101510', font=('Arial', 9, 'bold'))
                canvas.create_rectangle(501*sx, 0, 590*sx, 30*sy, fill='#ed1020', outline='')
                canvas.create_text(545*sx, 15*sy, text='EXIT', fill='#101510', font=('Arial', 11, 'bold'))
            else:
                canvas.create_rectangle(0, 195*sy, 32*sx, 272*sy, fill=WHITE, outline='')
                canvas.create_text(16*sx, 233*sy, text=f"{self.t('Floor').upper()} {self.floor-1}", angle=90, fill='#101510', font=('Arial', 10, 'bold'))
                if self.floor == 2:
                    canvas.create_rectangle(501*sx, 0, 590*sx, 30*sy, fill=WHITE, outline='')
                    canvas.create_text(545*sx, 15*sy, text=f"{self.t('Floor').upper()} 3", fill='#101510', font=('Arial', 10, 'bold'))
        canvas.bind('<Configure>', draw)
        canvas.bind('<Button-1>', self.click_space)
        bottom = tk.Frame(frame, bg=PANEL)
        bottom.pack(fill='x', padx=22, pady=(0, 16))
        if self.page == 'parking':
            if self.user['slot']:
                self.label(bottom, self.t('You already have an active parking session.'), 11, '#b6e9c6').pack(side='left')
            else:
                self.button(bottom, 'Done', self.plate_prompt, True).pack(side='left', padx=12)
        else:
            text = self.t('Click an occupied space to view vehicle information.') if self.user['role'] == 'Admin' else (f"Your car is in space {slot_name(self.user['slot'])}" if self.language == 'en' else f"Mobil Anda berada di slot {slot_name(self.user['slot'])}")
            self.label(bottom, text, 11, MUTED, wraplength=490).pack(side='left')
        if self.page == 'parking' or self.user['role'] == 'Admin':
            for f in (3, 2, 1):
                self.button(bottom, str(f), lambda n=f: self.change_floor(n), self.floor == f).pack(side='right', padx=5)
        draw()

    def change_floor(self, floor):
        self.floor, self.selected = floor, None
        self.render()

    def click_space(self, event):
        number = next((n for n, (x1, y1, x2, y2) in self.slot_boxes.items() if x1 <= event.x <= x2 and y1 <= event.y <= y2), None)
        if number is None: return
        record = next((a for a in self.store.accounts if a['slot'] == number), None)
        if self.user['role'] == 'Admin' and self.page == 'find':
            if record: self.car_info(record)
        elif self.page == 'parking' and not record and not self.user['slot']:
            self.selected = number
            self.render()

    def dialog(self, title):
        self.close_dialog()
        self.overlay = tk.Frame(self.root, bg=HEADER)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        panel = tk.Frame(self.overlay, bg=PANEL, padx=28, pady=25, highlightbackground='#6a6d81', highlightthickness=1)
        panel.place(relx=.5, rely=.5, anchor='center')
        self.label(panel, title, 22, bold=True).pack(anchor='w', pady=(0, 16))
        return panel

    def close_dialog(self):
        if self.overlay and self.overlay.winfo_exists(): self.overlay.destroy()
        self.overlay = None

    def plate_prompt(self):
        if not self.selected: return self.notify('Choose a parking space first.')
        panel = self.dialog(self.t('License Plate'))
        self.label(panel, f"{self.t('Parking Space')}: {slot_name(self.selected)}", 13, YELLOW).pack(anchor='w', pady=(0, 15))
        var = tk.StringVar()
        entry = tk.Entry(panel, textvariable=var, width=30, font=('Arial', 17), bg=CARD, fg=WHITE, insertbackground=WHITE)
        entry.pack(fill='x', ipady=6)
        def confirm():
            try:
                self.store.book(self.user, self.selected, var.get())
                self.selected = None
                self.render()
                self.notify('Parking confirmed. Please park in the selected space.')
            except ValueError as exc: self.notify(str(exc))
        actions = tk.Frame(panel, bg=PANEL)
        actions.pack(pady=(22, 0), fill='x')
        self.button(actions, 'Cancel', self.close_dialog).pack(side='left')
        self.button(actions, 'Confirm Parking', confirm, True).pack(side='right', padx=(12, 0))
        entry.bind('<Return>', lambda e: confirm())
        entry.focus_set()

    def car_info(self, record):
        panel = self.dialog(f"{self.t('Vehicle Information')} · {slot_name(record['slot'])}")
        self.details(panel, [('Name', f"{record['first']} {record['last']}"), ('Email', record['email']), ('License Plate', record['plate'])])
        self.button(panel, 'Close', self.close_dialog, True).pack(anchor='e', pady=(15, 0))

    def payment(self):
        if self.user['role'] == 'Admin':
            search = tk.Frame(self.main, bg=BG)
            search.pack(fill='x', pady=(0, 12))
            self.label(search, self.t('License Plate'), 12).pack(side='left', padx=(0, 12))
            var = tk.StringVar(value=self.target['plate'] if self.target else '')
            entry = tk.Entry(search, textvariable=var, width=25, bg=CARD, fg=WHITE, insertbackground=WHITE, font=('Arial', 13))
            entry.pack(side='left', ipady=5)
            def lookup():
                self.target = self.store.lookup(var.get())
                self.render()
                if not self.target: self.notify('License plate not found.')
            self.button(search, 'Search', lookup, True).pack(side='left', padx=12)
            entry.bind('<Return>', lambda e: lookup())
        record = self.target if self.user['role'] == 'Admin' else self.user
        panel = tk.Frame(self.main, bg=PANEL, padx=25, pady=20)
        panel.pack(fill='both', expand=True)
        if not record:
            self.label(panel, self.t('Enter a license plate to view the vehicle transaction.'), 15, MUTED, wraplength=760).place(relx=.5, rely=.5, anchor='center')
            return
        self.bill_end = time.time()
        self.label(panel, 'PARKING APPS', 10, YELLOW, True).pack(anchor='w', pady=(0, 18))
        self.label(panel, f"{self.t('Billing To').upper()}:   {record['first']} {record['last']}", 13, bold=True).pack(anchor='w')
        self.label(panel, 'Kampus Ketintang\nJl. Ketintang, Surabaya 60231', 10, justify='left').pack(anchor='w', pady=(12, 20))
        table = tk.Frame(panel, bg=PANEL)
        table.pack(fill='x')
        table.columnconfigure(0, weight=3)
        table.columnconfigure(1, weight=1)
        for i, text in enumerate(['Description', 'Quantity']):
            self.label(table, self.t(text).upper(), 11, WHITE, True, YELLOW, pady=8).grid(row=0, column=i, sticky='ew')
        duration = int(max(0, self.bill_end - record['start']) // 3600)
        rows = [('License Plate', record['plate']), ('Parking Duration', f"{duration} {'jam' if self.language == 'id' else 'Hours'}"), ('Total Payment', rupiah(price(record['start'], self.bill_end)))]
        for row, (name, value) in enumerate(rows, 1):
            self.label(table, self.t(name), 12, anchor='w', padx=35, pady=11).grid(row=row, column=0, sticky='ew')
            self.label(table, value, 13, anchor='w', pady=11).grid(row=row, column=1, sticky='ew')
        self.button(panel, 'Done', lambda: self.checkout(record), True).pack(side='bottom', pady=(20, 0))

    def checkout(self, record):
        try:
            receipt = self.store.checkout(record, self.bill_end)
            self.target = None
            self.page = 'home'
            self.render()
            self.invoice(receipt)
        except ValueError as exc: self.notify(str(exc))

    def details(self, panel, rows):
        frame = tk.Frame(panel, bg=PANEL)
        frame.pack(fill='x')
        for i, (key, value) in enumerate(rows):
            self.label(frame, self.t(key), 12, MUTED, anchor='w').grid(row=i, column=0, sticky='w', padx=(0, 24), pady=7)
            self.label(frame, str(value), 12, wraplength=320, justify='left', anchor='w').grid(row=i, column=1, sticky='w', pady=7)

    def invoice_rows(self, receipt):
        minutes = int(max(0, receipt['end'] - receipt['start']) // 60)
        return [('Name', receipt['name']), ('License Plate', receipt['plate']), ('Parking Space', f"{self.t('Floor')} {floor_of(receipt['slot'])} · {slot_name(receipt['slot'])}"),
                ('Entry Time', datetime.fromtimestamp(receipt['start']).strftime('%d %b %Y %H:%M')),
                ('Exit Time', datetime.fromtimestamp(receipt['end']).strftime('%d %b %Y %H:%M')),
                ('Duration', f'{minutes//60} jam {minutes%60} menit' if self.language == 'id' else f'{minutes//60} hours {minutes%60} minutes')]

    def invoice(self, receipt):
        panel = self.dialog('Invoice')
        self.label(panel, 'E-PARKING', 13, YELLOW, True).pack(anchor='w')
        self.label(panel, receipt['id'], 11, MUTED).pack(anchor='w', pady=8)
        self.label(panel, self.t('PAYMENT COMPLETED'), 11, '#9ee4b7').pack(anchor='w')
        self.details(panel, self.invoice_rows(receipt))
        self.label(panel, f"{self.t('Total Payment')}:  {rupiah(receipt['total'])}", 20, YELLOW, True).pack(anchor='w', pady=15)
        self.label(panel, self.t('E-Parking simulated transaction receipt.'), 10, MUTED).pack(anchor='w')
        actions = tk.Frame(panel, bg=PANEL)
        actions.pack(fill='x', pady=(20, 0))
        self.button(actions, 'Close', self.close_dialog).pack(side='left')
        self.button(actions, 'Download Invoice', lambda: self.save_invoice(receipt), True).pack(side='right', padx=(15, 0))

    def save_invoice(self, receipt, path=None):
        from reportlab.pdfgen import canvas
        from reportlab.lib.colors import HexColor
        if path is None:
            path = filedialog.asksaveasfilename(parent=self.root, defaultextension='.pdf', initialfile=receipt['id']+'.pdf', filetypes=[('PDF invoice', '*.pdf')])
        if not path: return
        try:
            c = canvas.Canvas(str(path), pagesize=(300, 380), pageCompression=1)
            c.setTitle('E-Parking Invoice ' + receipt['id'])
            c.setFillColor(HexColor('#24273a'))
            c.setFont('Helvetica-Bold', 15); c.drawString(20, 352, 'E-PARKING')
            c.setFont('Helvetica-Bold', 12); c.drawString(20, 330, 'Invoice')
            c.setFont('Helvetica', 8); c.drawString(20, 313, receipt['id'])
            c.drawString(20, 296, self.t('PAYMENT COMPLETED'))
            c.line(20, 283, 280, 283)
            y = 262
            from reportlab.lib.utils import simpleSplit
            for key, value in self.invoice_rows(receipt):
                c.setFont('Helvetica', 8)
                c.drawString(20, y, self.t(key))
                lines = simpleSplit(str(value), 'Helvetica', 8, 147)
                for line in lines:
                    c.drawString(130, y, line); y -= 11
                y -= 12
            c.line(20, y, 280, y)
            c.setFont('Helvetica-Bold', 11); c.drawString(20, y-25, self.t('Total Payment')); c.drawRightString(280, y-25, rupiah(receipt['total']))
            c.setFont('Helvetica', 7); c.drawString(20, 20, self.t('E-Parking simulated transaction receipt.'))
            c.save()
            self.notify('Invoice saved.')
        except (OSError, ValueError):
            self.notify('Unable to save invoice.' if self.language == 'en' else 'Invoice gagal disimpan.')

    def open_profile(self):
        if self.profile and self.profile.winfo_exists():
            self.profile.destroy(); self.profile = None; return
        self.profile = tk.Frame(self.root, bg=HEADER, padx=18, pady=18, highlightbackground='#5d5f70', highlightthickness=1)
        self.profile.place(relx=1, x=-25, y=77, anchor='ne')
        photo = self.user.get('photo')
        if photo:
            try: self.label(self.profile, '', image=self.image(photo, (72, 72))).pack(pady=(0, 10))
            except (OSError, ValueError): self.label(self.profile, '◉', 36, YELLOW).pack()
        else: self.label(self.profile, '◉', 36, YELLOW).pack()
        self.label(self.profile, f"{self.user['first']} {self.user['last']}", 14, bold=True).pack(pady=(0, 12))
        self.button(self.profile, 'Upload / change photo', self.upload_photo).pack(fill='x')
        self.label(self.profile, self.t('Language'), 12).pack(anchor='w', pady=(16, 6))
        var = tk.StringVar(value='English' if self.language == 'en' else 'Indonesia')
        choice = ttk.Combobox(self.profile, textvariable=var, values=['English', 'Indonesia'], state='readonly', width=25)
        choice.pack(fill='x')
        def change(e):
            self.language = 'en' if var.get() == 'English' else 'id'
            self.user['language'] = self.language
            self.store.save()
            self.render()
        choice.bind('<<ComboboxSelected>>', change)
        self.button(self.profile, 'Log out', self.logout).pack(fill='x', pady=(16, 0))

    def upload_photo(self):
        path = filedialog.askopenfilename(parent=self.root, filetypes=[('Profile image', '*.png *.jpg *.jpeg *.webp')])
        if not path: return
        try:
            with Image.open(path) as im:
                thumb = ImageOps.fit(im.convert('RGB'), (160, 160))
                destination = self.store.path.parent / 'photos' / (self.user['id'] + '.jpg')
                destination.parent.mkdir(parents=True, exist_ok=True)
                thumb.save(destination, quality=85)
            self.user['photo'] = str(destination)
            self.store.save()
            self.render()
            self.notify('Profile photo updated.')
        except (OSError, ValueError): self.notify('Unable to read this image.' if self.language == 'en' else 'Gambar tidak dapat dibaca.')

    def outside_profile(self, event):
        if not self.profile or not self.profile.winfo_exists(): return
        widget = event.widget
        while widget:
            if widget == self.profile: return
            widget = getattr(widget, 'master', None)
        # The profile button itself toggles the menu in its command handler.
        if isinstance(event.widget, tk.Button) and 'Hi,' in str(event.widget.cget('text')): return
        self.profile.destroy(); self.profile = None

    def escape(self, event=None):
        self.close_dialog()
        if self.profile and self.profile.winfo_exists(): self.profile.destroy()
        self.profile = None

    def logout(self):
        self.user, self.target, self.selected = None, None, None
        self.page, self.language = 'login', 'en'
        self.render()

    def tick(self):
        if self.user and hasattr(self, 'clock') and self.clock.winfo_exists():
            self.clock.configure(text=f"{self.t('Date')}                         {self.t('Time')}\n{datetime.now():%d %b %Y}          {datetime.now():%H:%M:%S}")
        self.root.after(1000, self.tick)


def main():
    root = tk.Tk()
    EParkingApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
