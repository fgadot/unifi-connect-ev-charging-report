# Contributing to UniFi Connect EV Charge Report

Thank you for your interest! Contributions are welcome and appreciated.

## Ways to contribute

- **Bug reports** — open an issue describing what happened, what you expected, and your Docker version
- **Feature requests** — open an issue with the `enhancement` label
- **Pull requests** — fork the repo, make your changes, and open a PR against `main`

## Local development setup

```bash
git clone https://github.com/fgadot/unifi-connect-ev-charging-report.git
cd unifi-connect-ev-charging-report

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export DJANGO_SECRET_KEY=dev-key
export DEBUG=true
python manage.py runserver
```

Open **http://localhost:8000** and upload a UniFi EV Station CSV to test.

## Pull request guidelines

- Keep changes focused — one feature or fix per PR
- Test with a real CSV before submitting
- Update `README.md` if your change affects usage
- Bump `VERSION` in `ev_app/version.py` if you're making a release-worthy change

## CSV format

The app expects a UniFi EV Station charging history export with at minimum:
- `Date (console local time)` or `Date (UTC time)`
- `Power Usage (kWh)`
- `Charge Time (s)`
- `Total Time (s)`
