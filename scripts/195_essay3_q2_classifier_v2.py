"""
ESSAY 3 QUERY 2 — PART C, REVISION 2: ITEM 5.02 DEPARTURE CLASSIFIER v2 (NEW; deterministic rules, no ML)
==========================================================================================================
v2 of scripts/188 (v1 frozen in commit d39bc6d, blob af2c97c). Revised after round-1 validation against
Claude-coded reference codes (Tim did not hand-code; see VALIDATION_REFERENCE_CODES_R1_README.txt).
Changes, all general rules (Tim's instruction, 2026-09-11):
  - departure stem "retir(e|es|ed|ement|ing)" (v1 never matched "retiring");
  - departures from a PRIOR employer ("forfeited upon his departure", "previous/former employer") ignored;
  - titles kept via "continue(s) in his/her role/position as <title>" are not the title being left;
    "no longer serve the Company as <title>" binds to that title;
  - new departure phrasings: "no longer be an (executive) officer", "decline to stand/seek re-election",
    "does not wish/intend to seek re-election", "will be leaving", "has left his position",
    "<Name>'s employment ... will terminate";
  - ONE narrow implied-departure rule (IMPLIED_RULE): "successor to / in succession to <Name> [as <title>]"
    with a covered officer title; tagged verb='implied_succession' so round-2 false positives can be counted;
  - rulings: (1) restated mentions ("Previously,", "had resigned", "previously held by", "as previously
    announced/disclosed") are coded as departures tagged restated=1; outcomes count each departure once per
    person within parent CIK, dated to its earliest disclosing filing (c2_departure_events.csv); the
    restatement-dated filing-level outcomes are kept as the rs_* sensitivity; (2) pay-agreement-only
    departures count; (3) vacancy mentions ("vacancy created by the retirement of X") count for DIRECTOR
    departures only; (4) pre-announced uses every date in a departure sentence, including effective dates.
Outputs use the c2_ prefix (v1's c_ outputs are left intact).
Input : outputs/essay3_q2/b_scope_filings.csv (+ the documents it names under
        Data/edgar/item5_02_text/), b_scope_events.csv, b_event_filing_pairs.csv.
Rules (all in this file; nothing learned):
  C1 parse   - de-HTML; isolate the Item 5.02 section (from an "Item 5.02" header to the
               next Item x.xx HEADER, i.e. an item number followed by a capitalised caption,
               or SIGNATURE); strip the 5.02 caption wherever it appears; record sub-item
               labels (a)-(f) where the filing prints them.
  C2 code    - sentence level. A DEPARTURE mention needs a departure verb and must not be
               (i) conditional contract language, (ii) biography, (iii) a reference to an
               earlier departure ("Previously, ...", "had resigned"), unless the sentence
               also carries a current-departure marker (notified, will retire, effective
               <date>, resigned, ...). Retirement-plan nouns are masked first.
               Role class = the title nearest the verb ("resign AS/FROM <title>" binds
               first); priority CEO > CFO > COO > PAO > president > other exec > director.
               Committee-only moves are not departures. "succeed(s)/replacing X as <officer
               title>" is a departure of X. Person = nearest name (subject first), pronouns
               carry the last named person, "Mr. Surname" expands to the full name.
               Appointment / election / compensation are coded when no departure is.
               Dates: filing date (outcome date), notice date, effective date.
               Context flags on the departure sentences and the two that follow.
  C3 outcome - per event and anchor (reported_date primary, breach_date sensitivity):
               exec/ceo/director departure and any-5.02 at 30/90/180d in (t0, t0+w];
               days to first exec departure; placebo window (t0-180d, t0]; baseline count
               in [t0-730d, t0-181d].
Outputs: outputs/essay3_q2/c_filing_codes.csv, c_person_rows.csv, c_sections.csv,
         c_outcomes_events.csv, c_crosswalk.csv, 188_classifier.log
`--dev` prints the development set only (dev_ids.csv + the 28 T-Mobile documents read in
Query 1 that are not calibration documents). Validation and calibration codes are never printed.
"""

import re
import sys
import html
import hashlib
from datetime import timedelta
from pathlib import Path
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/essay3_q2')
L = []


def log(m=''):
    print(m, flush=True)
    L.append(str(m))


MONTHS = ('January|February|March|April|May|June|July|August|September|October|'
          'November|December')
DATE_RE = re.compile(rf'\b({MONTHS})\.?\s+(\d{{1,2}}),?\s+(\d{{4}})')


def parse_date(m):
    try:
        return pd.Timestamp(f'{m.group(1)} {m.group(2)} {m.group(3)}')
    except Exception:
        return None


# ------------------------------------------------------------------ C1 parse
def to_text(raw):
    s = raw.decode('utf-8', errors='replace') if isinstance(raw, bytes) else raw
    s = re.sub(r'(?is)<(script|style|head)\b.*?</\1\s*>', ' ', s)
    s = re.sub(r'(?i)<br\s*/?>|</(p|div|tr|li|h\d|table)\s*>', '\n', s)
    s = re.sub(r'(?s)<[^>]+>', ' ', s)
    s = html.unescape(s).replace('\xa0', ' ').replace('\u200b', '').replace('\ufeff', '')
    s = re.sub(r'[ \t\r\f\v]+', ' ', s)
    s = re.sub(r' *\n[ \n]*', '\n', s)
    return s.strip()


HDR = re.compile(r'(?i:item)\s*5\s*\.\s*02')
ITEM_BOUND = re.compile(r'\b(?i:item)\s*(\d{1,2})\s*\.\s*(\d{2})\b\s*\.?\s*[-–—:.]?\s*(?=[A-Z(])')
SIG = re.compile(r'\bSIGNATURES?\b|\bEXHIBIT INDEX\b|(?i:\bforward[- ]looking\s+statements\b)')
CAP = re.compile(
    r'(?i)(?:item\s*5\s*\.\s*0[12]\s*\.?\s*[-–—:]?\s*)?(?:(?:departure|resignation)s?\s+of\s+directors?\s+or\s+'
    r'(?:certain|principal)\s+officers?\s*[;,]?|(?:departure|resignation)s?\s+of\s+directors?\s*[;,]\s*(?=election))'
    r'\s*(?:election\s+of\s+directors?\s*[;,]?\s*)?'
    r'(?:appointment\s+of\s+(?:certain|principal)\s+officers?\s*[;,]?\s*)?(?:and\s+)?'
    r'(?:compensatory\s+arrangements?\s+(?:of|with)\s+certain\s+officers?\s*\.?)?')
