<div align="center">

# 🅿️ E-Parking
### Park smart. Move easy.

An interactive parking experience — choose a space, find your vehicle, and finish your parking session in a few clicks.

[![Try the live demo](https://img.shields.io/badge/TRY_THE_LIVE_DEMO-126f58?style=for-the-badge&logo=vercel&logoColor=white)](https://eparking-wawutriambodo.vercel.app)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES_Modules-f7df1e?logo=javascript&logoColor=black)](web/)
[![Original project](https://img.shields.io/badge/Original_Project-Python_%2B_Tkinter-3776ab?logo=python&logoColor=white)](E-Parking.ipynb)

**60 parking spaces · 3 floors · A complete parking simulation**

</div>

## The experience

E-Parking brings a desktop parking management project to the browser. Visitors can explore a live parking map, start a session, locate a vehicle by its license plate, and complete a simulated transaction. The interface adapts to desktop and mobile screens and can be explored immediately without an account.

| Feature | What you can try |
| --- | --- |
| Interactive parking map | Browse three floors, each with 20 spaces, from A1 through L5. |
| Start parking | Choose an available space and enter a visitor name and license plate. |
| Find a vehicle | Search a plate and see the floor, space, start time, and estimated fee. |
| Parking transactions | Finish a session, generate a receipt, and make its space available again. |
| Transaction history | Review completed sessions and export them as CSV. |
| Admin demo | Inspect all active vehicles and simulate their checkout. |
| Browser persistence | Keep sessions and history after a page refresh on the same browser. |

## Try it in a minute

1. Open the **[live demo](https://eparking-wawutriambodo.vercel.app)**.
2. Select a green space and enter an example name and plate, such as `B 2026 XYZ`.
3. Click **Mulai parkir**. Your selected space becomes occupied.
4. Use **Temukan kendaraan** to search the plate.
5. Click **Selesaikan parkir**, finish the simulation, and view the receipt in **Riwayat transaksi**.

You can also search the preloaded example plate `B 1234 ABC`, switch to **Admin demo**, or use **Reset demo** to start again.

### Pricing

The web version preserves the desktop application's pricing formula:

```text
Total = Rp20,000 + (Rp5,000 × completed hours)
```

Examples: 45 minutes → Rp20,000; 1 hour 30 minutes → Rp25,000; 2 hours → Rp30,000.

### Demo scope

This is a public portfolio simulation. No real payment is collected. Data lives in your browser's local storage; it is not shared across visitors or devices. The role selector demonstrates an admin workflow and is not an authenticated account system. Use example visitor details rather than personal information.

## From desktop to web

The original project was built with **Python, Tkinter, Pillow, and pandas**, using CSV records for account and parking data. It includes **bubble sort** and **binary search** in its account lookup flow.

The browser version carries over the parking workflow, three-floor layout, space labels, vehicle search, and pricing while introducing a responsive interface and an immediate demo experience. Its UI and state management use vanilla JavaScript with ES modules; no frontend framework or production dependencies are required.

```text
web/                 Browser application
  index.html         Interface and page structure
  style.css          Responsive styles
  app.js             Interactions and browser storage
  logic.js           Parking rules and pricing
  favicon.svg        Application icon
tests/               Parking lifecycle and pricing tests
E-Parking.ipynb      Original desktop implementation
E-Parking.csv        Original desktop dataset (not served by the web app)
Gambar/              Original desktop interface assets
vercel.json          Web hosting configuration
```

## Run locally

With Python 3 installed:

```bash
python3 -m http.server 3000 --directory web
```

Open `http://localhost:3000`. With Node.js 20 or newer, verify the parking logic using `npm test`. No dependency installation is needed.

---

Created by **[Wawu Tri Ambodo](https://wawutriambodo.my.id)** · [Explore the source](https://github.com/UWWAWWU/E-Parking)
