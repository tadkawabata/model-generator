# stockmodel pull.py
# pulls numbers straight from sec filings and prints a clean table
#   python pull.py check --ua "stockmodel you@email.com"            can we reach the sec
#   python pull.py latest klic --ua "stockmodel you@email.com"      newest 10q or 10k
#   python pull.py table klic --ua "stockmodel you@email.com"       every model row, csv, plus main stuff and checks
# the sec wants a contact email on every request. it goes in --ua (or a SEC_UA environment variable)
# nothing personal is saved in this file, so the repo stays clean
# standard library only. $ millions, eps per share, shares in millions

import os, sys, json, csv, gzip, time, urllib.request, urllib.error
from datetime import date, timedelta

ua = os.environ.get("SEC_UA", "")  # set from --ua in main()

M = 1_000_000
_last = [0.0]


def get(url):
    # one request to the sec, stays under 10 a second
    if "@" not in ua:
        sys.exit('stop: the sec needs a contact email. add --ua "stockmodel you@email.com" to the command')
    wait = 0.15 - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
    finally:
        _last[0] = time.time()
    return json.loads(raw)


def d(s):
    return date.fromisoformat(s)


# model rows and the xbrl tags to try, first tag that has the period wins
TAGS = {
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
                "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueNet", "SalesRevenueGoodsNet"],
    "cogs": ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold",
             "CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization"],
    "gross profit": ["GrossProfit"],
    "sga": ["SellingGeneralAndAdministrativeExpense"],
    "s&m": ["SellingAndMarketingExpense"],          # helper: some companies split sga
    "g&a": ["GeneralAndAdministrativeExpense"],     # helper
    "r&d": ["ResearchAndDevelopmentExpense", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"],
    "operating income": ["OperatingIncomeLoss"],
    "pretax income": ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
                      "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"],
    "taxes": ["IncomeTaxExpenseBenefit"],
    "net income": ["NetIncomeLoss", "ProfitLoss"],
    "diluted shares": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
    "eps": ["EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted"],
    "cfo": ["NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"],
}

# what the csv prints, in sheet order, with the exact labels the template uses
# segments, end markets, backlog and guidance come from the filing text, claude fills them
OUT = ["revenue", "revenue y/y", "cogs", "gross profit", "gross margin", "sga", "r&d",
       "other operating items", "operating income", "operating margin", "interest and other",
       "pretax income", "taxes", "tax rate", "net income", "diluted shares", "eps",
       "cfo", "capex", "fcf"]
SHOW = {"revenue": "Revenue", "revenue y/y": "Revenue Y/Y", "cogs": "COGS", "gross profit": "Gross profit",
        "gross margin": "Gross margin", "sga": "SG&A", "r&d": "R&D", "other operating items": "Other operating items",
        "operating income": "Operating income", "operating margin": "Operating margin",
        "interest and other": "Interest and other", "pretax income": "Pretax income", "taxes": "Taxes",
        "tax rate": "Tax rate", "net income": "Net income", "diluted shares": "Diluted shares", "eps": "EPS",
        "cfo": "CFO", "capex": "Capex", "fcf": "FCF"}


def periodic(x):
    # only 10q and 10k numbers, proxies and 8ks can carry tagged copies too
    return x.get("form", "").startswith("10-")


def newer(x, y):
    return (x["filed"], x["accn"]) > (y["filed"], y["accn"])


def series(facts, tags):
    # {(start, end): fact}. same period in many filings: latest filed wins
    out = {}
    for tag in tags:
        got, first = {}, {}
        for items in facts.get("us-gaap", {}).get(tag, {}).get("units", {}).values():
            for x in items:
                if "start" not in x or not periodic(x):
                    continue
                k = (d(x["start"]), d(x["end"]))
                if k not in got or newer(x, got[k]):
                    got[k] = dict(x, tag=tag)
                if k not in first or newer(first[k], x):
                    first[k] = x
        for k in got:
            got[k]["orig"] = first[k]["accn"]  # the filing where this period was new
            got[k]["orig_form"] = first[k]["form"]
        for k, x in got.items():
            out.setdefault(k, x)
    return out


def instant(facts, tags, tax="us-gaap"):
    # newest balance sheet style value for the first tag that has one
    best = None
    for tag in tags:
        for items in facts.get(tax, {}).get(tag, {}).get("units", {}).values():
            for x in items:
                if "start" in x or not periodic(x):
                    continue
                if best is None or (x["end"], x["filed"]) > (best["end"], best["filed"]):
                    best = dict(x, tag=tag)
        if best:
            return best
    return None