LABEL = re.compile(r'(?:^|(?<=[\s.:;—–-]))\(([a-f])\)(?=\s*(?:and\s*\([a-f]\)\s*)?[A-Z(“"])')


CAP_START = re.compile(r'(?i)(?:departure|resignation)s?\s+of\s+directors?\s*(?:or\s+(?:certain|principal)\s+'
                       r'officers?\s*)?[;,]\s*election')


def section_502(t):
    best = ''
    starts = list(HDR.finditer(t)) or list(CAP_START.finditer(t))  # fallback: caption without a 5.02 header
    for m in starts:
        rest = t[m.end():]
        end = len(rest)
        for bm in ITEM_BOUND.finditer(rest):
            if (bm.group(1).lstrip('0') or '0', bm.group(2)) != ('5', '02'):
                end = bm.start()
                break
        sm = SIG.search(rest)
        if sm and sm.start() < end:
            end = sm.start()
        seg = t[m.start(): m.end() + end]
        if len(seg) > len(best):
            best = seg
    return best


def strip_caption(sec):
    s = CAP.sub(' ', sec)
    s = re.sub(r'^(?i:item)\s*5\s*\.\s*02\s*[.:\-–—]?', ' ', s.strip())
    return re.sub(r'[ \n]+', ' ', s).strip()


ABBR = re.compile(r'\b(Mr|Mrs|Ms|Messrs|Dr|Jr|Sr|Inc|Corp|Co|Ltd|No|St|Esq|vs|approx|Jan|Feb|Mar|Apr|'
                  r'Aug|Sept|Sep|Oct|Nov|Dec|Ph\.D|L\.P|N\.A)\.')
INIT = re.compile(r'\b([A-Z])\.(?=\s?[A-Z])')


