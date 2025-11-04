"""
Verification script to check supplement image mapping
"""
import pandas as pd

# Load both CSVs
disease_info = pd.read_csv('Model_assest/disease_info.csv')
supplement_info = pd.read_csv('Model_assest/supplement_info.csv', encoding='cp1252')

print("=" * 80)
print("SUPPLEMENT IMAGE VERIFICATION")
print("=" * 80)

print(f"\nTotal diseases in disease_info.csv: {len(disease_info)}")
print(f"Total supplements in supplement_info.csv: {len(supplement_info)}")

# Check for missing mappings
print("\n" + "=" * 80)
print("CHECKING INDEX MAPPING")
print("=" * 80)

missing_indices = []
for idx in range(len(disease_info)):
    disease_name = disease_info['disease_name'][idx]
    supplement_row = supplement_info[supplement_info['index'] == idx]
    
    if supplement_row.empty:
        missing_indices.append((idx, disease_name))
        print(f"❌ Index {idx}: {disease_name} - NO SUPPLEMENT FOUND")
    else:
        supplement_name = supplement_row['supplement name'].values[0]
        supplement_img = supplement_row['supplement image'].values[0]
        has_image = supplement_img and str(supplement_img).strip() != '' and str(supplement_img) != 'nan'
        
        if has_image:
            print(f"✅ Index {idx}: {disease_name} -> {supplement_name}")
        else:
            print(f"⚠️  Index {idx}: {disease_name} -> {supplement_name} (NO IMAGE URL)")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if missing_indices:
    print(f"\n❌ {len(missing_indices)} diseases have NO supplement mapping:")
    for idx, name in missing_indices:
        print(f"   - Index {idx}: {name}")
else:
    print("\n✅ All diseases have supplement mappings!")

# Check for empty image URLs
empty_images = supplement_info[
    (supplement_info['supplement image'].isna()) | 
    (supplement_info['supplement image'].astype(str).str.strip() == '')
]

if not empty_images.empty:
    print(f"\n⚠️  {len(empty_images)} supplements have empty image URLs:")
    for _, row in empty_images.iterrows():
        print(f"   - Index {row['index']}: {row['disease_name']}")
else:
    print("\n✅ All supplements have image URLs!")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
