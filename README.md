# Supply Chain Intelligence

A system that looks at supply chain data and tells you what to do next. It predicts demand, spots inventory problems, flags risky suppliers, and suggests better delivery routes.

## What It Does

Most supply chain tools show you charts. This one goes further and actually recommends actions:

- Predicts what you will need
- Warns when stock is running low
- Flags suppliers that might cause problems
- Suggests better delivery routes
- Simulates disruptions so you can test your plan

## Getting Started

`ash
pip install -r requirements.txt
python main.py
`

## How It Works

Raw operational data goes in. The system runs forecasting and optimization models. Actionable recommendations come out through an API and a live dashboard.