def sentences(s):
    s = ABBR.sub(lambda m: m.group(1) + '<D>', s)
    s = INIT.sub(r'\1<D>', s)
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z(“"•●\d])', s)
    return [p.replace('<D>', '.').strip() for p in parts if len(p.strip()) > 3]


# ------------------------------------------------------------------ C2 rules
RET_PLAN = re.compile(r'(?i)(?:supplemental\s+)?(?:executive\s+)?retirement\s+(?:plan|savings|benefit|program|'
                      r'account|income|eligib|contribution|arrangement)s?|401\s*\(k\)|'
                      r'(?:early|normal)\s+retirement\s+(?:eligib|age|date\s+under)')
DEP = re.compile(
    r'(?i)\b(resign(?:s|ed|ing|ation|ations)?|retir(?:e|es|ed|ement|ing)|step(?:s|ped|ping)?\s+down|'
    r'depart(?:s|ed|ing|ure)?|terminat(?:e|es|ed|ing|ion)\s+(?:of\s+)?(?:his|her|their|the)?\s*'
    r'(?:employment|service)|(?:his|her|their|[a-z][\w\-]+(?:’|\')s)\s+employment\s+(?:with\s+(?:the\s+)?[\w\-.&]+\s+)?'
    r'(?:thereunder\s+)?(?:will\s+)?'
    r'(?:be\s+)?(?:automatically\s+)?(?:terminat\w+|end\w*|cease\w*)|(?:was|were|has\s+been|have\s+been)\s+'
    r'terminated\s+(?:as|from|without|for|by)|will\s+(?:be\s+)?leav(?:e|ing)|(?:has\s+)?left\s+the\s+(?:company|corporation|'
    r'bank|firm)|cease[sd]?\s+(?:to\s+)?(?:serve|serving|be\s+employed|be\s+an?\s+)|no\s+longer\s+'
    r'(?:serve|be\s+(?:employed|serving))|not\s+(?:to\s+)?(?:stand|seek|be\s+nominated|run)\s+for\s+'
    r're-?election|(?:decided|elected|determined|chose)\s+not\s+to\s+(?:stand|seek|run)|passed\s+away|'
    r'\bdied\b|death\s+of|separat(?:e|ed|ion)\s+from|succeeded\s+by|removed\s+(?:as|from)|'
    r'transition(?:ed|ing)?\s+(?:out\s+of|from)\s+(?:his|her|the)\s+(?:role|position)|will\s+not\s+return|'
    r'(?:decision|decided|intention|intends)\s+to\s+leave|leave\s+the\s+(?:company|corporation|bank|firm)|'
    r'no\s+longer\s+(?:be\s+)?(?:an?\s+)?(?:on|part\s+of|a\s+member\s+of)\s+(?:the\s+)?(?:\w+\W?s\s+)?'
    r'executive\s+(?:team|leadership|officers?)|no\s+longer\s+be\s+an?\s+(?:executive\s+)?officer|'
    r'(?:has|have|had)\s+left\s+(?:his|her|their)\s+(?:positions?|roles?|posts?)|'
    r'(?:decline[sd]?|declining)\s+to\s+(?:stand|seek|run)\s+for\s+re-?election|'
    r'(?:does|do|did)\s+not\s+(?:wish|intend|plan)\s+to\s+(?:seek|stand\s+for|run\s+for)\s+re-?election)')
STRONG = re.compile(
    rf'(?i)\b(notified|informed|advised|tendered|submitted\s+(?:his|her|a)\s+(?:letter\s+of\s+)?resignation|'
    rf'announced|will\s+(?:retire|resign|step\s+down|depart|leave|cease|no\s+longer)|has\s+(?:decided|elected|'
    rf'determined|agreed)\s+to|(?:decided|determined|agreed|elected)\s+(?:that|to)|effective\s+(?:as\s+of\s+|'
    rf'on\s+)?(?:{MONTHS}|immediately|the\s+close|today)|stepped\s+down|resigned|retired|terminated|departed|'
    rf'last\s+day|separation\s+date|retirement\s+date|'
    rf'retir(?:e|es|ed|ement|ing)\s+(?:on|effective|as\s+of|from)\s+(?:or\s+about\s+)?(?:{MONTHS}|his|her|the)|'
    rf'is\s+retiring|will\s+be\s+leaving|has\s+left|no\s+longer\s+be)')
# HARD conditional markers: contract / hypothetical language. They block a departure unless the
# sentence also states an explicit effective calendar date (EFF_DATE).
HARD = re.compile(
    r'(?i)\b(if|unless|in\s+the\s+event|in\s+the\s+case\s+of|may\s+(?:be\s+)?(?:resign|retire|terminat|leave)\w*|'
    r'shall|should|could|would|qualifying\s+(?:termination|retirement)|good\s+reason|for\s+any\s+reason|'
    r'non-renewal|retirement[- ]eligib\w*|eligible\s+(?:to|for)\s+(?:retire|retirement)|proposed\s+retirement|'
    r'option\s+(?:upon|to)\s+[^.]{0,40}retire)\b')
EFF_DATE = re.compile(rf'(?i)effective\s+(?:as\s+of\s+|on\s+)?(?:{MONTHS})\.?\s+\d')
# SOFT conditional markers: block unless a current-departure marker (STRONG) is present.
CONDITIONAL = re.compile(
    r'(?i)\b(in\s+the\s+event|if\s+(?:he|she|mr\.|ms\.|mrs\.|dr\.|the\s+executive|his|her|such|any|the\s+company|'
    r'the\s+executive\W?s)|upon\s+(?:(?:a|any|his|her|such|the\s+executive\W?s)\s+)?(?:qualifying\s+)?'
    r'(?:termination|resignation|retirement|death|disability)|upon\s+(?:qualifying\s+)?(?:termination|separation)\s+of\s+'
    r'(?:employment|service)|(?:following|after|at)\s+(?:a\s+|any\s+)?(?:termination|separation)\s+of\s+employment|'
    r'upon\s+(?:mr|ms|mrs|dr)\.\s+[\w\-]+\W?s\s+(?:resignation|retirement|departure)|contingent|'
    r'for\s+good\s+reason|without\s+cause\s+or|'
    r'with\s+or\s+without\s+cause|would\s+be\s+entitled|in\s+connection\s+with\s+(?:a|any)\s+(?:qualifying\s+)?'
    r'termination|change\s+(?:in|of)\s+control|terminated\s+by\s+the\s+company\s+without)')
BIO = re.compile(
    r'(?i)\b(age\s+\d{2}|has\s+served|previously\s+served|served\s+(?:as|on|in)|prior\s+to\s+(?:joining|his|her|'
    r'that)|from\s+(?:19|20)\d{2}\s+(?:to|until|through)|since\s+(?:19|20)\d{2}|began\s+(?:his|her)\s+career|'
    r'holds?\s+(?:a|an)\s+(?:bachelor|master|j\.?d|b\.?a|b\.?s|m\.?b\.?a)|graduated|received\s+(?:a|an|his|her)\s+'
    r'(?:bachelor|master|degree))')
PRIOR_REF = re.compile(r'(?i)^(?:previously|prior\s+to\s+this)\b|\bhad\s+(?:previously\s+)?(?:resigned|retired|'
                       r'departed|stepped\s+down|stated)|previously\s+held\s+by')
VACANCY = re.compile(r'(?i)vacanc(?:y|ies)\s+(?:created|resulting|caused|arising)\s+(?:by|from)')
PRIOR_EMP = re.compile(r'(?i)(?:prior|previous|former)\s+employer|forfeit\w*\s+(?:upon|in\s+connection\s+with|as\s+a\s+'
                       r'result\s+of)\s+(?:his|her|their)\s+departure')
IMPLIED_RULE = True
IMPLIED = re.compile(r'\b(?i:successor\s+to|in\s+succession\s+to)\s+(?P<pred>(?:(?:Mr|Ms|Mrs|Dr)\.\s+)?'
                     r'[A-Z][\w\'’\-.]+(?:\s+[A-Z][\w\'’\-.]+){0,3})(?:,?\s+as\s+(?P<title>[^,.;]{3,90}))?')
SUCC = re.compile(r'\b(?i:succeed(?:s|ing)?|replac(?:e|es|ing))\s+(?P<pred>(?:(?:Mr|Ms|Mrs|Dr)\.\s+)?'
                  r'[A-Z][\w\'’\-.]+(?:\s+[A-Z][\w\'’\-.]+){0,3})(?:,?\s+as\s+(?P<title>[^,.;]{3,90}))?')
APPOINT = re.compile(r'(?i)\b(appoint(?:ed|s|ment)?|named(?!\s+executive)|promot(?:ed|ion)|hired|'
                     r'will\s+(?:join|become|serve\s+as)|to\s+serve\s+as|designated)\b')
ELECT = re.compile(r'(?i)\b(elected|appointed|named)\b.{0,100}?\b(director|board)\b|\b(increase[sd]?|expand(?:ed)?)'
                   r'\s+(?:the\s+)?(?:size\s+of\s+the\s+)?board')
COMP = re.compile(r'(?i)\b(compensat\w*|salary|bonus|equity\s+award|restricted\s+stock|stock\s+options?|'
                  r'performance[- ]based|RSUs?|PRSUs?|incentive|severance|retention|employment\s+agreement|'
                  r'letter\s+agreement|term\s+sheet|award|grant(?:ed)?)\b')
TITLES = [
    ('CEO', r'chief\s+executive\s+officer|\bc\.?e\.?o\b|principal\s+executive\s+officer'),
    ('CFO', r'chief\s+financial\s+officer|\bc\.?f\.?o\b|principal\s+financial\s+officer'),
    ('COO', r'chief\s+operating\s+officer|\bc\.?o\.?o\b|principal\s+operating\s+officer'),
    ('PAO', r'principal\s+accounting\s+officer|chief\s+accounting\s+officer|\bcorporate\s+controller\b|'
            r'\bcontroller\b|\bcomptroller\b'),
    ('president', r'\bpresident\b'),
    ('other_exec', r'executive\s+vice\s+president|senior\s+vice\s+president|\bvice\s+president\b|group\s+president|'
                   r'chief\s+[a-z&]+(?:\s+[a-z&]+){0,3}\s+officer|general\s+counsel|named\s+executive\s+officer|'
                   r'executive\s+officer|\bofficer\b|executive\s+chair(?:man|woman|person)?|'
                   r'vice\s+chair(?:man|woman|person)?|\btreasurer\b|\bsecretary\b'),
    ('director', r'\bdirectors?\b|board\s+of\s+directors|\bboard\b|\btrustees?\b|non-executive\s+chair'),
]
TITLE_RE = [(c, re.compile(p, re.I)) for c, p in TITLES]
PRIO = {c: i for i, (c, _) in enumerate(TITLES)}
EXEC_CLASSES = {'CEO', 'CFO', 'COO', 'PAO', 'president', 'other_exec'}
BIND = re.compile(r'(?i)^\s*(?:(?:his|her|their)\s+(?:positions?|roles?|duties)\s+)?'
                  r'(?:(?:the\s+)?(?:company|corporation|bank|registrant|firm)\s+)?(?:as|from)\s+(?:the\s+)?'
                  r'(?:\w+\W?s\s+)?(?:company\W?s\s+)?')

NAME_STOP = set('''Company Board Directors Director Chief Executive Officer Financial Operating Vice President
Senior Committee Compensation Audit Annual Meeting Stockholders Shareholders Item Section Agreement Plan Exhibit
Current Report Form Securities Exchange Commission Inc Corporation Corp LLC LP Ltd The On In As At For From To
Effective Following Pursuant Upon Under During After Before With This That Such Registrant Bank Trust Group
Holdings Partners Capital Global International Services Communications Mobile Wireless Telekom Deutsche SoftBank
United States Nominating Governance Chairman General Counsel Secretary Treasurer Accounting Principal Officers
Employment Letter Release Separation Retirement Incentive Omnibus Equity Stock Restricted Performance Units
Mr Ms Mrs Dr Messrs New York Nasdaq NYSE Class Term Sheet Amended Restated Second First Third Chair Interim
Executives Human Resources Technology Strategy Development Legal Operations Corporate Business Transaction
Merger Closing Our We He She His Her Their It Its Arrangements Compensatory Date Grant Jurisdiction Other
Policy Hedging Advisor Strategic Hewlett Packard Enterprise Original Filing Report Effective Transition Consulting
Services Change Control Severance Plan Director Directors Election Appointment Resignation Departure Award
Awards Options Shares Common Special Annual Long Short Incentive Program Committee Subcommittee Section
Name Position Number Air Lines Industries Ingalls'''.split()) \
    | set(MONTHS.split('|'))
UC, LC = "A-ZÀ-ÖØ-Þ", "a-zß-öø-ÿ"
NAME_RE = re.compile(rf"\b(?:(?:Mr|Ms|Mrs|Dr)\.\s+[{UC}][{UC}{LC}'’\-]+|[{UC}][{LC}]+(?:\s+[{UC}]\.)?"
                     rf"(?:\s+[{UC}][{UC}{LC}'’\-]+){{1,2}}(?:,?\s+(?:Jr|Sr)\.|\s+I{{2,3}})?)")


def clean_name(n):
    return re.sub(r"[’']s?$", '', n.strip()) if n else n


def person_key(p):
    """Surname key for merging one person's departure across filings (ruling 1)."""
    if not isinstance(p, str) or not p.strip():
        return None
    toks = [t.strip('.,') for t in clean_name(p).split()]
    if any(t.lower() in CORP_WORDS for t in toks):  # organisation names are never merge keys
        return None
    toks = [t for t in toks if t and t not in ('Mr', 'Ms', 'Mrs', 'Dr', 'Jr', 'Sr', 'II', 'III', 'IV')]
    return toks[-1].lower() if toks else None


CORP_WORDS = set('''energy airlines airline systems technologies technology holdings group bank bancorp services
communications networks solutions pharmaceuticals research foods stores motors financial capital partners
industries international global company corporation corp inc llc plc ltd trust insurance entertainment media
wireless mobile telecom utilities resources petroleum progress'''.split())


def names_in(s):
    out = []
    for m in NAME_RE.finditer(s):
        toks = [t.strip('.,') for t in re.split(r'\s+', m.group(0))]
        core = [t for t in toks if t not in ('Mr', 'Ms', 'Mrs', 'Dr', 'Jr', 'Sr')]
        if not core or any(t in NAME_STOP for t in core):
            continue
        out.append((m.start(), m.end(), m.group(0)))
    return out


def title_spans(s):
    spans = []
    for cls, rx in TITLE_RE:
        for m in rx.finditer(s):
            if cls == 'president' and re.search(r'(?i)(vice[\s-]|group\s)$', s[max(0, m.start() - 6):m.start()]):
                continue
            spans.append((m.start(), m.end(), cls, m.group(0)))
    spans.sort(key=lambda x: (x[0], PRIO[x[2]]))
    kept = []
    for sp in spans:  # overlap resolution: higher-priority class wins
        clash = [k for k in kept if not (sp[1] <= k[0] or sp[0] >= k[1])]
        if not clash:
            kept.append(sp)
        elif all(PRIO[sp[2]] < PRIO[k[2]] for k in clash):
            kept = [k for k in kept if k not in clash] + [sp]
    return sorted(kept)


def role_near(s, pos_start, pos_end):
    """Class and stated title nearest the departure verb at s[pos_start:pos_end]."""
    spans = [sp for sp in title_spans(s)  # titles the person keeps are not the ones being left
             if not re.search(r'(?i)(remain\w*|continu\w*|retain\w*|keep\w*)\s+(?:to\s+serve\s+|in\s+(?:his|her|their)\s+'
                              r'(?:current\s+)?(?:roles?|positions?|capacit(?:y|ies))\s+)?(?:as\s+)?'
                              r'(?:the\s+)?(?:\w+\W?s\s+)?(?:company\W?s\s+)?(?:\w+\s+){0,3}$',
                              s[max(0, sp[0] - 45):sp[0]])]
    if not spans:
        return None, ''
    best, bd = None, 1e9
    for sp in spans:
        if sp[0] >= pos_end:
            gap = s[pos_end:sp[0]]
            d = 0 if BIND.match(gap) and len(gap) < 60 else sp[0] - pos_end
        else:
            d = pos_start - sp[1] + 5
        if d < bd or (d == bd and best is not None and PRIO[sp[2]] < PRIO[best[2]]):
            best, bd = sp, d
    if bd > 220:
        return None, ''
    cluster = [sp for sp in spans if abs(sp[0] - best[0]) <= 50 or abs(sp[1] - best[1]) <= 50]
    cls = min(cluster, key=lambda sp: PRIO[sp[2]])[2]
    if cls == 'director' and any(sp[2] in EXEC_CLASSES for sp in cluster if sp[2] != 'director') \
            and best[2] != 'director':
        cls = min((sp for sp in cluster if sp[2] != 'director'), key=lambda sp: PRIO[sp[2]])[2]
    lo, hi = min(sp[0] for sp in cluster), max(sp[1] for sp in cluster)
    return cls, s[lo:hi]


def nearest_name(s, pos, full_by_surname, last_person):
    nm = names_in(s)
    before = [n for n in nm if n[1] <= pos and pos - n[1] < 250]
    after = [n for n in nm if n[0] >= pos and n[0] - pos < 150]
    pick = before[-1][2] if before else (after[0][2] if after else None)
    if pick is None:
        return last_person
    pick = clean_name(pick)
    sur = pick.split()[-1].strip('.,')
    if pick.startswith(('Mr.', 'Ms.', 'Mrs.', 'Dr.')) and sur in full_by_surname:
        return full_by_surname[sur]
    return pick


def dates_in(s):
    return [d for d in (parse_date(m) for m in DATE_RE.finditer(s)) if d is not None]


NOTICE = re.compile(r'(?i)\b(notified|informed|advised|tendered|submitted|delivered|announced|provided\s+notice)')
EFFECTIVE = re.compile(rf'(?i)effective\s+(?:as\s+of\s+|on\s+|upon\s+)?(?:({MONTHS})\.?\s+(\d{{1,2}}),?\s+(\d{{4}})|(immediately))')
FLAGS = {
    'flag_retirement': re.compile(r'(?i)\bretir'),
    'flag_health': re.compile(r'(?i)\b(health|medical|illness|disabilit|passed\s+away|died|death)'),
    'flag_transaction': re.compile(r'(?i)\b(merger|acquisition|business\s+combination|closing\s+of\s+the\s+'
                                   r'(?:transaction|merger)|spin-?off|in\s+connection\s+with\s+the\s+(?:sale|'
                                   r'transaction|acquisition|merger|closing))'),
    'flag_termination': re.compile(r'(?i)\b(terminat\w*|without\s+cause|for\s+cause|dismiss\w*|removed)'),
    'flag_severance_release': re.compile(r'(?i)\b(severance|separation\s+(?:and\s+release\s+)?agreement|release\s+of\s+'
                                         r'claims|general\s+release|release\s+agreement|in\s+exchange\s+for\s+a\s+release)'),
}
NODIS = re.compile(r'(?i)\b(not\s+(?:the\s+|a\s+)?result(?:ed)?\s+(?:of|from)\s+any\s+disagreement|no\s+disagreement|'
                   r'did\s+not\s+(?:involve|result\s+from|arise\s+from)\s+any\s+disagreement|not\s+(?:due\s+to|'
                   r'because\s+of|based\s+on)\s+any\s+disagreement|without\s+any\s+disagreement)')
PREV_PHRASE = re.compile(r'(?i)\b(?:as\s+)?previously\s+(?:announced|disclosed|reported)')
REF_CTX = re.compile(r'(?i)\b(announc|disclos|notif|inform|advis|tender|press\s+release|previously)')
AGREE_CTX = re.compile(r'(?i)\b(agreement|dated|letter|term\s+sheet)\b')
PERSONAL_CTX = re.compile(r'(?i)\b(employment|separation|retire|transition|succession|departure|resign|severance|'
                          r'term\s+sheet|letter\s+agreement)')


def classify(sec):
    """Return filing-level codes, person rows, and the dated references for pre-announcement."""
    labels = sorted(set(LABEL.findall(sec)))
    sents = sentences(sec)
    full_by_surname, title_by_surname = {}, {}
    for s in sents:
        for a, b, n in names_in(s):
            n = clean_name(n)
            sur = n.split()[-1].strip('.,')
            if not n.startswith(('Mr.', 'Ms.', 'Mrs.', 'Dr.')):
                full_by_surname.setdefault(sur, n)
            # apposition: "Name, (the Company's) <title>," or "<title>, Name"
            post = s[b:b + 130]
            pre = s[max(0, a - 110):a]
            cand = None
            if re.match(r'^\s*,\s', post):
                seg = re.split(r'\(|\bof\s+(?:the\s+)?(?:company|registrant)|,\s+(?:notified|informed|will|has|agreed|'
                               r'announced|resigned|retired)', post[1:], maxsplit=1, flags=re.I)[0]
                cand = [sp for sp in title_spans(seg) if sp[0] < 70]
            elif re.search(r',\s*$', pre):
                cand = [sp for sp in title_spans(pre) if len(pre) - sp[1] < 8]
            if cand and sur not in title_by_surname:
                offc = [sp for sp in cand if sp[2] != 'director'] or cand
                best = min(offc, key=lambda sp: PRIO[sp[2]])
                title_by_surname[sur] = (best[2], ' '.join(sp[3] for sp in offc))
    persons, dep_idx = [], []
    last_person = None
    ref_dates, notice_dates, eff_dates = [], [], []
    for i, s in enumerate(sents):
        sm = RET_PLAN.sub(' ', s)
        strong = bool(STRONG.search(sm))
        vacancy = bool(VACANCY.search(sm))
        restated = bool(PRIOR_REF.search(sm) or PREV_PHRASE.search(sm))
        skip = (((CONDITIONAL.search(sm) or BIO.search(sm)) and not strong)
                or (bool(HARD.search(sm)) and not EFF_DATE.search(sm)) or bool(PRIOR_EMP.search(sm)))
        found = False
        if not skip:
            for m in DEP.finditer(sm):
                cls, title = role_near(sm, m.start(), m.end())
                person = nearest_name(sm, m.start(), full_by_surname, last_person)
                sur = person.split()[-1].strip('.,') if person else None
                bound = bool(BIND.match(sm[m.end():m.end() + 60]))
                if sur in title_by_surname and not bound and (cls is None or cls == 'director' or
                                                               title_by_surname[sur][0] in EXEC_CLASSES):
                    known = title_by_surname[sur]
                    if cls is None or not re.search(r'(?i)\bboard\b|\bdirectors?\b', sm[m.end():m.end() + 40]):
                        cls, title = known
                if cls is None:
                    continue
                if vacancy and cls != 'director':  # ruling (3): vacancy mentions count for directors only
                    continue
                if re.search(r'(?i)committee', sm[max(0, m.start() - 60):m.end() + 60]) and cls == 'director' \
                        and not re.search(r'(?i)\bboard\b|\bdirector', sm[m.end():m.end() + 40]):
                    continue
                persons.append(dict(person=person, title=title, role_class=cls, action='departure',
                                    verb=m.group(0), sentence=s[:500], restated=int(restated),
                                    vacancy=int(vacancy)))
                found = True
                break
            for m in SUCC.finditer(sm):
                ctx = sm[max(0, m.start() - 60):m.end() + 60]
                t = m.group('title') or ''
                cls = next((c for c, rx in TITLE_RE if rx.search(t)), None) if t else None
                if cls is None:
                    cls, t = role_near(sm, m.start(), m.end())
                if cls in EXEC_CLASSES and not re.search(r'(?i)committee', ctx if not m.group('title') else t):
                    pred = m.group('pred')
                    sur = pred.split()[-1].strip('.,')
                    persons.append(dict(person=full_by_surname.get(sur, pred), title=t, role_class=cls,
                                        action='departure', verb='succeed/replace', sentence=s[:500],
                                        restated=int(restated), vacancy=0))
                    found = True
            for m in (IMPLIED.finditer(sm) if IMPLIED_RULE else []):  # narrow implied-departure rule
                t = m.group('title') or ''
                cls = next((c for c, rx in TITLE_RE if rx.search(t)), None) if t else None
                if cls is None:
                    cls, t = role_near(sm, m.start(), m.end())
                if cls in EXEC_CLASSES and not re.search(r'(?i)committee', t or ''):
                    pred = m.group('pred')
                    sur = pred.split()[-1].strip('.,')
                    persons.append(dict(person=full_by_surname.get(sur, pred), title=t, role_class=cls,
                                        action='departure', verb='implied_succession', sentence=s[:500],
                                        restated=int(restated), vacancy=0))
                    found = True
        if found:
            dep_idx.append(i)
            ref_dates += dates_in(s)  # ruling (4): every date in a departure sentence, incl. effective dates
            if NOTICE.search(s):
                notice_dates += dates_in(s)
            for em in EFFECTIVE.finditer(s):
                eff_dates.append('immediately' if em.group(4) else parse_date(em))
        else:
            if ELECT.search(sm):
                persons.append(dict(person=nearest_name(sm, 0, full_by_surname, last_person), title='director',
                                    role_class='director', action='election', verb='elect', sentence=s[:500]))
            elif APPOINT.search(sm):
                am = APPOINT.search(sm)
                cls, title = role_near(sm, am.start(), am.end())
                if cls in EXEC_CLASSES:
                    persons.append(dict(person=nearest_name(sm, am.end(), full_by_surname, last_person),
                                        title=title, role_class=cls, action='appointment', verb=am.group(0),
                                        sentence=s[:500]))
        nm = names_in(s)
        if nm:
            n = clean_name(nm[0][2])
            last_person = full_by_surname.get(n.split()[-1].strip('.,'), n)
        if REF_CTX.search(s) or (AGREE_CTX.search(s) and PERSONAL_CTX.search(s)):
            ref_dates += dates_in(s)
    ctx = ' '.join(sents[j] for i in dep_idx for j in range(i, min(i + 3, len(sents))))
    deps = [p for p in persons if p['action'] == 'departure']
    exec_names = {p['person'] for p in deps if p['role_class'] in EXEC_CLASSES}
    codes = dict(
        labels=','.join(labels),
        exec_departure_new=int(any(p['role_class'] in EXEC_CLASSES and not p.get('restated') for p in deps)),
        ceo_departure_new=int(any(p['role_class'] == 'CEO' and not p.get('restated') for p in deps)),
        restated_mention=int(any(p.get('restated') for p in deps)),
        vacancy_mention=int(any(p.get('vacancy') for p in deps)),
        implied_succession=int(any(p['verb'] == 'implied_succession' for p in deps)),
        exec_departure=int(any(p['role_class'] in EXEC_CLASSES for p in deps)),
        ceo_departure=int(any(p['role_class'] == 'CEO' for p in deps)),
        director_departure=int(any(p['role_class'] == 'director' and (p['person'] not in exec_names or p['person'] is None)
                                   for p in deps)),
        appointment=int(any(p['action'] == 'appointment' for p in persons)),
        election=int(any(p['action'] == 'election' for p in persons)),
        compensation=int(bool(COMP.search(sec))),
        notice_date=min(notice_dates).date().isoformat() if notice_dates else '',
        effective_date=next((e if isinstance(e, str) else e.date().isoformat() for e in eff_dates if e is not None), ''),
        previously_phrase=int(bool(PREV_PHRASE.search(sec))),
        **{k: int(bool(rx.search(ctx))) for k, rx in FLAGS.items()},
        flag_no_disagreement=int(bool(NODIS.search(sec))),
    )
    codes['action'] = ('departure' if deps else 'appointment' if codes['appointment'] else
                       'election' if codes['election'] else 'compensation only' if codes['compensation'] else 'other')
    refs = sorted({d for d in ref_dates + notice_dates})
    return codes, persons, refs


def pre_announced(codes, refs, t0):
    if any(d < t0 for d in refs):
        return 'Y'
    if codes['previously_phrase']:
        return 'unclear'
    return 'N'


# ------------------------------------------------------------------ run
if __name__ == '__main__':
    me = Path(__file__).read_bytes()
    sha = hashlib.sha256(me).hexdigest()
    log(f'classifier file sha256 {sha}')
    S = pd.read_csv(OUT / 'b_scope_filings.csv', dtype={'accession': str})
    rows, prow, secs = [], [], []
    for _, r in S.iterrows():
        fp = Path(r['local_file'])
        if not fp.exists():
            rows.append(dict(accession=r['accession'], cik=r['cik'], filing_date=r['filing_date'], text_ok=0))
            continue
        t = to_text(fp.read_bytes())
        sec_raw = section_502(t)
        found = int(bool(sec_raw))
        sec = strip_caption(sec_raw if sec_raw else t[:20000])
        codes, persons, refs = classify(sec)
        rows.append(dict(accession=r['accession'], cik=r['cik'], filing_date=r['filing_date'], form=r['form'],
                         items=r['items'], text_ok=1, section_found=found, section_chars=len(sec),
                         ref_dates=';'.join(d.date().isoformat() for d in refs), **codes))
        for k, p in enumerate(persons):
            prow.append(dict(accession=r['accession'], sub_row=k + 1, **p))
        secs.append(dict(accession=r['accession'], section_text=sec))
    F = pd.DataFrame(rows)
    F.to_csv(OUT / 'c2_filing_codes.csv', index=False)
    pd.DataFrame(prow).to_csv(OUT / 'c2_person_rows.csv', index=False)
    pd.DataFrame(secs).to_csv(OUT / 'c2_sections.csv', index=False)
    log(f'Filings coded: {int(F["text_ok"].sum())}/{len(F)}; Item 5.02 section found: '
        f'{int(F["section_found"].sum())}; labels printed: {int((F["labels"].fillna("") != "").sum())}')
    for c in ['exec_departure', 'ceo_departure', 'director_departure', 'appointment', 'election']:
        log(f'  filings with {c}: {int(F[c].sum())}')
    log('  action (filing level): ' + F['action'].value_counts().to_string().replace('\n', '; '))

    # ---------------- C3 outcomes ----------------
    ev = pd.read_csv(OUT / 'b_scope_events.csv', low_memory=False)
    ev['bdt'] = pd.to_datetime(ev['breach_date'])
    ev['rdt'] = pd.to_datetime(ev['reported_date'])
    F['fdt'] = pd.to_datetime(F['filing_date'])
    F['ref_list'] = F['ref_dates'].fillna('').apply(lambda s: [pd.Timestamp(x) for x in s.split(';') if x])
    by_cik = {c: g for c, g in F.groupby('cik')}
    out = []
    for _, e in ev.iterrows():
        g = by_cik.get(e['final_cik'], F.iloc[0:0])
        rec = dict(final_cik=e['final_cik'], breach_date=e['breach_date'], reported_date=e['reported_date'],
                   fcc_form499=e['fcc_form499'])
        for anc, t0 in [('rd', e['rdt']), ('bd', e['bdt'])]:
            for w in (30, 90, 180):
                x = g[(g['fdt'] > t0) & (g['fdt'] <= t0 + timedelta(days=w))]
                rec[f'rs_exec_departure_{w}_{anc}'] = int(x['exec_departure'].sum() > 0)
                rec[f'rs_ceo_departure_{w}_{anc}'] = int(x['ceo_departure'].sum() > 0)
                rec[f'rs_director_departure_{w}_{anc}'] = int(x['director_departure'].sum() > 0)
                rec[f'any_502_{w}_{anc}'] = int(len(x) > 0)
                xe = x[x['exec_departure'] == 1]
                rec[f'rs_exec_departure_nopre_{w}_{anc}'] = int(any(
                    pre_announced(rr, rr['ref_list'], t0) == 'N' for _, rr in xe.iterrows()))
            x = g[(g['fdt'] > t0) & (g['fdt'] <= t0 + timedelta(days=180)) & (g['exec_departure'] == 1)]
            rec[f'rs_days_to_first_exec_departure_{anc}'] = (x['fdt'].min() - t0).days if len(x) else np.nan
            pl = g[(g['fdt'] > t0 - timedelta(days=180)) & (g['fdt'] <= t0)]
            rec[f'rs_placebo_exec_departure_{anc}'] = int(pl['exec_departure'].sum() > 0)
            bl = g[(g['fdt'] >= t0 - timedelta(days=730)) & (g['fdt'] <= t0 - timedelta(days=181))]
            rec[f'rs_baseline_exec_departures_{anc}'] = int(bl['exec_departure'].sum())
            rec[f'rs_baseline_exec_rate_py_{anc}'] = round(int(bl['exec_departure'].sum()) / (550 / 365), 4)
        out.append(rec)
    O = pd.DataFrame(out)

    # ---- ruling (1): ONE departure per person within parent CIK, dated to its earliest disclosing filing ----
    # A person's departure mentions in several filings (the original, restatements, 8-K/As, pay agreements) merge
    # into one departure event; a mention more than 540 days after the previous one starts a new event.
    # Mentions with no person name cannot be merged and stay separate events.
    PR = pd.DataFrame(prow)
    PR = PR[PR['action'] == 'departure'].merge(F[['accession', 'cik', 'fdt']], on='accession', suffixes=('', '_f'))
    PR['grp'] = np.where(PR['role_class'].isin(list(EXEC_CLASSES)), 'exec', 'director')
    PR['pkey'] = PR['person'].apply(person_key)
    evs = []
    for (cik, grp), g in PR.groupby(['cik', 'grp']):
        for key, gk in g[g['pkey'].notna()].groupby('pkey'):
            cur = None
            for _, r in gk.sort_values('fdt').iterrows():
                if cur is None or (r['fdt'] - cur['last']).days > 540:
                    if cur is not None:
                        evs.append(cur)
                    cur = dict(cik=cik, grp=grp, pkey=key, first=r['fdt'], last=r['fdt'], rows=[r])
                else:
                    cur['last'] = r['fdt']
                    cur['rows'].append(r)
            evs.append(cur)
        for _, r in g[g['pkey'].isna()].iterrows():
            evs.append(dict(cik=cik, grp=grp, pkey=None, first=r['fdt'], last=r['fdt'], rows=[r]))
    E = pd.DataFrame([dict(cik=v['cik'], grp=v['grp'], pkey=v['pkey'], first_date=v['first'],
                           n_mentions=len(v['rows']), n_filings=len({r['accession'] for r in v['rows']}),
                           accessions=';'.join(sorted({r['accession'] for r in v['rows']})),
                           first_accession=min(v['rows'], key=lambda r: r['fdt'])['accession'],
                           persons=' | '.join(sorted({str(r['person']) for r in v['rows']})),
                           is_ceo=int(any(r['role_class'] == 'CEO' for r in v['rows'])),
                           restated_only=int(all(r.get('restated') == 1 for r in v['rows'])),
                           vacancy_only=int(all(r.get('vacancy') == 1 for r in v['rows'])))
                      for v in evs])
    ex_keys = E[E['grp'] == 'exec'][['cik', 'pkey', 'first_date']]
    E['director_only'] = 1
    for i, r in E[(E['grp'] == 'director') & E['pkey'].notna()].iterrows():
        m = ex_keys[(ex_keys['cik'] == r['cik']) & (ex_keys['pkey'] == r['pkey'])]
        if len(m) and (m['first_date'] - r['first_date']).abs().dt.days.min() <= 540:
            E.at[i, 'director_only'] = 0
    E.to_csv(OUT / 'c2_departure_events.csv', index=False)
    mg = E[E['n_filings'] > 1]
    log(f'\nRuling (1) merge: {len(PR)} departure mentions -> {len(E)} departure events '
        f'(exec {int((E.grp == "exec").sum())}, director {int((E.grp == "director").sum())}); '
        f'{len(mg)} events merge >1 filing ({int(mg["n_filings"].sum() - len(mg))} filings folded into an '
        f'earlier disclosure); unmergeable (no name) mentions: {int(E["pkey"].isna().sum())}')
    log('Spot-check of merged events (random 25 of the multi-filing events, seed 7): cik | group | key | persons | accessions')
    for _, r in mg.sample(min(25, len(mg)), random_state=7).iterrows():
        log(f"  {r['cik']} | {r['grp']} | {r['pkey']} | {r['persons'][:120]} | {r['accessions']}")

    Fx = F.set_index('accession')
    by_cik_E = {c: g for c, g in E.groupby('cik')}
    add = []
    for _, e in ev.iterrows():
        g = by_cik_E.get(e['final_cik'], E.iloc[0:0])
        ex = g[g['grp'] == 'exec']
        dr = g[(g['grp'] == 'director') & (g['director_only'] == 1)]
        rec = {}
        for anc, t0 in [('rd', e['rdt']), ('bd', e['bdt'])]:
            for w in (30, 90, 180):
                inw = lambda d: d[(d['first_date'] > t0) & (d['first_date'] <= t0 + timedelta(days=w))]
                xe = inw(ex)
                rec[f'exec_departure_{w}_{anc}'] = int(len(xe) > 0)
                rec[f'ceo_departure_{w}_{anc}'] = int((xe['is_ceo'] == 1).any())
                rec[f'director_departure_{w}_{anc}'] = int(len(inw(dr)) > 0)
                rec[f'exec_departure_nopre_{w}_{anc}'] = int(any(
                    pre_announced(Fx.loc[a], Fx.loc[a, 'ref_list'], t0) == 'N' for a in xe['first_accession']))
            x = ex[(ex['first_date'] > t0) & (ex['first_date'] <= t0 + timedelta(days=180))]
            rec[f'days_to_first_exec_departure_{anc}'] = (x['first_date'].min() - t0).days if len(x) else np.nan
            pl = ex[(ex['first_date'] > t0 - timedelta(days=180)) & (ex['first_date'] <= t0)]
            rec[f'placebo_exec_departure_{anc}'] = int(len(pl) > 0)
            bl = ex[(ex['first_date'] >= t0 - timedelta(days=730)) & (ex['first_date'] <= t0 - timedelta(days=181))]
            rec[f'baseline_exec_departures_{anc}'] = len(bl)
            rec[f'baseline_exec_rate_py_{anc}'] = round(len(bl) / (550 / 365), 4)
        add.append(rec)
    O = pd.concat([O, pd.DataFrame(add)], axis=1)
    O.to_csv(OUT / 'c2_outcomes_events.csv', index=False)

    # ---------------- C4 crosswalk ----------------
    cv = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
    O2 = O.merge(cv[['final_cik', 'breach_date', 'executive_change_30d', 'executive_change_90d',
                     'executive_change_180d', 'immediate_disclosure']], on=['final_cik', 'breach_date'])
    cw = []
    for samp, d in [('scope 341', O2), ('Q1 Essay 3 sample 340', O2[O2['immediate_disclosure'].notna()])]:
        for anc in ('rd', 'bd'):
            for w in (30, 90, 180):
                row = dict(sample=samp, anchor=anc, window=w, N=len(d))
                for g, lab in [(1, 'treated'), (0, 'control')]:
                    dd = d[d['fcc_form499'] == g]
                    for o in ('any_502', 'exec_departure', 'ceo_departure', 'director_departure'):
                        row[f'{o}_{lab}'] = round(dd[f'{o}_{w}_{anc}'].mean(), 4)
                    row[f'v3_any502_{lab}'] = round(dd[f'executive_change_{w}d'].mean(), 4)
                row['any502_not_exec_events'] = int(((d[f'any_502_{w}_{anc}'] == 1) &
                                                     (d[f'exec_departure_{w}_{anc}'] == 0)).sum())
                row['any502_events'] = int(d[f'any_502_{w}_{anc}'].sum())
                if anc == 'bd':
                    row['bd_any502_vs_v3_mismatch'] = int((d[f'any_502_{w}_bd'] != d[f'executive_change_{w}d']).sum())
                cw.append(row)
    CW = pd.DataFrame(cw)
    CW.to_csv(OUT / 'c2_crosswalk.csv', index=False)
    log('\nC4 crosswalk:\n' + CW.to_string(index=False))

    if '--dev' in sys.argv:
        dev = set(pd.read_csv(OUT / 'dev_ids.csv', dtype=str)['accession'])
        cal = {p.name.split('_')[2] for p in Path('outputs/rebuild/calibration_5_02').glob('*.htm')}
        tmo = {p.name.split('_')[0] for p in Path('outputs/essay3_q1/tmobile_8k').glob('*.htm')} - cal
        val = set(pd.read_csv(OUT / 'validation_ids.csv', dtype=str)['accession'])
        show = (dev | tmo) - cal - val
        P = pd.DataFrame(prow)
        Sx = pd.DataFrame(secs).set_index('accession')
        for _, r in F[F['accession'].isin(show)].iterrows():
            print('\n' + '-' * 100)
            print(f"{r['accession']} {r['filing_date']} labels={r['labels']} | exec={r['exec_departure']} "
                  f"ceo={r['ceo_departure']} dir={r['director_departure']} action={r['action']} "
                  f"notice={r['notice_date']} eff={r['effective_date']}")
            for _, p in P[P['accession'] == r['accession']].iterrows():
                print(f"   [{p['action']}/{p['role_class']}] {p['person']} | {p['title']} | verb={p['verb']}")
            print('   TEXT: ' + Sx.loc[r['accession'], 'section_text'][:1400])
    (OUT / '195_classifier.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
