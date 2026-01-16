#!/usr/bin/env python3
"""
Script para probar la extracción mejorada
"""
from llm_service.llm_openai import extract_structured_data_with_openai
import json

# Casos de prueba
test_cases = [
    "Diciembre 31 - De Liverpool en 12 días, por el sol. Antio, cap. Ranton, ton. 106, con vivares y loidines, a los Sres. Dua ke, H. y comp.",
    "De Nueva Orleans y escalas en 5 dias, vap. america-C no Cliton, cap. Morgan, trip. 32, tons. 717: con carga general á Lawton y Hnos.",
    "De Scarsport en 15 días berg am. Isaac Carter, cap. Clark, ton. 196, con envasos, á D. S. O. F.undam y comp.",
    "De Liverpool en 18 días berg esp. Historia, cap. Porton do, ton. 124, con mercadería, a los Sres. Clarke",
]

print("🧪 TESTING IMPROVED EXTRACTION")
print("="*70)

for i, text in enumerate(test_cases, 1):
    print(f"\n📝 Test {i}:")
    print(f"Input: {text[:80]}...")
    
    result = extract_structured_data_with_openai(text)
    
    print(f"\nOutput:")
    print(f"  ship_type: {result.get('ship_type')}")
    print(f"  ship_name: {result.get('ship_name')}")
    print(f"  travel_departure_port: {result.get('travel_departure_port')}")
    print(f"  travel_duration: {result.get('travel_duration')}")
    print(f"  master_role: {result.get('master_role')}")
    print(f"  master_name: {result.get('master_name')}")
    print(f"  ship_tons_capacity: {result.get('ship_tons_capacity')}")
    print("-"*70)

print("\n✅ Test complete")