def fy_names(facts):
    # fiscal year label = fy of the 10k where that year was the current one
    # (fy on a fact belongs to the filing, so comparatives carry the wrong fy)
    best = {}
    for tag in TAGS["net income"] + TAGS["revenue"]:
        for items in facts.get("us-gaap", {}).get(tag, {}).get("units", {}).values():
            for x in items:
                if not x.get("form", "").startswith("10-K") or "start" not in x or not x.get("fy"):
                    continue
                e = d(x["end"])
                if 350 <= (e - d(x["start"])).days <= 380:
                    if x["accn"] not in best or e > best[x["accn"]][0]:
                        best[x["accn"]] = (e, x["fy"])
    return {e: fy for e, fy in best.values()}


def fiscal_years(S, names):
    ann = {}
    for ser in S.values():
        for (a, b) in ser:
            if 350 <= (b - a).days <= 380:
                ann[b] = a
    years = []
    off = None
    for b in sorted(ann):
        if b in names:
            off = names[b] - b.year
    for b in sorted(ann):
        fy = names.get(b, b.year + (off or 0))
        years.append({"fy": fy, "start": ann[b], "end": b})
    # year still in progress: starts the day after the last 10k year
    if years:
        last = years[-1]
        years.append({"fy": last["fy"] + 1, "start": last["end"] + timedelta(days=1), "end": None})
    return years


def quarters(S, y):
    # find the quarter ends inside one fiscal year, from ytd facts and 3 month facts
    s, e = y["start"], y["end"]
    ends, starts = set(), {}
    for ser in S.values():
        for (a, b) in ser:
            if e and b > e:
                continue
            days = (b - a).days
            if a == s and days >= 80:
                ends.add(b)
            if 80 <= days <= 100 and a >= s:
                ends.add(b)
                starts[b] = a
    qs = {}
    for b in sorted(ends):
        n = min(4, max(1, round((b - s).days / 91.25)))
        if n == 4 and e and b != e:
            continue
        qs.setdefault(n, b)
    out, prev = [], None
    for n in sorted(qs):
        b = qs[n]
        a = s if n == 1 else starts.get(b, prev + timedelta(days=1) if prev else None)
        if a is None:
            prev = b
            continue
        out.append({"fy": y["fy"], "n": n, "start": a, "end": b, "fystart": s, "prev_end": a - timedelta(days=1)})
        prev = b
    return out


def flow(ser, q):
    # quarter value: the 3 month fact, or ytd minus last ytd (q4 = fy minus 9 month ytd)
    x = ser.get((q["start"], q["end"]))
    if x:
        return x["val"], {"accn": x["orig"], "form": x["orig_form"]}, False
    cur = ser.get((q["fystart"], q["end"]))
    if not cur:
        return None, None, False
    if q["n"] == 1:
        return cur["val"], {"accn": cur["orig"], "form": cur["orig_form"]}, False
    prior = ser.get((q["fystart"], q["prev_end"]))
    if not prior:
        return None, None, False
    return cur["val"] - prior["val"], {"accn": cur["orig"], "form": cur["orig_form"], "less": prior["orig"]}, True


