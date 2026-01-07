"""Direct Ollama test to see what's happening"""

import ollama

print("=" * 60)
print("🔍 DIRECT OLLAMA DEBUG TEST")
print("=" * 60)

try:
    print("\n1️⃣ Calling ollama.list()...")
    result = ollama.list()
    
    print(f"\n✅ Success!")
    print(f"📦 Result type: {type(result)}")
    print(f"📦 Result: {result}")
    
    # Try to access models
    print(f"\n2️⃣ Trying to access models...")
    
    if isinstance(result, dict):
        print("   It's a dict!")
        print(f"   Keys: {result.keys()}")
        models = result.get('models', [])
        print(f"   Models: {models}")
        
        if models:
            first_model = models[0]
            print(f"\n   First model type: {type(first_model)}")
            print(f"   First model: {first_model}")
            
            if isinstance(first_model, dict):
                print(f"   First model keys: {first_model.keys()}")
                print(f"   First model name: {first_model.get('name')}")
            else:
                print(f"   First model attributes: {dir(first_model)}")
                if hasattr(first_model, 'name'):
                    print(f"   First model name: {first_model.name}")
    else:
        print("   It's an object!")
        print(f"   Attributes: {[a for a in dir(result) if not a.startswith('_')]}")
        
        if hasattr(result, 'models'):
            print(f"   Has 'models' attribute")
            models = result.models
            print(f"   Models type: {type(models)}")
            print(f"   Models: {models}")
            
            if models:
                first_model = models[0]
                print(f"\n   First model type: {type(first_model)}")
                print(f"   First model: {first_model}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    print("\n📋 Full traceback:")
    traceback.print_exc()

print("\n" + "=" * 60)