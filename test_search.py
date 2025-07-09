
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tools.basalam_search import search_basalam

def test_search():
    print("🧪 Testing search functionality...")
    
    try:
        # Test simple search
        query = "کیف"
        print(f"🔍 Searching for: {query}")
        
        results = search_basalam(query)
        
        print(f"✅ Search completed. Found {len(results)} products")
        
        if results:
            print("\n📦 First few results:")
            for i, product in enumerate(results[:3], 1):
                print(f"{i}. {product.get('name', 'Unknown')}")
                print(f"   Price: {product.get('price', 0):,} Toman")
                print(f"   Vendor: {product.get('vendor_name', 'Unknown')}")
                print(f"   Link: {product.get('link', '')}")
                print()
        else:
            print("❌ No products found")
            
    except Exception as e:
        print(f"❌ Error during search: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search()
