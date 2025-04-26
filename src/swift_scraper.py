"""
Swift Documentation Scraper for CodeBridge AI

This module scrapes Swift documentation from Apple's developer website
and other Swift resources, then saves it to the data directory.
"""

import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time

class SwiftDocumentationScraper:
    def __init__(self, output_dir="../data/docs/swift"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def scrape_urls(self, urls, selector="main", delay=1):
        """
        Scrape content from a list of URLs.
        
        Args:
            urls (list): List of URLs to scrape
            selector (str): CSS selector for the main content
            delay (int): Delay between requests to avoid rate limiting
        """
        print(f"Scraping {len(urls)} Swift documentation pages...")
        
        for url in tqdm(urls):
            try:
                # Add delay to avoid rate limiting
                time.sleep(delay)
                
                # Make request with headers to mimic a browser
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
                }
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                
                # Parse HTML content
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract main content using the selector
                content_element = soup.select_one(selector)
                
                if content_element:
                    content = content_element.get_text(separator="\n", strip=True)
                    
                    # Create filename from URL
                    filename = url.split('/')[-1].replace('.html', '')
                    if not filename or filename == '':
                        filename = url.split('/')[-2]
                    
                    # Clean filename
                    filename = filename.replace('?', '_').replace('&', '_').replace('=', '_')
                    
                    # Save to file
                    with open(os.path.join(self.output_dir, f"{filename}.txt"), 'w', encoding='utf-8') as f:
                        # Add URL as reference
                        f.write(f"Source: {url}\n\n")
                        f.write(content)
                    
                    print(f"Saved {filename}.txt")
                else:
                    print(f"Could not find content with selector '{selector}' at {url}")
            
            except Exception as e:
                print(f"Error scraping {url}: {e}")
    
    def save_swift_guide(self, content, filename):
        """Save a Swift guide directly to the documentation folder"""
        filepath = os.path.join(self.output_dir, f"{filename}.txt")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved {filename}.txt")
    
    def scrape_swift_forums(self, num_pages=5, topics_per_page=20):
        """
        Scrape Swift Forum posts to get common issues and solutions
        
        Args:
            num_pages (int): Number of pages to scrape
            topics_per_page (int): Number of topics per page to process
        """
        base_url = "https://forums.swift.org/c/development/14.json"
        topic_base_url = "https://forums.swift.org/t/"
        
        all_posts = []
        
        print(f"Scraping Swift Forums (up to {num_pages} pages)...")
        
        for page in tqdm(range(num_pages)):
            try:
                time.sleep(1)  # Be nice to the server
                url = f"{base_url}?page={page}"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                topics = data.get('topic_list', {}).get('topics', [])
                
                for i, topic in enumerate(topics[:topics_per_page]):
                    if i >= topics_per_page:
                        break
                        
                    topic_id = topic.get('id')
                    title = topic.get('title', '')
                    
                    # Skip if no topic_id
                    if not topic_id:
                        continue
                    
                    # Get the full topic
                    time.sleep(1)  # Be nice to the server
                    topic_url = f"{topic_base_url}{topic_id}.json"
                    try:
                        topic_response = requests.get(topic_url, timeout=10)
                        topic_response.raise_for_status()
                        
                        topic_data = topic_response.json()
                        posts = topic_data.get('post_stream', {}).get('posts', [])
                        
                        # Get the first post (question) and the accepted answer if available
                        if posts:
                            first_post = posts[0]
                            content = first_post.get('cooked', '')
                            
                            # Find accepted answer (if any)
                            accepted_answer = None
                            for post in posts[1:]:
                                if post.get('accepted_answer', False):
                                    accepted_answer = post.get('cooked', '')
                                    break
                            
                            # Combine the content
                            full_content = f"Topic: {title}\n\nQuestion:\n{content}\n"
                            if accepted_answer:
                                full_content += f"\nAccepted Solution:\n{accepted_answer}"
                            
                            # Create a clean version (removing HTML)
                            soup = BeautifulSoup(full_content, 'html.parser')
                            clean_content = soup.get_text(separator="\n", strip=True)
                            
                            # Save to file
                            filename = f"swift_forum_{topic_id}"
                            with open(os.path.join(self.output_dir, f"{filename}.txt"), 'w', encoding='utf-8') as f:
                                f.write(f"Source: https://forums.swift.org/t/{topic_id}\n\n")
                                f.write(clean_content)
                            
                            print(f"Saved forum topic: {filename}.txt")
                    
                    except Exception as e:
                        print(f"Error processing topic {topic_id}: {e}")
            
            except Exception as e:
                print(f"Error scraping page {page}: {e}")


