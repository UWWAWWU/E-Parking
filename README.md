<div align="center">

# 🅿️ E-Parking

### Find vacant space, then park up wherever

A parking management application built with Python and Tkinter, now available in the browser using the **original GUI design and image assets**.

[![Open E-Parking](https://img.shields.io/badge/OPEN_E--PARKING-ffc800?style=for-the-badge&logo=vercel&logoColor=black)](https://eparking-wawutriambodo.vercel.app)
[![Python](https://img.shields.io/badge/Python-Tkinter-3776ab?logo=python&logoColor=white)](E-Parking.ipynb)
[![Web](https://img.shields.io/badge/Web-HTML_CSS_JavaScript-f7df1e?logo=javascript&logoColor=black)](web/)

![Original E-Parking dashboard](Gambar/dashboard.jpg)

**3 floors · 60 spaces · User and admin workflows**

</div>

## About the project

E-Parking helps users choose a parking space, locate their vehicle, and calculate parking fees. The original desktop application uses Tkinter for its GUI, Pillow for image assets, and pandas for CSV records. Bubble sort and binary search support account lookup in the Python implementation.

The browser version adapts the original desktop interface for web use. Backgrounds, banners, navigation artwork, and action buttons come directly from the repository's **Gambar** folder. The original 1280 × 730 layout, purple and yellow palette, labels, slot positions, and page flows are retained. The interface fills the browser viewport and adapts the original layout to the screen size while preserving the original artwork.

## Features

| Feature | Workflow |
| --- | --- |
| Create account | Enter first name, last name, license plate, email, role, and password. |
| Log in | Access the user or admin interface with your account details. |
| Start parking | Select a vacant yellow slot and confirm with **Done**. |
| Floor selection | Explore 20 spaces on each floor, from A1 to L5. |
| Nearest available spaces | See the first two available spaces in the original slot order. |
| Find my car | Locate the user's parked vehicle, highlighted in green. |
| Admin lookup | Search a user's plate from Home, then locate the vehicle or complete its transaction. |
| Transaction | Review the parking duration and fee, then finish with **Done**. |

## Try the web version

1. Open **[E-Parking](https://eparking-wawutriambodo.vercel.app)**.
2. Create an account with example details and the **Pengguna** role.
3. Log in with the same email, password, and plate.
4. Click **Start Parking**, select a yellow space, then click **Done**.
5. Use **Find my car** to see your vehicle's location.
6. Open **Transaction** and click **Done** to finish the simulated payment.

To explore the admin workflow, log out using the top-right account icon, create an **Admin** account with another plate, and search the user's plate on the admin Home screen.

### Parking fee

The web version follows the original application's formula:

```text
Fee = Rp20,000 + Rp5,000 × completed hours
```

### Browser demo

Accounts, parking sessions, and simulated transactions are stored locally in the browser. Visitors do not share records, and accounts do not sync across devices. Passwords are stored as salted PBKDF2 hashes. Admin selection is part of the original demo workflow, not a production access-control system. No real payment is collected. Use example account details and a password you do not use elsewhere.

## Original GUI assets

| Screen | Original design |
| --- | --- |
| Registration and login | `Gambar/Bg dasar.jpg` |
| Home | `Gambar/dashboard.jpg` |
| Parking map | `Gambar/start park bg.jpg`, floor 2 and 3 variants |
| Vehicle location | `Gambar/find my car.jpg`, floor 2 and 3 variants |
| Transaction | `Gambar/transaksi page.jpg` |

![Original parking design](Gambar/start%20park%20bg.jpg)

## Project structure

```text
E-Parking.ipynb       Original Python / Tkinter implementation
E-Parking.csv        Original desktop dataset
Gambar/              Original GUI backgrounds and buttons
web/                 Browser adaptation of the original GUI
  index.html         Web entry point
  style.css          Original canvas layout and scaling
  app.js             Account, navigation, and parking interactions
  logic.js           Slot labels and fee calculation
tests/               Parking rule tests
vercel.json          Web hosting configuration
```

## Run locally

```bash
python3 -m http.server 3000 --directory web
```

Open `http://localhost:3000`. To run the parking rule tests with Node.js 20 or newer, use `npm test`.

---

Created by **[Wawu Tri Ambodo](https://wawutriambodo.my.id)**
