import csv

def monthly_totals(path):
    totals = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            try:
                hours = float(row["hours"])
            except ValueError:
                continue
            client = row["client"].strip()
            totals[client] = totals.get(client, 0) + hours
    return totals

def write_report(totals, out="report.txt"):
    with open(out, "w") as f:
        for client, hours in sorted(totals.items()):
            f.write(f"{client}: {hours}\n")

write_report(monthly_totals("hours.csv"))