if __name__ == "__main__":
    # Swift documentation URLs
    swift_urls = [
        # Swift language guide sections
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/thebasics",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/basicoperators",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/stringsandcharacters",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/collectiontypes",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/controlflow",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/functions",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/closures",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/enumerations",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/structures-and-classes",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/properties",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/methods",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/inheritance",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/initialization",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/deinitialization",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/optionalchaining",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/errorhandling",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/types",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/patterns",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/generics",
        
        # SwiftUI basics
        "https://developer.apple.com/documentation/swiftui/app",
        "https://developer.apple.com/documentation/swiftui/view",
        "https://developer.apple.com/documentation/swiftui/text",
        "https://developer.apple.com/documentation/swiftui/image",
        "https://developer.apple.com/documentation/swiftui/button",
        "https://developer.apple.com/documentation/swiftui/state",
        "https://developer.apple.com/documentation/swiftui/binding",
        "https://developer.apple.com/documentation/swiftui/environment",
        "https://developer.apple.com/documentation/swiftui/environmentobject",
        "https://developer.apple.com/documentation/swiftui/navigationlink",
        "https://developer.apple.com/documentation/swiftui/form",
        "https://developer.apple.com/documentation/swiftui/list",
        "https://developer.apple.com/documentation/swiftui/navigationview",
        "https://developer.apple.com/documentation/swiftui/tabview",
        
        # UIKit basics for iOS
        "https://developer.apple.com/documentation/uikit/uiviewcontroller",
        "https://developer.apple.com/documentation/uikit/uiview",
        "https://developer.apple.com/documentation/uikit/uitableview",
        "https://developer.apple.com/documentation/uikit/uicollectionview",
        "https://developer.apple.com/documentation/uikit/uibutton",
        "https://developer.apple.com/documentation/uikit/uitextfield",
        "https://developer.apple.com/documentation/uikit/uitableviewcontroller",
        
        # Common Swift errors and troubleshooting
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/_compiling-and-debugging-guide",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/attributes"
    ]
    
    scraper = SwiftDocumentationScraper()
    
    # Scrape regular documentation pages
    scraper.scrape_urls(swift_urls, selector="#main-content, article, .documentation-container, .content")
    
    # Scrape Swift forums for common issues and solutions
    scraper.scrape_swift_forums(num_pages=3)
    
    # Add common Swift and Xcode error guide
    common_errors = """
# Common Swift and Xcode Errors and Solutions

## 1. "Cannot find type in scope" Error

**Problem:**
```
Cannot find type 'X' in scope
```

**Causes:**
- Missing import statements
- Type name misspelled
- Type not defined in the project
- Access control issues (private or internal types)

**Solutions:**
- Check import statements at the top of the file
- Verify type name spelling and case sensitivity
- Make sure the type is defined in your project or in an imported framework
- Check access control modifiers (private, internal, public)

## 2. "Value of type 'X' has no member 'Y'" Error

**Problem:**
```
Value of type 'X' has no member 'Y'
```

**Causes:**
- Trying to access a property or method that doesn't exist
- Typo in property or method name
- Extension defining the property/method not imported
- Wrong type inference

**Solutions:**
- Check documentation for correct property/method names
- Verify spelling of the property/method
- Ensure all necessary extensions are imported
- Use explicit type annotations to confirm the correct type

## 3. Thread-related crashes ("Main thread checker: UI API called on a background thread")

**Problem:**
App crashes with "Main thread checker: UI API called on a background thread" warning

**Causes:**
- Attempting to update UI elements from a background thread

**Solutions:**
- Dispatch UI updates to the main thread:
```swift
DispatchQueue.main.async {
    // UI code here
}
```

## 4. Memory leaks and retain cycles

**Problem:**
Memory usage grows over time, objects not being deallocated

**Causes:**
- Strong reference cycles (especially in closures)
- Not using weak/unowned references appropriately

**Solutions:**
- Use weak or unowned references in closures:
```swift
weak var weakSelf = self
closure = { [weak self] in
    guard let self = self else { return }
    // Use self safely here
}
```

## 5. "Unexpectedly found nil while unwrapping an Optional value" Error

**Problem:**
Runtime crash with "Unexpectedly found nil while unwrapping an Optional value"

**Causes:**
- Force unwrapping (!) an optional that contains nil
- Implicitly unwrapped optionals that are nil

**Solutions:**
- Use optional binding (if let, guard let)
- Use nil coalescing operator (??)
- Use optional chaining (?.)
```swift
// Instead of: let value = optionalValue!
// Use:
if let value = optionalValue {
    // Use value safely here
}
// Or:
guard let value = optionalValue else {
    // Handle nil case
    return
}
// Or:
let value = optionalValue ?? defaultValue
```

## 6. Build Errors: "No such module"

**Problem:**
```
No such module 'ModuleName'
```

**Causes:**
- Framework not properly linked
- Missing import statement
- CocoaPods/SPM/Carthage issue
- Clean build folder needed

**Solutions:**
- Check Target > General > Frameworks/Libraries
- Clean the build folder (Cmd+Shift+K)
- Close and reopen Xcode
- Reset package caches for SPM
- For CocoaPods: pod deintegrate && pod install

## 7. "Expression was too complex to be solved in reasonable time" Error

**Problem:**
```
Expression was too complex to be solved in reasonable time
```

**Causes:**
- Type inference with complex expressions
- Long chains of operations

**Solutions:**
- Break expressions into smaller parts
- Add explicit type annotations
- Store intermediate results in variables

## 8. Xcode "Command failed with exit code" Errors

**Problem:**
Build fails with "Command failed with exit code"

**Causes:**
- Previous build artifacts interfering
- Permissions issues
- Resource conflicts

**Solutions:**
- Clean build folder (Cmd+Shift+K)
- Delete derived data (~/Library/Developer/Xcode/DerivedData)
- Restart Xcode and/or computer

## 9. SwiftUI Preview Not Working

**Problem:**
SwiftUI previews not displaying or constantly refreshing

**Causes:**
- Build errors in the project
- Heavy resource usage
- Xcode bugs

**Solutions:**
- Check for build errors in the project
- Simplify preview content
- Use basic PreviewProvider
- Restart Xcode

## 10. "Use of unresolved identifier" Error

**Problem:**
```
Use of unresolved identifier 'X'
```

**Causes:**
- Variable or function not defined
- Typo in variable/function name
- Out of scope variable/function
- Missing import

**Solutions:**
- Check spelling of the identifier
- Ensure variable is defined before use
- Check scope (e.g., local variables in if/else blocks)
- Add missing import statements
"""
    
    scraper.save_swift_guide(common_errors, "common_swift_errors")
    
    # Add Xcode debugging guide
    xcode_debugging = """
# Xcode Debugging Guide

## Breakpoints

### Setting Breakpoints
- Click in the gutter (left margin) of your code editor
- Use keyboard shortcut: Cmd+\
- Add conditions to breakpoints by right-clicking and selecting "Edit Breakpoint..."

### Types of Breakpoints
1. **Line Breakpoint**: Stops execution at a specific line
2. **Symbolic Breakpoint**: Breaks when a specific method/function is called
3. **Exception Breakpoint**: Breaks when an exception is thrown
4. **Runtime Issue Breakpoint**: Breaks on runtime issues like memory leaks

### Exception Breakpoints
To catch Swift errors before they crash your app:
1. Open Breakpoint Navigator (Cmd+7)
2. Click + at bottom left
3. Choose "Exception Breakpoint"
4. Leave settings at default to catch all exceptions

## LLDB Debugging Commands

Common LLDB commands in the debug console:

- `po object` - Print description of an object
- `p expression` - Print result of expression
- `expr value = 10` - Change a value during debugging
- `bt` - Show backtrace/call stack
- `frame variable` - Show all variables in current frame
- `continue` or `c` - Continue execution
- `step` or `s` - Step into
- `next` or `n` - Step over
- `finish` - Step out

## Memory Graph Debugger

To find memory leaks and retain cycles:
1. Run your app
2. Perform actions that might create leaks
3. Click Debug Memory Graph button in debug area
4. Look for objects with exclamation marks

## View Debugging

To inspect view hierarchies:
1. Run your app
2. Click Debug View Hierarchy button in debug area
3. Inspect 3D view hierarchy, constraints, and properties

## Instruments

For deeper performance analysis:
1. Product > Profile (Cmd+I)
2. Choose an instrument:
   - Time Profiler: CPU usage
   - Allocations: Memory usage
   - Leaks: Memory leaks
   - Network: Network activity

## Console Logging

### Basic print
```swift
print("Variable value: \(variable)")
```

### OS Log (Better for Production)
```swift
import os.log

let logger = Logger(subsystem: "com.yourcompany.appname", category: "networking")
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

## Debugging SwiftUI

### Print View Lifecycle Events
```swift
.onAppear { print("View appeared") }
.onDisappear { print("View disappeared") }
.onChange(of: someValue) { oldValue, newValue in 
    print("Value changed from \(oldValue) to \(newValue)") 
}
```

### Preview Different States
```swift
struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        Group {
            ContentView(isLoading: true)
                .previewDisplayName("Loading State")
            
            ContentView(isLoading: false)
                .previewDisplayName("Loaded State")
            
            ContentView(hasError: true)
                .previewDisplayName("Error State")
        }
    }
}
```

## Common Debugging Tips

1. **Bisect Problems**: Comment out half your code, then half again until you find the problematic section

2. **Use Assertions**: Add debug-only checks
```swift
assert(index < array.count, "Index out of bounds")
```

3. **Debug Build Configuration**:
```swift
#if DEBUG
    print("Debug-only code")
#endif
```

4. **Symbolicate Crash Logs**:
   - Window > Devices and Simulators
   - Select your device
   - View Device Logs
   - Drag .dSYM files to symbolicate

5. **Network Debugging**:
   - Enable OS_ACTIVITY_MODE in scheme environment variables
   - Use Charles Proxy or Proxyman to inspect network traffic
"""
    
    scraper.save_swift_guide(xcode_debugging, "xcode_debugging_guide")
    
    print("Swift documentation scraping complete!")
