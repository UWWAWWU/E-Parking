"""Shared desktop parking rules and durable local records."""
from pathlib import Path
import hashlib
import json
import os
import re
import secrets
import time
import uuid


def normalize_plate(value):
    return ' '.join(value.strip().upper().split())


def valid_plate(value):
    return bool(re.fullmatch(r'[A-Z]{1,2}\s?\d{1,4}\s?[A-Z]{0,3}', normalize_plate(value)))


def slot_name(number):
    return f'{chr(65 + (number - 1) // 5)}{(number - 1) % 5 + 1}'


def floor_of(number):
    return (number - 1) // 20 + 1


def price(start, end):
    return 20000 + int(max(0, end - start) // 3600) * 5000


def password_hash(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 100000).hex()


class ParkingStore:
    def __init__(self, path=None):
        self.path = Path(path or os.environ.get('EPARKING_DATA_PATH', Path.home() / '.e-parking' / 'records.json'))
        self.accounts = []
        self.history = []
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding='utf-8'))
            if data.get('version') != 1:
                raise ValueError('Unsupported parking records version')
            self.accounts = data['accounts']
            self.history = data['history']

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps({'version': 1, 'accounts': self.accounts, 'history': self.history}, ensure_ascii=False, indent=2), encoding='utf-8')
        temporary.replace(self.path)

    def register(self, first, last, email, role, password, confirm):
        first, last, email = first.strip(), last.strip(), email.strip().lower()
        if not first or not last or len(first)>40 or len(last)>40 or len(email)>100 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
            raise ValueError('Enter your name and a valid email address.')
        if role not in ('User', 'Admin'):
            raise ValueError('Choose a role.')
        if len(password) < 6:
            raise ValueError('Passwords need at least 6 characters.')
        if password != confirm:
            raise ValueError('Passwords do not match.')
        if any(a['email'] == email for a in self.accounts):
            raise ValueError('This email is already registered.')
        salt = secrets.token_hex(16)
        account = dict(id=uuid.uuid4().hex, first=first, last=last, email=email, role=role,
                       salt=salt, passwordHash=password_hash(password, salt), slot=0, start=None, plate='', photo='')
        self.accounts.append(account)
        self.save()
        return account

    def login(self, email, password):
        account = next((a for a in self.accounts if a['email'] == email.strip().lower()), None)
        if not account or not secrets.compare_digest(account['passwordHash'], password_hash(password, account['salt'])):
            raise ValueError('Incorrect email or password.')
        return account

    def lookup(self, plate):
        normalized = normalize_plate(plate).replace(' ', '')
        return next((a for a in self.accounts if a['slot'] and a['plate'].replace(' ', '') == normalized), None)

    def book(self, account, slot, plate, now=None):
        if account['role'] == 'Admin':
            raise ValueError('Admin accounts cannot start a parking session.')
        if account['slot']:
            raise ValueError('You already have an active parking session.')
        if not isinstance(slot, int) or not 1 <= slot <= 60:
            raise ValueError('Choose a parking space first.')
        plate = normalize_plate(plate)
        if not valid_plate(plate):
            raise ValueError('Enter a valid plate, for example B 2026 XYZ.')
        if self.lookup(plate):
            raise ValueError('This vehicle is already parked.')
        if any(a['slot'] == slot for a in self.accounts):
            raise ValueError('This parking space is occupied.')
        account.update(slot=slot, plate=plate, start=now if now is not None else time.time())
        self.save()

    def checkout(self, account, now=None):
        if not account['slot']:
            raise ValueError('No active parking session.')
        end = now if now is not None else time.time()
        receipt = dict(id='EP-' + uuid.uuid4().hex[:10].upper(), name=f"{account['first']} {account['last']}",
                       plate=account['plate'], slot=account['slot'], start=account['start'], end=end, total=price(account['start'], end))
        self.history.insert(0, receipt)
        account.update(slot=0, start=None, plate='')
        self.save()
        return receipt

    def overview(self, now=None):
        from datetime import datetime
        today = datetime.fromtimestamp(now if now is not None else time.time()).date()
        active = [a for a in self.accounts if a['slot']]
        transactions = [r for r in self.history if datetime.fromtimestamp(r['end']).date() == today]
        return dict(parked=len(active), available=60 - len(active), transactions=len(transactions),
                    revenue=sum(r['total'] for r in transactions), floors=[sum(floor_of(a['slot']) == f for a in active) for f in (1, 2, 3)])
