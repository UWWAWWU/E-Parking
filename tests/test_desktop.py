"""Desktop workflow regression tests; no display required."""
import tempfile
import unittest
from pathlib import Path
from parking_core import ParkingStore, price, slot_name, floor_of


class DesktopFlows(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'records.json'
        self.store = ParkingStore(self.path)
        self.user = self.store.register('Test', 'Driver', 'driver@example.test', 'User', 'password1', 'password1')
        self.admin = self.store.register('Test', 'Admin', 'admin@example.test', 'Admin', 'password2', 'password2')

    def tearDown(self):
        self.temp.cleanup()

    def test_account_persistence_and_passwords(self):
        self.assertNotIn('password1', self.path.read_text())
        loaded = ParkingStore(self.path)
        self.assertEqual(loaded.login('DRIVER@example.test', 'password1')['id'], self.user['id'])
        with self.assertRaises(ValueError): loaded.login('driver@example.test', 'incorrect')
        with self.assertRaises(ValueError): self.store.register('Other', 'Driver', 'driver@example.test', 'User', 'password1', 'password1')

    def test_booking_lookup_collision_and_checkout(self):
        self.assertIsNone(self.store.lookup('B 1234 AB'))
        self.store.book(self.user, 22, 'b 1234 ab', 1000)
        self.assertIs(self.store.lookup('B1234AB'), self.user)
        other = self.store.register('Other', 'Driver', 'other@example.test', 'User', 'password1', 'password1')
        with self.assertRaises(ValueError): self.store.book(other, 22, 'D 12 AA', 1000)
        with self.assertRaises(ValueError): self.store.book(other, 23, 'B1234AB', 1000)
        with self.assertRaises(ValueError): self.store.book(self.admin, 23, 'D 12 AA', 1000)
        receipt = self.store.checkout(self.user, 8200)
        self.assertEqual(receipt['total'], 30000)
        self.assertEqual(receipt['plate'], 'B 1234 AB')
        self.assertEqual((self.user['slot'], self.user['plate'], self.user['start']), (0, '', None))
        self.assertEqual(ParkingStore(self.path).history[0]['id'], receipt['id'])
        with self.assertRaises(ValueError): self.store.checkout(self.user, 8300)

    def test_admin_overview_and_three_floors(self):
        self.store.book(self.user, 47, 'L 12 AB', 1000)
        overview = self.store.overview(8200)
        self.assertEqual((overview['parked'], overview['available'], overview['floors']), (1, 59, [0, 0, 1]))
        self.store.checkout(self.user, 8200)
        overview = self.store.overview(8200)
        self.assertEqual((overview['transactions'], overview['revenue']), (1, 30000))
        self.assertEqual(self.store.overview(8200 + 86400)['transactions'], 0)
        self.assertEqual((slot_name(22), floor_of(22), slot_name(60)), ('E2', 2, 'L5'))
        self.assertEqual(price(1000, 4599), 20000)


if __name__ == '__main__':
    unittest.main()
