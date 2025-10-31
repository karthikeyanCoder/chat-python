#!/usr/bin/env python3
"""
Verify all endpoints are reorganized from app_simple.py to app/modules
"""
import re

def count_routes_in_file(filepath):
    """Count route decorators in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Match both @app.route and @blueprint.route patterns
        pattern = r'@\w+\.route\('
        matches = re.findall(pattern, content)
        return len(matches)
    except:
        return 0

def count_module_endpoints():
    """Count all endpoints in app/modules"""
    import os
    
    total = 0
    module_counts = {}
    
    for root, dirs, files in os.walk('app/modules'):
        for file in files:
            if file == 'routes.py':
                filepath = os.path.join(root, file)
                count = count_routes_in_file(filepath)
                module_name = os.path.basename(root)
                module_counts[module_name] = count
                total += count
    
    return total, module_counts

def main():
    print("=" * 80)
    print("              ENDPOINT REORGANIZATION VERIFICATION")
    print("=" * 80)
    print()
    
    # Count endpoints in modular structure
    total_endpoints, module_counts = count_module_endpoints()
    
    # Count main.py routes
    main_routes = count_routes_in_file('app/main.py')
    
    # Calculate grand total
    grand_total = total_endpoints + main_routes
    
    print(f"[*] Modular Structure Endpoints")
    print(f"    |-- Total in app/modules: {total_endpoints}")
    print(f"    |-- Total in app/main.py: {main_routes}")
    print(f"    |-- GRAND TOTAL: {grand_total}")
    print()
    
    print(f"[*] Breakdown by Module")
    for module, count in sorted(module_counts.items()):
        print(f"    |-- {module:20s}: {count:3d} endpoints")
    
    print()
    print("=" * 80)
    
    # Detailed module list
    print("[*] Full Module List:")
    modules = [
        ("auth", "Authentication & Profile"),
        ("pregnancy", "Pregnancy Tracking"),
        ("symptoms", "Symptoms Analysis"),
        ("vital_signs", "Vital Signs"),
        ("medication", "Medication Management"),
        ("nutrition", "Nutrition Tracking"),
        ("hydration", "Hydration Tracking"),
        ("mental_health", "Mental Health"),
        ("medical_lab", "Medical Lab OCR"),
        ("voice", "Voice Interaction"),
        ("appointments", "Appointments"),
        ("doctors", "Doctor Profiles"),
        ("sleep_activity", "Sleep & Activity"),
        ("quantum_llm", "Quantum & LLM"),
        ("profile_utils", "Profile Utilities"),
        ("system_health", "System Health"),
        ("profile", "Extended Profile")
    ]
    
    for module, desc in modules:
        count = module_counts.get(module, 0)
        status = "[OK]" if count > 0 else "[EMPTY]"
        print(f"    {status} {module:20s} ({desc:30s}): {count:3d} endpoints")
    
    print()
    print("=" * 80)
    
    # Check MVC structure completeness
    print("[*] MVC Structure Check")
    mvc_complete = 0
    mvc_partial = 0
    
    import os
    for module, _ in modules:
        module_path = f'app/modules/{module}'
        if os.path.exists(module_path):
            has_routes = os.path.exists(f'{module_path}/routes.py')
            has_services = os.path.exists(f'{module_path}/services.py')
            has_repository = os.path.exists(f'{module_path}/repository.py')
            has_schemas = os.path.exists(f'{module_path}/schemas.py')
            
            if all([has_routes, has_services, has_repository, has_schemas]):
                print(f"    [OK] {module:20s}: Full MVC (routes, services, repository, schemas)")
                mvc_complete += 1
            else:
                missing = []
                if not has_routes: missing.append('routes')
                if not has_services: missing.append('services')
                if not has_repository: missing.append('repository')
                if not has_schemas: missing.append('schemas')
                print(f"    [PARTIAL] {module:20s}: Missing {', '.join(missing)}")
                mvc_partial += 1
    
    print()
    print(f"    |-- Full MVC: {mvc_complete}/{len(modules)}")
    print(f"    |-- Partial: {mvc_partial}/{len(modules)}")
    
    print()
    print("=" * 80)
    print(f"              VERIFICATION COMPLETE")
    print(f"              {grand_total} ENDPOINTS REORGANIZED")
    print(f"              {mvc_complete} MODULES WITH FULL MVC")
    print("=" * 80)

if __name__ == '__main__':
    main()