def build(S, cols):
    # raw values in dollars, per column
    for c in cols:
        v, src, approx = {}, {}, set()
        for r in TAGS:
            if r in ("diluted shares", "eps"):
                continue
            if c["kind"] == "fy":
                x = S[r].get((c["start"], c["end"]))
                v[r] = x["val"] if x else None
                if x:
                    src[r] = {"accn": x["orig"], "form": x["orig_form"]}
            else:
                v[r], src[r], der = flow(S[r], c["q"])
                if der and r in ("revenue", "net income"):
                    c["derived"] = True  # no 10q for this quarter, eg q4
        # sga split into s&m and g&a at some companies
        if v["sga"] is None and v["s&m"] is not None and v["g&a"] is not None:
            v["sga"] = v["s&m"] + v["g&a"]
        # gross profit and cogs fill each other in
        v["gp tagged"] = v["gross profit"] is not None
        v["cogs tagged"] = v["cogs"] is not None
        if v["gross profit"] is None and v["revenue"] is not None and v["cogs"] is not None:
            v["gross profit"] = v["revenue"] - v["cogs"]
        if v["cogs"] is None and v["revenue"] is not None and v["gross profit"] is not None:
            v["cogs"] = v["revenue"] - v["gross profit"]
        # the plug: anything in operating income that isnt sga or r&d
        if None not in (v["gross profit"], v["operating income"], v["sga"]):
            v["other operating items"] = v["gross profit"] - v["sga"] - (v["r&d"] or 0) - v["operating income"]
        else:
            v["other operating items"] = None
        if v["pretax income"] is not None and v["operating income"] is not None:
            v["interest and other"] = v["pretax income"] - v["operating income"]
        else:
            v["interest and other"] = None
        v["fcf"] = v["cfo"] - v["capex"] if v["cfo"] is not None and v["capex"] is not None else None
        c["v"], c["src"], c["approx"] = v, src, approx

    # shares and eps dont add up, handle separately
    for c in cols:
        v = c["v"]
        sh = S["diluted shares"]
        ep = S["eps"]
        if c["kind"] == "fy":
            x, y = sh.get((c["start"], c["end"])), ep.get((c["start"], c["end"]))
            v["diluted shares"] = x["val"] if x else None
            v["eps"] = y["val"] if y else None
            continue
        q = c["q"]
        x, y = sh.get((q["start"], q["end"])), ep.get((q["start"], q["end"]))
        v["diluted shares"] = x["val"] if x else None
        v["eps"] = y["val"] if y else None
        if v["diluted shares"] is None:
            v["diluted shares"] = approx_shares(S, q)
            if v["diluted shares"] is not None:
                c["approx"].add("diluted shares")
        if v["eps"] is None and v["net income"] is not None and v["diluted shares"]:
            v["eps"] = v["net income"] / v["diluted shares"]
            c["approx"].add("eps")


def approx_shares(S, q):
    # q4: 4 times fy weighted avg minus the q1 q2 q3 weighted avgs
    sh = S["diluted shares"]
    cur = sh.get((q["fystart"], q["end"]))
    if not cur or q["n"] == 1:
        return None
    n = q["n"]
    earlier = [x for (a, b), x in sh.items() if a >= q["fystart"] and b < q["start"] and 80 <= (b - a).days <= 100]
    if len(earlier) == n - 1:
        return n * cur["val"] - sum(x["val"] for x in earlier)
    prior = sh.get((q["fystart"], q["prev_end"]))
    if prior:
        return n * cur["val"] - (n - 1) * prior["val"]
    return None


def r1(x, nd=1, div=M):
    return "" if x is None else round(x / div, nd)


def ratio(a, b):
    return "" if a is None or not b else round(a / b, 3)


