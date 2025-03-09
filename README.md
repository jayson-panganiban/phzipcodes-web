# 🏷️ PH Zipcodes

Find zip codes across the Philippines with ease! 📫

## 🌟 About

PH Zipcodes helps you find postal or zip codes across the Philippines with a clean, fast, and reliable search experience. The data comes directly from PHLPost (Philippine Postal Corporation), the official postal service of the Philippines.

Built using [phzipcodes](https://github.com/jayson-panganiban/phzipcodes) - A Python package for Philippines zip codes.

## 🛠️ Tech Stack

- FastAPI
- HTMX
- TailwindCSS
- Python
- phzipcodes

## 🏃‍♂️ Running Locally

### Clone the repository

```bash
git clone https://github.com/jayson-panganiban/phzipcodes-web.git
cd phzipcodes-web
```

### Install dependencies

```bash
uv sync
source .venv/bin/activate
```

### Install development dependencies

```bash
uv pip install -e ".[dev]"
```

### Running the App

Start the development server:

```bash
uvicorn app.main:app --reload
```

### Running Tests

Install browser binaries for Playwright:

```bash
playwright install
```

Run the tests:

```bash
pytest tests
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
