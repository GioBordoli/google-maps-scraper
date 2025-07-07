# 🗺️ Google Maps Scraper

Effortlessly extract business data and valuable information from Google Maps using Python and Selenium.

---

## ⚡ Overview

**Google Maps Scraper** is a powerful, easy-to-use tool for scraping business listings, reviews, and metadata directly from Google Maps. Whether you're conducting market research, building lead lists, or analyzing local competitors, this scraper helps automate the tedious process of gathering data from Google Maps.

---

## 🚀 Features

- **Automated Data Extraction**: Scrape business names, addresses, phone numbers, ratings, review counts, and more.
- **Customizable Search**: Easily specify keywords, locations, and result counts.
- **Headless Browsing**: Runs in the background using Selenium with optional headless mode.
- **Export to CSV/JSON**: Output your data in formats ready for analysis.
- **Robust Error Handling**: Includes logic for retries, timeouts, and captcha detection.
- **Modular & Extensible**: Built for easy updates and customization.

---

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/GioBordoli/google-maps-scraper.git
   cd google-maps-scraper
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the correct [ChromeDriver](https://sites.google.com/chromium.org/driver/) for your Chrome version and add it to your PATH.**

---

## 🚦 Usage

```bash
python scraper.py --query "coffee shops" --location "San Francisco, CA" --output results.csv
```

**Options:**
- `--query`: Search keyword(s) (e.g. "restaurants", "bookstores").
- `--location`: The location to search in.
- `--output`: Output file (CSV or JSON).
- `--max-results`: Limit the number of results (optional).
- `--headless`: Run browser in headless mode (optional).

**Example:**
```bash
python scraper.py --query "pizza" --location "New York, NY" --output pizza_ny.csv --max-results 50 --headless
```

---

## 💡 Example Output

| Name              | Address                   | Phone         | Rating | Reviews | Website               |
|-------------------|--------------------------|---------------|--------|---------|-----------------------|
| Joe's Pizza       | 7 Carmine St, NY, NY     | (212) 366-1182| 4.5    | 2458    | www.joespizzanyc.com  |
| ...               | ...                      | ...           | ...    | ...     | ...                   |

---

## 🧩 How It Works

1. Uses Selenium to open Google Maps and perform a search.
2. Parses the search results and collects data fields.
3. Handles pagination and scrolling automatically.
4. Exports the data in your chosen format.

---

## ⚠️ Disclaimer

- **For educational and research purposes only.**
- Scraping Google Maps may violate [Google's Terms of Service](https://developers.google.com/maps/terms).
- Use responsibly and at your own risk.

---

## 🤝 Contributions

Pull requests, bug reports, and feature requests are welcome! Please open an issue or submit a PR.

---

## 📄 License

[MIT License](LICENSE)

---

## 👤 Author

Made with ❤️ by [GioBordoli](https://github.com/GioBordoli)