def table(ticker):
    cik, title = cik_for(ticker)
    sub = get(f"https://data.sec.gov/submissions/CIK{cik}.json")
    facts = get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")["facts"]

    S = {r: series(facts, t) for r, t in TAGS.items()}
    years = fiscal_years(S, fy_names(facts))
    if not years:
        sys.exit(f"stop: no annual numbers tagged for {ticker}, cant build a model")

    # columns: last 8 quarters, last 3 fiscal years
    qcols = []
    for y in years:
        for q in quarters(S, y):
            qcols.append({"kind": "q", "q": q, "fy": q["fy"], "start": q["start"], "end": q["end"], "derived": False})
    build(S, qcols)
    qcols = [c for c in qcols if c["v"]["revenue"] is not None or c["v"]["net income"] is not None][-8:]
    ycols = [{"kind": "fy", "fy": y["fy"], "start": y["start"], "end": y["end"], "derived": False}
             for y in years if y["end"]][-3:]
    build(S, ycols)
    cols = qcols + ycols

    # does the template fit
    if all(c["v"]["revenue"] is None for c in cols):
        print("note: no revenue tagged. filling what exists. biotech mode isnt built yet", file=sys.stderr)
    elif all(c["v"]["cogs"] is None and c["v"]["gross profit"] is None for c in cols):
        sys.exit(f"stop: template doesnt fit this company ({title} has no cogs or gross profit, "
                 "looks like a bank or insurer). nothing written")

    # ratios
    by_key = {(c["kind"], c["fy"], c.get("q", {}).get("n")): c for c in cols}
    for c in cols:
        v = c["v"]
        ago = by_key.get((c["kind"], c["fy"] - 1, c.get("q", {}).get("n")))
        v["revenue y/y"] = ratio(v["revenue"] - ago["v"]["revenue"], ago["v"]["revenue"]) \
            if ago and v["revenue"] is not None and ago["v"]["revenue"] is not None else ""
        v["gross margin"] = ratio(v["gross profit"], v["revenue"])
        v["operating margin"] = ratio(v["operating income"], v["revenue"])
        v["tax rate"] = ratio(v["taxes"], v["pretax income"])

    w = csv.writer(sys.stdout, lineterminator="\n")
    srcs = [source(c, cik) for c in cols]
    w.writerow(["Model", ticker.upper(), nice(title)])
    w.writerow(["Fiscal label"] + [label(c) for c in cols])
    w.writerow(["Period end"] + [c["end"].isoformat() for c in cols])
    w.writerow(["Weeks"] + [round(((c["end"] - c["start"]).days + 1) / 7) for c in cols])
    w.writerow(["Kind"] + [kind(c) for c in cols])
    w.writerow(["Source"] + [s[0] for s in srcs])
    w.writerow(["Link"] + [s[1] for s in srcs])
    w.writerow(["Accession"] + [s[2] for s in srcs])
    for r in OUT:
        row = [SHOW[r]]
        for c in cols:
            x = c["v"].get(r)
            if r in ("revenue y/y", "gross margin", "operating margin", "tax rate"):
                row.append(x)
            elif r == "eps":
                row.append("" if x is None else round(x, 2))
            else:
                row.append(r1(x))
        w.writerow(row)
    w.writerow(["Approx"] + [", ".join(SHOW[a] for a in sorted(c["approx"])) for c in cols])

    # main stuff
    w.writerow([])
    w.writerow(["Main", "Value", "As of", "Source", "Link", "Detail"])
    w.writerow(["Ticker", ticker.upper(), "", "", "", ""])
    w.writerow(["Company", nice(title), "", "SEC", "", "Write it the way the 10-K cover does"])
    w.writerow(["CIK", cik, "", "SEC", "", ""])
    fye = sub.get("fiscalYearEnd") or ""
    w.writerow(["Fiscal year end", f"{int(fye[:2])}/{int(fye[2:])}" if len(fye) == 4 else fye, "", "SEC", "", ""])
    sh = instant(facts, ["EntityCommonStockSharesOutstanding"], "dei")
    if sh:
        w.writerow(["Shares out", r1(sh["val"], 3), sh["end"], filing_label(sh) + " cover", link(cik, sh["accn"]),
                    f"dei:{sh['tag']} {sh['accn']}"])
    else:
        w.writerow(["Shares out", "", "", "", "", "Not tagged (often multiple share classes). Read the 10-Q cover"])
    found = {}
    for name, tags in [("Cash", ["CashAndCashEquivalentsAtCarryingValue",
                                 "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"]),
                       ("ST investments", ["ShortTermInvestments", "MarketableSecuritiesCurrent",
                                           "AvailableForSaleSecuritiesDebtSecuritiesCurrent"])]:
        x = found[name] = instant(facts, tags)
        if x:
            w.writerow([name, r1(x["val"]), x["end"], filing_label(x), link(cik, x["accn"]), f"us-gaap:{x['tag']} {x['accn']}"])
        else:
            w.writerow([name, 0, "", "", "", "None tagged. Check the balance sheet"])
    x_cash = found["Cash"]
    asof = x_cash["end"] if x_cash else max(c["end"] for c in cols).isoformat()
    debt, parts = debt_total(facts, asof)
    if parts:
        w.writerow(["Debt", r1(debt), asof, filing_label(parts[0]), link(cik, parts[0]["accn"]),
                    " + ".join(f"us-gaap:{p['tag']}" for p in parts) + f" {parts[0]['accn']}"])
    else:
        w.writerow(["Debt", "", asof, "", "", "No debt tagged on the newest balance sheet. Check it; no borrowings means 0"])
    dates = found

    # checks
    w.writerow([])
    w.writerow(["Check", "Result", "Detail"])
    for row in checks(S, cols, years, sub, facts):
        w.writerow(row)
    # 9 main as of dates vs the newest quarter
    newest = max(c["end"] for c in cols).isoformat()
    for name, x in dates.items():
        if x and x["end"] < newest:
            w.writerow(["9 Main as of", "Flag", f"{name} is from {x['end']} but the newest quarter ends {newest}. "
                        "Take it from the newest 10-Q balance sheet"])


def debt_total(facts, asof):
    # only debt tagged on the newest balance sheet counts. an old tag from years ago means nothing now
    cur = lambda t: (lambda x: x if x and x["end"] == asof else None)(instant(facts, [t]))
    parts = []
    tot = cur("LongTermDebt")
    if tot:
        parts.append(tot)
    else:
        parts += [x for x in (cur("LongTermDebtNoncurrent"), cur("LongTermDebtCurrent")) if x]
    parts += [x for x in (cur("ShortTermBorrowings"), cur("CommercialPaper")) if x]
    if not parts:
        return None, []
    return sum(p["val"] for p in parts), parts


