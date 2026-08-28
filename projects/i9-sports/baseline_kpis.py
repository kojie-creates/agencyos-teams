#!/usr/bin/env python3
"""
Baseline KPI extractor for i9-sports discovery.
Saves baseline_summary.md and baseline_metrics.csv into projects/i9-sports/data/ when CSVs are present.

Usage: python baseline_kpis.py
"""
import csv
import glob
import os
from collections import defaultdict
from datetime import datetime

ROOT = os.path.dirname(__file__)
DATA_DIR = os.path.join(ROOT, 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

# Helpers

def read_csv(path):
    rows = []
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    except Exception as e:
        print(f"Warning: failed to read {path}: {e}")
    return rows

# Load datasets if present
registrations = read_csv(os.path.join(DATA_DIR, 'registrations.csv'))
sessions = read_csv(os.path.join(DATA_DIR, 'sessions.csv'))
coaches = read_csv(os.path.join(DATA_DIR, 'coaches.csv'))
communications = read_csv(os.path.join(DATA_DIR, 'communications.csv'))
transactions = read_csv(os.path.join(DATA_DIR, 'transactions.csv'))
ops_time = read_csv(os.path.join(DATA_DIR, 'ops_time_sample_week1.csv'))

metrics = {}
notes = []

# Registrations
if registrations:
    total_regs = len(registrations)
    cancelled = sum(1 for r in registrations if r.get('status','').lower() in ('cancelled','canceled'))
    metrics['registrations_total'] = total_regs
    metrics['registrations_cancelled'] = cancelled
    try:
        regs_by_prog = defaultdict(int)
        for r in registrations:
            regs_by_prog[r.get('program_id') or r.get('program_name') or 'unknown'] += 1
        top_program = max(regs_by_prog.items(), key=lambda kv: kv[1])
        metrics['top_program_by_registrations'] = f"{top_program[0]} ({top_program[1]})"
    except Exception:
        pass
else:
    notes.append('registrations.csv not found or empty')

# Sessions & reschedules
if sessions:
    total_sessions = len(sessions)
    metrics['sessions_total'] = total_sessions
    reschedules = 0
    for s in sessions:
        rc = s.get('reschedule_count') or s.get('reschedules') or s.get('reschedule') or '0'
        try:
            reschedules += int(rc)
        except Exception:
            try:
                reschedules += int(float(rc))
            except Exception:
                pass
    metrics['reschedule_count_total'] = reschedules
    if total_sessions:
        metrics['reschedule_rate_per_session'] = round(reschedules / total_sessions, 3)
else:
    notes.append('sessions.csv not found or empty')

# Coach utilization (simple)
if coaches and sessions:
    assigned_counts = defaultdict(int)
    for s in sessions:
        cid = s.get('coach_id')
        if cid:
            assigned_counts[cid] += 1
    avg_assigned = sum(assigned_counts.values()) / max(1, len(assigned_counts))
    metrics['coaches_count'] = len(assigned_counts)
    metrics['avg_assigned_sessions_per_coach'] = round(avg_assigned, 2)
elif coaches:
    metrics['coaches_count'] = len(coaches)
else:
    notes.append('coaches.csv not found or empty')

# Communications: delivery/open rates
if communications:
    total_comms = len(communications)
    delivered = sum(1 for c in communications if c.get('delivered','').lower() in ('y','yes','true','1'))
    opened = sum(1 for c in communications if c.get('opened','').lower() in ('y','yes','true','1'))
    metrics['communications_total'] = total_comms
    metrics['communications_delivered_pct'] = round(100 * delivered / total_comms, 1) if total_comms else 0
    metrics['communications_opened_pct'] = round(100 * opened / total_comms, 1) if total_comms else 0
else:
    notes.append('communications.csv not found or empty')

# Ops time: average scheduling time per session
if ops_time:
    schedule_durations = [float(r.get('duration_minutes') or 0) for r in ops_time if (r.get('task_type','').lower()=='schedule')]
    if schedule_durations:
        metrics['avg_schedule_minutes'] = round(sum(schedule_durations)/len(schedule_durations),1)
    else:
        notes.append('No schedule tasks found in ops_time_sample_week1.csv')
else:
    notes.append('ops_time_sample_week1.csv not found or empty')

# Financials: revenue
if transactions:
    total_amount = 0.0
    for t in transactions:
        a = t.get('net_amount') or t.get('amount') or '0'
        try:
            total_amount += float(a)
        except Exception:
            pass
    metrics['transactions_count'] = len(transactions)
    metrics['transactions_total_net'] = round(total_amount,2)
else:
    notes.append('transactions.csv not found or empty')

# Write baseline_metrics.csv
metrics_path = os.path.join(DATA_DIR, 'baseline_metrics.csv')
try:
    with open(metrics_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['metric','value'])
        for k,v in metrics.items():
            writer.writerow([k,v])
    print(f'Wrote metrics to {metrics_path}')
except Exception as e:
    print(f'Failed to write metrics CSV: {e}')

# Write baseline_summary.md
summary_path = os.path.join(DATA_DIR, 'baseline_summary.md')
try:
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write('# i9 Sports — Baseline Summary\n\n')
        f.write(f'Generated: {datetime.utcnow().isoformat()}Z\n\n')
        f.write('## Key metrics\n\n')
        for k,v in metrics.items():
            f.write(f'- **{k}**: {v}\n')
        if notes:
            f.write('\n## Notes\n\n')
            for n in notes:
                f.write(f'- {n}\n')
    print(f'Wrote summary to {summary_path}')
except Exception as e:
    print(f'Failed to write summary: {e}')

print('\nDone. Place CSV exports in the data/ folder and re-run this script to compute updated baselines.')
