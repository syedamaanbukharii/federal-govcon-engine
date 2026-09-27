import pandas as pd
import glob

csv_files = glob.glob('*.csv')
for f in csv_files:
    df = pd.read_csv(f)
    print(f"File: {f}")
    print(f"Columns: {df.columns.tolist()}")
    if len(df) > 0:
        row = df.iloc[0]
        name_col = 'CEO Name' if 'CEO Name' in row else 'Director / VP / CEO Name'
        name_col = 'Executive Name' if 'Executive Name' in row else name_col
        print(f"name_col chosen: {name_col}")
        print(f"Value: {row.get(name_col, 'Unknown')}")
        
        email = str(row.get('Verified Email', ''))
        phone = str(row.get('Corporate Phone', ''))
        print(f"Email: {email}, Phone: {phone}")
    print("-" * 40)