def nice(t):
    # sec titles come in all caps sometimes. claude fixes brand styling (eg BioCryst) from the 10k cover
    return t.title() if t.isupper() else t


def fyl(fy):
    return f"FY{str(fy)[-2:]}"


def label(c):
    return fyl(c["fy"]) if c["kind"] == "fy" else f"Q{c['q']['n']} {fyl(c['fy'])}"


def kind(c):
    if c["kind"] == "fy":
        return "Fiscal year"
    return "Derived quarter" if c["derived"] else "Quarter"


def link(cik, accn):
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn.replace('-', '')}/"


def form_of(f):
    return "10-K" if f.startswith("10-K") else "10-Q"


def filing_label(x):
    # short name for the filing a balance sheet or cover value came from, eg 10-Q Q2 FY26
    form, fy, fp = form_of(x.get("form", "")), x.get("fy"), x.get("fp")
    if not fy:
        return form
    return f"10-K {fyl(fy)}" if form == "10-K" or fp == "FY" else f"10-Q {fp} {fyl(fy)}"


def source(c, cik):
    # short label, link, accession(s) for a model column
    s = c["src"].get("net income") or c["src"].get("revenue")
    if not s:
        return "", "", ""
    form = form_of(s["form"])
    if c["kind"] == "q" and "less" in s:
        lab = f"{form} {fyl(c['fy'])} less Q{c['q']['n'] - 1}"
        acc = f"{s['accn']} less {s['less']}"
    else:
        lab, acc = f"{form} {label(c)}", s["accn"]
    return lab, link(cik, s["accn"]), acc


def checks(S, cols, years, sub, facts):
    out = []
    near = lambda a, b, tol: a is not None and b is not None and abs(a - b) <= tol

    def tol(*vals):
        # 0.2 normally. companies that report in whole millions round each line, allow that
        vals = [x for x in vals if x is not None]
        if vals and all(x % M == 0 for x in vals):
            return max(0.2 * M, 0.5 * M * len(vals))
        return 0.2 * M

    # newest filing actually in the xbrl data yet
    lat = latest_filing(sub)
    if lat:
        col = next((c for c in cols if c["end"].isoformat() == lat["period"]), None)
        if col and col["v"]["revenue"] is not None and col["v"]["net income"] is not None:
            out.append(["Newest filing", "OK", f"{lat['form']} for {lat['period']} is in the data"])
        else:
            out.append(["Newest filing", "Fail", f"{lat['form']} {lat['accn']} for {lat['period']} isn't fully in the SEC "
                        "XBRL API yet or uses other tags. Read the filing for that quarter"])

    for c in cols:
        v, L = c["v"], label(c)
        # holes in core rows
        miss = [r for r in ["revenue", "gross profit", "operating income", "net income"] if v.get(r) is None]
        if miss:
            out.append(["Missing", "Fail", f"{L}: {', '.join(SHOW[m] for m in miss)} not in the SEC API for this period. Read the filing"])
        # 1 gross profit ties
        if v["gp tagged"] and v["cogs tagged"] and v["revenue"] is not None:
            ok = near(v["revenue"] - v["cogs"], v["gross profit"], tol(v["revenue"], v["cogs"], v["gross profit"]))
            out.append(["1 Gross profit ties", "OK" if ok else "Fail",
                        f"{L}: revenue minus COGS vs reported {r1(v['gross profit'])}"])
        # 2 net income ties
        if None not in (v["pretax income"], v["taxes"], v["net income"]):
            gap = v["pretax income"] - v["taxes"] - v["net income"]
            ok = abs(gap) <= tol(v["pretax income"], v["taxes"], v["net income"])
            out.append(["2 Net income ties", "OK" if ok else "Flag",
                        f"{L}: pretax minus taxes vs net income, gap {r1(gap)}"
                        + ("" if ok else ". Minority interest or discontinued ops?")])
        # 3 eps
        if v["eps"] is not None and v["net income"] is not None and v["diluted shares"] and "eps" not in c["approx"]:
            calc = v["net income"] / v["diluted shares"]
            out.append(["3 EPS", "OK" if abs(calc - v["eps"]) <= 0.02 else "Fail",
                        f"{L}: reported {round(v['eps'], 2)} vs net income over shares {round(calc, 2)}"])
        # 7 big one offs
        o = v["other operating items"]
        if o is not None and v["revenue"] and abs(o) > 0.05 * abs(v["revenue"]):
            out.append(["7 One-off", "Flag",
                        f"{L}: other operating items of {r1(o)} are {round(100 * abs(o) / abs(v['revenue']))}% of revenue. Read the filing"])
        # weeks
        wk = round(((c["end"] - c["start"]).days + 1) / 7)
        if c["kind"] == "q" and wk != 13:
            out.append(["Weeks", "Flag", f"{L} is {wk} weeks, so year over year is distorted"])

    # 4 q1 + q2 + q3 equals the 9 month ytd, 5 fy equals its 4 quarters. only years in the sheet
    first = min(c["start"] for c in cols)
    for y in [y for y in years if y["end"] is None or y["end"] >= first]:
        qs = {q["n"]: q for q in quarters(S, y)}
        for r in ["revenue", "operating income", "net income"]:
            ser = S[r]
            if all(n in qs for n in (1, 2, 3)):
                ytd = ser.get((y["start"], qs[3]["end"]))
                direct = [ser.get((qs[n]["start"], qs[n]["end"])) for n in (1, 2, 3)]
                if ytd and all(direct):
                    tot = sum(x["val"] for x in direct)
                    ok = near(tot, ytd["val"], tol(ytd["val"], *[x["val"] for x in direct]))
                    out.append(["4 Nine-month YTD", "OK" if ok else "Fail",
                                f"{fyl(y['fy'])} {SHOW[r].lower()}: Q1+Q2+Q3 {r1(tot)} vs YTD {r1(ytd['val'])}"
                                + ("" if ok else ". Something was restated")])
            if y["end"] and len(qs) == 4:
                full = ser.get((y["start"], y["end"]))
                parts = [flow(ser, qs[n])[0] for n in (1, 2, 3, 4)]
                if full and None not in parts:
                    ok = near(sum(parts), full["val"], tol(full["val"], *parts))
                    out.append(["5 Fiscal year sums", "OK" if ok else "Fail",
                                f"{fyl(y['fy'])} {SHOW[r].lower()}: 4 quarters {r1(sum(parts))} vs FY {r1(full['val'])}"])
    return out


