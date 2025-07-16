
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain.tools import tool
from tools.eco_search import eco_search_expand
from tools.basalam_search import search_basalam

@tool("perform_eco_search", return_direct=False)
def perform_eco_search(query: str, max_price: int = 0, min_rating: float = 0.0, vendor_city: str = "") -> Dict[str, Any]:
    """
    انجام جستجوی هوشمند اکولوژیک که به طور خودکار اجزاء مرتبط را شناسایی و جستجو می‌کند.
    این ابزار جستجوی کلی را به جستجوهای تخصصی چندگانه تبدیل می‌کند.
    """
    try:
        # Step 1: Expand the query to find related components
        expansion_result = eco_search_expand.invoke({"query": query})
        
        all_products = []
        search_results = {}
        
        # Step 2: Search for the original query
        original_products = search_basalam.invoke({
            "query": query,
            "max_price": max_price,
            "min_rating": min_rating,
            "vendor_city": vendor_city
        })
        
        if original_products:
            all_products.extend(original_products)
            search_results["جستجوی اصلی"] = len(original_products)
        
        # Step 3: Search for each expanded component
        for component in expansion_result.expanded_components[:5]:  # Limit to 5 components to avoid too many requests
            try:
                component_products = search_basalam.invoke({
                    "query": component,
                    "max_price": max_price,
                    "min_rating": min_rating,
                    "vendor_city": vendor_city
                })
                
                if component_products:
                    # Filter out duplicates based on product ID
                    existing_ids = {p.get('id', '') for p in all_products}
                    new_products = [p for p in component_products if p.get('id', '') not in existing_ids]
                    
                    all_products.extend(new_products)
                    search_results[component] = len(new_products)
                    
            except Exception as e:
                print(f"خطا در جستجوی {component}: {str(e)}")
                continue
        
        # Step 4: Sort all products by price
        all_products.sort(key=lambda x: x.get('price', 0))
        
        # Step 5: Prepare result summary
        result = {
            "original_query": query,
            "expanded_components": expansion_result.expanded_components,
            "search_strategy": expansion_result.search_strategy,
            "search_results": search_results,
            "total_products": len(all_products),
            "products": all_products[:20],  # Limit to 20 products for display
            "eco_search_summary": f"جستجوی اکولوژیک برای '{query}' انجام شد. {len(expansion_result.expanded_components)} جزء شناسایی و {len(all_products)} محصول یافت شد."
        }
        
        return result
        
    except Exception as e:
        return {
            "error": f"خطا در جستجوی اکولوژیک: {str(e)}",
            "original_query": query,
            "products": []
        }

@tool("explain_eco_search", return_direct=False)
def explain_eco_search(concept: str) -> str:
    """
    توضیح اینکه جستجوی اکولوژیک چگونه یک مفهوم را گسترش می‌دهد.
    """
    expansion_result = eco_search_expand.invoke({"query": concept})
    
    explanation = f"""
🌱 **جستجوی اکولوژیک برای "{concept}"**

🎯 **مفهوم اصلی:** {concept}

🔍 **اجزاء شناسایی شده:**
"""
    
    for i, component in enumerate(expansion_result.expanded_components, 1):
        explanation += f"{i}. {component}\n"
    
    explanation += f"""
📋 **استراتژی جستجو:** {expansion_result.search_strategy}

💡 **چرا این روش مفید است؟**
- جستجوی جامع‌تر و کامل‌تر
- یافتن محصولاتی که ممکن است فراموش شده باشند
- کشف گزینه‌های جایگزین و مکمل
- صرفه‌جویی در زمان جستجو
"""
    
    return explanation

if __name__ == "__main__":
    # Test the eco search
    test_result = perform_eco_search.invoke({"query": "V60 material"})
    print("نتیجه جستجوی اکولوژیک:")
    print(f"تعداد کل محصولات: {test_result.get('total_products', 0)}")
    print(f"اجزاء گسترده شده: {test_result.get('expanded_components', [])}")
