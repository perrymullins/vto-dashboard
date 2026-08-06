"""Declarative map of the VTO workbook.

Row numbers are real Excel rows so every entry can be checked against the
spreadsheet by eye. When next year's workbook shifts rows, edit here — not
extract.py.

Block types
  timeseries  rows are periods           -> line chart
  stacked     one column, two definitions stacked vertically (Wellness)
  categorical rows are categories, not time
  matrix      rows are entities, columns are periods
  irregular   overlapping/non-comparable periods (Disaster)
"""

SOURCE = "CMV Communities 2026 VTO Data Ingathering V2- SM.xlsx"
REPORTING_YEAR = 2026
LATEST_DATA_YEAR = 2025
BASELINE_YEAR = 2019

THEMES = [
    ("reach", "Reach & Impact",
     "How many people the diocese and its institutions touch in a year."),
    ("growth", "Congregational Growth",
     "Attendance, membership, and movement between size tiers."),
    ("planting", "Planting & New Communities",
     "Church plants, missional communities, and campus ministry."),
    ("pipeline", "Leadership Pipeline",
     "Discernment, postulancy, seminarians, and clergy transitions."),
    ("congleadership", "Congregational Leadership",
     "Who leads our largest congregations."),
    ("formation", "Formation & Training",
     "Youth and adult formation, licensing, and safeguarding."),
    ("support", "Congregational Support",
     "Coaching, foundations, and disaster response."),
    ("diversity", "Diversity & Representation",
     "Gender and ethnicity across boards, clergy, staff, and teams."),
    ("comms", "Communications Reach",
     "Newsletters, social media, and web audience."),
    ("finance", "Financial & Social Impact",
     "Dollars deployed into communities by diocesan entities."),
]

# Shorthand builders ---------------------------------------------------------

def n(sid, label, col, hib=True):
    return {"id": sid, "label": label, "col": col, "unit": "count",
            "format": "integer", "higherIsBetter": hib}

def pct(sid, label, col, hib=None):
    return {"id": sid, "label": label, "col": col, "unit": "percent",
            "format": "percent1", "higherIsBetter": hib}

def usd(sid, label, col, hib=True):
    return {"id": sid, "label": label, "col": col, "unit": "usd",
            "format": "usd0", "higherIsBetter": hib}