def latest_filing(sub):
    r = sub["filings"]["recent"]
    for i, form in enumerate(r["form"]):
        if form in ("10-Q", "10-K"):
            return {"form": form, "accn": r["accessionNumber"][i],
                    "filed": r["filingDate"][i], "period": r["reportDate"][i]}
    return None


def cik_for(ticker):
    t = ticker.upper().replace(".", "-")
    for row in get("https://www.sec.gov/files/company_tickers.json").values():
        if row["ticker"] == t:
            return str(row["cik_str"]).zfill(10), row["title"]
    sys.exit(f"stop: cant find ticker {ticker} on the sec ticker list")


def latest(ticker):
    cik, title = cik_for(ticker)
    sub = get(f"https://data.sec.gov/submissions/CIK{cik}.json")
    f = latest_filing(sub)
    if not f:
        sys.exit(f"stop: no 10q or 10k found for {ticker}")
    print(f"{ticker.lower()} {title.lower()}")
    print(f"newest {f['form']}: period end {f['period']}, accession {f['accn']}, filed {f['filed']}")


def check():
    sub = get("https://data.sec.gov/submissions/CIK0000056978.json")
    print(f"ok: reached the sec ({sub['name'].lower()})")


def main():
    global ua
    a = sys.argv[1:]
    if "--ua" in a:
        i = a.index("--ua")
        if i + 1 < len(a):
            ua = a[i + 1]
        a = a[:i] + a[i + 2:]
    try:
        if a[:1] == ["check"]:
            check()
        elif len(a) == 2 and a[0] == "latest":
            latest(a[1])
        elif len(a) == 2 and a[0] == "table":
            table(a[1])
        else:
            sys.exit('use: python pull.py check | latest <ticker> | table <ticker>, plus --ua "stockmodel you@email.com"')
    except urllib.error.HTTPError as e:
        sys.exit(f"blocked: sec said {e.code} {e.reason} for {e.url}. "
                 "403 usually means --ua is missing an email or the sec domains arent allowed")
    except urllib.error.URLError as e:
        sys.exit(f"blocked: cant reach the sec ({e.reason}). add data.sec.gov and www.sec.gov to allowed domains")


if __name__ == "__main__":
    main()
