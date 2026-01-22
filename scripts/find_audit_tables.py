import wrds

print("=" * 60)
print("FINDING CORRECT AUDIT ANALYTICS TABLES")
print("=" * 60)

# Connect to WRDS
print("\nConnecting to WRDS...")
db = wrds.Connection()

# List all libraries
print("\n[1/3] Available libraries:")
try:
    libraries = db.list_libraries()
    audit_libs = [lib for lib in libraries if 'audit' in lib.lower()]
    print(f"Audit-related libraries: {audit_libs}")
except Exception as e:
    print(f"Error: {e}")

# List tables in audit library
print("\n[2/3] Tables in 'audit' library:")
try:
    tables = db.list_tables(library='audit')
    print(f"Total tables: {len(tables)}")
    print("\nSOX-related tables:")
    sox_tables = [t for t in tables if 'sox' in t.lower() or '404' in t.lower() or 'control' in t.lower()]
    for table in sox_tables:
        print(f"  - {table}")
    
    print("\nRestatement-related tables:")
    restate_tables = [t for t in tables if 'restat' in t.lower() or 'nonreli' in t.lower()]
    for table in restate_tables:
        print(f"  - {table}")
except Exception as e:
    print(f"Error: {e}")

# Try to sample from likely tables
print("\n[3/3] Sampling from candidate tables:")

candidate_tables = [
    'audit.soxcontrols',
    'audit.sox404',
    'audit.icmw',
    'audit.auditnonreli',
    'audit.restatements',
    'audit.feed11_sox_404_internal_controls',
    'audit.feed39_financial_restatements'
]

for table in candidate_tables:
    try:
        print(f"\nTrying: {table}")
        test = db.raw_sql(f"SELECT * FROM {table} LIMIT 3", date_cols=['fiscal_year_end', 'file_date'])
        print(f"  ✓ SUCCESS! Columns: {test.columns.tolist()}")
        print(f"  Sample:\n{test.head(2)}")
    except Exception as e:
        print(f"  ✗ Failed: {str(e)[:100]}")

db.close()
print("\n✓ Done")