#!/usr/bin/env python3
"""
Test script to verify that get_page_content and add_web_source functions work
"""

def test_functions():
    print("🧪 Testing function accessibility...")
    
    try:
        # Method 1: Direct import
        print("\n1️⃣ Testing direct import...")
        from src.tools.web_serch import WebSearchTool
        from src.tools.citation_formatter import CitationFormatterTool
        
        web_tool = WebSearchTool()
        citation_tool = CitationFormatterTool()
        
        print(f"✅ WebSearchTool created: {type(web_tool)}")
        print(f"✅ CitationFormatterTool created: {type(citation_tool)}")
        
        # Check if methods exist
        print(f"✅ get_page_content available: {hasattr(web_tool, 'get_page_content')}")
        print(f"✅ add_web_source available: {hasattr(citation_tool, 'add_web_source')}")
        
    except Exception as e:
        print(f"❌ Direct import failed: {e}")
    
    try:
        # Method 2: Tool manager
        print("\n2️⃣ Testing tool manager...")
        from src.tools import get_tool
        
        web_tool = get_tool("web_serch")
        citation_tool = get_tool("citation_formatter")
        
        print(f"✅ Web tool from manager: {type(web_tool)}")
        print(f"✅ Citation tool from manager: {type(citation_tool)}")
        
        # Check if methods exist
        print(f"✅ get_page_content available: {hasattr(web_tool, 'get_page_content')}")
        print(f"✅ add_web_source available: {hasattr(citation_tool, 'add_web_source')}")
        
    except Exception as e:
        print(f"❌ Tool manager failed: {e}")
    
    try:
        # Method 3: Actually call the functions
        print("\n3️⃣ Testing function calls...")
        
        # Test add_web_source
        citation_id = citation_tool.add_web_source(
            url="https://example.com",
            title="Test Page",
            author="Test Author"
        )
        print(f"✅ add_web_source returned citation ID: {citation_id}")
        
        # Test get_page_content (using a reliable test URL)
        content = web_tool.get_page_content("https://httpbin.org/html")
        print(f"✅ get_page_content returned: {type(content)}")
        if content:
            print(f"   - Title: {content.get('title', 'No title')[:50]}...")
            print(f"   - Content length: {len(content.get('content', ''))}")
        
    except Exception as e:
        print(f"❌ Function calls failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_functions()