BLOCKS = [

    # ================================================== Communities — growth
    {
        "id": "communities.asa", "sheet": "Communities", "theme": "growth",
        "title": "EDOT Average Sunday Attendance",
        "subtitle": "as reported 12/31 of previous year",
        "type": "timeseries", "rows": (3, 11), "noteCol": 2, "owner": "CMV",
        "series": [n("asa", "ASA", 1)],
        "caveats": [
            {"period": "2021", "type": "coverage",
             "text": "Represents only up until March 8, 2020."},
            {"period": "2022", "type": "covid",
             "text": "Pandemic trough. Compare to 2019 as well as to last year."},
            {"period": "2019", "type": "methodology",
             "text": "22,888 here, but the Average Weekly Worship block on the same tab "
                     "records 22,288 for 2019 and the Population tab records 22,288 in "
                     "its 2018 row. Every other year in the two blocks agrees exactly, "
                     "so one of the two is probably a transposed 8 and 2. Confirm which "
                     "before quoting the 2019 pre-COVID baseline."},
        ],
    },
    {
        "id": "communities.growth_1plus", "sheet": "Communities", "theme": "growth",
        "title": "Congregations Growing by 1 or More ASA",
        "subtitle": "based on prior year's parochial report",
        "type": "timeseries", "rows": (16, 23), "owner": "CMV",
        "series": [
            n("churches", "# of Churches", 1),
            pct("share", "% of Total Churches", 2, True),
            n("family", "Family (1–75)", 3),
            n("pastoral", "Pastoral (76–150)", 4),
            n("transitional", "Transitional (151–225)", 5),
            n("program", "Program (226–450)", 6),
            n("resource", "Resource (451+)", 7),
        ],
        "caveats": [
            {"period": "2022", "type": "covid",
             "text": "Only 17 congregations grew — the pandemic low point."},
            {"period": None, "type": "methodology",
             "text": "The size-tier columns add up to the church count every year. The "
                     "'% of Total Churches' column does not use a consistent "
                     "denominator, though: it implies 152–166 churches depending on the "
                     "year, and only 2025 matches the congregation count on this tab "
                     "(160). Read the counts; treat the percentage as approximate."},
        ],
    },
    {
        "id": "communities.counts", "sheet": "Communities", "theme": "growth",
        "title": "Number of Communities",
        "subtitle": "based on prior year's parochial report",
        "type": "timeseries", "rows": (28, 35), "owner": "CMV",
        "series": [
            n("total", "Total", 1),
            n("congregations", "Congregations", 2),
            n("missional", "Missional Communities", 3),
            n("campus", "Campus Missions", 4),
            n("fellowships", "Fellowships", 5),
        ],
        "caveats": [
            {"period": "2025", "type": "methodology",
             "text": "The jump from 251 to 330 is driven almost entirely by "
                     "Missional Communities (50 → 141). Confirm whether this "
                     "reflects new communities or a change in what is counted "
                     "before reading it as growth."},
            {"period": "2018", "type": "methodology",
             "text": "The components add to 253 but the workbook's Total says 252. "
                     "Every other year adds up exactly."},
        ],
    },
    {
        "id": "communities.awwa", "sheet": "Communities", "theme": "growth",
        "title": "Average Weekly Worship Attendance",
        "subtitle": "based on prior year's parochial report",
        "type": "timeseries", "rows": (40, 48), "owner": "CMV",
        "series": [n("total", "Average Weekly Worship Attendance", 1)],
        "notes": ["2017 & 2018 totals do not include missional communities, campus "
                  "missions, or weekday attendance averages of congregations."],
        "caveats": [{"period": "2017", "type": "coverage",
                     "text": "2017–2018 exclude missional communities, campus missions, "
                             "and weekday averages — not comparable to later years."}],
    },
    {
        "id": "communities.awwa_breakdown", "sheet": "Communities", "theme": "growth",
        "title": "Weekly Worship Attendance by Type (2025)",
        "subtitle": "components of the 39,507 total weekly worship count",
        "type": "categorical", "headerRow": 39, "valueRow": 40,
        "cols": (2, 8), "owner": "CMV",
        "valueLabel": "Weekly Attendance",
        "notes": ["Collected for 2025 only. The 21,104 figure in the trend above is a "
                  "different measure and is not the sum of these components."],
    },
    {
        "id": "communities.membership", "sheet": "Communities", "theme": "growth",
        "title": "Total Membership of Congregations",
        "subtitle": "based on prior year's parochial report",
        "type": "timeseries", "rows": (52, 54), "noteCol": 2, "owner": "CMV",
        "series": [n("members", "Members", 1)],
        "trackingStart": "2023",
        "notes": ["Fellowship number is estimated as ASA × 2."],
    },
    {
        "id": "communities.visitors", "sheet": "Communities", "theme": "growth",
        "title": "Total Reported Visitors",
        "type": "timeseries", "rows": (57, 59), "noteCol": 2, "owner": "CMV",
        "series": [n("visitors", "Visitors", 1)],
        "trackingStart": "2024",
        "caveats": [
            {"period": "2024", "type": "coverage",
             "text": "Gathered from 152 congregations and plants."},
            {"period": "2025", "type": "coverage",
             "text": "The extension report is not mandatory and most churches did not "
                     "complete it, so no diocese-wide figure exists."},
        ],
    },
    {
        "id": "communities.missional_ranked", "sheet": "Communities", "theme": "growth",
        "title": "Congregations Ranked as Missional",
        "type": "timeseries", "rows": (62, 64), "noteCol": 2, "owner": "CMV",
        "series": [n("congregations", "Congregations", 1)],
        "trackingStart": "2023",
    },

    # ============================================ Communities — planting
    {
        "id": "communities.missions_fellowships", "sheet": "Communities",
        "theme": "planting", "title": "Missions & Fellowships",
        "type": "timeseries", "rows": (70, 78), "owner": "CMV",
        "series": [n("missions", "Missions", 1), n("fellowships", "Fellowships", 2)],
    },
    {
        "id": "communities.plants_infancy", "sheet": "Communities", "theme": "planting",
        "title": "Plants in Infancy Stages",
        "type": "timeseries", "rows": (81, 89), "owner": "CMV",
        "series": [n("plants", "Plants", 1)],
    },
    {
        "id": "communities.mission_sites", "sheet": "Communities", "theme": "planting",
        "title": "Possible Mission Sites Identified",
        "type": "timeseries", "rows": (92, 100), "owner": "CMV",
        "series": [n("sites", "Sites", 1)],
        "notes": ["The stage each year's count refers to varies — identified, remaining "
                  "after due diligence, submitted to the Bishop, or approved. Hover a "
                  "point for the original wording."],
        "caveats": [{"period": None, "type": "definition",
                     "text": "Counts are not strictly comparable year to year; the "
                             "pipeline stage being counted changed over time."}],
    },
    {
        "id": "communities.plants_sustainability", "sheet": "Communities",
        "theme": "planting", "title": "New Plants Moving to Sustainability",
        "subtitle": "new plants are those established August–July",
        "type": "timeseries", "rows": (104, 110), "owner": "CMV",
        "series": [n("plants", "Plants", 1)],
    },
    {
        "id": "communities.iona_plants", "sheet": "Communities", "theme": "planting",
        "title": "Iona Students Assigned to Church Plants",
        "type": "timeseries", "rows": (113, 120), "noteCol": 2, "owner": "CMV",
        "series": [n("students", "Students", 1)],
    },
    {
        "id": "communities.new_plants", "sheet": "Communities", "theme": "planting",
        "title": "New Church Plants",
        "type": "timeseries", "rows": (124, 131), "owner": "CMV",
        "series": [n("diocese", "Whole Diocese", 1), n("north", "North Region", 2)],
    },
    {
        "id": "communities.new_hispanic", "sheet": "Communities", "theme": "planting",
        "title": "New Hispanic Ministries",
        "type": "timeseries", "rows": (135, 137), "owner": "CMV",
        "series": [n("diocese", "Whole Diocese", 1), n("north", "North Region", 2)],
        "trackingStart": "2023",
    },
    {
        "id": "communities.new_missional", "sheet": "Communities", "theme": "planting",
        "title": "New Missional Communities",
        "type": "timeseries", "rows": (141, 148), "owner": "CMV",
        "series": [n("diocese", "Whole Diocese", 1), n("north", "North Region", 2)],
    },
    {
        "id": "communities.mc_asa", "sheet": "Communities", "theme": "planting",
        "title": "Missional Communities Total ASA",
        "type": "timeseries", "rows": (151, 158), "owner": "CMV",
        "series": [n("asa", "ASA", 1)],
        "caveats": [{"period": None, "type": "methodology",
                     "text": "Values repeat across pairs of years (690, 800, 1472), "
                             "suggesting figures were carried forward rather than "
                             "recollected annually."}],
    },
    {
        "id": "communities.new_campus", "sheet": "Communities", "theme": "planting",
        "title": "New Campus Ministries",
        "type": "timeseries", "rows": (161, 168), "owner": "CMV",
        "series": [n("ministries", "New Ministries", 1)],
    },
    {
        "id": "communities.campus_all", "sheet": "Communities", "theme": "planting",
        "title": "Total ASA Across All Campus Ministries",
        "type": "timeseries", "rows": (174, 182), "periodType": "schoolYear",
        "owner": "CMV", "series": [n("asa", "Total ASA", 1)],
    },
    {
        "id": "communities.campus_by_school", "sheet": "Communities", "theme": "planting",
        "title": "Campus Ministry ASA by Campus",
        "type": "matrix", "periodType": "schoolYear", "owner": "CMV",
        "entityLabel": "Campus", "valueLabel": "ASA",
        # (label, header_row, first_row, last_row)
        "entities": [
            ("Baylor Univ", 185, 186, 194),
            ("Rice Univ", 197, 198, 206),
            ("Univ of Houston", 209, 210, 218),
            ("Univ of Texas", 221, 222, 230),
            ("Texas A&M", 233, 234, 242),
            ("UTMB Galveston", 245, 246, 254),
            ("Sam Houston State Univ", 257, 258, 261),
            ("Lamar", 264, 265, 267),
            ("Prairie View A&M", 270, 271, 273),
            ("South Austin Canterbury (ACC)", 276, 277, 279),
            ("Southwestern University", 282, 283, 285),
            ("Stephen F. Austin State", 288, 289, 291),
            ("Tarleton", 294, 295, 297),
            ("UT-Tyler", 300, 301, 303),
            ("Temple College", 306, 307, 309),
            ("TCU", 312, 313, 315),
            # Listed under "ANY NEW CAMPUS MISSIONS?" with no year header, so the
            # period is supplied here (5th element) rather than read from col A.
            ("UT Arlington", None, 320, 320, "2024-2025"),
        ],
        "notes": ["Univ of Texas excludes the counseling center.",
                  "UTMB Galveston counts students served weekly; Southwestern counts "
                  "students served monthly. Neither is an ASA and they are not "
                  "comparable to the other campuses.",
                  "Several 2024-2025 figures are estimates."],
    },

    # ================================================== Population — reach
    {
        "id": "population.impact", "sheet": "Population", "theme": "reach",
        "title": "Individuals Impacted by Diocesan Ministries",
        "type": "timeseries", "rows": (2, 10), "owner": "CMV",
        "series": [
            n("asa", "EDOT Total ASA", 1),
            n("campus", "Campus Ministries ASA", 2),
            n("missional", "Missional Communities ASA", 3),
            n("ssw", "SSW Students", 4),
            n("iona", "Iona School Students", 5),
            n("campers", "Camp Allen Campers", 6),
            n("discovery", "Camp Allen Discovery Students", 7),
            n("confguests", "Camp Allen Conf Center Guests", 8),
            n("elbuen", "El Buen Clients", 9),
            n("stvincents", "St. Vincent's House Clients", 10),
            n("schools", "EDOT Schools' Students", 11),
            n("total", "TOTAL", 12),
        ],
        "headline": "total",
        "caveats": [
            {"period": None, "type": "methodology",
             "text": "The 'EDOT Total ASA' column on this tab is out of step with the "
                     "Communities tab for 2017–2023: each figure appears one year "
                     "late (this tab's 2022 = 16,394 is the Communities tab's 2023). "
                     "2024 and 2025 agree. The TOTAL is the exact sum of the columns "
                     "beside it, so the totals for 2017–2023 inherit the shift. "
                     "Reconcile the two tabs before using the earlier totals as a "
                     "baseline."},
            {"period": None, "type": "methodology",
             "text": "The \"EDOT Schools' Students\" column comes from the TOTALS row of "
                     "the school table on this same tab, and that row is not the sum of "
                     "the column above it before 2024-25. It is short by 168 to 273 "
                     "students every year from 2017-18 to 2023-24 (2017-18: 11,182 "
                     "stated against 11,446 actual), and no contiguous block of schools "
                     "explains the gap, so those totals appear to be stale hard-coded "
                     "figures rather than live sums. Only 2024-25 (12,851) and 2025-26 "
                     "(12,970) reconcile exactly."},
        ],
    },
    {
        "id": "population.schools", "sheet": "Population", "theme": "reach",
        "title": "Episcopal School Enrollment",
        "type": "matrix", "periodType": "schoolYear", "owner": "CMV",
        "entityLabel": "School", "valueLabel": "Students",
        "nameCol": 13, "cols": (14, 22), "headerRow": 1,
        "rows": (2, 60), "noteCol": 23, "totalRow": 62,
        "notes": ["2025-26 figures for some schools are estimated from the previous year.",
                  "Schools with trailing NA values have closed or are no longer "
                  "Episcopal; the note column gives the date."],
    },

    # ================================================== Coaching — support
    {
        "id": "coaching.activities", "sheet": "Coaching", "theme": "support",
        "title": "Congregational Coaching & Consulting (2025)",
        "subtitle": "congregations served, by activity",
        "type": "categorical", "rows": (3, 9), "nameCol": 0, "owner": "CMV",
        "totalRow": 11,
        "series": [
            n("staff", "By Staff", 1),
            n("consultants", "By Consultants", 2),
            n("factor", "Impact Factor", 3, None),
            n("impacted", "# Impacted", 4),
        ],
        "extraCol": {"col": 5, "label": "Factor Explanation"},
        "notes": ["2025 only — this is a snapshot, not a trend.",
                  "'# Impacted' is congregations served multiplied by an impact factor "
                  "estimating how many people each engagement reaches. It is an "
                  "estimate, not a count.",
                  "The workbook leaves '# of Coaches/Consultants Utilized by the "
                  "Diocese' blank."],
    },

    # ================================================== Foundations — support
    {
        "id": "foundations.coaching", "sheet": "Foundations", "theme": "support",
        "title": "Foundations Coaching",
        "type": "timeseries", "rows": (3, 7), "owner": "DF",
        "series": [n("entities", "Entities Assisted", 1)],
        "notes": ["Coaching includes assisting with establishing an endowment, updating "
                  "endowment bylaws, investments, implementing grant strategies, or the "
                  "creation of spending policies."],
    },

    # ================================================== COM — pipeline
    {
        "id": "com.discovery_retreats", "sheet": "COM", "theme": "pipeline",
        "title": "Discovery Retreats",
        "type": "timeseries", "rows": (5, 14), "owner": "AG",
        "series": [n("events", "Events", 1), n("participants", "Participants", 2)],
    },
    {
        "id": "com.discernment_committees", "sheet": "COM", "theme": "pipeline",
        "title": "Discernment Committees",
        "type": "timeseries", "rows": (18, 27), "noteCol": 3, "owner": "AG",
        "series": [n("local", "Local", 1), n("regional", "Regional", 2)],
        "caveats": [{"period": "2019", "type": "methodology",
                     "text": "Committees were counted as entirely regional through 2019 "
                             "and shift to mostly local from 2020 — a change in "
                             "structure, not a collapse in one and a surge in the other."}],
    },
    {
        "id": "com.discernment_trainings", "sheet": "COM", "theme": "pipeline",
        "title": "Discernment Committee Trainings",
        "type": "timeseries", "rows": (31, 40), "noteCol": 3, "owner": "AG",
        "series": [n("trainings", "Trainings", 1), n("trained", "Total Trained", 2)],
    },
    {
        "id": "com.new_aspirants", "sheet": "COM", "theme": "pipeline",
        "title": "New Aspirants",
        "subtitle": "total for application period ending in May of year reported",
        "type": "timeseries", "rows": (44, 51), "owner": "AG",
        "series": [n("total", "Aspirants", 1)],
    },
    {
        "id": "com.deacon_aspirants_bilingual", "sheet": "COM", "theme": "pipeline",
        "title": "Deacon Aspirants in Bilingual Congregations",
        "type": "timeseries", "rows": (55, 62), "noteCol": 2, "owner": "AG",
        "series": [n("total", "Aspirants", 1)],
    },
    {
        "id": "com.postulancy_granted", "sheet": "COM", "theme": "pipeline",
        "title": "Postulancy Applications Granted",
        "type": "timeseries", "rows": (66, 76), "owner": "AG",
        "series": [
            n("deacon", "Deacon", 1),
            n("bivo", "Priest (Bi-vo Track)", 2),
            n("seminary", "Priest (Seminary Track)", 3),
            n("canon10", "Canon 10", 4),
        ],
        "caveats": [{"period": "2025", "type": "definition",
                     "text": "Canon 10 is reported for 2025 only; earlier years have no "
                             "figure rather than a zero."}],
    },
    {
        "id": "com.postulancy_not_granted", "sheet": "COM", "theme": "pipeline",
        "title": "Postulancy Applications Not Granted",
        "type": "timeseries", "rows": (80, 90), "owner": "AG",
        "series": [
            n("deacon", "Deacon", 1, False),
            n("bivo", "Priest (Bi-vo Track)", 2, False),
            n("seminary", "Priest (Seminary Track)", 3, False),
        ],
    },
    {
        "id": "com.seminarians", "sheet": "COM", "theme": "pipeline",
        "title": "EDOT Seminarians",
        "subtitle": "all seminaries, not including Iona School",
        "type": "timeseries", "rows": (94, 104), "periodType": "schoolYear",
        "owner": "AG", "series": [n("enrolled", "Total Enrolled", 1)],
    },

    # ================================================== Other — pipeline
    {
        "id": "other.diocesan_council", "sheet": "Other", "theme": "pipeline",
        "title": "Diocesan Council Attendance",
        "type": "timeseries", "rows": (3, 14),
        "series": [
            n("clergy", "Clergy Delegates & Licensed", 1),
            n("lay", "Lay Delegates", 2),
            n("layalt", "Lay Alternates", 3),
            n("laypastoral", "Lay Pastoral Leaders", 4),
            n("visitors", "Visitors, Spouses, Other", 5),
            n("staff", "EDOT Staff & Officers", 6),
            n("youth", "Youth Delegates, Alt & Sponsors", 7),
            n("college", "College Delegates & Alt", 8),
            n("subtotal", "Subtotal", 9),
            n("volunteers", "Volunteers", 10),
            n("vendors_non", "Non-EDOT Vendors", 11),
            n("vendors_edot", "EDOT Vendors", 12),
            n("total", "Total", 13),
        ],
        "headline": "total",
        "caveats": [{"period": "2021", "type": "covid",
                     "text": "Held virtually; several categories were not counted."}],
    },
    {
        "id": "other.visitations", "sheet": "Other", "theme": "pipeline",
        "title": "Bishops' Visitations",
        "type": "timeseries", "rows": (19, 29), "owner": "KBD",
        "series": [
            n("confirmations", "Confirmations", 1),
            n("receptions", "Receptions", 2),
            n("reaffirmations", "Reaffirmations", 3),
            n("baptisms", "Adult Baptisms", 4),
        ],
        "headline": "confirmations",
        "caveats": [{"period": "2025", "type": "coverage",
                     "text": "Not yet reported in the workbook."}],
    },
    {
        "id": "other.canonical_transfers", "sheet": "Other", "theme": "pipeline",
        "title": "Clergy Canonical Transfers",
        "type": "timeseries", "rows": (34, 44), "owner": "MIL",
        "series": [n("in", "In", 1), n("out", "Out", 2, False)],
        "caveats": [{"period": "2022", "type": "methodology",
                     "text": "81 transfers in is far outside the normal 3–24 range. "
                             "Likely a bulk canonical action or a data error — verify "
                             "before using."}],
    },
    {
        "id": "other.clergy_transitions", "sheet": "Other", "theme": "pipeline",
        "title": "Clergy Transitions",
        "type": "timeseries", "rows": (49, 59),
        "series": [
            n("curates", "Curates Placed", 1),
            n("rectors", "Rectors / Priests-in-Charge Placed", 2),
            n("vicars", "Vicars / Bi-Vos / Planters Placed", 3),
        ],
    },

    # ============================================ Leadership — congleadership
    {
        "id": "leadership.asa_200plus", "sheet": "Leadership", "theme": "congleadership",
        "title": "Churches with ASA 200+",
        "subtitle": "based on parochial report numbers",
        "type": "timeseries", "rows": (3, 11), "noteCol": 10, "tier": "ASA 200+",
        "series": [
            n("total", "Total Churches", 1),
            n("transition", "In Transition", 2, None),
            pct("transition_pct", "% In Transition", 3, None),
            n("women", "Women Rectors", 4),
            pct("women_pct", "% Women Rectors", 5),
            n("poc", "POC Rectors", 6),
            pct("poc_pct", "% POC Rectors", 7),
            n("women_poc", "Women POC Rectors", 8),
            pct("women_poc_pct", "% Women POC Rectors", 9),
        ],
        "caveats": [{"period": "2022", "type": "methodology",
                     "text": "The denominator behind the Women and POC percentages "
                             "changes here. Through 2021 they are a share of filled "
                             "rectorships (total churches minus those in transition); "
                             "from 2022 they are a share of all churches in the tier. "
                             "That makes the earlier percentages read high: 2019's "
                             "15.4% POC is 4 of 26 filled posts, which on the current "
                             "basis is 4 of 33 — 12.1%. The rise to 20% in 2025 is "
                             "therefore larger than the line suggests. The counts "
                             "underneath are on one consistent basis; the percentages "
                             "are not."}],
    },
    {
        "id": "leadership.asa_200_400", "sheet": "Leadership", "theme": "congleadership",
        "title": "Churches with ASA 200–400",
        "subtitle": "based on parochial report numbers",
        "type": "timeseries", "rows": (14, 22), "tier": "ASA 200–400",
        "series": [
            n("total", "Total Churches", 1),
            n("transition", "In Transition", 2, None),
            pct("transition_pct", "% In Transition", 3, None),
            n("women", "Women Rectors", 4),
            pct("women_pct", "% Women Rectors", 5),
            n("poc", "POC Rectors", 6),
            pct("poc_pct", "% POC Rectors", 7),
            n("women_poc", "Women POC Rectors", 8),
            pct("women_poc_pct", "% Women POC Rectors", 9),
        ],
        "caveats": [{"period": "2021", "type": "methodology",
                     "text": "Same denominator change as the ASA 200+ block, one year "
                             "earlier in this tier: through 2020 the Women and POC "
                             "percentages are a share of filled rectorships, from 2021 "
                             "a share of all churches. Compare the counts across the "
                             "break, not the percentages."}],
    },
    {
        "id": "leadership.asa_400plus", "sheet": "Leadership", "theme": "congleadership",
        "title": "Churches with ASA 400+",
        "subtitle": "based on parochial report numbers",
        "type": "timeseries", "rows": (25, 33), "tier": "ASA 400+",
        "series": [
            n("total", "Total Churches", 1),
            n("transition", "In Transition", 2, None),
            pct("transition_pct", "% In Transition", 3, None),
            n("women", "Women Rectors", 4),
            pct("women_pct", "% Women Rectors", 5),
            n("poc", "POC Rectors", 6),
            pct("poc_pct", "% POC Rectors", 7),
            n("women_poc", "Women POC Rectors", 8),
            pct("women_poc_pct", "% Women POC Rectors", 9),
        ],
        "notes": ["With only 4–9 churches in this tier, a single appointment moves the "
                  "percentage by 10–25 points. Read the counts, not the percentages.",
                  "This tier and the ASA 200–400 tier add up to the ASA 200+ tier every "
                  "year — 200+ is the total, not a fourth group."],
        "caveats": [{"period": "2021", "type": "methodology",
                     "text": "The 2018 and 2019 percentages exclude churches in "
                             "transition from the denominator; from 2021 all churches "
                             "are counted. With so few churches in this tier the "
                             "difference is one post either way."}],
    },

    # ================================================== Formation
    {
        "id": "formation.youth_events", "sheet": "Formation", "theme": "formation",
        "title": "Youth Formation Events",
        "subtitle": "including Happening and other youth gatherings",
        "type": "timeseries", "rows": (3, 13),
        "series": [
            n("events", "Events", 1), n("youth", "Youth", 2), n("adults", "Adults", 3),
        ],
        "caveats": [{"period": None, "type": "covid",
                     "text": "Events ran 13–17 per year through 2019 and 4–7 since. "
                             "Participation per event is higher, but total reach has "
                             "not returned to pre-2020 levels."}],
    },
    {
        "id": "formation.leadership_dev", "sheet": "Formation", "theme": "formation",
        "title": "Christian Formation Leadership Development",
        "type": "timeseries", "rows": (17, 24),
        "series": [
            n("retreat", "Retreat/Summit", 1), n("sradult", "Sr. Adult", 2),
            n("youngadult", "Young Adult", 3), n("youthdel", "Youth Delegates", 4),
        ],
        "trackingStart": "2024",
        "caveats": [{"period": None, "type": "definition",
                     "text": "Tracking began in 2024. The zeros recorded for 2018–2023 "
                             "mean the measure did not exist, not that nothing "
                             "happened, and are shown as untracked."}],
    },
    {
        "id": "formation.licensing", "sheet": "Formation", "theme": "formation",
        "title": "Licensing and Micro-Certifications",
        "type": "timeseries", "rows": (28, 35),
        "series": [
            n("lem", "LEM", 1), n("lev", "LEV", 2), n("worship", "Worship", 3),
            n("preaching", "Preaching", 4), n("catechist", "Catechist", 5),
            n("evangelist", "Evangelist", 6),
        ],
        "trackingStart": "2025",
        "caveats": [{"period": None, "type": "definition",
                     "text": "Tracking began in 2025. The zeros recorded for 2018–2024 "
                             "mean the measure did not exist, so 2025 is a first "
                             "reading — not growth from zero."}],
    },
    {
        "id": "formation.online", "sheet": "Formation", "theme": "formation",
        "title": "Online Formation & Leadership Development",
        "type": "timeseries", "rows": (39, 46),
        "series": [
            n("micro", "Micro-Courses", 1), n("podcast", "Podcast", 2),
            n("forum", "Formation Forum", 3),
        ],
        "trackingStart": "2025",
        "caveats": [{"period": None, "type": "definition",
                     "text": "Tracking began in 2025. The zeros recorded for 2018–2024 "
                             "mean the measure did not exist, so 2025 is a first "
                             "reading — not growth from zero."}],
    },
    {
        "id": "formation.grants", "sheet": "Formation", "theme": "formation",
        "title": "Formation Micro-Grants & Continuing Education",
        "type": "timeseries", "rows": (50, 57),
        "series": [
            n("grants", "Grants", 1), n("lay", "Continuing Ed — Lay", 2),
            n("clergy", "Continuing Ed — Clergy", 3),
        ],
        "trackingStart": "2025",
        "caveats": [{"period": None, "type": "definition",
                     "text": "Tracking began in 2025. The zeros recorded for 2018–2024 "
                             "mean the measure did not exist, so 2025 is a first "
                             "reading — not growth from zero."}],
    },

    # ================================================== Wellness
    {
        "id": "wellness.safeguarding_all", "sheet": "Wellness", "theme": "formation",
        "title": "Safeguarding — All Participants",
        "type": "stacked",
        "series": [
            {"id": "certified", "label": "Individuals who completed all Safeguarding "
             "requirements", "unit": "count", "format": "integer",
             "higherIsBetter": True, "rows": (4, 5), "col": 1},
            {"id": "attendance", "label": "Attendance in all training sessions",
             "unit": "count", "format": "integer", "higherIsBetter": True,
             "rows": (8, 16), "col": 1},
        ],
        "caveats": [{"period": "2024", "type": "definition",
                     "text": "The measure changed. Through 2023 the workbook counted "
                             "training-session attendance; from 2024 it counts distinct "
                             "individuals who completed all requirements. The two are "
                             "plotted as separate series and must not be compared "
                             "directly."}],
        "notes": ["2024 was the first full year that Praesidium Academy courses were "
                  "required for everyone going through Safeguarding under the new "
                  "Universal Engagement Training process."],
    },
    {
        "id": "wellness.safeguarding_clergy", "sheet": "Wellness", "theme": "formation",
        "title": "Safeguarding — Clergy",
        "type": "stacked",
        "series": [
            {"id": "certified", "label": "Clergy who completed all Safeguarding "
             "requirements", "unit": "count", "format": "integer",
             "higherIsBetter": True, "rows": (19, 20), "col": 1},
            {"id": "attendance", "label": "Clergy attendance in all training sessions",
             "unit": "count", "format": "integer", "higherIsBetter": True,
             "rows": (23, 31), "col": 1},
        ],
        "caveats": [{"period": "2024", "type": "definition",
                     "text": "Same definitional change as the all-participants view: "
                             "attendance through 2023, distinct individuals from 2024."}],
    },
    {
        "id": "wellness.praesidium_all", "sheet": "Wellness", "theme": "formation",
        "title": "Praesidium Academy — All Participants",
        "type": "stacked",
        "series": [
            {"id": "individuals", "label": "Individuals who took at least one course",
             "unit": "count", "format": "integer", "higherIsBetter": True,
             "rows": (35, 36), "col": 1},
            {"id": "attendance", "label": "Attendance in online training sessions",
             "unit": "count", "format": "integer", "higherIsBetter": True,
             "rows": (39, 47), "col": 1},
        ],
        "caveats": [{"period": "2024", "type": "definition",
                     "text": "Attendance through 2023; distinct individuals from 2024, "
                             "when Praesidium courses became universally required."}],
    },
    {
        "id": "wellness.praesidium_clergy", "sheet": "Wellness", "theme": "formation",
        "title": "Praesidium Academy — Clergy",
        "type": "stacked",
        "series": [
            {"id": "individuals", "label": "Clergy who took at least one course",
             "unit": "count", "format": "integer", "higherIsBetter": True,
             "rows": (50, 51), "col": 1},
            {"id": "attendance", "label": "Clergy attendance in online training sessions",
             "unit": "count", "format": "integer", "higherIsBetter": True,
             "rows": (54, 62), "col": 1},
        ],
        "caveats": [{"period": "2024", "type": "definition",
                     "text": "Attendance through 2023; distinct individuals from 2024."}],
    },
    {
        "id": "wellness.antiracism", "sheet": "Wellness", "theme": "formation",
        "title": "Lighting the Path to Antiracism",
        "subtitle": "racial work and difficult conversations",
        "type": "timeseries", "rows": (66, 76),
        "series": [
            n("events", "Events", 1), n("lay", "Lay", 2),
            n("clergy", "Clergy", 3), n("total", "Total", 4),
        ],
        "headline": "total",
        "caveats": [{"period": "2017", "type": "methodology",
                     "text": "The Lay and Clergy columns look transposed in 2017 "
                             "(32 lay / 420 clergy) against every neighbouring year. "
                             "Verify before citing."}],
    },

    # ================================================== Diversity
    {
        "id": "diversity.boards_gender", "sheet": "Diversity", "theme": "diversity",
        "title": "Boards — Gender", "population": "Boards", "dimension": "gender",
        "type": "timeseries", "rows": (3, 14),
        "series": [pct("men", "Men", 1), pct("women", "Women", 2)],
        "notes": ["2021 and 2025 sum to 99.5% and 99.6% rather than 100%. Every other "
                  "year is exact, so a small number of board members are unaccounted "
                  "for in those two."],
    },
    {
        "id": "diversity.boards_ethnicity", "sheet": "Diversity", "theme": "diversity",
        "title": "Boards — Ethnicity", "population": "Boards", "dimension": "ethnicity",
        "type": "timeseries", "rows": (17, 28),
        "series": [pct("asian", "Asian", 1), pct("black", "Black", 2),
                   pct("latino", "Latino", 3), pct("white", "White", 4, None)],
        "notes": ["Four categories only — the workbook records no 'other' or "
                  "'undisclosed' bucket. 2021 sums to 99.5% rather than 100%."],
    },
    {
        "id": "diversity.clergy_gender", "sheet": "Diversity", "theme": "diversity",
        "title": "EDOT Clergy — Gender", "population": "Clergy", "dimension": "gender",
        "subtitle": "canonically resident",
        "type": "timeseries", "rows": (32, 38),
        "series": [pct("men", "Men", 1), pct("women", "Women", 2)],
        "caveats": [{"period": "2026", "type": "methodology",
                     "text": "Women jump from 32.2% to 40.4% in a single year, after "
                             "six years between 31% and 35%. The percentages for 2020–"
                             "2025 resolve to a roster of roughly 440–590 clergy, while "
                             "2026's resolve to a much smaller one, so this looks like a "
                             "change in who is counted rather than 50 new women "
                             "clergy. Confirm the roster with the Registrar before "
                             "using it."}],
    },
    {
        "id": "diversity.clergy_ethnicity", "sheet": "Diversity", "theme": "diversity",
        "title": "EDOT Clergy — Ethnicity", "population": "Clergy",
        "dimension": "ethnicity", "subtitle": "canonically resident",
        "type": "timeseries", "rows": (41, 47),
        "series": [pct("asian", "Asian", 1), pct("black", "Black", 2),
                   pct("latino", "Latino", 3), pct("poc", "Total POC", 4),
                   pct("white", "White", 5, None)],
        "caveats": [{"period": "2026", "type": "methodology",
                     "text": "Total POC clergy more than doubles, 7.2% to 15.3%, after "
                             "six years between 6.8% and 10.0%. This is the largest "
                             "single-year move anywhere in the Diversity tab and it "
                             "coincides with the same break in the gender block, which "
                             "points to a change in the population being counted. It is "
                             "the figure most likely to be quoted from this dashboard — "
                             "verify it before it is."}],
    },
    {
        "id": "diversity.staff_gender", "sheet": "Diversity", "theme": "diversity",
        "title": "EDOT Staff — Gender", "population": "Staff", "dimension": "gender",
        "type": "timeseries", "rows": (51, 57),
        "series": [pct("men", "Men", 1), pct("women", "Women", 2)],
    },
    {
        "id": "diversity.staff_ethnicity", "sheet": "Diversity", "theme": "diversity",
        "title": "EDOT Staff — Ethnicity", "population": "Staff",
        "dimension": "ethnicity",
        "type": "timeseries", "rows": (60, 66),
        "series": [pct("asian", "Asian", 1), pct("black", "Black", 2),
                   pct("latino", "Latino", 3), pct("white", "White", 4, None)],
    },
    {
        "id": "diversity.supervisors_gender", "sheet": "Diversity", "theme": "diversity",
        "title": "EDOT Supervisors — Gender", "population": "Supervisors",
        "dimension": "gender",
        "type": "timeseries", "rows": (70, 76),
        "series": [pct("men", "Men", 1), pct("women", "Women", 2)],
    },
    {
        "id": "diversity.supervisors_ethnicity", "sheet": "Diversity",
        "theme": "diversity", "title": "EDOT Supervisors — Ethnicity",
        "population": "Supervisors", "dimension": "ethnicity",
        "type": "timeseries", "rows": (79, 85),
        "series": [pct("asian", "Asian", 1), pct("black", "Black", 2),
                   pct("latino", "Latino", 3), pct("white", "White", 4, None)],
    },
    {
        "id": "diversity.cmv_gender", "sheet": "Diversity", "theme": "diversity",
        "title": "CMV Team — Gender", "population": "CMV Team", "dimension": "gender",
        "type": "timeseries", "rows": (89, 95),
        "series": [pct("men", "Men", 1), pct("women", "Women", 2)],
    },
    {
        "id": "diversity.cmv_ethnicity", "sheet": "Diversity", "theme": "diversity",
        "title": "CMV Team — Ethnicity", "population": "CMV Team",
        "dimension": "ethnicity",
        "type": "timeseries", "rows": (98, 104),
        "series": [pct("asian", "Asian", 1), pct("black", "Black", 2),
                   pct("latino", "Latino", 3), pct("white", "White", 4, None)],
        "notes": ["The CMV team is small (7–9 people), so one person is 11–14 "
                  "percentage points."],
    },

    # ================================================== Comms
    {
        "id": "comms.diolog", "sheet": "Comms", "theme": "comms",
        "title": "Diolog E-News", "type": "timeseries", "rows": (4, 14),
        "periodType": "custom", "owner": "TL",
        "series": [n("recipients", "Recipients", 1),
                   pct("openrate", "Open Rate", 2)],
        "caveats": [{"period": "2025", "type": "methodology",
                     "text": "Recipients jumped from 12,694 to 31,794 while the open "
                             "rate fell from 38% to 12%. Consistent with a large list "
                             "import rather than audience growth — engaged readership "
                             "is roughly flat (≈4,800 → ≈3,800)."}],
    },
    {
        "id": "comms.spanish", "sheet": "Comms", "theme": "comms",
        "title": "Spanish E-News", "type": "timeseries", "rows": (17, 25),
        "periodType": "custom", "owner": "TL",
        "series": [n("recipients", "Recipients", 1), pct("openrate", "Open Rate", 2)],
        "caveats": [{"period": "2025", "type": "coverage",
                     "text": "Recipients fell from 5,585 to 2,153 — a list change worth "
                             "confirming."}],
    },
    {
        "id": "comms.ooo", "sheet": "Comms", "theme": "comms",
        "title": "OOO Newsletter", "type": "timeseries", "rows": (28, 37),
        "periodType": "custom", "owner": "TL",
        "series": [n("recipients", "Recipients", 1), pct("openrate", "Open Rate", 2)],
    },
    {
        "id": "comms.texas_episcopalian", "sheet": "Comms", "theme": "comms",
        "title": "The Texas Episcopalian", "type": "timeseries", "rows": (40, 49),
        "periodType": "custom", "owner": "TL",
        "series": [n("mailed", "No. Mailed", 1),
                   n("online", "Online Subscribers", 2)],
    },
    {
        "id": "comms.facebook_en", "sheet": "Comms", "theme": "comms",
        "title": "Facebook (English)", "type": "timeseries", "rows": (52, 62),
        "periodType": "custom", "owner": "TL",
        "series": [n("followers", "Followers", 1)],
    },
    {
        "id": "comms.facebook_es", "sheet": "Comms", "theme": "comms",
        "title": "Facebook (Spanish)", "type": "timeseries", "rows": (65, 73),
        "periodType": "custom", "owner": "TL",
        "series": [n("followers", "Followers", 1)],
    },
    {
        "id": "comms.epicenter", "sheet": "Comms", "theme": "comms",
        "title": "epicenter.org", "type": "timeseries", "rows": (76, 84),
        "periodType": "custom", "owner": "TL",
        "series": [n("views", "Unique Page Views", 1)],
        "notes": ["Periods before 2021 run August–July or similar, not calendar years."],
    },

    # ================================================== Social $
    {
        "id": "social.impact", "sheet": "Social $", "theme": "finance",
        "title": "Social Impact of Diocesan Entities",
        "subtitle": "dollars deployed into communities",
        "type": "timeseries", "rows": (3, 11),
        "series": [
            usd("ehf", "EHF", 1), usd("quin", "Quin", 2), usd("eft", "EFT", 3),
            usd("gcf", "GCF", 4), usd("edot", "EDOT", 5), usd("pecc", "PECC", 6),
            usd("total", "TOTAL", 7),
        ],
        "headline": "total",
    },

    # ================================================== Disaster
    {
        "id": "disaster.response", "sheet": "Disaster", "theme": "support",
        "title": "Disaster Response & Preparedness",
        "subtitle": "storm recovery 2018 – 2024/Q2; preparedness 2022/Q3 – 2024/Q2",
        "type": "irregular", "owner": "SS",
        "labelCol": 1,
        # (column, period label) — the canonical annual columns only. The
        # grant-split and "hide when printing" columns are deliberately dropped.
        "periods": [
            (7, "2018"), (10, "2019"), (11, "2020"),
            (14, "12 mos. ending 2021-06-30"),
            (17, "12 mos. ending 2022-06-30"),
            (18, "12 mos. ending 2023-06-30"),
            (19, "12 mos. ending 2024-06-30"),
        ],
        "metricRows": [
            (7, "Partners outside EDOT", "count"),
            (8, "Congregations engaged in storm response", "count"),
            (17, "Vulnerable community members served", "count"),
            (18, "Type 1: Home repairs / rebuilds", "count"),
            (19, "Type 2: Families assessed for recovery needs", "count"),
            (20, "Type 3a: Volunteers deployed", "count"),
            (21, "Type 3b: Volunteer hours", "count"),
            (22, "Type 4: Volunteers housed", "count"),
            (23, "Type 5: Behavioral health services provided", "count"),
            (24, "Type 6: “Home for the Holidays” sponsorships", "count"),
            (25, "Type 7: Move-in furnishings and/or appliances", "count"),
            (26, "Type 8: Standard unmet needs (families)", "count"),
            (27, "Type 9: Resource fair beneficiaries", "count"),
            (28, "Type 10: Other than home repair", "count"),
            (29, "Type 11: Feeding / food distribution", "count"),
            (30, "Other states sending volunteers", "count"),
            (31, "EDOT/ERD grants received", "usd"),
            (32, "EDOT/ERD funding carried over from prior term", "usd"),
            (33, "EDOT/ERD funding disbursed", "usd"),
            (34, "Outside grants secured by congregations", "usd"),
            (35, "Additional storms receiving recovery funding", "text"),
        ],
        "noteRows": [37, 38, 39, 41, 43, 45],
        "caveats": [
            {"period": "2025", "type": "coverage",
             "text": "No disaster response support was given in 2025 other than a "
                     "curate cohort disaster preparedness workshop. The table is "
                     "carried over from last year's submission."},
            {"period": None, "type": "definition",
             "text": "The program shifted from storm recovery to preparedness in 2022, "
                     "and staffing fell from 2 FTE to 0.25 FTE. Declining service "
                     "counts reflect that deliberate change, not a failure to deliver."},
            {"period": None, "type": "methodology",
             "text": "Types 7, 8 and 11 were progressively rolled into Type 10, so "
                     "those rows end rather than fall to zero."},
        ],
    },
]
